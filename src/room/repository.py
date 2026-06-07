import datetime
from typing import Optional

from sqlalchemy import insert, select, delete, update
from sqlalchemy.orm import selectinload

from src.user.models import User
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

class SlotRepository:
    @classmethod
    async def is_slot(cls, slot_id: int):
        async with async_session() as session:
            query = select(Slot).filter_by(id=slot_id)
            result = await session.execute(query)
            slot = result.one_or_none()
            return slot

    @classmethod
    async def get_slots(cls):
        async with async_session() as session:
            query = select(Slot)
            result = await session.execute(query)
            slots = result.scalars().all()
            return slots

class BookingRepository:
    @classmethod
    async def is_booking(cls, booking_id: int):
        async with async_session() as session:
            query = select(Booking).filter_by(id=booking_id)
            result = await session.execute(query)
            booking = result.one_or_none()
            return booking

    @classmethod
    async def is_bookings(cls):
        async with async_session() as session:
            query = select(Booking)
            result = await session.execute(query)
            booking = result.all()
            return booking

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
                    "booking_id": reservation.booking_id,
                    "room_id": reservation.room_id,
                    "room_name": reservation.room_name,
                    "booking": f"{reservation.date.strftime('%d.%m.%Y')} {reservation.start_time}-{reservation.end_time}",
            }
                for reservation in bookings
            ]

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
            return details

    @classmethod
    async def get_bookings_for_admin(cls, date: Optional[datetime.date] = None, page: int = 1, limit: int = 10):
        async with async_session() as session:
            offset_value = (page - 1) * limit
            query = (
                select(
                    Booking.id,
                    Booking.date,
                    User.username,
                    User.surname,
                    User.id.label("user_id"),
                    Room.name.label("room_name"),
                    Room.id.label("room_id"),
                    Slot.start_time,
                    Slot.end_time
                )
                .join(Slot, Booking.slot_id == Slot.id)
                .join(Room, Slot.room_id == Room.id)
                .join(User, Booking.user_id == User.id)
                .order_by(Booking.date.desc(), Slot.start_time)
                .offset(offset_value)
                .limit(limit)
            )

            if date:
                query = query.filter(Booking.date == date)

            result = await session.execute(query)
            bookings = result.all()

            return bookings

    @classmethod
    async def create_booking(cls, schema: dict, user_id: int):
        async with async_session() as session:
            slot_id = schema.get("slot_id")
            is_slot = await SlotRepository.is_slot(slot_id)
            if not is_slot:
                return False

            stmt = insert(Booking).values(**schema, user_id=user_id).returning(Booking.id)
            result = await session.execute(stmt)
            await session.commit()
            booking = result.scalar_one()
            return booking

    @classmethod
    async def delete_booking(cls, user_id: int, booking_id: int):
        async with async_session() as session:
            is_booking = await BookingRepository.is_booking(booking_id)
            if not is_booking:
                return False

            stmt = delete(Booking).filter_by(id=booking_id, user_id=user_id)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def delete_all_bookings(cls, user_id: int):
        async with async_session() as session:
            is_bookings = await cls.is_bookings()
            if not is_bookings:
                return False

            stmt = delete(Booking).filter_by(user_id=user_id)
            await session.execute(stmt)
            await session.commit()
            return True

    @classmethod
    async def delete_booking_for_admin(cls, booking_id: int):
        async with async_session() as session:
            is_booking = await cls.is_booking(booking_id)
            if not is_booking:
                return False

            stmt = delete(Booking).filter_by(id=booking_id)
            await session.execute(stmt)
            await session.commit()
            return True

    @classmethod
    async def delete_bookings_for_admin(cls):
        async with async_session() as session:
            is_bookings = await cls.is_bookings()
            if not is_bookings:
                return False

            stmt = delete(Booking)
            await session.execute(stmt)
            await session.commit()
            return True

    @classmethod
    async def slot_is_free(cls, slot_id: int, date: datetime.date):
        async with async_session() as session:
            query = select(Booking).filter_by(slot_id=slot_id, date=date)
            result = await session.execute(query)
            booking = result.scalars().one_or_none()
            return booking

