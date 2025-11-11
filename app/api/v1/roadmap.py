from typing import List, Annotated

from fastapi import APIRouter, Depends, status

from app.core.config import settings
from app.core.dependencies import get_roadmap_service
from app.core.handlers import router_handler
from app.core.types import BaseIdType
from app.schemas.roadmap import (
    RoadMapResponse,
    RoadMapCreate,
    RoadMapUpdate,
    RoadMapFilters,
)
from app.services import RoadMapService

router = APIRouter(
    prefix=settings.api.v1.roadmaps,
    tags=["Roadmaps"],
)


@router.get(
    "/all", response_model=List[RoadMapResponse], status_code=status.HTTP_200_OK
)
@router_handler
async def get_all_roadmaps(
    roadmap_service: Annotated[RoadMapService, Depends(get_roadmap_service)],
):
    return await roadmap_service.get_all_roadmaps()


# -------------------------------------- GET ----------------------------------------------
@router.get("/{roadmap_id}", response_model=RoadMapResponse)
@router_handler
async def get_roadmap(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,
    roadmap_service: Annotated[RoadMapService, Depends(get_roadmap_service)],
):
    return await roadmap_service.get_user_roadmap(user_id, roadmap_id)


@router.get("/", response_model=List[RoadMapResponse])
async def get_roadmaps(
    user_id: BaseIdType,  # = Depends(get_current_user)
    filters: Annotated[RoadMapFilters, Depends()],
    roadmap_service: Annotated[RoadMapService, Depends(get_roadmap_service)],
):
    return await roadmap_service.get_user_roadmaps(user_id, filters)


# -------------------------------------- CREATE --------------------------------------
@router.post("/", response_model=RoadMapResponse, status_code=201)
@router_handler
async def create_roadmap(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_data: RoadMapCreate,
    roadmap_service: Annotated[RoadMapService, Depends(get_roadmap_service)],
):
    return await roadmap_service.create_roadmap(user_id, roadmap_data)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{roadmap_id}", status_code=204)
@router_handler
async def delete_roadmap(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,
    roadmap_service: Annotated[RoadMapService, Depends(get_roadmap_service)],
):
    await roadmap_service.delete_roadmap(user_id, roadmap_id)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{roadmap_id}", response_model=RoadMapResponse)
@router_handler
async def update_roadmap(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,
    roadmap_data: RoadMapUpdate,
    roadmap_service: Annotated[RoadMapService, Depends(get_roadmap_service)],
):
    return await roadmap_service.update_roadmap(user_id, roadmap_id, roadmap_data)
