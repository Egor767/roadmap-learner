from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.models import User
from app.services import UserManager

from .auth import get_access_tokens_db
from .db import get_db_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.access_token import SQLAlchemyAccessTokenDatabase
    from app.models.user import SQLAlchemyUserDatabase


async def get_users_db(
    session: Annotated["AsyncSession", Depends(get_db_session)],
):
    yield User.get_db(session=session)


async def get_user_manager(
    users_db: Annotated["SQLAlchemyUserDatabase", Depends(get_users_db)],
    access_tokens_db: Annotated["SQLAlchemyAccessTokenDatabase", Depends(get_access_tokens_db)],
):
    yield UserManager(users_db, access_tokens_db)
