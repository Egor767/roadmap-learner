from typing import List

from app.core.handlers import service_handler
from app.core.types import BaseIDType
from app.repositories.roadmap import RoadmapRepository
from app.schemas.roadmap import (
    RoadMapCreate,
    RoadMapResponse,
    RoadMapUpdate,
    RoadMapFilters,
)
from app.core.logging import roadmap_service_logger as logger
from shared.generate_id import generate_base_id


class RoadMapService:
    def __init__(self, repo: RoadmapRepository):
        self.repo = repo

    @service_handler
    async def get_all_roadmaps(self) -> List[RoadMapResponse]:
        roadmaps = await self.repo.get_all_roadmaps()
        validated_roadmaps = [
            RoadMapResponse.model_validate(roadmap) for roadmap in roadmaps
        ]
        logger.info(f"Successful get all roadmaps, count: {len(validated_roadmaps)}")
        return validated_roadmaps

    @service_handler
    async def get_user_roadmap(
        self, user_id: BaseIDType, roadmap_id: BaseIDType
    ) -> RoadMapResponse:
        roadmap = await self.repo.get_user_roadmap(user_id, roadmap_id)
        if not roadmap:
            logger.warning(f"Roadmap not found or access denied")
            raise ValueError("Roadmap not found or access denied")
        logger.info(f"Successful get user roadmap")
        return RoadMapResponse.model_validate(roadmap)

    @service_handler
    async def get_user_roadmaps(
        self, user_id: BaseIDType, filters: RoadMapFilters
    ) -> List[RoadMapResponse]:
        roadmaps = await self.repo.get_user_roadmaps(user_id, filters)
        validated_roadmaps = [
            RoadMapResponse.model_validate(roadmap) for roadmap in roadmaps
        ]
        logger.info(
            f"Retrieved {len(validated_roadmaps)} roadmaps with filters: {filters}"
        )
        return validated_roadmaps

    @service_handler
    async def create_roadmap(
        self, user_id: BaseIDType, roadmap_create_data: RoadMapCreate
    ) -> RoadMapResponse:
        # need to check here if existing

        roadmap_data = roadmap_create_data.model_dump()
        roadmap_data["user_id"] = user_id
        roadmap_data["id"] = await generate_base_id()

        logger.info(
            f"Creating new roadmap: {roadmap_create_data.title} for user: {user_id}"
        )
        created_roadmap = await self.repo.create_roadmap(roadmap_data)

        logger.info(f"Roadmap created successfully: {created_roadmap.id}")
        return RoadMapResponse.model_validate(created_roadmap)

    @service_handler
    async def delete_roadmap(self, user_id: BaseIDType, roadmap_id: BaseIDType) -> bool:
        success = await self.repo.delete_roadmap(user_id, roadmap_id)
        if success:
            logger.info(f"Roadmap deleted successfully: {roadmap_id}")
        else:
            logger.warning(f"Roadmap not found for deletion: {roadmap_id}")
        return success

    @service_handler
    async def update_roadmap(
        self,
        user_id: BaseIDType,
        roadmap_id: BaseIDType,
        roadmap_update_data: RoadMapUpdate,
    ) -> RoadMapResponse:
        roadmap_data = roadmap_update_data.model_dump(exclude_unset=True)
        logger.info(f"Updating roadmap {roadmap_id}: {roadmap_data}")
        updated_roadmap = await self.repo.update_roadmap(
            user_id, roadmap_id, roadmap_data
        )

        if not updated_roadmap:
            logger.warning(f"Roadmap not found for update: {roadmap_id}")
            raise ValueError("Roadmap not found")

        logger.info(f"Successful updating roadmap: {roadmap_id}")
        return RoadMapResponse.model_validate(updated_roadmap)
