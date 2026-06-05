from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select, update

from src.auth.repository import UserRepository
from src.auth.router import cur_user
from src.auth.schemas import ProfileRead
from src.database import async_session
from src.auth.models import User
from src.logger_config import setup_logging, get_logger
from src.room.repository import BookingRepository

setup_logging()
logger = get_logger(__name__)

router = APIRouter(
    tags=["User"],
    prefix="/user"
)

@router.get("/profile", summary="Просмотр профиля пользователя")
async def get_profile_rep(user: User = Depends(cur_user)):
    user = await UserRepository.get_profile(user_id=user.id)
    alr = [ProfileRead.model_validate(p) for p in user]
    try:
        logger.info(f"The user {user.id} viewed the profile")
        return {
            "status": 200,
            "Profile": alr,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.get("/my_reservations", summary="Просмотр броней пользователя")
async def get_my_reservations(user: User = Depends(cur_user)):
    reservations = await BookingRepository.get_bookings_by_user_id(user_id=user.id)
    return reservations

@router.put("/change_data", summary="Change user data")
async def change_data_for_user(new_username: str, new_surname: str, new_email: EmailStr, user: User = Depends(cur_user)):
    async with async_session() as session:
        query = select(User).filter_by(id=user.id)
        result = await session.execute(query)
        res = result.unique().scalars().all()
        # noinspection PyBroadException
        try:
            if res:
                stmt = (
                    update(User)
                    .values(username=new_username, surname=new_surname, email=new_email)
                    .filter_by(id=user.id)
                )
                await session.execute(stmt)
                await session.commit()

                return {
                    "status": 200,
                    "message": "Данные успешно обновлены"
                }
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователь с ID {res.id} не найден")

        except:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Проверьте поля на корректность")
