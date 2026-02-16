import random
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.core.loggers import session_manager_service_logger as logger
from app.external.requests import (
    get_cards_by_filters,
    get_blocks_by_filters,
)
from app.shared.access import get_accessed_filters, user_can_read_entity
from app.shared.generate_id import generate_base_id
from app.utils.mappers.orm_to_models import session_orm_to_model
from app.schemas.session import (
    SessionMode,
    SessionStatus,
    SessionResult,
    SessionCardsFilter,
)

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from app.core.custom_types import BaseIdType
    from app.repositories import SessionRepository
    from app.schemas.session import (
        SessionRead,
        SessionCreate,
        SessionFilters,
        SessionUpdate,
    )
    from app.models import User


class SessionService:
    def __init__(
        self,
        repo: "SessionRepository",
        redis: "Redis",
    ):
        self.repo = repo
        self.redis = redis

    @service_handler
    async def get_all(self) -> list["SessionRead"]:
        db_sessions = await self.repo.get_all()
        if not db_sessions:
            logger.warning("Sessions not found in DB")
            return []

        validated_sessions = [
            session_orm_to_model(db_session) for db_session in db_sessions
        ]

        return validated_sessions

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: "SessionFilters",
    ) -> list["SessionRead"]:
        filters_dict = filters.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        accessed_filters = get_accessed_filters(
            current_user,
            filters_dict,
        )

        db_sessions = await self.repo.get_by_filters(accessed_filters)
        if not db_sessions:
            logger.warning(
                "Sessions with filters(%r) not found",
                filters,
            )
            return []

        validated_sessions = [
            session_orm_to_model(db_session) for db_session in db_sessions
        ]

        return validated_sessions

    @service_handler
    async def get_by_id(
        self,
        current_user: "User",
        session_id: "BaseIdType",
    ) -> "SessionRead":
        db_session = await self.repo.get_by_id(session_id)
        if not db_session:
            logger.error("Session(id=%r) not found", session_id)
            raise ValueError("NOT_FOUND")

        validated_session = session_orm_to_model(db_session)
        user_can_read_entity(current_user, validated_session.model_dump())

        return validated_session

    @service_handler
    async def get_cards(
        self,
        current_user: "User",
        session_id: "BaseIdType",
        filters: "SessionCardsFilter",
    ) -> list["BaseIdType"]:
        session = await self.get_by_id(current_user, session_id)
        try:
            cards = session.card_ids_queue[
                filters.offset : filters.offset + filters.limit
            ]
        except Exception as e:
            logger.warning(
                "Cards access failed for session %r: queue=%r, index=%r, error=%r",
                session_id,
                getattr(session, "card_ids_queue", None),
                getattr(session, "current_card_index", None),
                e,
            )
            raise ValueError("Cards ids not found or invalid session state") from e

        return cards

    @service_handler
    async def create(
        self,
        current_user: "User",
        session_create_data: "SessionCreate",
        token: str,
    ) -> "SessionRead":
        filters = session_create_data.model_dump(
            exclude={"mode", "mix"},
            exclude_none=True,
            exclude_unset=True,
        )
        if session_create_data.mode is SessionMode.REVIEW:
            filters["status"] = "review"

        accessed_filters = get_accessed_filters(
            current_user,
            filters,
        )

        if not accessed_filters.get("block_id", None):
            blocks_filters = filters.copy()
            blocks_filters.pop("status", None)
            blocks_ids = [
                block.get("id")
                for block in await get_blocks_by_filters(token, blocks_filters)
            ]
        else:
            blocks_ids = [accessed_filters.get("block_id")]

        cards_ids = []
        if blocks_ids:
            accessed_filters["block_id"] = blocks_ids.copy()
            cards_data = await get_cards_by_filters(token, accessed_filters)
            cards_ids = [card["id"] for card in cards_data]

        session_dict = session_create_data.model_dump(exclude={"mix"})
        session_dict["user_id"] = current_user.id
        session_dict["id"] = generate_base_id()
        if session_create_data.mix:
            random.shuffle(cards_ids)
        session_dict["card_ids_queue"] = cards_ids

        created_session = await self.repo.create(session_dict)
        if not created_session:
            logger.error(
                "Session with params(%r) for User(id=%r) not created",
                created_session,
                current_user.id,
            )
            raise ValueError("OPERATION_FAILED")

        validated_created_session = session_orm_to_model(created_session)

        return validated_created_session

    @service_handler
    async def delete(
        self,
        current_user: "User",
        session_id: "BaseIdType",
    ) -> None:
        await self.get_by_id(current_user, session_id)

        success = await self.repo.delete(session_id)
        if success:
            logger.info("Session(id=%r) was deleted successfully", session_id)
        else:
            logger.error("Failed to delete Session(id=%r)", session_id)
            raise ValueError("OPERATION_FAILED")

    @service_handler
    async def update(
        self,
        current_user: "User",
        session_id: "BaseIdType",
        session_update_data: "SessionUpdate",
    ) -> "SessionRead":
        session = await self.get_by_id(current_user, session_id)

        session_dict = session_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        updated_session = await self.repo.update(session_id, session_dict)
        if not updated_session:
            logger.error("Failed to update Session(id=%r)", session_id)
            raise ValueError("OPERATION_FAILED")

        validated_updated_session = session_orm_to_model(updated_session)

        return validated_updated_session

    @service_handler
    async def finish(
        self,
        current_user: "User",
        session_id: "BaseIdType",
    ) -> SessionResult:
        session = await self.get_by_id(current_user, session_id)

        update_data = {
            "status": SessionStatus.COMPLETED,
            "completed_at": datetime.now(),
        }

        updated_session = await self.repo.update(session_id, update_data)
        if not updated_session:
            logger.error("Failed to update Session(id=%r)", session_id)
            raise ValueError("OPERATION_FAILED")

        session = session_orm_to_model(updated_session)

        reviewed_answers = session.correct_answers + session.incorrect_answers
        cards_len = len(session.card_ids_queue)

        accuracy = (
            int((session.correct_answers / reviewed_answers) * 100)
            if reviewed_answers != 0
            else 0
        )

        result = SessionResult(
            **session.model_dump(
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

        return result
