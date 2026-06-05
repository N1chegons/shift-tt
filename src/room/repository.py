import datetime

from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from src.auth.models import User
from src.room.models import Slot, Room, Booking
from src.database import async_session


class RoomRepository:
    @classmethod
    async def get_rooms(cls):
        async with async_session() as session:
            query = select(Room).options(selectinload(Room.slots_room))
            result = await session.execute(query)
            rooms = result.scalars().all()
            return rooms

    @classmethod
    async def create_room(cls, name: str):
        async with async_session() as session:
            stmt = insert(Room).values(name=name).returning(Room)
            result = await session.execute(stmt)
            await session.commit()
            room = result.scalar_one()
            return room

class SlotRepository:
    @classmethod
    async def get_slots(cls):
        async with async_session() as session:
            query = select(Slot)
            result = await session.execute(query)
            slots = result.scalars().all()
            return slots

    @classmethod
    async def create_slot(cls, schema: dict):
        async with async_session() as session:
            stmt = insert(Slot).values(**schema).returning(Slot)
            result = await session.execute(stmt)
            await session.commit()
            slot = result.scalar_one()
            return slot

class BookingRepository:
    @classmethod
    async def get_bookings(cls, room_id: int, date: datetime.date):
        async with async_session() as session:
            stmt = (
                select(Slot)
                .filter_by(room_id=room_id)
                .outerjoin(
                    Booking,
                    (Slot.id == Booking.slot_id) & (Booking.date == date)
                )
                .where(Booking.id.is_(None))
            )
            result = await session.execute(stmt)
            free_slots = result.scalars().all()
            return free_slots

    @classmethod
    async def get_bookings_by_user_id(cls, user_id: int):
        async with async_session() as session:
            query = (
                select(
                    Booking.id.label("booking_id"),
                    Booking.date,
                    Room.name.label("room_name"),
                    Slot.start_time,
                    Slot.end_time,
                    Slot.room_id
                )
                .join(Slot, Booking.slot_id == Slot.id)
                .join(Room, Slot.room_id == Room.id)
                .where(Booking.user_id == user_id)
                .order_by(Booking.date, Slot.start_time)
            )

            result = await session.execute(query)
            bookings = result.all()

            return [
                {
                    "booking_id": row.booking_id,
                    "room_id": row.room_id,
                    "room_name": row.room_name,
                    "time": f"{row.start_time}-{row.end_time}",
                    "date": row.date.isoformat(),
            }
                for row in bookings
            ]

    @classmethod
    async def slot_is_free(cls, slot_id: int, date: datetime.date):
        async with async_session() as session:
            query = select(Booking).filter_by(slot_id=slot_id, date=date)
            result = await session.execute(query)
            booking = result.scalars().one_or_none()
            return booking

    @classmethod
    async def get_booking_details(cls, booking_id: int):
        async with async_session() as session:
            query = (
                select(
                    Booking.id.label("booking_id"),
                    Booking.date,
                    Room.name.label("room_name"),
                    Slot.start_time,
                    Slot.end_time
                )
                .join(Slot, Booking.slot_id == Slot.id)
                .join(Room, Slot.room_id == Room.id)
                .where(Booking.id == booking_id)
            )

            result = await session.execute(query)
            details = result.first()

            return f"Бронь {details.booking_id} создана. Переговорная комната «{details.room_name}» забронирована на {details.date.isoformat()} с {details.start_time}-{details.end_time}"

    @classmethod
    async def create_booking(cls, schema: dict, user_id: int):
        async with async_session() as session:
            stmt = insert(Booking).values(**schema, user_id=user_id).returning(Booking.id)
            result = await session.execute(stmt)
            await session.commit()
            booking = result.scalar_one()
            return booking
