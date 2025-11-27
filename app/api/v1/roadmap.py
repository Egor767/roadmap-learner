from typing import Annotated, TYPE_CHECKING

from fastapi import APIRouter, Depends
from starlette import status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.dependencies.services import get_roadmap_service
from app.core.handlers import router_handler
from app.core.types import BaseIdType
from app.schemas.roadmap import (
    RoadmapRead,
    RoadmapCreate,
    RoadmapUpdate,
    RoadmapFilters,
)

if TYPE_CHECKING:
    from app.services import RoadmapService
    from app.models import User


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
async def get_all_roadmaps(
    roadmap_service: Annotated[
        "RoadmapService",
        Depends(get_roadmap_service),
    ],
) -> list[RoadmapRead]:
    return await roadmap_service.get_all()


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
) -> list[RoadmapRead]:
    return await roadmap_service.get_by_filters(
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
) -> RoadmapRead:
    return await roadmap_service.get_by_id(
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
    roadmap_create_data: RoadmapCreate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    roadmap_service: Annotated[
        "RoadmapService",
        Depends(get_roadmap_service),
    ],
) -> RoadmapRead:
    return await roadmap_service.create(
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
) -> None:
    await roadmap_service.delete(
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
    roadmap_update_data: RoadmapUpdate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    roadmap_service: Annotated[
        "RoadmapService",
        Depends(get_roadmap_service),
    ],
) -> RoadmapRead:
    return await roadmap_service.update(
        current_user,
        roadmap_id,
        roadmap_update_data,
    )
