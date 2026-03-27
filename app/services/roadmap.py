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
from app.utils.mappers import (
    cache_to_schema,
    cache_to_schemas,
    orm_to_schema,
    orms_to_schemas,
    schema_to_cache,
    schemas_to_cache,
)

if TYPE_CHECKING:
    from app.core.cache import CacheHelper, CacheScope
    from app.models import User
    from app.repositories import RoadmapRepository


class RoadmapService:
    """Service for roadmap business logic"""

    def __init__(self, repo: "RoadmapRepository", cache: "CacheHelper"):
        self.repo = repo
        self.cache = cache

    def _scope(self, current_user: "User") -> "CacheScope":
        """Return cache scope"""
        return self.cache.scope("roadmaps", str(current_user.id))

    @service_handler
    async def get_all(self, user: "User") -> list[RoadmapRead]:
        """Return all roadmaps"""
        scope = self._scope(user)
        cache = await scope.get("list")
        if cache:
            return cache_to_schemas(RoadmapRead, cache)
        orms = await self.repo.get_all(user.id)
        schemas = orms_to_schemas(RoadmapRead, orms)
        await scope.put(schemas_to_cache(schemas), "list")
        return schemas

    @service_handler
    async def get_by_filters(self, user: "User", filters: RoadmapFilters) -> list[RoadmapRead]:
        """Return roadmaps matching filters"""
        filters_dump = filters.model_dump(exclude_none=True)
        orms = await self.repo.get_by_filters(filters_dump, user.id)
        schemas = orms_to_schemas(RoadmapRead, orms)
        return schemas

    @service_handler
    async def get_by_id(self, user: "User", id: BaseIdType) -> RoadmapRead:
        """Return roadmap by id"""
        scope = self._scope(user)
        cache = await scope.get("roadmap", str(id), "detail")
        if cache:
            return cache_to_schema(RoadmapRead, cache)
        orm = await self.repo.get_by_id(id, user.id)
        schema = orm_to_schema(RoadmapRead, orm)
        await scope.put(schema_to_cache(schema), "roadmap", str(id), "detail")
        return schema

    @service_handler
    async def create(self, user: "User", payload: RoadmapCreate) -> RoadmapRead:
        """Create new roadmap"""
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        data["id"] = generate_base_id()
        data["user_id"] = user.id
        orm = await self.repo.create(data)
        schema = orm_to_schema(RoadmapRead, orm)
        await self._scope(user).drop(("list",))
        return schema

    @service_handler
    async def update(self, user: "User", id: BaseIdType, payload: RoadmapUpdate) -> RoadmapRead:
        """Update roadmap"""
        data = payload.model_dump(exclude_unset=True)
        orm = await self.repo.update(id, data, user.id)
        schema = orm_to_schema(RoadmapRead, orm)
        await self._scope(user).drop(("list",), ("roadmap", str(id), "detail"))
        return schema

    @service_handler
    async def delete(self, user: "User", id: BaseIdType) -> None:
        """Delete roadmap"""
        await self.repo.delete(id, user.id)
        await self._scope(user).drop(("list",), ("roadmap", str(id), "detail"))
