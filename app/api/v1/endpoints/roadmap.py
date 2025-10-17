import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_roadmap_service
from app.core.handlers import router_handler
from app.schemas.roadmap import RoadMapResponse, RoadMapCreate, RoadMapInDB, RoadMapUpdate
from app.services.roadmap.service import RoadMapService

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


@router.get("/",
            response_model=List[RoadMapResponse],
            status_code=status.HTTP_200_OK)
@router_handler
async def get_user_roadmaps(
    user_id: uuid.UUID,
    roadmap_service: RoadMapCreate = Depends(get_roadmap_service)
):
    return await roadmap_service.get_user_roadmaps(user_id)


@router.get("/{roadmap_id}",
            response_model=RoadMapResponse,
            status_code=status.HTTP_200_OK)
@router_handler
async def get_user_roadmap(
    roadmap_id: uuid.UUID,
    user_id: uuid.UUID,  # = Depends(get_current_user) / access_token.user_id
    roadmap_service: RoadMapService = Depends(get_roadmap_service)
):
    return await roadmap_service.get_user_roadmap(user_id, roadmap_id)


@router.post("/create",
             response_model=RoadMapResponse,
             status_code=status.HTTP_201_CREATED)
@router_handler
async def create_roadmap(
    roadmap_data: RoadMapCreate,
    roadmap_service: RoadMapService = Depends(get_roadmap_service)
):
    return await roadmap_service.create_roadmap(roadmap_data)


@router.delete("/{roadmap_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_roadmap(
    roadmap_id: uuid.UUID,
    user_id: uuid.UUID,  # = Depends(get_current_user) / access_token.user_id
    roadmap_service: RoadMapService = Depends(get_roadmap_service)
):
    await roadmap_service.delete_roadmap(user_id, roadmap_id)
    return {"road_id": str(roadmap_id), "status": "deleted"}
