from typing import Annotated, TYPE_CHECKING
from fastapi import Depends

from .db import get_db_session
from repositories import RoadmapRepository
from services import RoadmapService, AccessService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_roadmap_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> RoadmapRepository:
    yield RoadmapRepository(session)


async def get_roadmap_service(
    repo: Annotated[
        RoadmapRepository,
        Depends(get_roadmap_repository),
    ],
) -> RoadmapService:

    yield RoadmapService(repo)
