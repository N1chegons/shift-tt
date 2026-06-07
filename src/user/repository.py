from sqlalchemy import select, update

from src.user.models import User
from src.database import async_session


class UserRepository:
    @classmethod
    async def get_profile(cls, user_id: int):
        async with async_session() as session:
            query = select(User).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.unique().scalars().all()
            return user

    @classmethod
    async def update_user(cls, user_id: int, values: dict) -> bool:
        async with async_session() as session:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(**values)
                .returning(User.id)
            )
            await session.execute(stmt)
            await session.commit()