from typing import Annotated, TYPE_CHECKING

from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.strategy import DatabaseStrategy
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from app.core.authentication.transport import bearer_transport
from app.core.config import settings
from app.models import AccessToken
from .db import get_db_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi_users.authentication.strategy import AccessTokenDatabase


async def get_access_tokens_db(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


async def get_database_strategy(
    access_token_db: Annotated[
        "AccessTokenDatabase[AccessToken]",
        Depends(get_access_tokens_db),
    ],
) -> DatabaseStrategy:
    yield DatabaseStrategy(
        access_token_db,
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )


authentication_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
