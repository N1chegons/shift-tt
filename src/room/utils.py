from src.database import async_session
from src.logger_config import setup_logging, get_logger
from src.room.models import Room, Slot
from sqlalchemy import select

setup_logging()
logger = get_logger(__name__)

async def created_rooms_and_slots():
    async with async_session() as session:
        result = await session.execute(select(Room))
        rooms = result.scalars().all()

        if rooms:
            logger.warning("Rooms already exist")
            return

        logger.info("Creating rooms")

        room_a = Room(name="Переговорная А")
        room_b = Room(name="Переговорная Б")
        room_c = Room(name="Переговорная В")

        session.add_all([room_a, room_b, room_c])
        await session.flush()

        time_slots = [
            ("10:00", "12:00"), ("13:00", "15:00"), ("16:00", "18:00"),
            ("19:00", "21:00")
        ]

        slots = []
        for room in [room_a, room_b, room_c]:
            for start, end in time_slots:
                slots.append(Slot(room_id=room.id, start_time=start, end_time=end))

        session.add_all(slots)
        await session.commit()

        logger.info(f"Created {len([room_a, room_b, room_c])} rooms and {len(slots)} slots")