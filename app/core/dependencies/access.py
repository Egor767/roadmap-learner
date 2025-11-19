from typing import Annotated
from fastapi import Depends

from repositories import RoadmapRepository
from services import AccessService
from .roadmaps import get_roadmap_repository


async def get_access_service(
    roadmap_repo: Annotated[
        RoadmapRepository,
        Depends(get_roadmap_repository),
    ],
) -> AccessService:
    yield AccessService(roadmap_repo)
