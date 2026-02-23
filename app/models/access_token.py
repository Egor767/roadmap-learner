import logging
from datetime import UTC, datetime, timedelta

from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase as SQLAlchemyAccessTokenDatabaseGeneric,
)
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTable,
)
from fastapi_users_db_sqlalchemy.generics import TIMESTAMPAware, now_utc
from sqlalchemy import asc, delete, select
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.core.custom_types import BaseIdType

from .base import Base
from .db_helper import db_helper
from .mixins import UserRelationMixin

logger = logging.getLogger("ACCESS-TOKEN")


class AccessToken(UserRelationMixin, Base, SQLAlchemyBaseAccessTokenTable[BaseIdType]):
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMPAware(timezone=True),
        index=True,
        nullable=False,
        # default=(
        #     lambda: now_utc()
        #     + timedelta(seconds=settings.access_token.lifetime_seconds),
        # ),
    )

    # _user_back_populates = "tokens"

    def __str__(self):
        return f"{self.__class__.__name__}(token={self.token}, user={self.user_id!r}, expires_at={self.expires_at})"

    def __repr__(self):
        return str(self)


class SQLAlchemyAccessTokenDatabase(SQLAlchemyAccessTokenDatabaseGeneric[AccessToken]):
    async def create(self, token_dict: dict) -> AccessToken:
        now = now_utc()
        token_dict["created_at"] = now
        token_dict["expires_at"] = now + timedelta(seconds=settings.access_token.lifetime_seconds)
        token = AccessToken(**token_dict)

        async with db_helper.session_factory() as session:
            session.add(token)
            await session.commit()
            await session.refresh(token)

        return token

    async def delete_expired_for_user(self, user_id) -> int:
        stmt = delete(AccessToken).where(
            AccessToken.user_id == user_id,
            AccessToken.expires_at <= datetime.now(UTC),
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount or 0

    async def enforce_max_active_tokens(self, user_id) -> int:
        stmt = select(AccessToken.token).where(AccessToken.user_id == user_id).order_by(asc(AccessToken.created_at))
        tokens = (await self.session.execute(stmt)).scalars().all()

        max_tokens = settings.access_token.max_active_tokens
        if len(tokens) <= max_tokens:
            return 0

        tokens_to_delete = tokens[: len(tokens) - max_tokens]

        result = await self.session.execute(delete(AccessToken).where(AccessToken.token.in_(tokens_to_delete)))
        await self.session.commit()
        return result.rowcount or 0

    async def cleanup_user_tokens(self, user_id) -> dict:
        deleted_expired = await self.delete_expired_for_user(user_id)
        deleted_old = await self.enforce_max_active_tokens(user_id)

        return {
            "expired": deleted_expired,
            "old": deleted_old,
        }
