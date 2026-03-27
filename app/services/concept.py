import asyncio
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.concept import (
    ConceptCreate,
    ConceptFilters,
    ConceptRead,
    ConceptUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils.mappers import (
    cache_to_schema,
    cache_to_schemas,
    schema_to_cache,
    schemas_to_cache,
)
from app.utils.mappers.orm_to_schema import orm_to_schema
from app.utils.parent_filter import is_single_parent_filter

if TYPE_CHECKING:
    from app.core.cache import CacheHelper, CacheScope
    from app.models import User
    from app.repositories import ConceptRepository


class ConceptService:
    """Service for concept business logic"""

    def __init__(self, repo: "ConceptRepository", cache: "CacheHelper"):
        self.repo = repo
        self.cache = cache

    def _scope(self, user: "User") -> "CacheScope":
        """Return cache scope for current user"""
        return self.cache.scope("concepts", str(user.id))

    @service_handler
    async def get_by_filters(self, user: "User", filters: ConceptFilters) -> list[ConceptRead]:
        """Return concepts matching filters"""
        data = filters.model_dump(exclude_none=True)
        scope = self._scope(user)
        parent = is_single_parent_filter(data, "roadmap_id")
        if parent:
            cache = await scope.get("roadmap", str(data["roadmap_id"]), "list")
            if cache:
                return cache_to_schemas(ConceptRead, cache)
        orms = await self.repo.get_by_filters(data, user.id)
        statuses = await self.repo.get_statuses(user.id, [orm.id for orm in orms])
        schemas = [
            orm_to_schema(ConceptRead, orm).model_copy(update={"status": statuses[orm.id]})
            for orm in orms
        ]
        if parent:
            await scope.put(schemas_to_cache(schemas), "roadmap", str(data["roadmap_id"]), "list")
        return schemas

    @service_handler
    async def get_by_id(self, user: "User", id: BaseIdType) -> ConceptRead:
        """Return concept by id"""
        scope = self._scope(user)
        cache = await scope.get("concept", str(id), "detail")
        if cache:
            return cache_to_schema(ConceptRead, cache)
        orm, status = await asyncio.gather(
            self.repo.get_by_id(id, user.id),
            self.repo.get_status(id, user.id),
        )
        schema = orm_to_schema(ConceptRead, orm).model_copy(update={"status": status})
        await scope.put(schema_to_cache(schema), "concept", str(id), "detail")
        return schema

    @service_handler
    async def create(self, user: "User", payload: ConceptCreate) -> ConceptRead:
        """Create new concept for current user"""
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        data["id"] = generate_base_id()
        data["user_id"] = user.id
        orm = await self.repo.create(data)
        await self.repo.create_status(orm.id, user.id)
        schema = orm_to_schema(ConceptRead, orm)
        await self._scope(user).drop(("roadmap", str(schema.roadmap_id), "list"))
        return schema

    @service_handler
    async def update(self, user: "User", id: BaseIdType, payload: ConceptUpdate) -> ConceptRead:
        """Update concept"""
        data = payload.model_dump(exclude_unset=True)
        status = data.pop("status", None)
        clean = {k: v for k, v in data.items() if v or k in {"example", "comment", "definition"}}
        if clean:
            await self.repo.update(id, clean, user.id)
        if status:
            await self.repo.update_status(id, status, user.id)
        orm, actual = await asyncio.gather(
            self.repo.get_by_id(id, user.id),
            self.repo.get_status(id, user.id),
        )
        schema = orm_to_schema(ConceptRead, orm).model_copy(update={"status": actual})
        await self._scope(user).drop(
            ("roadmap", str(schema.roadmap_id), "list"),
            ("concept", str(id), "detail"),
        )
        return schema

    @service_handler
    async def delete(self, user: "User", id: BaseIdType) -> None:
        """Delete concept"""
        orm = await self.repo.delete(id, user.id)
        await self._scope(user).drop(
            ("roadmap", str(orm.roadmap_id), "list"),
            ("concept", str(id), "detail"),
        )
