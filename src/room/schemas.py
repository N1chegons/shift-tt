import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

# SLOT
class SlotBase(BaseModel):
    id: int

class SlotRead(SlotBase):
    start_time: str = Field(max_length=5, min_length=5, default="00:00")
    end_time: str = Field(max_length=5, min_length=5, default="00:00")

    model_config = ConfigDict(from_attributes=True)

class SlotCreate(BaseModel):
    room_id: int
    start_time: str = Field(max_length=5, min_length=5, default="00:00")
    end_time: str = Field(max_length=5, min_length=5, default="00:00")

    model_config = ConfigDict(from_attributes=True)
# ROOM
class RoomRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

# BOOKING
class BookingRead(BaseModel):
    id: int
    user_id: int
    room_id: int
    start_time: str

class BookingCreate(BaseModel):
    slot_id: int
    date: datetime.date = Field(default=datetime.date.today(), description="Формат ГГГГ-ММ-ДД")
