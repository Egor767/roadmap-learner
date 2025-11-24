from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from app.repositories import (
    BlockRepository,
    CardRepository,
    RoadmapRepository,
    SessionManagerRepository,
    UserRepository,
)
from .db import get_db_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> UserRepository:
    yield UserRepository(session)


async def get_roadmap_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> RoadmapRepository:
    yield RoadmapRepository(session)


async def get_block_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> BlockRepository:
    yield BlockRepository(session)


async def get_card_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> CardRepository:
    yield CardRepository(session)


async def get_session_manager_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> SessionManagerRepository:
    yield SessionManagerRepository(session)
