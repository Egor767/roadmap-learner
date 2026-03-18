import json
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
from app.utils.mappers.cache_to_schema import (
    cache_to_schema,
    cache_to_schemas,
)
from app.utils.mappers.orm_to_schema import (
    orm_list_to_schemas,
    orm_to_schema,
)
from app.utils.parent_filter import is_single_parent_filter

if TYPE_CHECKING:
    from app.core.cache import CacheHelper, CacheScope
    from app.models import User
    from app.repositories import ModuleRepository, VerifyRepository


class ModuleService:
    """Service for module business logic"""

    def __init__(self, repo: "ModuleRepository", verify: "VerifyRepository", cache: "CacheHelper"):
        self.repo = repo
        self.verify = verify
        self.cache = cache

    def _scope(self, current_user: "User") -> "CacheScope":
        """Return cache scope for current user"""
        return self.cache.scope("modules", str(current_user.id))

    @service_handler
    async def get_all(self) -> list[ModuleRead]:
        """Return all modules"""
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(ModuleRead, orm)
        return schema

    @service_handler
    async def get_by_filters(self, current_user: "User", filters: ModuleFilters) -> list[ModuleRead]:
        """Return modules matching filters for current user"""
        filters_dict = filters.model_dump(exclude_none=True, exclude_unset=True)
        scope = self._scope(current_user)
        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cached = await scope.get("roadmap", str(filters_dict["roadmap_id"]), "list")
            if cached:
                return cache_to_schemas(ModuleRead, cached)
        orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        schema = orm_list_to_schemas(ModuleRead, orm)
        if is_single_parent_filter(filters_dict, "roadmap_id"):
            await scope.put(
                json.dumps([u.model_dump(mode="json") for u in schema], default=str),
                "roadmap",
                str(filters_dict["roadmap_id"]),
                "list",
            )
        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", module: BaseIdType) -> ModuleRead:
        """Return module by id for current user"""
        scope = self._scope(current_user)
        cached = await scope.get("module", str(module), "detail")
        if cached:
            return cache_to_schema(ModuleRead, cached)
        orm = await self.verify.verify_module(module, current_user.id)
        schema = orm_to_schema(ModuleRead, orm)
        await scope.put(json.dumps([schema.model_dump(mode="json")]), "module", str(module), "detail")
        return schema

    @service_handler
    async def create(self, current_user: "User", data: ModuleCreate) -> ModuleRead:
        """Create new module for current user"""
        await self.verify.verify_roadmap(data.roadmap_id, current_user.id)
        module_dict = data.model_dump(exclude_none=True, exclude_unset=True)
        module_dict["id"] = generate_base_id()
        module_dict.pop("position", None)
        module_dict.pop("previous", None)
        orm = await self.repo.create(
            data.roadmap_id,
            module_dict,
            data.position,
            data.previous,
        )
        schema = orm_to_schema(ModuleRead, orm)
        await self._scope(current_user).drop(("roadmap", str(schema.roadmap_id), "list"))
        return schema

    @service_handler
    async def update(self, current_user: "User", module: BaseIdType, data: ModuleUpdate) -> ModuleRead:
        """Update module for current user"""
        await self.verify.verify_module(module, current_user.id)
        module_dict = data.model_dump(exclude_none=True, exclude_unset=True)
        orm = await self.repo.update(module, module_dict)
        schema = orm_to_schema(ModuleRead, orm)
        await self._scope(current_user).drop(
            ("roadmap", str(schema.roadmap_id), "list"),
            ("module", str(module), "detail"),
        )
        return schema

    @service_handler
    async def move(self, current_user: "User", module: BaseIdType, data: ModuleMove) -> ModuleRead:
        """Move module to new position for current user"""
        await self.verify.verify_roadmap(data.roadmap_id, current_user.id)
        orm, affected = await self.repo.move(data.roadmap_id, module, data.previous)
        schema = orm_to_schema(ModuleRead, orm)
        scope = self._scope(current_user)
        await scope.drop(
            ("roadmap", str(schema.roadmap_id), "list"),
            ("module", str(module), "detail"),
            *[("module", str(affected_id), "detail") for affected_id in affected],
        )
        return schema

    @service_handler
    async def delete(self, current_user: "User", module: BaseIdType) -> None:
        """Delete module for current user"""
        orm = await self.verify.verify_module(module, current_user.id)
        await self.repo.delete(module)
        await self._scope(current_user).drop(
            ("roadmap", str(orm.roadmap_id), "list"),
            ("module", str(module), "detail"),
        )

    @service_handler
    async def create_multiple(self, current_user: "User", request: "ModuleConfirmRequest") -> list[ModuleRead]:
        """Create multiple modules for current user"""
        await self.verify.verify_roadmap(request.roadmap_id, current_user.id)
        modules_dict = [module.model_dump(exclude_none=True, exclude_unset=True) for module in request.modules]
        for module in modules_dict:
            module["id"] = generate_base_id()
            module["roadmap_id"] = request.roadmap_id
        orm = await self.repo.create_multiple(request.roadmap_id, modules_dict)
        schema = orm_list_to_schemas(ModuleRead, orm)
        await self._scope(current_user).drop(("roadmap", str(request.roadmap_id), "list"))
        return schema
