import asyncio
import json
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.question import (
    QuestionConfirmRequest,
    QuestionCreate,
    QuestionFilters,
    QuestionMove,
    QuestionRead,
    QuestionStatus,
    QuestionUpdate,
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
    from app.repositories import QuestionRepository, VerifyRepository


class QuestionService:
    """Service for question business logic."""

    def __init__(self, repo: "QuestionRepository", verify: "VerifyRepository", cache: "CacheHelper"):
        self.repo = repo
        self.verify = verify
        self.cache = cache

    def _scope(self, current_user: "User") -> "CacheScope":
        """Return cache scope for current user."""
        return self.cache.scope("questions", str(current_user.id))

    @service_handler
    async def get_all(self) -> list[QuestionRead]:
        """Return all questions."""
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(QuestionRead, orm)
        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", question: BaseIdType) -> QuestionRead:
        """Return question by id for current user."""
        scope = self._scope(current_user)
        cache = await scope.get("question", str(question), "detail")
        if cache:
            return cache_to_schema(QuestionRead, cache)
        question, status = await asyncio.gather(
            self.verify.verify_question(question, current_user.id),
            self.repo.get_status(current_user.id, question),
        )
        schema = orm_to_schema_status(QuestionRead, question, status)
        await scope.put(json.dumps([schema.model_dump(mode="json")]), "question", str(question), "detail")
        return schema

    @service_handler
    async def get_by_filters(
        self, current_user: "User", filters: QuestionFilters, module_filter: list[BaseIdType]
    ) -> list[QuestionRead]:
        """Return questions matching filters for current user."""
        filters_dump = filters.model_dump(exclude_none=True, exclude_unset=True)
        status_filter = filters_dump.pop("status", None)
        filters_dict = {k: v for k, v in filters_dump.items() if v is not None}
        if module_filter is not None:
            filters_dict["module_id"] = module_filter
        scope = self._scope(current_user)
        if is_single_parent_filter(filters_dict, "module_id"):
            cache = await scope.get("module", str(filters_dict["module_id"][0]), "list")
            if cache:
                return cache_to_schemas(QuestionRead, cache)
        if status_filter is not None:
            allowed_ids = await self.repo.get_ids_by_status(current_user.id, status_filter)
            if not allowed_ids:
                return []
            filters_dict["id"] = allowed_ids
        orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        statuses = await self.repo.get_statuses(current_user.id, [q.id for q in orm])
        schemas = orm_list_to_schemas_statuses(QuestionRead, orm, statuses)
        if is_single_parent_filter(filters_dict, "module_id") and status_filter is None:
            await scope.put(
                json.dumps([s.model_dump(mode="json") for s in schemas], default=str),
                "module",
                str(filters_dict["module_id"][0]),
                "list",
            )
        return schemas

    @service_handler
    async def create(self, current_user: "User", data: QuestionCreate) -> QuestionRead:
        """Create new question for current user."""
        await self.verify.verify_module(data.module_id, current_user.id)
        question_dict = data.model_dump(exclude_none=True, exclude_unset=True)
        question_dict["id"] = generate_base_id()
        question_dict.pop("position", None)
        question_dict.pop("previous", None)
        orm = await self.repo.create(
            data.module_id,
            question_dict,
            data.position,
            data.previous,
        )
        schema = orm_to_schema_status(QuestionRead, orm, QuestionStatus.UNKNOWN)
        await self._scope(current_user).drop(("module", str(schema.module_id), "list"))
        return schema

    @service_handler
    async def update(self, current_user: "User", question: BaseIdType, data: QuestionUpdate) -> QuestionRead:
        """Update question for current user."""
        await self.verify.verify_question(question, current_user.id)
        update_dict = data.model_dump(exclude_none=True, exclude_unset=True)
        status = update_dict.pop("status", None)
        tasks = []
        if update_dict:
            tasks.append(self.repo.update(question, update_dict))
        if status is not None:
            tasks.append(self.repo.update_progress(current_user.id, question, status))
        await asyncio.gather(*tasks)
        orm, final_status = await asyncio.gather(
            self.repo.get_by_id(question),
            self.repo.get_status(current_user.id, question),
        )
        schema = orm_to_schema_status(QuestionRead, orm, final_status)
        await self._scope(current_user).drop(
            ("module", str(schema.module_id), "list"),
            ("question", str(question), "detail"),
        )
        return schema

    @service_handler
    async def move(self, current_user: "User", question: BaseIdType, data: QuestionMove) -> QuestionRead:
        """Move question to new position for current user."""
        await self.verify.verify_module(data.module_id, current_user.id)
        orm, affected = await self.repo.move(
            module_id=data.module_id,
            question_id=question,
            previous=data.previous,
        )
        status = await self.repo.get_status(current_user.id, question)
        schema = orm_to_schema_status(QuestionRead, orm, status)
        await self._scope(current_user).drop(
            ("module", str(schema.module_id), "list"),
            ("question", str(question), "detail"),
            *[("question", str(affected_id), "detail") for affected_id in affected],
        )
        return schema

    @service_handler
    async def delete(self, current_user: "User", question: BaseIdType) -> None:
        """Delete question for current user."""
        orm = await self.verify.verify_question(question, current_user.id)
        await self.repo.delete(question)
        await self._scope(current_user).drop(
            ("module", str(orm.module_id), "list"),
            ("question", str(question), "detail"),
        )

    @service_handler
    async def create_multiple(self, current_user: "User", request: "QuestionConfirmRequest") -> list[QuestionRead]:
        """Create multiple questions for current user."""
        module_ids = [item.module_id for item in request.items]
        await self.verify.verify_modules(module_ids, current_user.id)
        questions_by_module: dict[BaseIdType, list[dict]] = {}
        for item in request.items:
            questions_dict = []
            for q in item.questions:
                q_dict = q.model_dump(exclude_none=True, exclude_unset=True)
                q_dict["id"] = generate_base_id()
                q_dict["module_id"] = item.module_id
                questions_dict.append(q_dict)
            questions_by_module[item.module_id] = questions_dict
        orm = await self.repo.create_multiple(questions_by_module)
        schemas = [orm_to_schema_status(QuestionRead, q, QuestionStatus.UNKNOWN) for q in orm]
        await self._scope(current_user).drop(*[("module", str(module_id), "list") for module_id in questions_by_module])
        return schemas

    @service_handler
    async def link_concept(self, current_user: "User", question: BaseIdType, concept: BaseIdType) -> None:
        """Link concept to question for current user."""
        await asyncio.gather(
            self.verify.verify_question(question, current_user.id),
            self.verify.verify_concept(concept, current_user.id),
        )
        await self.repo.link_concept(question, concept)
