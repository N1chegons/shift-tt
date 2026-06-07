from sqlalchemy import update, select

from src.database import async_session
from src.user.models import User


class AdminRepository:
    @classmethod
    async def become_admin(cls, user_id: int):
        async with async_session() as session:
            stmt = update(User).values(is_superuser=True).filter_by(id=user_id)
            await session.execute(stmt)
            await session.commit()