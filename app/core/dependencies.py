from typing import Annotated

from fastapi import Depends
from fastapi_users.authentication.strategy import AccessTokenDatabase, DatabaseStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db_session
from app.models.postgres import User, AccessToken
from app.repositories import (
    UserRepository,
    RoadmapRepository,
    BlockRepository,
    CardRepository,
    SessionManagerRepository,
)

from app.services import (
    UserService,
    RoadMapService,
    BlockService,
    CardService,
    SessionManagerService,
)


# AUTH
async def get_access_tokens_db(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
):
    yield SQLAlchemyAccessTokenDatabase(
        session,
        AccessToken,
    )


def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken],
        Depends(get_access_tokens_db),
    ],
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db,
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )


# USER
async def get_user_db(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> UserRepository:
    return UserRepository(session)


async def get_user_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


# ROADMAP
async def get_roadmap_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> RoadmapRepository:
    return RoadmapRepository(session)


async def get_roadmap_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> RoadMapService:
    repo = RoadmapRepository(session)
    return RoadMapService(repo)


# BLOCK
async def get_block_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> BlockRepository:
    return BlockRepository(session)


async def get_block_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> BlockService:
    repo = BlockRepository(session)
    return BlockService(repo)


# CARD
async def get_card_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> CardRepository:
    return CardRepository(session)


async def get_card_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> CardService:
    repo = CardRepository(session)
    return CardService(repo)


# SESSION_MANAGER
async def get_session_manager_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> SessionManagerRepository:
    return SessionManagerRepository(session)


async def get_session_manager_service(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> SessionManagerService:
    repo = SessionManagerRepository(session)
    return SessionManagerService(repo)
