from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.auth.user_router import router as user_router
from src.room.router import router as room_router
from src.admin.router import router as admin_router

app = FastAPI(
    title="Booking meeting rooms",
    description="Test task for SHIFT",
)

app.include_router(user_router)
app.include_router(room_router)
app.include_router(admin_router)
app.include_router(auth_router)