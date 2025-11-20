from typing import Annotated, TYPE_CHECKING

from fastapi import APIRouter, Depends
from starlette import status

from core.authentication.fastapi_users import current_active_user
from core.config import settings
from core.dependencies.services import get_roadmap_service
from core.handlers import router_handler
from core.types import BaseIdType
from schemas.roadmap import (
    RoadmapRead,
    RoadmapUpdate,
    RoadmapFilters,
    RoadmapCreate,
)

if TYPE_CHECKING:
    from services import RoadmapService
    from models import User

router = APIRouter(
    prefix=settings.api.v1.roadmaps,
    tags=["Roadmaps"],
)


@router.get(
    "",
    name="roadmaps:all_roadmaps",
    response_model=list[RoadmapRead],
)
@router_handler
async def get_roadmaps(
    roadmap_service: Annotated[
        "RoadmapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.get_all_roadmaps()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/filters",
    name="roadmaps:filter_roadmaps",
    response_model=list[RoadmapRead],
)
@router_handler
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
        "RoadmapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.get_roadmaps_by_filters(
        current_user,
        filters,
    )


@router.get(
    "/{roadmap_id}",
    name="roadmaps:roadmap",
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
        "RoadmapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.get_roadmap_by_id(
        current_user,
        roadmap_id,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "/",
    name="roadmaps:create_roadmap",
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
        "RoadmapService",
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
    name="roadmaps:delete_roadmap",
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
        "RoadmapService",
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
    name="roadmaps:path_roadmap",
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
        "RoadmapService",
        Depends(get_roadmap_service),
    ],
):
    return await roadmap_service.update_roadmap(
        current_user,
        roadmap_id,
        roadmap_data,
    )
