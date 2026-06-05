from sqlalchemy.exc import IntegrityError

from src.auth.router import fastapi_users
from asyncpg import UniqueViolationError
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.params import Query

from src.auth.models import User
from src.logger_config import setup_logging, get_logger
from src.room.repository import RoomRepository, SlotRepository
from src.room.schemas import SlotCreate

setup_logging()
logger = get_logger(__name__)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)
admin_user = fastapi_users.current_user(superuser=True)

@router.post("/create_room", summary="Создание переговорной комнаты")
async def create_room(user: User = Depends(admin_user), name: str = Query(min_length=1, max_length=100)):
    try:
        new_room = await RoomRepository.create_room(name=name)

        logger.info(f"User {user.id} created room {new_room.name}")
        return {"status": 204, "message": f"Комната {name} успешно создана"}

    except UniqueViolationError:
        logger.warning(f"Room {name} already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Переговорная с названием {name} уже создана")

    except Exception as e:
        logger.error(f"Error on creation {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неизвестная ошибка")

@router.post("/create_slot", summary="Создание слотов к определенной переговорной комнате")
async def create_slot(slot_schema: SlotCreate = Depends(), user: User = Depends(admin_user)):
    try:
        schema = slot_schema.model_dump()
        new_slot = await SlotRepository.create_slot(schema)

        logger.info(f"Admin {user.id} created slot {new_slot.start_time}-{new_slot.end_time} for room id {new_slot.room_id}")
        return {"status": 204, "message": f"Слот с интервалом {new_slot.start_time}-{new_slot.end_time} для комнаты {new_slot.room_id} успешно создан"}

    except IntegrityError:
        logger.warning(f"Room {slot_schema.room_id} unfounded")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Комната с ID {slot_schema.room_id} не найдена")

    except Exception as e:
        logger.error(f"Error on creation {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Неизвестная ошибка")
