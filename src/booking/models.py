import datetime
import enum

from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

class Slots(enum.Enum):
    morning = "09:00–11:00"
    lunch = "12:00-14:00"
    afternoon = "15:00-17:00"
    evening = "18:00-20:00"
    night = "21:00-23:00"

class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    slot: Mapped[Slots] = mapped_column(nullable=True)
    booking_date: Mapped[datetime.date] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text(
            "TIMEZONE('utc', now())")
    )
    cancelled_at: Mapped[datetime.datetime] = mapped_column(nullable=True)

    users_booking:  Mapped[list["User"]] = relationship(
        back_populates="room"
    )

from src.auth.models import User
