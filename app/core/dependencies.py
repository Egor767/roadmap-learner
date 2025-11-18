from typing import Annotated, TYPE_CHECKING, Optional

from fastapi import Depends, Query
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication.strategy import DatabaseStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from core.authentication.transport import bearer_transport
from core.config import settings
from core.db import get_db_session
from models import User, AccessToken
from repositories import (
    UserRepository,
    RoadmapRepository,
    BlockRepository,
    CardRepository,
    SessionManagerRepository,
)
from schemas.user import UserFilters
from services import (
    UserService,
    RoadMapService,
    BlockService,
    CardService,
    SessionManagerService,
    UserManager,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi_users.authentication.strategy import AccessTokenDatabase


# AUTH
async def get_access_tokens_db(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
):
    yield SQLAlchemyAccessTokenDatabase(
        session,
        AccessToken,
    )


def get_database_strategy(
    access_token_db: Annotated[
        "AccessTokenDatabase[AccessToken]",
        Depends(get_access_tokens_db),
    ],
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db,
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )


authentication_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)


# USER
async def get_users_db(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
):
    yield User.get_db(session=session)


async def get_user_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> UserRepository:
    return UserRepository(session)


async def get_user_service(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


async def get_user_filters(
    email: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
) -> UserFilters:
    return UserFilters(
        email=email,
        username=username,
        is_active=is_active,
        is_verified=is_verified,
    )


# USER MANAGER
async def get_user_manager(
    users_db: Annotated[
        "SQLAlchemyUserDatabase",
        Depends(get_users_db),
    ],
):
    yield UserManager(users_db)


# ROADMAP
async def get_roadmap_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> RoadmapRepository:
    return RoadmapRepository(session)


async def get_roadmap_service(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> RoadMapService:
    repo = RoadmapRepository(session)
    return RoadMapService(repo)


# BLOCK
async def get_block_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> BlockRepository:
    return BlockRepository(session)


async def get_block_service(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> BlockService:
    repo = BlockRepository(session)
    return BlockService(repo)


# CARD
async def get_card_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> CardRepository:
    return CardRepository(session)


async def get_card_service(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> CardService:
    repo = CardRepository(session)
    return CardService(repo)


# SESSION_MANAGER
async def get_session_manager_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> SessionManagerRepository:
    return SessionManagerRepository(session)


async def get_session_manager_service(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> SessionManagerService:
    repo = SessionManagerRepository(session)
    return SessionManagerService(repo)
