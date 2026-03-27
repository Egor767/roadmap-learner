from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.custom_types import BaseIdType
from app.core.dependencies.services import get_roadmap_service
from app.core.handlers import router_handler
from app.schemas.roadmap import (
    RoadmapCreate,
    RoadmapFilters,
    RoadmapRead,
    RoadmapUpdate,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services import RoadmapService


router = APIRouter(
    prefix=settings.api.v1.roadmaps,
    tags=["Roadmaps"],
)


# -------------------------------------- GET ----------------------------------------------
@router.get("", name="roadmaps:all_roadmaps", response_model=list[RoadmapRead])
@router_handler
async def get_all_roadmaps(
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["RoadmapService", Depends(get_roadmap_service)],
) -> list[RoadmapRead]:
    return await service.get_all(user)


@router.get("/filters", name="roadmaps:filter_roadmaps", response_model=list[RoadmapRead])
@router_handler
async def get_roadmaps(
    filters: Annotated[RoadmapFilters, Depends()],
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["RoadmapService", Depends(get_roadmap_service)],
) -> list[RoadmapRead]:
    return await service.get_by_filters(user, filters)


@router.get("/{id}", name="roadmaps:roadmap", response_model=RoadmapRead)
@router_handler
async def get_roadmap(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["RoadmapService", Depends(get_roadmap_service)],
) -> RoadmapRead:
    return await service.get_by_id(user, id)


# -------------------------------------- CREATE --------------------------------------
@router.post("", name="roadmaps:create_roadmap", response_model=RoadmapRead)
@router_handler
async def create_roadmap(
    payload: RoadmapCreate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["RoadmapService", Depends(get_roadmap_service)],
) -> RoadmapRead:
    return await service.create(user, payload)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{id}", name="roadmaps:patch_roadmap", response_model=RoadmapRead)
@router_handler
async def update_roadmap(
    id: BaseIdType,
    payload: RoadmapUpdate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["RoadmapService", Depends(get_roadmap_service)],
) -> RoadmapRead:
    return await service.update(user, id, payload)


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{id}",
    name="roadmaps:delete_roadmap",
)
@router_handler
async def delete_roadmap(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["RoadmapService", Depends(get_roadmap_service)],
) -> None:
    await service.delete(user, id)
