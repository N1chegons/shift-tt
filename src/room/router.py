import datetime

from fastapi import APIRouter, status, HTTPException, Depends, Query

from src.auth.models import User
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
        rooms_view = [RoomRead.model_validate(room) for room in rooms]

        if not rooms:
            logger.warning("Rooms unfounded")
            return {"message": "Комнат не найдено"}

        logger.info(f"User {user.id} viewed list of rooms")
        return {"status": 200, "Rooms": rooms_view}

    except Exception as e:
        logger.error(f"Error on receipt {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неизвестная ошибка")

@router.get("/get_free_rooms/{rooms_id}", summary="Получение свободных слотов времени у определенной переговорной комнаты")
async def get_free_rooms(rooms_id: int, date: datetime.date = Query(default=datetime.date.today(), description="Формат ГГГГ-ММ-ДД"), user: User = Depends(cur_user)):
    try:
        free_slots = await BookingRepository.get_bookings(rooms_id, date)

        if date < datetime.date.today():
            logger.warning("Date is less than today")
            return {"message": "Бронирование переговорных комнат не может быть в прошлом"}

        if not free_slots:
            logger.warning("Rooms unfounded")
            return {"message": f"Нету свободных слотов времени к переговорной комнате {rooms_id}"}

        logger.info(f"User {user.id} viewed free rooms")
        return {"status": 200, "message":f"Свободные слоты для переговорной комнаты номер {rooms_id} на {date}", "Slots": [SlotRead.model_validate(slot) for slot in free_slots]}

    except Exception as e:
        logger.error(f"Error on receipt {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неизвестная ошибка")

@router.post("/to_book_room", summary="Забронировать переговорную комнаты")
async def to_book_room(booked_schema: BookingCreate = Depends(), user: User = Depends(cur_user)):
    try:
        free_slot = await BookingRepository.slot_is_free(booked_schema.slot_id, booked_schema.date)
        if free_slot:
            logger.warning(f"Room already booked for this time")
            return {"message": f"Комната уже забронирована на это время"}

        schema = booked_schema.model_dump()
        booked_room = await BookingRepository.create_booking(schema, user.id)
        booked_details = await BookingRepository.get_booking_details(booked_room)

        return {"status": 204, "message": booked_details}

    except Exception as e:
        logger.error(f"Error on booking {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неизвестная ошибка")
