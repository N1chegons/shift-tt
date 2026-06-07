import datetime

from src.admin.repository import AdminRepository
from src.auth.router import fastapi_users, cur_user
from fastapi import APIRouter, status, HTTPException, Depends

from src.room.schemas import BookingRead
from src.user.models import User
from src.logger_config import setup_logging, get_logger
from src.room.repository import BookingRepository


setup_logging()
logger = get_logger(__name__)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)
admin_user = fastapi_users.current_user(superuser=True)

@router.put("/become_admin_permission", summary="Получение прав адмнистратора (Для теста прав администратора)")
async def become_admin_permission(user: User = Depends(cur_user)):
    try:
        if user.is_superuser:
            return {"detail": "Вы уже являетесь администратором"}

        await AdminRepository.become_admin(user.id)

        logger.info(f"The user {user.id} become admin permission")
        return {"status": 200, "detail": "Вы получили права администратора"}

    except Exception as e:
        logger.error(f"Error on become admin permission {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.get("/get_all_reservations", summary="Просмотр всех броней")
async def get_all_reservations(page: int = 1, limit: int = 10, user: User = Depends(admin_user)):
    try:
        all_reservations = await BookingRepository.get_bookings_for_admin(None, page, limit)

        if not all_reservations:
            logger.warning(f"The reservations was not found")
            return {"detail": f"Нету активных броней"}

        logger.info(f"The admin {user.id} viewed all reservations")
        return {"status": 200, "detail": f"Все активные брони", "Reservations": [BookingRead.model_validate(room) for room in all_reservations]}

    except Exception as e:
        logger.error(f"Error on getting all reservations {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.get("/get_all_reservations/{date}", summary="Просмотр всех броней по определенной дате")
async def get_all_reservations_by_date(date: datetime.date, page: int = 1, limit: int = 10, user: User = Depends(admin_user)):
    try:
        all_reservations = await BookingRepository.get_bookings_for_admin(date, page, limit)

        if not all_reservations:
            logger.warning(f"The reservations was not found")

            if date < datetime.date.today():
                return {"detail": f"Не было активных броней на {date}"}

            return {"detail": f"Нету активных броней на {date}"}

        logger.info(f"The admin {user.id} viewed all reservations")

        if date < datetime.date.today():
            return {"status": 200, "detail": f"История броней на {date.strftime('%d.%m.%Y')}", "Reservations": all_reservations}

        return {"status": 200, "detail": f"Все брони на {date.strftime('%d.%m.%Y')}", "Reservations": all_reservations}

    except Exception as e:
        logger.error(f"Error on getting all reservations {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.delete("/delete_reservation/{booking_id}", summary="Отмена брони")
async def delete_reservations_admin(booking_id: int, user: User = Depends(admin_user)):
    try:
        del_reservation = await BookingRepository.delete_booking_for_admin(booking_id)
        if not del_reservation:
            logger.warning(f"The reservation  was not found")
            return {"message": f"Бронь с booking_id = {booking_id} не найена"}

        logger.info(f"The admin {user.id} cancelled the reservation with id={booking_id}")
        return {"status": 200, "detail": f"Бронь {booking_id} отменена"}

    except Exception as e:
        logger.error(f"Error on deleted {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")

@router.delete("/delete_resercvations", summary="Отменить все активные брони")
async def delete_reservations_admin(user: User = Depends(admin_user)):
    try:
        del_reservations = await BookingRepository.delete_bookings_for_admin()

        if not del_reservations:
            logger.warning(f"The reservations was not found")
            return {"detail": f"Нету активных броней для отмены"}

        logger.info(f"The admin {user.id} cancelled all reservations")
        return {"status": 200, "detail": "Все активные брони были отменены"}

    except Exception as e:
        logger.error(f"Error on deleted {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Неизвестная ошибка: {str(e)}")
