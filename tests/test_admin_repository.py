import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text, select

from src.user.models import User
from src.admin.repository import AdminRepository
from src.database import Base
import src.database

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test_db"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    test_engine = create_async_engine(TEST_DB_URL)

    async with test_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)

    original_engine = src.database.async_engine
    original_session = src.database.async_session

    src.database.async_engine = test_engine
    src.database.async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    import importlib
    importlib.reload(src.admin.repository)

    async with src.database.async_session() as session:
        yield session

    src.database.async_engine = original_engine
    src.database.async_session = original_session
    importlib.reload(src.admin.repository)

    await test_engine.dispose()

@pytest.mark.asyncio
async def test_become_admin(db_session: AsyncSession):
    user = User(
        username="simpleuser",
        surname="Обычный",
        email="user@test.com",
        hashed_password="hash123",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    assert user.is_superuser is False

    await AdminRepository.become_admin(user.id)

    await db_session.refresh(user)

    assert user.is_superuser is True


@pytest.mark.asyncio
async def test_become_admin_already_admin(db_session: AsyncSession):
    user = User(
        username="adminuser",
        surname="Админ",
        email="admin@test.com",
        hashed_password="hash123",
        is_active=True,
        is_superuser=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    assert user.is_superuser is True

    await AdminRepository.become_admin(user.id)

    await db_session.refresh(user)

    assert user.is_superuser is True


@pytest.mark.asyncio
async def test_become_admin_user_not_exists(db_session: AsyncSession):
    await AdminRepository.become_admin(99999)

    users = await db_session.execute(select(User).filter_by(id=99999))
    assert users.first() is None