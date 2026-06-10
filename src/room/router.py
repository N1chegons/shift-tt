import datetime

from fastapi import APIRouter, status, HTTPException, Depends, Query

from src.user.models import User
from src.auth.router import cur_user
from src.logger_config import setup_logging, get_logger
from src.room.repository import RoomRepository, BookingRepository
from src.room.schemas import RoomRead, SlotRead, BookingCreate

setup_logging()
logger = get_logger(__name__)

router = APIRouter(
    prefix="/room",
    tags=["Room"],
)

@router.get("/get_rooms", summary="Получение всех доступных переговорных комнат")
async def get_rooms_list(user: User = Depends(cur_user)):
    try:
        rooms = await RoomRepository.get_rooms()
        if not rooms:
            logger.warning("Rooms unfounded")
            return {"detail": "Комнат не найдено"}

        logger.info(f"User {user.id} viewed list of rooms")
        return {"status": 200, "Rooms": [RoomRead.model_validate(room) for room in rooms]}

    except Exception as e:
        logger.error(f"Error on receipt {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неизвестная ошибка")

@router.get("/get_rooms_slots/{room_id}", summary="Получение свободных слотов времени у определенной переговорной комнаты")
async def get_free_slots(room_id: int, date: datetime.date = Query(default=datetime.date.today(), description="Формат ГГГГ-ММ-ДД"), user: User = Depends(cur_user)):
    try:
        free_slots = await BookingRepository.get_bookings(room_id, date)

        if date < datetime.date.today():
            logger.warning("Date is less than today")
            return {"detail": "Бронирование переговорных комнат не может быть в прошлом"}

        if not free_slots:
            logger.warning("Rooms unfounded")
            return {"detail": f"Нету свободных слотов времени к переговорной комнате {room_id}"}

        logger.info(f"User {user.id} viewed free rooms")
        return {"status": 200, "detail": f"Свободные слоты для переговорной комнаты номер {room_id} на {date}", "Slots": [SlotRead.model_validate(slot) for slot in free_slots]}

    except Exception as e:
        logger.error(f"Error on receipt {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неизвестная ошибка")

@router.post("/to_book_room", summary="Забронировать переговорную комнаты")
async def to_book_room(booked_schema: BookingCreate, user: User = Depends(cur_user)):
    try:
        free_slot = await BookingRepository.slot_is_free(booked_schema.slot_id, booked_schema.date)
        if free_slot:
            logger.warning(f"Room already booked for this time")
            return {"detail": f"Комната уже забронирована на это время"}

        if not free_slot:
            logger.warning(f"Slot {booked_schema.slot_id} unfounded")
            return {"details": f"Слот {booked_schema.slot_id} не найден"}

        schema = booked_schema.model_dump()
        booked_room = await BookingRepository.create_booking(schema, user.id)

        booked_details = await BookingRepository.get_booking_details(booked_room)

        return {"status": 204, "detail": f"Бронь {booked_details.booking_id} создана. Переговорная комната «{booked_details.room_name}» забронирована на {booked_details.date.isoformat()} с {booked_details.start_time}-{booked_details.end_time}"}

    except Exception as e:
        logger.error(f"Error on booking {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неизвестная ошибка")
