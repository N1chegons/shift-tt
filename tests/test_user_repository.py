import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from src.user.models import User
from src.user.repository import UserRepository
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
    importlib.reload(src.user.repository)

    async with src.database.async_session() as session:
        yield session

    src.database.async_engine = original_engine
    src.database.async_session = original_session
    importlib.reload(src.user.repository)

    await test_engine.dispose()

@pytest.mark.asyncio
async def test_get_profile(db_session: AsyncSession):
    user = User(
        username="testuser",
        surname="Тестов",
        email="test@test.com",
        hashed_password="hash123",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    result = await UserRepository.get_profile(user.id)

    assert len(result) == 1
    assert result[0].username == "testuser"
    assert result[0].email == "test@test.com"
    assert result[0].surname == "Тестов"


@pytest.mark.asyncio
async def test_get_profile_not_found(db_session: AsyncSession):
    result = await UserRepository.get_profile(99999)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    user = User(
        username="olduser",
        surname="Старый",
        email="old@test.com",
        hashed_password="hash123",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    old_username = user.username
    old_surname = user.surname
    old_email = user.email

    new_values = {
        "username": "newuser",
        "surname": "Новый",
        "email": "new@test.com"
    }

    await UserRepository.update_user(user.id, new_values)

    await db_session.refresh(user)

    assert user.username != old_username
    assert user.username == "newuser"
    assert user.surname != old_surname
    assert user.surname == "Новый"
    assert user.email != old_email
    assert user.email == "new@test.com"


@pytest.mark.asyncio
async def test_update_user_partial(db_session: AsyncSession):
    user = User(
        username="partialuser",
        surname="Частичный",
        email="partial@test.com",
        hashed_password="hash123",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()

    old_username = user.username
    old_surname = user.surname
    old_email = user.email

    new_values = {
        "username": "updateduser"
    }

    await UserRepository.update_user(user.id, new_values)

    await db_session.refresh(user)

    assert user.username != old_username
    assert user.username == "updateduser"
    assert user.surname == old_surname
    assert user.email == old_email


@pytest.mark.asyncio
async def test_update_user_not_found(db_session: AsyncSession):
    new_values = {"username": "nonexistent"}

    await UserRepository.update_user(99999, new_values)

    users = await UserRepository.get_profile(99999)
    assert len(users) == 0