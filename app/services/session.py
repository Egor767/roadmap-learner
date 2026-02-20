import random
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.external.requests import (
    get_cards_by_filters,
    get_blocks_by_filters,
)
from app.shared.generate_id import generate_base_id
from app.utils.mappers.orm_to_schema import (
    orms_to_schemas,
    orm_to_schema,
)
from app.schemas.session import (
    SessionMode,
    SessionStatus,
    SessionResult,
    SessionCardsFilter,
)
from app.core.custom_types import BaseIdType
from app.schemas.session import (
    SessionRead,
    SessionCreate,
    SessionFilters,
    SessionUpdate,
)
from app.models import User

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from app.repositories import SessionRepository


class SessionService:
    def __init__(
        self,
        repo: "SessionRepository",
        redis: "Redis",
    ):
        self.repo = repo
        self.redis = redis

    @service_handler
    async def get_all(self) -> list[SessionRead]:
        sessions_orm = await self.repo.get_all()
        sessions_schema = orms_to_schemas(SessionRead, sessions_orm)
        return sessions_schema

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: SessionFilters,
    ) -> list[SessionRead]:
        filters_dict = filters.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        sessions_orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        sessions_schema = orms_to_schemas(SessionRead, sessions_orm)
        return sessions_schema

    @service_handler
    async def get_by_id(
        self,
        current_user: "User",
        session_id: BaseIdType,
    ) -> SessionRead:
        session_orm = await self.repo.get_by_id(session_id, current_user.id)
        session_schema = orm_to_schema(SessionRead, session_orm)
        return session_schema

    @service_handler
    async def get_cards(
        self,
        current_user: "User",
        session_id: BaseIdType,
        filters: SessionCardsFilter,
    ) -> list[BaseIdType]:
        session = await self.get_by_id(current_user, session_id)
        cards = session.card_ids_queue[filters.offset : filters.offset + filters.limit]
        return cards

    @service_handler
    async def create(
        self,
        current_user: "User",
        session_create_data: SessionCreate,
        token: str,
    ) -> SessionRead:
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
            blocks_ids = [
                block.get("id")
                for block in await get_blocks_by_filters(token, blocks_filters)
            ]
        else:
            blocks_ids = [filters.get("block_id")]

        cards_ids = []
        if blocks_ids:
            filters["block_id"] = blocks_ids.copy()
            cards_data = await get_cards_by_filters(token, filters)
            cards_ids = [card["id"] for card in cards_data]

        session_dict = session_create_data.model_dump(exclude={"mix"})
        session_dict["user_id"] = current_user.id
        session_dict["id"] = generate_base_id()
        if session_create_data.mix:
            random.shuffle(cards_ids)
        session_dict["card_ids_queue"] = cards_ids

        session_orm = await self.repo.create(session_dict)

        session_schema = orm_to_schema(SessionRead, session_orm)

        return session_schema

    @service_handler
    async def delete(
        self,
        current_user: "User",
        session_id: BaseIdType,
    ):
        await self.repo.delete(session_id, current_user.id)

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

        session_orm = await self.repo.update(session_id, session_dict, current_user.id)

        session_schema = orm_to_schema(SessionRead, session_orm)

        return session_schema

    @service_handler
    async def finish(
        self,
        current_user: "User",
        session_id: BaseIdType,
    ) -> SessionResult:
        update_data = {
            "status": SessionStatus.COMPLETED,
            "completed_at": datetime.now(),
        }

        session_orm = await self.repo.update(session_id, update_data, current_user.id)

        session_schema = orm_to_schema(SessionRead, session_orm)

        reviewed_answers = (
            session_schema.correct_answers + session_schema.incorrect_answers
        )
        cards_len = len(session_schema.card_ids_queue)

        accuracy = (
            int((session_schema.correct_answers / reviewed_answers) * 100)
            if reviewed_answers != 0
            else 0
        )

        session_result = SessionResult(
            **session_schema.model_dump(
                exclude={
                    "card_ids_queue",
                    "current_card_index",
                    "status",
                    "created_at",
                    "updated_at",
                }
            ),
            total_cards=cards_len,
            accuracy_percentage=accuracy,
        )

        return session_result
