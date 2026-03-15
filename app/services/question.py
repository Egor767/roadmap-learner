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
from app.utils.cache import get_cache_key, is_single_parent_filter
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
    from app.core.cache import CacheHelper
    from app.models import User
    from app.repositories import QuestionCardRepository, QuestionRepository
    from app.repositories import UserQuestionProgressRepository as ProgressRepository


class QuestionService:
    def __init__(
        self,
        repo: "QuestionRepository",
        progress_repo: "ProgressRepository",
        question_card_repo: "QuestionCardRepository",
        cache: "CacheHelper",
    ):
        self.repo = repo
        self.progress_repo = progress_repo
        self.question_card_repo = question_card_repo
        self.cache = cache

    @service_handler
    async def get_all(self) -> list[QuestionRead]:
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(QuestionRead, orm)
        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", question_id: BaseIdType) -> QuestionRead:
        key = get_cache_key(
            "questions",
            "user",
            str(current_user.id),
            "question",
            str(question_id),
            "detail",
        )
        if cache := await self.cache.get(key):
            return cache_to_schema(QuestionRead, cache)

        question, status = await asyncio.gather(
            self.repo.get_by_id(question_id, current_user.id),
            self.progress_repo.get_status(current_user.id, question_id),
        )
        schema = orm_to_schema_status(QuestionRead, question, status)

        await self.cache.set(key, json.dumps([schema.model_dump(mode="json")]))

        return schema

    @service_handler
    async def get_by_filters(
        self, current_user: "User", filters: QuestionFilters, block_filter: list[BaseIdType]
    ) -> list[QuestionRead]:
        filters_dump = filters.model_dump(exclude_none=True, exclude_unset=True)
        status_filter = filters_dump.pop("status", None)
        filters_dict = {
            **{k: v for k, v in filters_dump.items() if v is not None},
        }

        if block_filter is not None:
            filters_dict["block_id"] = block_filter

        if is_single_parent_filter(filters_dict, "block_id"):
            key = get_cache_key(
                "questions",
                "user",
                str(current_user.id),
                "block",
                str(filters_dict["block_id"][0]),
                "list",
            )
            if cache := await self.cache.get(key):
                return cache_to_schemas(QuestionRead, cache)

        if status_filter is not None:
            allowed_ids = await self.progress_repo.get_ids_by_status(current_user.id, status_filter)
            filters_dict["id"] = allowed_ids

        orm = await self.repo.get_by_filters(filters_dict, current_user.id)

        statuses = await self.progress_repo.get_statuses(current_user.id, [q.id for q in orm])
        schemas = orm_list_to_schemas_statuses(QuestionRead, orm, statuses)

        if is_single_parent_filter(filters_dict, "block_id") and status_filter is None:
            await self.cache.set(
                key,
                json.dumps(
                    [s.model_dump(mode="json") for s in schemas],
                    default=str,
                ),
            )

        return schemas

    @service_handler
    async def create(self, current_user: "User", question_create: QuestionCreate) -> QuestionRead:
        question_dict = question_create.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        question_dict["id"] = generate_base_id()

        question_dict.pop("position", None)
        question_dict.pop("previous", None)

        orm = await self.repo.create(
            question_create.block_id,
            question_dict,
            current_user.id,
            question_create.position,
            question_create.previous,
        )

        schema = orm_to_schema_status(QuestionRead, orm, QuestionStatus.UNKNOWN)

        await self.cache.delete(
            get_cache_key(
                "questions",
                "user",
                str(current_user.id),
                "block",
                str(schema.block_id),
                "list",
            )
        )

        return schema

    @service_handler
    async def update(
        self,
        current_user: "User",
        question_id: BaseIdType,
        question_update_data: QuestionUpdate,
    ) -> QuestionRead:
        update_dict = question_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        status = update_dict.pop("status", None)

        tasks = []
        if update_dict:
            tasks.append(self.repo.update(question_id, update_dict, current_user.id))
        if status is not None:
            tasks.append(self.progress_repo.update(current_user.id, question_id, status))
        await asyncio.gather(*tasks)

        orm, final_status = await asyncio.gather(
            self.repo.get_by_id(question_id, current_user.id),
            self.progress_repo.get_status(current_user.id, question_id),
        )
        schema = orm_to_schema_status(QuestionRead, orm, final_status)

        await self.cache.delete(
            get_cache_key(
                "questions",
                "user",
                str(current_user.id),
                "block",
                str(schema.block_id),
                "list",
            ),
            get_cache_key(
                "questions",
                "user",
                str(current_user.id),
                "question",
                str(question_id),
                "detail",
            ),
        )

        return schema

    @service_handler
    async def move(
        self,
        current_user: "User",
        question_id: BaseIdType,
        move_data: QuestionMove,
    ) -> QuestionRead:
        orm = await self.repo.move(
            block_id=move_data.block_id,
            question_id=question_id,
            previous=move_data.previous,
            user=current_user.id,
        )

        schema = orm_to_schema_status(QuestionRead, orm, QuestionStatus.UNKNOWN)

        await self.cache.delete(
            get_cache_key(
                "questions",
                "user",
                str(current_user.id),
                "block",
                str(schema.block_id),
                "list",
            ),
            get_cache_key(
                "questions",
                "user",
                str(current_user.id),
                "question",
                str(question_id),
                "detail",
            ),
        )

        return schema

    @service_handler
    async def delete(self, current_user: "User", question_id: BaseIdType):
        orm = await self.repo.delete(question_id, current_user.id)

        await self.cache.delete(
            get_cache_key(
                "questions",
                "user",
                str(current_user.id),
                "block",
                str(orm.block_id),
                "list",
            ),
            get_cache_key(
                "questions",
                "user",
                str(current_user.id),
                "question",
                str(question_id),
                "detail",
            ),
        )

    @service_handler
    async def create_multiple(
        self,
        current_user: "User",
        request: "QuestionConfirmRequest",
    ) -> list[QuestionRead]:
        questions_by_block: dict[BaseIdType, list[dict]] = {}

        for item in request.items:
            questions_dict = []
            for q in item.questions:
                q_dict = q.model_dump(exclude_none=True, exclude_unset=True)
                q_dict["id"] = generate_base_id()
                q_dict["block_id"] = item.block_id
                questions_dict.append(q_dict)
            questions_by_block[item.block_id] = questions_dict

        orm = await self.repo.create_multiple(questions_by_block, current_user.id)

        schema = [orm_to_schema_status(QuestionRead, q, QuestionStatus.UNKNOWN) for q in orm]

        # инвалидируем кэш для каждого затронутого блока
        for block_id in questions_by_block:
            await self.cache.delete(
                get_cache_key(
                    "questions",
                    "user",
                    str(current_user.id),
                    "block",
                    str(block_id),
                    "list",
                )
            )

        return schema

    @service_handler
    async def link_card(self, current_user: "User", question_id: BaseIdType, card_id: BaseIdType):
        await self.repo.get_by_id(question_id, current_user.id)
        await self.question_card_repo.create(question_id, card_id)
