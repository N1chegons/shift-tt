from fastapi import APIRouter, Depends, HTTPException, status

from src.user.repository import UserRepository
from src.auth.router import cur_user
from src.user.schemas import ProfileRead, UpdateUser
from src.user.models import User
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
    user_profile = await UserRepository.get_profile(user.id)
    alr = [ProfileRead.model_validate(p) for p in user_profile]
    try:
        logger.info(f"The user {user.id} viewed the profile")
        return {
            "status": 200,
            "Profile": alr,
        }

    except Exception as e:
        logger.error(f"Error on receipt {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.patch("/update_user", summary="Обновление данных пользователя")
async def update_user_info(update_schema: UpdateUser = Depends(), user: User = Depends(cur_user)):
    try:
        schema = update_schema.model_dump(exclude_unset=True)
        data = {k: v for k, v in schema.items() if v is not None}

        if not data:
            logger.warning(f"The user {user.id} did not fill in the data for the change")
            return {"detail": "Поля не заполнены, нет данных для изменения"}

        await UserRepository.update_user(user.id, data)

        logger.info(f"The user {user.id} was updated his info")
        return {"status": 200, "detail": "Данные успешно обновлены"}

    except Exception as e:
        logger.error(f"Error on updated {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.get("/get_user_reservation", summary="Просмотр броней пользователя")
async def get_reservations(user: User = Depends(cur_user)):
    try:
        logger.info(f"The user {user.id} viewed the reservations")
        reservations = await BookingRepository.get_bookings_by_user_id(user.id)

        if not reservations:
            logger.warning(f"The user's reservation was not found")
            return {"message": "У вас нету активных броней"}

        logger.info(f"The user {user.id} viewed his reservations")
        return {"status": 200, "detail": "Ваши активные брони", "Reservations": reservations}

    except Exception as e:
        logger.error(f"Error on receipt {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.delete("/delete_user_reservation/{booking_id}", summary="Отмена брони пользователя")
async def delete_reservation(booking_id: int, user: User = Depends(cur_user)):
    try:
        del_reservation = await BookingRepository.delete_booking(user.id, booking_id)

        logger.info(f"The user {user.id} cancelled the reservation with id={booking_id}")
        return {"status": 200, "message": f"Бронь {booking_id} отменена"}

    except Exception as e:
        logger.error(f"Error on deleted {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.delete("/delete_user_resercvations", summary="Отменить все активные брони пользователя")
async def delete_reservations(user: User = Depends(cur_user)):
    try:
        del_reservations = await BookingRepository.delete_all_bookings(user.id)
        if not del_reservations:
            logger.warning(f"The user's reservation was not found")
            return {"message": "У вас нету активных броней для удаления"}

        return {"status": 200, "detail": "Все ваши брони были отменены"}

    except Exception as e:
        logger.error(f"Error on deleted {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

