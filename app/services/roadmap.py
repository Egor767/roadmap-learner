import json
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.roadmap import (
    RoadmapCreate,
    RoadmapFilters,
    RoadmapRead,
    RoadmapUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils.mappers.cache_to_schema import (
    cache_to_schema,
    cache_to_schemas,
)
from app.utils.mappers.orm_to_schema import orm_list_to_schemas, orm_to_schema

if TYPE_CHECKING:
    from app.core.cache import CacheHelper, CacheScope
    from app.models import User
    from app.repositories import RoadmapRepository, VerifyRepository


class RoadmapService:
    """Service for roadmap business logic"""

    def __init__(self, repo: "RoadmapRepository", verify: "VerifyRepository", cache: "CacheHelper"):
        self.repo = repo
        self.verify = verify
        self.cache = cache

    def _scope(self, current_user: "User") -> "CacheScope":
        """Return cache scope for current user"""
        return self.cache.scope("roadmaps", str(current_user.id))

    @service_handler
    async def get_all(self) -> list[RoadmapRead]:
        """Return all roadmaps"""
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(RoadmapRead, orm)
        return schema

    @service_handler
    async def get_by_filters(self, current_user: "User", filters: RoadmapFilters) -> list[RoadmapRead]:
        """Return roadmaps matching filters for current user"""
        filters_dict = filters.model_dump(exclude_none=True, exclude_unset=True)
        scope = self._scope(current_user)
        if not filters_dict:
            cached = await scope.get("list")
            if cached:
                return cache_to_schemas(RoadmapRead, cached)
        orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        schema = orm_list_to_schemas(RoadmapRead, orm)
        if not filters_dict:
            await scope.put(json.dumps([u.model_dump(mode="json") for u in schema], default=str), "list")
        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", roadmap: BaseIdType) -> RoadmapRead:
        """Return roadmap by id for current user"""
        scope = self._scope(current_user)
        cached = await scope.get("roadmap", str(roadmap), "detail")
        if cached:
            return cache_to_schema(RoadmapRead, cached)
        orm = await self.verify.verify_roadmap(roadmap, current_user.id)
        schema = orm_to_schema(RoadmapRead, orm)
        await scope.put(json.dumps([schema.model_dump(mode="json")]), "roadmap", str(roadmap), "detail")
        return schema

    @service_handler
    async def create(self, current_user: "User", data: RoadmapCreate) -> RoadmapRead:
        """Create new roadmap for current user"""
        roadmap_dict = data.model_dump(exclude_none=True, exclude_unset=True)
        roadmap_dict["id"] = generate_base_id()
        roadmap_dict["user_id"] = current_user.id
        orm = await self.repo.create(roadmap_dict)
        schema = orm_to_schema(RoadmapRead, orm)
        await self._scope(current_user).drop(("list",))
        return schema

    @service_handler
    async def update(self, current_user: "User", roadmap: BaseIdType, data: RoadmapUpdate) -> RoadmapRead:
        """Update roadmap for current user"""
        await self.verify.verify_roadmap(roadmap, current_user.id)
        roadmap_dict = data.model_dump(exclude_none=True, exclude_unset=True)
        orm = await self.repo.update(roadmap, roadmap_dict)
        schema = orm_to_schema(RoadmapRead, orm)
        await self._scope(current_user).drop(
            ("list",),
            ("roadmap", str(roadmap), "detail"),
        )
        return schema

    @service_handler
    async def delete(self, current_user: "User", roadmap: BaseIdType) -> None:
        """Delete roadmap for current user"""
        await self.verify.verify_roadmap(roadmap, current_user.id)
        await self.repo.delete(roadmap)
        await self._scope(current_user).drop(
            ("list",),
            ("roadmap", str(roadmap), "detail"),
        )
