import random
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.models import User
from app.schemas.question import QuestionStatus
from app.schemas.session import (
    SessionCardsFilter,
    SessionCreate,
    SessionFilters,
    SessionFinishResult,
    SessionItemRead,
    SessionMode,
    SessionRead,
    SessionStatus,
    SessionUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils.mappers.orm_to_schema import orm_list_to_schemas, orm_to_schema

if TYPE_CHECKING:
    from app.core.cache import CacheHelper
    from app.repositories import (
        BlockRepository,
        QuestionRepository,
        SessionItemRepository,
        SessionRepository,
    )


class SessionService:
    """Service for managing learning sessions: creation, navigation, and lifecycle."""

    def __init__(
        self,
        repo: "SessionRepository",
        block_repo: "BlockRepository",
        question_repo: "QuestionRepository",
        session_item_repo: "SessionItemRepository",
        cache: "CacheHelper",
    ):
        self.repo = repo
        self.block_repo = block_repo
        self.question_repo = question_repo
        self.session_item_repo = session_item_repo
        self.cache = cache

    @service_handler
    async def get_all(self) -> list[SessionRead]:
        """Return all sessions across all users."""
        orm = await self.repo.get_all()
        return orm_list_to_schemas(SessionRead, orm)

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: SessionFilters,
    ) -> list[SessionRead]:
        """Return sessions belonging to the current user that match the given filters."""
        filters_dict = filters.model_dump(exclude_none=True, exclude_unset=True)
        orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        schema = orm_list_to_schemas(SessionRead, orm)
        return schema

    @service_handler
    async def get_by_id(
        self,
        current_user: "User",
        session_id: BaseIdType,
    ) -> SessionRead:
        """Return a single session by ID, scoped to the current user."""
        orm = await self.repo.get_by_id(session_id, current_user.id)
        schema = orm_to_schema(SessionRead, orm)
        return schema

    @service_handler
    async def get_session_questions(
        self,
        current_user: "User",
        session_id: BaseIdType,
        filters: SessionCardsFilter,
    ) -> list[BaseIdType]:
        """Return a paginated slice of question IDs for the given session."""
        orm = await self.repo.get_questions(session_id, current_user.id)
        result = orm[filters.offset : filters.offset + filters.limit]
        return result

    @service_handler
    async def get_next_question(
        self,
        current_user: "User",
        session_id: BaseIdType,
    ) -> BaseIdType | None:
        """Return the ID of the next unanswered question in the session, or None if all are answered."""
        session = await self.repo.get_by_id(session_id, current_user.id)
        answered_ids = await self.session_item_repo.get_answered_ids(session_id)
        result = next(
            (q for q in session.questions if q not in answered_ids),
            None,
        )
        return result

    @service_handler
    async def create(self, current_user: "User", session_create_data: SessionCreate) -> SessionRead:
        """Create a new session with a fixed ordered list of questions resolved from filters.

        In REPEAT mode, only questions with status 'review' are included.
        If mix is enabled, the question order is randomized before saving.
        """
        filters = session_create_data.model_dump(
            exclude={"mode", "mix", "auto_check"},
            exclude_none=True,
            exclude_unset=True,
        )
        if session_create_data.mode is SessionMode.REPEAT:
            filters["status"] = "review"

        if filters.get("block_id") is None:
            blocks_filters = {k: v for k, v in filters.items() if k != "status"}
            blocks_ids = [b.id for b in await self.block_repo.get_by_filters(blocks_filters, current_user.id)]
        else:
            blocks_ids = [filters.get("block_id")]

        questions = []
        if blocks_ids:
            filters["block_id"] = blocks_ids.copy()
            questions = [q.id for q in await self.question_repo.get_by_filters(filters, current_user.id)]

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
        """Apply a partial update to the session and return the updated state."""
        session_dict = session_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        orm = await self.repo.update(session_id, session_dict, current_user.id)
        schema = orm_to_schema(SessionRead, orm)
        return schema

    @service_handler
    async def finish(
        self,
        current_user: "User",
        session_id: BaseIdType,
    ) -> SessionFinishResult:
        """Mark the session as completed and return a summary of results.

        In auto_check mode, raises if the last question has not yet been evaluated by AI.
        Calculates known/unknown/repeat counts and accuracy percentage across all answered items.
        """
        session = await self.repo.get_by_id(session_id, current_user.id)
        items = await self.session_item_repo.get_by_session(session_id)

        if session.auto_check:
            last_item = next(
                (i for i in items if i.question_id == session.questions[-1]),
                None,
            )
            if last_item is None or last_item.result is None:
                raise Exception("Session evaluation is not complete yet")

        known_count = sum(1 for i in items if i.result == QuestionStatus.KNOWN)
        unknown_count = sum(1 for i in items if i.result == QuestionStatus.UNKNOWN)
        repeat_count = sum(1 for i in items if i.result == QuestionStatus.REPEAT)
        total = len(items)

        await self.repo.update(
            session_id,
            {"status": SessionStatus.COMPLETED, "completed_at": datetime.now()},
            current_user.id,
        )

        return SessionFinishResult(
            id=session.id,
            roadmap_id=session.roadmap_id,
            block_id=session.block_id,
            mode=SessionMode(session.mode),
            auto_check=session.auto_check,
            total=total,
            known_count=known_count,
            unknown_count=unknown_count,
            repeat_count=repeat_count,
            accuracy_percentage=round(known_count / total * 100, 2) if total else 0,
            items=orm_list_to_schemas(SessionItemRead, items),
        )

    @service_handler
    async def delete(
        self,
        current_user: "User",
        session_id: BaseIdType,
    ):
        """Delete the session owned by the current user."""
        await self.repo.delete(session_id, current_user.id)
