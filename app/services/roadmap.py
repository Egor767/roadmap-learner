from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.core.logging import roadmap_service_logger as logger
from app.shared.generate_id import generate_base_id
from app.utils.mappers.orm_to_models import roadmap_orm_to_model

if TYPE_CHECKING:
    from app.core.types import BaseIdType
    from app.services import AccessService
    from app.repositories import RoadmapRepository
    from app.models import User
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
    async def get_all(self) -> list["RoadmapRead"]:
        db_roadmaps = await self.repo.get_all()
        if not db_roadmaps:
            logger.warning("Roadmaps not found in DB")
            return []

        validated_roadmaps = [
            await roadmap_orm_to_model(db_roadmap) for db_roadmap in db_roadmaps
        ]

        return validated_roadmaps

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: "RoadmapFilters",
    ) -> list["RoadmapRead"]:
        filters_dict = filters.model_dump()
        accessed_filters = await self.access.filter_roadmaps_for_user(
            current_user,
            filters_dict,
        )

        db_roadmaps = await self.repo.get_by_filters(accessed_filters)
        if not db_roadmaps:
            logger.warning("Roadmaps with filters(%r) not found", filters)
            return []

        validated_roadmaps = [
            await roadmap_orm_to_model(db_roadmap) for db_roadmap in db_roadmaps
        ]

        return validated_roadmaps

    @service_handler
    async def get_by_id(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
    ) -> "RoadmapRead":
        db_roadmap = await self.repo.get_by_id(roadmap_id)
        if not db_roadmap:
            logger.error("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("NOT_FOUND")

        validated_roadmap = await roadmap_orm_to_model(db_roadmap)
        await self.access.ensure_can_view_roadmap(
            current_user, validated_roadmap.model_dump()
        )

        return validated_roadmap

    @service_handler
    async def create(
        self,
        current_user: "User",
        roadmap_create_data: "RoadmapCreate",
    ) -> "RoadmapRead":
        roadmap_dict = roadmap_create_data.model_dump()
        roadmap_dict["user_id"] = current_user.id
        roadmap_dict["id"] = await generate_base_id()

        created_roadmap = await self.repo.create(roadmap_dict)
        if not created_roadmap:
            logger.error(
                "Roadmap with params(%r) for User(id=%r) not created",
                roadmap_create_data,
                current_user.id,
            )
            raise ValueError("OPERATION_FAILED")

        validated_created_roadmap = await roadmap_orm_to_model(created_roadmap)

        return validated_created_roadmap

    @service_handler
    async def delete(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
    ) -> None:
        await self.get_by_id(current_user, roadmap_id)

        success = await self.repo.delete(roadmap_id)
        if success:
            logger.info("Roadmap(id=%r) was deleted successfully", roadmap_id)
        else:
            logger.error("Failed to delete Roadmap(id=%r)", roadmap_id)
            raise ValueError("OPERATION_FAILED")

    @service_handler
    async def update(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
        roadmap_update_data: "RoadmapUpdate",
    ) -> "RoadmapRead":
        await self.get_by_id(current_user, roadmap_id)

        roadmap_dict = roadmap_update_data.model_dump(exclude_unset=True)

        updated_roadmap = await self.repo.update(roadmap_id, roadmap_dict)
        if not updated_roadmap:
            logger.error("Failed to update Roadmap(id=%r)", roadmap_id)
            raise ValueError("OPERATION_FAILED")

        validated_updated_roadmap = await roadmap_orm_to_model(updated_roadmap)

        return validated_updated_roadmap
