import datetime

from fastapi_users import schemas
from pydantic import EmailStr, field_validator, BaseModel, ConfigDict

class ProfileRead(BaseModel):
    id: int
    username: str
    surname: str
    email: EmailStr
    registered_at: datetime.datetime

    # noinspection PyMethodParameters
    @field_validator('registered_at')
    def custom(cls, v):
        return datetime.datetime.strftime(v, "%m.%d.%Y %H:%M")

    model_config = ConfigDict(from_attributes=True)


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    surname: str
    email: EmailStr
    hashed_password: str
    registered_at: datetime.datetime
    is_active: bool
    is_superuser: bool
    is_verified: bool
    
    # noinspection PyMethodParameters
    @field_validator('registered_at')
    def custom(cls, v):
        return datetime.datetime.strftime(v, "%m.%d.%Y")

class UserCreate(schemas.BaseUserCreate):
    username: str
    surname: str
    password: str
    email: EmailStr

class UpdateUser(BaseModel):
    username: str | None = None
    surname: str | None = None
    email: EmailStr | None = None
