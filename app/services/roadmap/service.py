import uuid
from typing import List

from app.core.handlers import service_handler
from app.repositories.roadmap.interface import IRoadMapRepository
from app.schemas.roadmap import RoadMapCreate, RoadMapResponse, RoadMapUpdate
from app.core.logging import roadmap_service_logger as logger


class RoadMapService:
    def __init__(self, repo: IRoadMapRepository):
        self.repo = repo

    @service_handler
    async def create_roadmap(self, roadmap_create_data: RoadMapCreate) -> RoadMapResponse:
        roadmap_data = roadmap_create_data.model_dump()
        logger.info(f"Creating new roadmap: {roadmap_create_data.title} for user: {roadmap_create_data.user_id}")
        created_roadmap = await self.repo.create_roadmap(RoadMapCreate(**roadmap_data))

        logger.info(f"User created successfully: {created_roadmap.road_id}")
        return RoadMapResponse.model_validate(created_roadmap)

    async def get_user_roadmaps(self, user_id: uuid.UUID) -> List[RoadMapResponse]:
        roadmaps = await self.repo.get_user_roadmaps(user_id)
        if not roadmaps:
            logger.warning(f"This user has no roadmaps")
            raise ValueError("This user has no roadmaps")

        validated_roadmaps = [RoadMapResponse.model_validate(roadmap) for roadmap in roadmaps]
        logger.info(f"Successful get all user roadmaps")
        return validated_roadmaps

    async def get_user_roadmap(self, user_id: uuid.UUID, roadmap_id: uuid.UUID) -> RoadMapResponse:
        roadmap = await self.repo.get_user_roadmap(user_id, roadmap_id)
        if not roadmap:
            logger.warning(f"Roadmap not found or access denied")
            raise ValueError("Roadmap not found or access denied")
        logger.info(f"Successful get user roadmap")
        return RoadMapResponse.model_validate(roadmap)

    async def delete_roadmap(self, user_id: uuid.UUID, roadmap_id: uuid.UUID) -> bool:
        success = await self.repo.delete_roadmap(user_id, roadmap_id)
        if success:
            logger.info(f"Roadmap deleted successfully: {roadmap_id}")
        else:
            logger.warning(f"Roadmap not found for deletion: {roadmap_id}")
        return success

    async def update_roadmap(self, roadmap_update_data: RoadMapUpdate) -> RoadMapResponse:
        ...

