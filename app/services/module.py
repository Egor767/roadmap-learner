from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.module import (
    ModuleConfirmRequest,
    ModuleCreate,
    ModuleFilters,
    ModuleMove,
    ModuleRead,
    ModuleUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils import is_single_parent_filter
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
    from app.repositories import ModuleRepository


class ModuleService:
    """Service for module business logic"""

    def __init__(self, repo: "ModuleRepository", cache: "CacheHelper"):
        self.repo = repo
        self.cache = cache

    def _scope(self, user: "User") -> "CacheScope":
        """Return cache scope"""
        return self.cache.scope("modules", str(user.id))

    @service_handler
    async def get_by_filters(self, user: "User", filters: ModuleFilters) -> list[ModuleRead]:
        """Return modules matching filters"""
        data = filters.model_dump(exclude_none=True)
        scope = self._scope(user)
        parent = is_single_parent_filter(data, "roadmap_id")
        if parent:
            cache = await scope.get("roadmap", str(data["roadmap_id"]), "list")
            if cache:
                return cache_to_schemas(ModuleRead, cache)
        orms = await self.repo.get_by_filters(data, user.id)
        schemas = orms_to_schemas(ModuleRead, orms)
        if parent:
            await scope.put(schemas_to_cache(schemas), "roadmap", str(data["roadmap_id"]), "list")
        return schemas

    @service_handler
    async def get_by_id(self, user: "User", id: BaseIdType) -> ModuleRead:
        """Return module by id"""
        scope = self._scope(user)
        cache = await scope.get("module", str(id), "detail")
        if cache:
            return cache_to_schema(ModuleRead, cache)
        orm = await self.repo.get_by_id(id, user.id)
        schema = orm_to_schema(ModuleRead, orm)
        await scope.put(schema_to_cache(schema), "module", str(id), "detail")
        return schema

    @service_handler
    async def create(self, user: "User", payload: ModuleCreate) -> ModuleRead:
        """Create new module"""
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        data["id"] = generate_base_id()
        data["user_id"] = user.id
        orm = await self.repo.create(data)
        schema = orm_to_schema(ModuleRead, orm)
        await self._scope(user).drop(("roadmap", str(schema.roadmap_id), "list"))
        return schema

    @service_handler
    async def update(self, user: "User", id: BaseIdType, payload: ModuleUpdate) -> ModuleRead:
        """Update module"""
        data = payload.dump()
        orm = await self.repo.update(id, data, user.id)
        schema = orm_to_schema(ModuleRead, orm)
        await self._scope(user).drop(
            ("roadmap", str(schema.roadmap_id), "list"), ("module", str(id), "detail")
        )
        return schema

    @service_handler
    async def move(self, user: "User", id: BaseIdType, payload: ModuleMove) -> ModuleRead:
        """Move module to new position"""
        orm = await self.repo.move(id, payload.previous, user.id)
        schema = orm_to_schema(ModuleRead, orm)
        scope = self._scope(user)
        await scope.drop(("roadmap", str(schema.roadmap_id), "list"))
        await scope.flush("module")
        return schema

    @service_handler
    async def delete(self, user: "User", id: BaseIdType) -> None:
        """Delete module"""
        orm = await self.repo.delete(id, user.id)
        await self._scope(user).drop(
            ("roadmap", str(orm.roadmap_id), "list"),
            ("module", str(id), "detail"),
        )

    @service_handler
    async def create_multiple(
        self, user: "User", payload: "ModuleConfirmRequest"
    ) -> list[ModuleRead]:
        """Create multiple modules"""
        data = [module.model_dump(exclude_unset=True) for module in payload.modules]
        for module in data:
            module["id"] = generate_base_id()
            module["roadmap_id"] = payload.roadmap_id
        orms = await self.repo.create_multiple(payload.roadmap_id, user.id, data)
        schemas = orms_to_schemas(ModuleRead, orms)
        await self._scope(user).drop(("roadmap", str(payload.roadmap_id), "list"))
        return schemas
