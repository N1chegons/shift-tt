from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.room.utils import created_rooms_and_slots
from src.user.router import router as user_router
from src.room.router import router as room_router
from src.admin.router import router as admin_router

# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await created_rooms_and_slots()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Booking meeting rooms",
    description="Test task for SHIFT",
)

app.include_router(user_router)
app.include_router(room_router)
app.include_router(admin_router)
app.include_router(auth_router)