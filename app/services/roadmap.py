import json
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.handlers import service_handler
from app.core.loggers import roadmap_service_logger as logger
from app.shared.generate_id import generate_base_id
from app.shared.access import get_accessed_filters, user_can_read_entity
from app.utils.mappers.orm_to_models import roadmap_orm_to_model
from app.utils.mappers.cache_to_model import (
    roadmap_cache_to_models,
)
from app.utils.cache import get_cache_key

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from app.core.custom_types import BaseIdType
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
        redis: "Redis",
    ):
        self.repo = repo
        self.redis = redis

    @service_handler
    async def get_all(self) -> list["RoadmapRead"]:
        db_roadmaps = await self.repo.get_all()
        if not db_roadmaps:
            logger.warning("Roadmaps not found in DB")
            return []

        validated_roadmaps = [
            roadmap_orm_to_model(db_roadmap) for db_roadmap in db_roadmaps
        ]

        return validated_roadmaps

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: "RoadmapFilters",
    ) -> list["RoadmapRead"]:
        logger.warning("REDIS: %r", self.redis)
        filters_dict = filters.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        if not filters_dict:
            key = get_cache_key(
                "roadmaps",
                "user",
                str(current_user.id),
                "list",
            )
            cached = await self.redis.get(key)
            if cached:
                return roadmap_cache_to_models(cached)

        accessed_filters = get_accessed_filters(
            current_user,
            filters_dict,
        )

        db_roadmaps = await self.repo.get_by_filters(accessed_filters)
        if not db_roadmaps:
            logger.warning("Roadmaps with filters(%r) not found", filters)
            return []

        validated_roadmaps = [
            roadmap_orm_to_model(db_roadmap) for db_roadmap in db_roadmaps
        ]

        if not filters_dict:
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in validated_roadmaps], default=str
            )
            await self.redis.set(
                key,
                cache_data,
                ex=settings.cache.roadmap_list_ttl,
            )

        return validated_roadmaps

    @service_handler
    async def get_by_id(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
    ) -> "RoadmapRead":
        key = get_cache_key(
            "roadmaps",
            "user",
            str(current_user.id),
            "roadmap",
            str(roadmap_id),
            "detail",
        )
        cached = await self.redis.get(key)
        if cached:
            result_roadmap = roadmap_cache_to_models(cached)
            return result_roadmap[0]

        db_roadmap = await self.repo.get_by_id(roadmap_id)
        if not db_roadmap:
            logger.error("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("NOT_FOUND")

        validated_roadmap = roadmap_orm_to_model(db_roadmap)
        user_can_read_entity(
            current_user,
            validated_roadmap.model_dump(),
        )

        await self.redis.set(
            key,
            json.dumps([validated_roadmap.model_dump(mode="json")]),
            ex=settings.cache.roadmap_detail_ttl,
        )

        return validated_roadmap

    @service_handler
    async def create(
        self,
        current_user: "User",
        roadmap_create_data: "RoadmapCreate",
    ) -> "RoadmapRead":
        roadmap_dict = roadmap_create_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        roadmap_dict["id"] = generate_base_id()
        roadmap_dict["user_id"] = current_user.id

        created_roadmap = await self.repo.create(roadmap_dict)
        if not created_roadmap:
            logger.error(
                "Roadmap with params(%r) for User(id=%r) not created",
                roadmap_create_data,
                current_user.id,
            )
            raise ValueError("OPERATION_FAILED")

        validated_created_roadmap = roadmap_orm_to_model(created_roadmap)

        await self.redis.delete(
            get_cache_key("roadmaps", "user", str(current_user.id), "list"),
            get_cache_key("roadmaps", "user", str(current_user.id), "detail"),
        )

        return validated_created_roadmap

    @service_handler
    async def delete(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
    ) -> None:
        existed_roadmap = await self.get_by_id(current_user, roadmap_id)

        success = await self.repo.delete(roadmap_id)
        if not success:
            logger.error("Failed to delete Roadmap(id=%r)", roadmap_id)
            raise ValueError("OPERATION_FAILED")

        await self.redis.delete(
            get_cache_key(
                "roadmaps",
                "user",
                str(current_user.id),
                "list",
            ),
            get_cache_key(
                "roadmaps",
                "user",
                str(current_user.id),
                "roadmap",
                str(existed_roadmap.id),
                "detail",
            ),
        )

    @service_handler
    async def update(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
        roadmap_update_data: "RoadmapUpdate",
    ) -> "RoadmapRead":
        await self.get_by_id(current_user, roadmap_id)

        roadmap_dict = roadmap_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        updated_roadmap = await self.repo.update(roadmap_id, roadmap_dict)
        if not updated_roadmap:
            logger.error("Failed to update Roadmap(id=%r)", roadmap_id)
            raise ValueError("OPERATION_FAILED")

        validated_updated_roadmap = roadmap_orm_to_model(updated_roadmap)

        await self.redis.delete(
            get_cache_key(
                "roadmaps",
                "user",
                str(current_user.id),
                "list",
            ),
            get_cache_key(
                "roadmaps",
                "user",
                str(current_user.id),
                "roadmap",
                str(updated_roadmap.id),
                "detail",
            ),
        )

        return validated_updated_roadmap
