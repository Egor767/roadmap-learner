from typing import Optional, TYPE_CHECKING

from fastapi_users import BaseUserManager

from app.core.config import settings
from app.core.logging import user_manager_logger as logger
from app.core.types import BaseIdType
from app.models import User
from app.models.mixins import IdMixin

if TYPE_CHECKING:
    from fastapi import Request


class UserManager(IdMixin, BaseUserManager[User, BaseIdType]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(
        self,
        user: User,
        request: Optional["Request"] = None,
    ):
        logger.info(
            "User %r has registered.",
            user.id,
        )

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        logger.info(
            "User %r has forgot their password. Reset token: %r",
            user.id,
            token,
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        logger.info(
            f"Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )
