import datetime

from pydantic import BaseModel, ConfigDict, Field

# SLOT
class SlotRead(BaseModel):
    id: int
    start_time: str = Field(max_length=5, min_length=5, default="00:00")
    end_time: str = Field(max_length=5, min_length=5, default="00:00")

    model_config = ConfigDict(from_attributes=True)

# ROOM
class RoomRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

# BOOKING
class BookingCreate(BaseModel):
    slot_id: int
    date: datetime.date = Field(default=datetime.date.today())

class BookingRead(BaseModel):
    id: int
    user: str
    room: str
    time: str
    date: str
    user_id: int
    room_id: int