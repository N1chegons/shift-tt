from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager,IntegerIDMixin

from src.user.models import User
from src.config import settings
from src.database import get_user_db
from src.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

SECRET = settings.MANAGER_PASS

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")

    async def on_after_login_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has logged in. Login token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_reset_password(
            self, user: User, request: Request | None = None
    ):
        logger.info(f"User {user.id} has reset their password.")



async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)