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
from app.utils.cache import is_single_parent_filter
from app.utils.mappers.cache_to_schema import (
    cache_to_schema,
    cache_to_schemas,
)
from app.utils.mappers.orm_to_schema import (
    orm_list_to_schemas,
    orm_list_to_schemas_statuses,
    orm_to_schema_status,
)

if TYPE_CHECKING:
    from app.core.cache import CacheHelper, CacheScope
    from app.models import User
    from app.repositories import QuestionCardRepository, QuestionRepository, VerifyRepository
    from app.repositories import UserQuestionProgressRepository as ProgressRepository


class QuestionService:
    """Service for question business logic"""

    def __init__(
        self,
        repo: "QuestionRepository",
        verify: "VerifyRepository",
        progress_repo: "ProgressRepository",
        question_card_repo: "QuestionCardRepository",
        cache: "CacheHelper",
    ):
        self.repo = repo
        self.verify = verify
        self.progress_repo = progress_repo
        self.question_card_repo = question_card_repo
        self.cache = cache

    def _scope(self, current_user: "User") -> "CacheScope":
        """Return cache scope for current user"""
        return self.cache.scope("questions", str(current_user.id))

    @service_handler
    async def get_all(self) -> list[QuestionRead]:
        """Return all questions"""
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(QuestionRead, orm)
        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", question_id: BaseIdType) -> QuestionRead:
        """Return question by id for current user"""
        scope = self._scope(current_user)
        cached = await scope.get("question", str(question_id), "detail")
        if cached:
            return cache_to_schema(QuestionRead, cached)
        question, status = await asyncio.gather(
            self.verify.verify_question(question_id, current_user.id),
            self.progress_repo.get_status(current_user.id, question_id),
        )
        schema = orm_to_schema_status(QuestionRead, question, status)
        await scope.put(json.dumps([schema.model_dump(mode="json")]), "question", str(question_id), "detail")
        return schema

    @service_handler
    async def get_by_filters(
        self, current_user: "User", filters: QuestionFilters, block_filter: list[BaseIdType]
    ) -> list[QuestionRead]:
        """Return questions matching filters for current user"""
        filters_dump = filters.model_dump(exclude_none=True, exclude_unset=True)
        status_filter = filters_dump.pop("status", None)
        filters_dict = {k: v for k, v in filters_dump.items() if v is not None}
        if block_filter is not None:
            filters_dict["block_id"] = block_filter
        scope = self._scope(current_user)
        if is_single_parent_filter(filters_dict, "block_id"):
            cached = await scope.get("block", str(filters_dict["block_id"][0]), "list")
            if cached:
                return cache_to_schemas(QuestionRead, cached)
        if status_filter is not None:
            allowed_ids = await self.progress_repo.get_ids_by_status(current_user.id, status_filter)
            if not allowed_ids:
                return []
            filters_dict["id"] = allowed_ids
        orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        statuses = await self.progress_repo.get_statuses(current_user.id, [q.id for q in orm])
        schemas = orm_list_to_schemas_statuses(QuestionRead, orm, statuses)
        if is_single_parent_filter(filters_dict, "block_id") and status_filter is None:
            await scope.put(
                json.dumps([s.model_dump(mode="json") for s in schemas], default=str),
                "block",
                str(filters_dict["block_id"][0]),
                "list",
            )
        return schemas

    @service_handler
    async def create(self, current_user: "User", question_create: QuestionCreate) -> QuestionRead:
        """Create new question for current user"""
        await self.verify.verify_block(question_create.block_id, current_user.id)
        question_dict = question_create.model_dump(exclude_none=True, exclude_unset=True)
        question_dict["id"] = generate_base_id()
        question_dict.pop("position", None)
        question_dict.pop("previous", None)
        orm = await self.repo.create(
            question_create.block_id,
            question_dict,
            question_create.position,
            question_create.previous,
        )
        schema = orm_to_schema_status(QuestionRead, orm, QuestionStatus.UNKNOWN)
        await self._scope(current_user).drop(("block", str(schema.block_id), "list"))
        return schema

    @service_handler
    async def update(
        self, current_user: "User", question_id: BaseIdType, question_update_data: QuestionUpdate
    ) -> QuestionRead:
        """Update question for current user"""
        await self.verify.verify_question(question_id, current_user.id)
        update_dict = question_update_data.model_dump(exclude_none=True, exclude_unset=True)
        status = update_dict.pop("status", None)
        tasks = []
        if update_dict:
            tasks.append(self.repo.update(question_id, update_dict))
        if status is not None:
            tasks.append(self.progress_repo.update(current_user.id, question_id, status))
        await asyncio.gather(*tasks)
        orm, final_status = await asyncio.gather(
            self.repo.get_by_id(question_id),
            self.progress_repo.get_status(current_user.id, question_id),
        )
        schema = orm_to_schema_status(QuestionRead, orm, final_status)
        await self._scope(current_user).drop(
            ("block", str(schema.block_id), "list"),
            ("question", str(question_id), "detail"),
        )
        return schema

    @service_handler
    async def move(self, current_user: "User", question_id: BaseIdType, move_data: QuestionMove) -> QuestionRead:
        """Move question to new position for current user"""
        await self.verify.verify_block(move_data.block_id, current_user.id)
        orm, affected = await self.repo.move(
            block_id=move_data.block_id,
            question_id=question_id,
            previous=move_data.previous,
        )
        status = await self.progress_repo.get_status(current_user.id, question_id)
        schema = orm_to_schema_status(QuestionRead, orm, status)
        await self._scope(current_user).drop(
            ("block", str(schema.block_id), "list"),
            ("question", str(question_id), "detail"),
            *[("question", str(affected_id), "detail") for affected_id in affected],
        )
        return schema

    @service_handler
    async def delete(self, current_user: "User", question_id: BaseIdType) -> None:
        """Delete question for current user"""
        question = await self.verify.verify_question(question_id, current_user.id)
        await self.repo.delete(question_id)
        await self._scope(current_user).drop(
            ("block", str(question.block_id), "list"),
            ("question", str(question_id), "detail"),
        )

    @service_handler
    async def create_multiple(self, current_user: "User", request: "QuestionConfirmRequest") -> list[QuestionRead]:
        """Create multiple questions for current user"""
        block_ids = [item.block_id for item in request.items]
        await self.verify.verify_blocks(block_ids, current_user.id)
        questions_by_block: dict[BaseIdType, list[dict]] = {}
        for item in request.items:
            questions_dict = []
            for q in item.questions:
                q_dict = q.model_dump(exclude_none=True, exclude_unset=True)
                q_dict["id"] = generate_base_id()
                q_dict["block_id"] = item.block_id
                questions_dict.append(q_dict)
            questions_by_block[item.block_id] = questions_dict
        orm = await self.repo.create_multiple(questions_by_block)
        schemas = [orm_to_schema_status(QuestionRead, q, QuestionStatus.UNKNOWN) for q in orm]
        await self._scope(current_user).drop(*[("block", str(block_id), "list") for block_id in questions_by_block])
        return schemas

    @service_handler
    async def link_card(self, current_user: "User", question_id: BaseIdType, card_id: BaseIdType) -> None:
        """Link card to question for current user"""
        await asyncio.gather(
            self.verify.verify_question(question_id, current_user.id),
            self.verify.verify_card(card_id, current_user.id),
        )
        await self.question_card_repo.create(question_id, card_id)
