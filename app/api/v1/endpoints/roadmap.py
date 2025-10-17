import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_roadmap_service
from app.core.handlers import router_handler
from app.schemas.roadmap import RoadMapResponse, RoadMapCreate, RoadMapInDB, RoadMapUpdate
from app.services.roadmap.service import RoadMapService

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


@router.post("/create",
             response_model=RoadMapResponse,
             status_code=status.HTTP_201_CREATED)
@router_handler
async def create_roadmap(
    roadmap_data: RoadMapCreate,
    roadmap_service: RoadMapService = Depends(get_roadmap_service)
):
    return await roadmap_service.create_roadmap(roadmap_data)

