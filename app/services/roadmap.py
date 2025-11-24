from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.core.logging import roadmap_service_logger as logger
from app.shared.generate_id import generate_base_id

if TYPE_CHECKING:
    from app.services import AccessService
    from app.repositories import RoadmapRepository
    from app.models import User
    from app.core.types import BaseIdType
    from app.schemas.roadmap import (
        RoadmapRead,
        RoadmapCreate,
        RoadmapUpdate,
        RoadmapFilters,
    )


class RoadmapService:
    def __init__(
        self,
        repo: "RoadmapRepository",
        access_service: "AccessService",
    ):
        self.repo = repo
        self.access = access_service

    @service_handler
    async def get_all_roadmaps(self) -> list["RoadmapRead"] | list[None]:
        roadmaps = await self.repo.get_all()
        if not roadmaps:
            logger.warning("Roadmaps not found in DB")
            return []

        return roadmaps

    @service_handler
    async def get_roadmap_by_id(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
    ) -> "RoadmapRead":

        roadmap = await self.repo.get_by_id(roadmap_id)

        if not roadmap:
            logger.error("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("NOT_FOUND")

        await self.access.ensure_can_view_roadmap(current_user, roadmap)

        return roadmap

    @service_handler
    async def get_roadmaps_by_filters(
        self,
        current_user: "User",
        filters: "RoadmapFilters",
    ) -> list["RoadmapRead"] | list[None]:

        roadmaps = await self.repo.get_by_filters(filters)

        if not roadmaps:
            logger.warning("Roadmaps with filters(%r) not found", filters)
            return []
            # or:
            # logger.error("Roadmaps with filters(%r) not found", filters)
            # raise ValueError("Roadmaps not found")
            # and current_func() -> list[RoadmapRead]

        filtered_roadmaps = await self.access.filter_roadmaps_for_user(
            current_user, roadmaps
        )

        return filtered_roadmaps

    @service_handler
    async def create_roadmap(
        self,
        current_user: "User",
        roadmap_create_data: "RoadmapCreate",
    ) -> "RoadmapRead":

        roadmap_data = roadmap_create_data.model_dump()
        roadmap_data["user_id"] = current_user.id
        roadmap_data["id"] = await generate_base_id()

        created_roadmap = await self.repo.create(roadmap_data)
        if not created_roadmap:
            logger.error(
                "Roadmap with params(%r) for USer(id=%r) not created",
                roadmap_create_data,
                current_user.id,
            )
            raise ValueError("OPERATION_FAILED")

        return created_roadmap

    @service_handler
    async def delete_roadmap(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
    ) -> None:
        roadmap = await self.repo.get_by_id(roadmap_id)
        if not roadmap:
            logger.error("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("NOT_FOUND")

        await self.access.ensure_can_view_roadmap(current_user, roadmap)

        success = await self.repo.delete(roadmap_id)
        if success:
            logger.info("Roadmap(id=%r) was deleted successfully", roadmap_id)
        else:
            logger.error("Failed to delete Roadmap(id=%r)", roadmap_id)
            raise ValueError("OPERATION_FAILED")

    @service_handler
    async def update_roadmap(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
        roadmap_update_data: "RoadmapUpdate",
    ) -> "RoadmapRead":

        roadmap = await self.repo.get_by_id(roadmap_id)

        if not roadmap:
            logger.error("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("NOT_FOUND")

        await self.access.ensure_can_view_roadmap(current_user, roadmap)

        roadmap_data = roadmap_update_data.model_dump(exclude_unset=True)

        updated_roadmap = await self.repo.update(roadmap_id, roadmap_data)

        if not updated_roadmap:
            logger.error("Failed to update Roadmap(id=%r)", roadmap_id)
            raise ValueError("OPERATION_FAILED")

        return updated_roadmap
