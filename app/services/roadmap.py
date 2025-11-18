from typing import List

from core.handlers import service_handler
from core.logging import roadmap_service_logger as logger
from core.types import BaseIdType
from models import User
from repositories import RoadmapRepository
from schemas.roadmap import (
    RoadmapRead,
    RoadmapCreate,
    RoadmapUpdate,
    RoadmapFilters,
)
from shared.generate_id import generate_base_id


class RoadMapService:
    def __init__(self, repo: RoadmapRepository):
        self.repo = repo

    @service_handler
    async def get_all_roadmaps(self) -> list[RoadmapRead]:
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
    async def get_roadmap(
        self,
        current_user: User,
        roadmap_id: BaseIdType,
    ) -> RoadmapRead:
        roadmap = await self.repo.get_roadmap_by_id(roadmap_id)
        if not roadmap:
            logger.error("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("Roadmap not found")
        if not current_user.is_superuser and roadmap.user_id != current_user.id:
            logger.error(
                "Access to Roadmap(id=%r), for User(id=%r) denied",
                roadmap_id,
                current_user,
            )
            raise PermissionError("Access denied")
        return roadmap

    @service_handler
    async def get_roadmaps(
        self,
        current_user: User,
        filters: RoadmapFilters,
    ) -> List[RoadmapRead]:
        roadmaps = await self.repo.get_roadmaps(filters)
        if not roadmaps:
            logger.error("Roadmaps with filters(%r) not found", filters)
            raise ValueError("Roadmaps not found")
        if not current_user.is_superuser:
            roadmaps = [r for r in roadmaps if r.user_id == current_user.id]
        return roadmaps

    @service_handler
    async def create_roadmap(
        self,
        current_user: User,
        roadmap_create_data: RoadmapCreate,
    ) -> RoadmapRead:

        roadmap_data = roadmap_create_data.model_dump()
        roadmap_data["user_id"] = current_user.id
        roadmap_data["id"] = await generate_base_id()

        created_roadmap = await self.repo.create_roadmap(roadmap_data)
        if not created_roadmap:
            logger.error("Roadmap with params(%r) not created", roadmap_create_data)
            raise ValueError("Creation failed")

        return created_roadmap

    @service_handler
    async def delete_roadmap(
        self,
        current_user: User,
        roadmap_id: BaseIdType,
    ) -> None:
        roadmap = await self.repo.get_roadmap_by_id(roadmap_id)
        if not roadmap:
            logger.error("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("Roadmap not found")

        if not current_user.is_superuser and roadmap.user_id != current_user.id:
            logger.warning(
                "Access denied to delete Roadmap(id=%r) by User(id=%r)",
                roadmap_id,
                current_user.id,
            )
            raise PermissionError("Access denied")

        success = await self.repo.delete_roadmap(roadmap_id)
        if success:
            logger.info("Roadmap(id=%r)deleted successfully", roadmap_id)
        else:
            logger.error("Failed to delete Roadmap(id=%r)", roadmap_id)
            raise ValueError("Deletion failed")

    @service_handler
    async def update_roadmap(
        self,
        current_user: User,
        roadmap_id: BaseIdType,
        roadmap_update_data: RoadmapUpdate,
    ) -> RoadmapRead:
        roadmap = await self.repo.get_roadmap_by_id(roadmap_id)
        if not roadmap:
            logger.error("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("Roadmap not found")

        if not current_user.is_superuser and roadmap.user_id != current_user.id:
            logger.warning(
                "Access denied to update Roadmap(id=%r) by User(id=%r)",
                roadmap_id,
                current_user.id,
            )
            raise PermissionError("Access denied")

        roadmap_data = roadmap_update_data.model_dump(exclude_unset=True)

        updated_roadmap = await self.repo.update_roadmap(roadmap_id, roadmap_data)

        if not updated_roadmap:
            logger.warning("Failed to update Roadmap(id=%r)", roadmap_id)
            raise ValueError("Updating failed")

        return updated_roadmap
