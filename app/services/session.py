import random
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.external.requests import (
    get_blocks_by_filters,
    get_questions_by_filters,
)
from app.models import User
from app.schemas.session import (
    SessionCardsFilter,
    SessionCreate,
    SessionFilters,
    SessionMode,
    SessionRead,
    SessionResult,
    SessionStatus,
    SessionUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils.mappers.orm_to_schema import (
    orm_list_to_schemas,
    orm_to_schema,
)

if TYPE_CHECKING:
    from app.core.cache import CacheHelper
    from app.repositories import SessionRepository


class SessionService:
    def __init__(self, repo: "SessionRepository", cache: "CacheHelper"):
        self.repo = repo
        self.cache = cache

    @service_handler
    async def get_all(self) -> list[SessionRead]:
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(SessionRead, orm)
        return schema

    @service_handler
    async def get_by_filters(self, current_user: "User", filters: SessionFilters) -> list[SessionRead]:
        filters_dict = filters.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        schema = orm_list_to_schemas(SessionRead, orm)
        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", session_id: BaseIdType) -> SessionRead:
        orm = await self.repo.get_by_id(session_id, current_user.id)
        schema = orm_to_schema(SessionRead, orm)
        return schema

    @service_handler
    async def get_questions(
        self, current_user: "User", session_id: BaseIdType, filters: SessionCardsFilter
    ) -> list[BaseIdType]:
        session = await self.get_by_id(current_user, session_id)
        questions = session.questions[filters.offset : filters.offset + filters.limit]
        return questions

    @service_handler
    async def create(self, current_user: "User", session_create_data: SessionCreate, token: str) -> SessionRead:
        filters = session_create_data.model_dump(
            exclude={"mode", "mix"},
            exclude_none=True,
            exclude_unset=True,
        )
        if session_create_data.mode is SessionMode.REVIEW:
            filters["status"] = "review"

        if filters.get("block_id", None) is None:
            blocks_filters = filters.copy()
            blocks_filters.pop("status", None)
            blocks_ids = [block.get("id") for block in await get_blocks_by_filters(token, blocks_filters)]
        else:
            blocks_ids = [filters.get("block_id")]

        questions = []
        if blocks_ids:
            filters["block_id"] = blocks_ids.copy()
            questions_data = await get_questions_by_filters(token, filters)
            questions = [q["id"] for q in questions_data]

        session_dict = session_create_data.model_dump(exclude={"mix"})
        session_dict["user_id"] = current_user.id
        session_dict["id"] = generate_base_id()
        if session_create_data.mix:
            random.shuffle(questions)
        session_dict["questions"] = questions

        orm = await self.repo.create(session_dict)

        schema = orm_to_schema(SessionRead, orm)

        return schema

    @service_handler
    async def update(
        self,
        current_user: "User",
        session_id: BaseIdType,
        session_update_data: SessionUpdate,
    ) -> SessionRead:
        session_dict = session_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        orm = await self.repo.update(session_id, session_dict, current_user.id)

        schema = orm_to_schema(SessionRead, orm)

        return schema

    @service_handler
    async def finish(self, current_user: "User", session_id: BaseIdType) -> SessionResult:
        update_data = {
            "status": SessionStatus.COMPLETED,
            "completed_at": datetime.now(),
        }

        orm = await self.repo.update(session_id, update_data, current_user.id)

        schema = orm_to_schema(SessionRead, orm)

        reviewed_answers = schema.correct_answers + schema.incorrect_answers
        questions_len = len(schema.questions)

        accuracy = int((schema.correct_answers / reviewed_answers) * 100) if reviewed_answers != 0 else 0

        result = SessionResult(
            **schema.model_dump(
                exclude={
                    "card_ids_queue",
                    "current_card_index",
                    "status",
                    "created_at",
                    "updated_at",
                }
            ),
            total_answers=questions_len,
            accuracy_percentage=accuracy,
        )

        return result

    @service_handler
    async def delete(self, current_user: "User", session_id: BaseIdType):
        await self.repo.delete(session_id, current_user.id)
