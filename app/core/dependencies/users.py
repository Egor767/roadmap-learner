from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.core.password import PasswordValidator
from app.models import User
from app.services import UserManager

from .auth import get_access_tokens_db
from .clients import get_email_client
from .db import get_db_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.clients import EmailClient
    from app.models.access_token import SQLAlchemyAccessTokenDatabase
    from app.models.user import SQLAlchemyUserDatabase


def get_password_validator() -> PasswordValidator:
    return PasswordValidator()


async def get_users_db(
    session: Annotated["AsyncSession", Depends(get_db_session)],
):
    yield User.get_db(session=session)


async def get_user_manager(
    users_db: Annotated["SQLAlchemyUserDatabase", Depends(get_users_db)],
    access_tokens_db: Annotated["SQLAlchemyAccessTokenDatabase", Depends(get_access_tokens_db)],
    validator: Annotated[PasswordValidator, Depends(get_password_validator)],
    client: Annotated["EmailClient", Depends(get_email_client)],
):
    yield UserManager(users_db, access_tokens_db, validator, client)
