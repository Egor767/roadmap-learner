from typing import Annotated, TYPE_CHECKING

from fastapi import APIRouter, Depends
from starlette import status

from core.authentication.fastapi_users import current_active_user
from core.config import settings
from core.dependencies import get_roadmap_service
from core.handlers import router_handler
from core.types import BaseIdType
from schemas.roadmap import (
    RoadmapRead,
    RoadmapUpdate,
    RoadmapFilters,
    RoadmapCreate,
)

if TYPE_CHECKING:
    from services import RoadMapService
    from models import User

router = APIRouter(
    prefix=settings.api.v1.roadmaps,
    tags=["Roadmaps"],
)


@router.get(
    "",
    response_model=list[RoadmapRead],
)
@router_handler
async def get_roadmaps(
    roadmap_service: Annotated[
        "RoadMapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.get_all_roadmaps()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/filters",
    response_model=list[RoadmapRead],
)
async def get_roadmaps(
    filters: Annotated[
        RoadmapFilters,
        Depends(),
    ],
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    roadmap_service: Annotated[
        "RoadMapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.get_roadmaps(
        current_user,
        filters,
    )


@router.get(
    "/{roadmap_id}",
    response_model=RoadmapRead,
)
@router_handler
async def get_roadmap(
    roadmap_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    roadmap_service: Annotated[
        "RoadMapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.get_roadmap(
        current_user,
        roadmap_id,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "/",
    response_model=RoadmapRead,
)
@router_handler
async def create_roadmap(
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    roadmap_create_data: RoadmapCreate,
    roadmap_service: Annotated[
        "RoadMapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.create_roadmap(
        current_user,
        roadmap_create_data,
    )


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{roadmap_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def delete_roadmap(
    roadmap_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    roadmap_service: Annotated[
        "RoadMapService",
        Depends(get_roadmap_service),
    ],
):
    await roadmap_service.delete_roadmap(
        current_user,
        roadmap_id,
    )


# -------------------------------------- UPDATE --------------------------------------
@router.patch(
    "/{roadmap_id}",
    response_model=RoadmapRead,
)
@router_handler
async def update_roadmap(
    roadmap_id: BaseIdType,
    roadmap_data: RoadmapUpdate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    roadmap_service: Annotated[
        "RoadMapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.update_roadmap(
        current_user,
        roadmap_id,
        roadmap_data,
    )
