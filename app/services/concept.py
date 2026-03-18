import asyncio
import json
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.concept import (
    ConceptCreate,
    ConceptFilters,
    ConceptRead,
    ConceptStatus,
    ConceptUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils.mappers.cache_to_schema import (
    cache_to_schema,
    cache_to_schemas,
)
from app.utils.mappers.orm_to_schema import (
    orm_list_to_schemas,
    orm_list_to_schemas_statuses,
    orm_to_schema_status,
)
from app.utils.parent_filter import is_single_parent_filter

if TYPE_CHECKING:
    from app.core.cache import CacheHelper, CacheScope
    from app.models import User
    from app.repositories import ConceptRepository, VerifyRepository


class ConceptService:
    """Service for concept business logic."""

    def __init__(self, repo: "ConceptRepository", verify: "VerifyRepository", cache: "CacheHelper"):
        self.repo = repo
        self.verify = verify
        self.cache = cache

    def _scope(self, current_user: "User") -> "CacheScope":
        """Return cache scope for current user."""
        return self.cache.scope("concepts", str(current_user.id))

    @service_handler
    async def get_all(self) -> list[ConceptRead]:
        """Return all concepts."""
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(ConceptRead, orm)
        return schema

    @service_handler
    async def get_by_filters(self, current_user: "User", filters: ConceptFilters) -> list[ConceptRead]:
        """Return concepts matching filters for current user."""
        filters_dump = filters.model_dump(exclude_none=True, exclude_unset=True)
        status_filter = filters_dump.pop("status", None)
        filters_dict = {k: v for k, v in filters_dump.items() if v is not None}
        scope = self._scope(current_user)
        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cached = await scope.get("roadmap", str(filters_dict["roadmap_id"]), "list")
            if cached:
                return cache_to_schemas(ConceptRead, cached)
        if status_filter is not None:
            allowed_ids = await self.repo.get_ids_by_status(current_user.id, status_filter)
            if not allowed_ids:
                return []
            filters_dict["id"] = allowed_ids
        orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        statuses = await self.repo.get_statuses(current_user.id, [q.id for q in orm])
        schemas = orm_list_to_schemas_statuses(ConceptRead, orm, statuses)
        if is_single_parent_filter(filters_dict, "roadmap_id") and status_filter is None:
            await scope.put(
                json.dumps([u.model_dump(mode="json") for u in schemas], default=str),
                "roadmap",
                str(filters_dict["roadmap_id"]),
                "list",
            )
        return schemas

    @service_handler
    async def get_by_id(self, current_user: "User", concept_id: BaseIdType) -> ConceptRead:
        """Return concept by id for current user."""
        scope = self._scope(current_user)
        cached = await scope.get("concept", str(concept_id), "detail")
        if cached:
            return cache_to_schema(ConceptRead, cached)
        concept, status = await asyncio.gather(
            self.verify.verify_concept(concept_id, current_user.id),
            self.repo.get_status(current_user.id, concept_id),
        )
        schema = orm_to_schema_status(ConceptRead, concept, status)
        await scope.put(json.dumps([schema.model_dump(mode="json")]), "concept", str(concept_id), "detail")
        return schema

    @service_handler
    async def create(self, current_user: "User", create_data: ConceptCreate) -> ConceptRead:
        """Create new concept for current user."""
        await self.verify.verify_roadmap(create_data.roadmap_id, current_user.id)
        data = create_data.model_dump(exclude_none=True, exclude_unset=True)
        data["id"] = generate_base_id()
        orm = await self.repo.create(data)
        await self.repo.create_progress(current_user.id, orm.id)
        schema = orm_to_schema_status(ConceptRead, orm, ConceptStatus.UNKNOWN)
        await self._scope(current_user).drop(("roadmap", str(schema.roadmap_id), "list"))
        return schema

    @service_handler
    async def update(self, current_user: "User", concept_id: BaseIdType, update_data: ConceptUpdate) -> ConceptRead:
        """Update concept for current user."""
        await self.verify.verify_concept(concept_id, current_user.id)
        data = update_data.model_dump(exclude_none=True, exclude_unset=True)
        status = data.pop("status", None)
        tasks = []
        if data:
            tasks.append(self.repo.update(concept_id, data))
        if status is not None:
            tasks.append(self.repo.update_progress(current_user.id, concept_id, status))
        await asyncio.gather(*tasks)
        orm, final_status = await asyncio.gather(
            self.repo.get_by_id(concept_id),
            self.repo.get_status(current_user.id, concept_id),
        )
        schema = orm_to_schema_status(ConceptRead, orm, final_status)
        await self._scope(current_user).drop(
            ("roadmap", str(schema.roadmap_id), "list"),
            ("concept", str(concept_id), "detail"),
        )
        return schema

    @service_handler
    async def delete(self, current_user: "User", concept_id: BaseIdType) -> None:
        """Delete concept for current user."""
        concept = await self.verify.verify_concept(concept_id, current_user.id)
        await self.repo.delete(concept_id)
        await self._scope(current_user).drop(
            ("roadmap", str(concept.roadmap_id), "list"),
            ("concept", str(concept_id), "detail"),
        )
