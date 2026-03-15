from typing import TYPE_CHECKING, Optional

from fastapi_users import BaseUserManager

from app.core.config import settings
from app.core.custom_types import BaseIdType
from app.core.loggers import user_manager_logger as logger
from app.models import User
from app.models.mixins import IdMixin

if TYPE_CHECKING:
    from fastapi import Request, Response

    from app.models.access_token import SQLAlchemyAccessTokenDatabase
    from app.models.user import SQLAlchemyUserDatabase


class UserManager(IdMixin, BaseUserManager[User, BaseIdType]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    def __init__(self, user_db: "SQLAlchemyUserDatabase", access_tokens_db: "SQLAlchemyAccessTokenDatabase"):
        super().__init__(user_db)
        self.access_tokens_db = access_tokens_db

    async def on_after_login(
        self, user: User, request: Optional["Request"] = None, response: Optional["Response"] = None
    ) -> None:
        logger.info("[on_after_login] user %r logged in", user.id)

        result = await self.access_tokens_db.cleanup_user_tokens(user.id)

        logger.info(
            "[on_after_login] token cleanup result for user %r: %r",
            user.id,
            result,
        )

    async def on_after_register(self, user: User, request: Optional["Request"] = None):
        logger.info(
            "User %r has registered.",
            user.id,
        )

    async def on_after_forgot_password(self, user: User, token: str, request: Optional["Request"] = None):
        logger.info(
            "User %r has forgot their password. Reset token: %r",
            user.id,
            token,
        )

    async def on_after_request_verify(self, user: User, token: str, request: Optional["Request"] = None):
        logger.info(
            "Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )
