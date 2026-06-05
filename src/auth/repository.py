from sqlalchemy import select

from src.auth.models import User
from src.database import async_session


class UserRepository:
    @classmethod
    async def get_profile(cls, user_id: int):
        async with async_session() as session:
            query = select(User).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.unique().scalars().all()
            return user