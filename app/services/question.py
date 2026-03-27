import asyncio
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.question import (
    QuestionConfirmRequest,
    QuestionCreate,
    QuestionFilters,
    QuestionRead,
    QuestionStatus,
    QuestionUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils.mappers import orm_to_schema, schema_to_cache, schemas_to_cache
from app.utils.mappers.cache_to_schema import (
    cache_to_schema,
    cache_to_schemas,
)
from app.utils.parent_filter import is_single_parent_filter

if TYPE_CHECKING:
    from app.core.cache import CacheHelper, CacheScope
    from app.models import User
    from app.repositories import QuestionRepository


class QuestionService:
    """Service for question business logic"""

    def __init__(self, repo: "QuestionRepository", cache: "CacheHelper"):
        self.repo = repo
        self.cache = cache

    def _scope(self, user: "User") -> "CacheScope":
        """Return cache scope"""
        return self.cache.scope("questions", str(user.id))

    @service_handler
    async def get_by_id(self, user: "User", id: BaseIdType) -> QuestionRead:
        """Return question by id"""
        scope = self._scope(user)
        cache = await scope.get("question", str(id), "detail")
        if cache:
            return cache_to_schema(QuestionRead, cache)
        orm, status = await asyncio.gather(
            self.repo.get_by_id(id, user.id),
            self.repo.get_status(id, user.id),
        )
        schema = orm_to_schema(QuestionRead, orm).model_copy(update={"status": status})
        await scope.put(schema_to_cache(schema), "question", str(id), "detail")
        return schema

    @service_handler
    async def get_by_filters(self, user: "User", filters: QuestionFilters) -> list[QuestionRead]:
        """Return questions matching filters"""
        filters_dump = filters.model_dump(exclude_none=True)
        status = filters_dump.pop("status", None)
        scope = self._scope(user)
        parent = is_single_parent_filter(filters_dump, "module_id")
        if parent:
            cache = await scope.get("module", str(filters_dump["module_id"]), "list")
            if cache:
                return cache_to_schemas(QuestionRead, cache)
        orms = await self.repo.get_by_filters(filters_dump, user.id)
        statuses = await self.repo.get_statuses(user.id, [q.id for q in orms])
        schemas = [
            orm_to_schema(QuestionRead, orm).model_copy(update={"status": statuses[orm.id]})
            for orm in orms
        ]
        if parent and status is None:
            await scope.put(
                schemas_to_cache(schemas), "module", str(filters_dump["module_id"]), "list"
            )
        return schemas

    @service_handler
    async def create(self, user: "User", payload: QuestionCreate) -> QuestionRead:
        """Create new question"""
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        data["id"] = generate_base_id()
        orm = await self.repo.create(payload.module_id, data, user.id)
        status = await self.repo.create_status(user.id, orm.id)
        schema = orm_to_schema(QuestionRead, orm).model_copy(update={"status": status})
        await self._scope(user).drop(("module", str(schema.module_id), "list"))
        return schema

    @service_handler
    async def update(self, user: "User", id: BaseIdType, payload: QuestionUpdate) -> QuestionRead:
        """Update question"""
        data = payload.dump()
        status = data.pop("status", None)
        if data:
            await self.repo.update(id, data, user.id)
        if status is not None:
            await self.repo.update_status(id, status, user.id)
        orm, actual = await asyncio.gather(
            self.repo.get_by_id(id, user.id),
            self.repo.get_status(id, user.id),
        )
        schema = orm_to_schema(QuestionRead, orm).model_copy(update={"status": actual})
        await self._scope(user).drop(
            ("module", str(schema.module_id), "list"),
            ("question", str(id), "detail"),
        )
        return schema

    @service_handler
    async def delete(self, user: "User", id: BaseIdType) -> None:
        """Delete question"""
        orm = await self.repo.delete(id, user.id)
        await self._scope(user).drop(
            ("module", str(orm.module_id), "list"),
            ("question", str(id), "detail"),
        )

    @service_handler
    async def create_multiple(
        self, user: "User", payload: "QuestionConfirmRequest"
    ) -> list[QuestionRead]:
        """Create multiple questions"""
        questions_by_module: dict[BaseIdType, list[dict]] = {}
        for item in payload.items:
            questions_dict = []
            for q in item.questions:
                q_dict = q.model_dump(exclude_none=True, exclude_unset=True)
                q_dict["id"] = generate_base_id()
                q_dict["module_id"] = item.module_id
                questions_dict.append(q_dict)
            questions_by_module[item.module_id] = questions_dict
        orms = await self.repo.create_multiple(questions_by_module)
        schemas = [
            orm_to_schema(QuestionRead, orm).model_copy(update={"status": QuestionStatus.UNKNOWN})
            for orm in orms
        ]
        scope = self._scope(user)
        module_ids = list({schema.module_id for schema in schemas})
        await scope.drop(*[("module", str(mid), "list") for mid in module_ids])
        await scope.flush("question")
        return schemas

    @service_handler
    async def link_concept(self, user: "User", id: BaseIdType, concept: BaseIdType) -> None:
        """Link concept to question"""
        await self.repo.link_concept(id, concept, user.id)

    @service_handler
    async def unlink_concept(self, user: "User", id: BaseIdType, concept: BaseIdType) -> None:
        """Link concept to question"""
        await self.repo.unlink_concept(id, concept, user.id)
