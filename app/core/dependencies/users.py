from typing import Annotated, TYPE_CHECKING

from fastapi import Depends, Query
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.models import User
from app.schemas.user import UserFilters
from app.services import UserManager
from .db import get_db_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_users_db(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
):
    yield User.get_db(session=session)


async def get_user_filters(
    email: str | None = Query(None),
    username: str | None = Query(None),
    is_active: str | None = Query(None),
    is_verified: str | None = Query(None),
) -> UserFilters:
    yield UserFilters(
        email=email,
        username=username,
        is_active=is_active,
        is_verified=is_verified,
    )


async def get_user_manager(
    users_db: Annotated[
        SQLAlchemyUserDatabase,
        Depends(get_users_db),
    ],
):
    yield UserManager(users_db)
