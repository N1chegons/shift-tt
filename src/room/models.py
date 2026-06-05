import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.auth.models import User

class Slot(Base):
    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    start_time: Mapped[str] = mapped_column(nullable=False)
    end_time: Mapped[str] = mapped_column(nullable=False)

    room: Mapped["Room"] = relationship(back_populates="slots_room")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="slot")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    slots_room: Mapped[list["Slot"]] = relationship(back_populates="room")

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    slot_id: Mapped[int] = mapped_column(ForeignKey("slots.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    date: Mapped[datetime.date] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text(
            "TIMEZONE('utc', now())")
    )

    slot: Mapped["Slot"] = relationship(back_populates="bookings")
    booked: Mapped["User"] = relationship(back_populates="user_bookings")
