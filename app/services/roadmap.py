from typing import List

from core.handlers import service_handler
from core.logging import roadmap_service_logger as logger
from core.types import BaseIdType
from repositories import RoadmapRepository
from schemas.roadmap import (
    RoadmapRead,
    RoadmapCreate,
    RoadMapUpdate,
    RoadmapFilters,
)
from shared.generate_id import generate_base_id


class RoadMapService:
    def __init__(self, repo: RoadmapRepository):
        self.repo = repo

    @service_handler
    async def get_all_roadmaps(self) -> List[RoadmapRead]:
        roadmaps = await self.repo.get_all_roadmaps()
        validated_roadmaps = [
            RoadmapRead.model_validate(roadmap) for roadmap in roadmaps
        ]
        logger.info(
            "Successful get all roadmaps, count: %r",
            len(validated_roadmaps),
        )
        return validated_roadmaps

    @service_handler
    async def get_user_roadmap(
        self, user_id: BaseIdType, roadmap_id: BaseIdType
    ) -> RoadmapRead:
        roadmap = await self.repo.get_user_roadmap(user_id, roadmap_id)
        if not roadmap:
            logger.warning("Roadmap not found or access denied")
            raise ValueError("Roadmap not found or access denied")
        logger.info("Successful get user roadmap")
        return RoadmapRead.model_validate(roadmap)

    @service_handler
    async def get_user_roadmaps(
        self, user_id: BaseIdType, filters: RoadmapFilters
    ) -> List[RoadmapRead]:
        roadmaps = await self.repo.get_user_roadmaps(user_id, filters)
        validated_roadmaps = [
            RoadmapRead.model_validate(roadmap) for roadmap in roadmaps
        ]
        logger.info(
            "Retrieved %r roadmaps with filters: %r",
            len(validated_roadmaps),
            filters,
        )
        return validated_roadmaps

    @service_handler
    async def create_roadmap(
        self, user_id: BaseIdType, roadmap_create_data: RoadmapCreate
    ) -> RoadmapRead:
        # need to check here if existing

        roadmap_data = roadmap_create_data.model_dump()
        roadmap_data["user_id"] = user_id
        roadmap_data["id"] = await generate_base_id()

        logger.info(
            "Creating new roadmap: %r for user: %r",
            roadmap_create_data.title,
            user_id,
        )
        created_roadmap = await self.repo.create_roadmap(roadmap_data)

        logger.info(
            "Roadmap created successfully: %r",
            created_roadmap.id,
        )
        return RoadmapRead.model_validate(created_roadmap)

    @service_handler
    async def delete_roadmap(self, user_id: BaseIdType, roadmap_id: BaseIdType) -> bool:
        success = await self.repo.delete_roadmap(user_id, roadmap_id)
        if success:
            logger.info("Roadmap deleted successfully: %r", roadmap_id)
        else:
            logger.warning("Roadmap not found for deletion: %r", roadmap_id)
        return success

    @service_handler
    async def update_roadmap(
        self,
        user_id: BaseIdType,
        roadmap_id: BaseIdType,
        roadmap_update_data: RoadMapUpdate,
    ) -> RoadmapCreate:
        roadmap_data = roadmap_update_data.model_dump(exclude_unset=True)
        logger.info(
            "Updating roadmap %r: %r",
            roadmap_id,
            roadmap_data,
        )
        updated_roadmap = await self.repo.update_roadmap(
            user_id, roadmap_id, roadmap_data
        )

        if not updated_roadmap:
            logger.warning("Roadmap not found for update: %r", roadmap_id)
            raise ValueError("Roadmap not found")

        logger.info("Successful updating roadmap: %r", roadmap_id)
        return RoadmapCreate.model_validate(updated_roadmap)
