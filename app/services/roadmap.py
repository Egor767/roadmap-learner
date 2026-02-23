import json
from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.shared.generate_id import generate_base_id
from app.utils.mappers.orm_to_schema import orm_to_schema, orms_to_schemas
from app.utils.mappers.cache_to_schema import (
    cache_to_schemas,
    cache_to_schema,
)
from app.utils.cache import get_cache_key

from app.schemas.roadmap import (
    RoadmapRead,
    RoadmapCreate,
    RoadmapUpdate,
    RoadmapFilters,
)
from app.core.custom_types import BaseIdType

if TYPE_CHECKING:
    from app.core.cache import CacheHelper
    from app.repositories import RoadmapRepository
    from app.models import User


class RoadmapService:
    def __init__(self, repo: "RoadmapRepository", cache: "CacheHelper"):
        self.repo = repo
        self.cache = cache

    @service_handler
    async def get_all(self) -> list[RoadmapRead]:
        roadmaps_orm = await self.repo.get_all()
        roadmap_schema = orms_to_schemas(RoadmapRead, roadmaps_orm)
        return roadmap_schema

    @service_handler
    async def get_by_filters(
        self, current_user: "User", filters: RoadmapFilters
    ) -> list[RoadmapRead]:
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
            cache = await self.cache.get(key)
            if cache:
                return cache_to_schemas(RoadmapRead, cache)

        roadmaps_orm = await self.repo.get_by_filters(filters_dict, current_user.id)

        roadmaps_schema = orms_to_schemas(RoadmapRead, roadmaps_orm)

        if not filters_dict:
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in roadmaps_schema],
                default=str,
            )
            await self.cache.set(key, cache_data)

        return roadmaps_schema

    @service_handler
    async def get_by_id(
        self, current_user: "User", roadmap_id: BaseIdType
    ) -> RoadmapRead:
        key = get_cache_key(
            "roadmaps",
            "user",
            str(current_user.id),
            "roadmap",
            str(roadmap_id),
            "detail",
        )
        cache = await self.cache.get(key)
        if cache:
            return cache_to_schema(RoadmapRead, cache)

        roadmap_orm = await self.repo.get_by_id(roadmap_id, current_user.id)

        roadmap_schema = orm_to_schema(RoadmapRead, roadmap_orm)

        await self.cache.set(key, json.dumps([roadmap_schema.model_dump(mode="json")]))

        return roadmap_schema

    @service_handler
    async def create(
        self, current_user: "User", roadmap_create_data: RoadmapCreate
    ) -> RoadmapRead:
        roadmap_dict = roadmap_create_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        roadmap_dict["id"] = generate_base_id()
        roadmap_dict["user_id"] = current_user.id

        roadmap_orm = await self.repo.create(roadmap_dict)

        roadmap_schema = orm_to_schema(RoadmapRead, roadmap_orm)

        await self.cache.delete(
            get_cache_key("roadmaps", "user", str(current_user.id), "list"),
        )

        return roadmap_schema

    @service_handler
    async def update(
        self,
        current_user: "User",
        roadmap_id: BaseIdType,
        roadmap_update_data: RoadmapUpdate,
    ) -> RoadmapRead:
        roadmap_dict = roadmap_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        roadmap_orm = await self.repo.update(roadmap_id, roadmap_dict, current_user.id)

        roadmap_schema = orm_to_schema(RoadmapRead, roadmap_orm)

        await self.cache.delete(
            get_cache_key("roadmaps", "user", str(current_user.id), "list"),
            get_cache_key(
                "roadmaps",
                "user",
                str(current_user.id),
                "roadmap",
                str(roadmap_id),
                "detail",
            ),
        )

        return roadmap_schema

    @service_handler
    async def delete(self, current_user: "User", roadmap_id: BaseIdType):
        await self.repo.delete(roadmap_id, current_user.id)

        await self.cache.delete(
            get_cache_key("roadmaps", "user", str(current_user.id), "list"),
            get_cache_key(
                "roadmaps",
                "user",
                str(current_user.id),
                "roadmap",
                str(roadmap_id),
                "detail",
            ),
        )
