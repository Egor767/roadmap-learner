import random
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.custom_exceptions import ServiceError
from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.models import User
from app.schemas.question import QuestionStatus
from app.schemas.session import (
    SessionCreate,
    SessionFilters,
    SessionFinishResult,
    SessionItemRead,
    SessionMode,
    SessionQuestionFilter,
    SessionRead,
    SessionStatus,
    SessionUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils.mappers.orm_to_schema import orm_to_schema, orms_to_schemas

if TYPE_CHECKING:
    from app.clients import AIClient
    from app.core.cache import CacheHelper
    from app.repositories import (
        ModuleRepository,
        QuestionRepository,
        SessionRepository,
    )


class SessionService:
    """Service for managing learning sessions: creation, navigation, and lifecycle"""

    def __init__(
        self,
        repo: "SessionRepository",
        module_repo: "ModuleRepository",
        question_repo: "QuestionRepository",
        cache: "CacheHelper",
        ai_client: "AIClient",
    ):
        self.repo = repo
        self.module_repo = module_repo
        self.question_repo = question_repo
        self.cache = cache
        self.ai_client = ai_client

    @service_handler
    async def get_all(self, user: "User") -> list[SessionRead]:
        """Return all sessions across"""
        orm = await self.repo.get_all(user.id)
        return orms_to_schemas(SessionRead, orm)

    @service_handler
    async def get_by_filters(self, user: "User", filters: SessionFilters) -> list[SessionRead]:
        """Return sessions  that match the given filters"""
        filters_dump = filters.model_dump(exclude_none=True, exclude_unset=True)
        orm = await self.repo.get_by_filters(filters_dump, user.id)
        schema = orms_to_schemas(SessionRead, orm)
        return schema

    @service_handler
    async def get_by_id(self, user: "User", id: BaseIdType) -> SessionRead:
        """Return a single session by id"""
        orm = await self.repo.get_by_id(id, user.id)
        schema = orm_to_schema(SessionRead, orm)
        return schema

    @service_handler
    async def get_session_questions(
        self, user: "User", id: BaseIdType, filters: SessionQuestionFilter
    ) -> list[BaseIdType]:
        """Return a paginated slice of question ids for the given sessin"""
        questions = await self.repo.get_questions(id, user.id)
        result = questions[filters.offset : filters.offset + filters.limit]
        return result

    @service_handler
    async def get_next_question(self, user: "User", id: BaseIdType) -> BaseIdType | None:
        """Return the id of the next unanswered question in the session"""
        session = await self.repo.get_by_id(id, user.id)
        answered_ids = await self.repo.get_answered_ids(id, user.id)
        result = next((q for q in session.questions if q not in answered_ids), None)
        return result

    @service_handler
    async def create(self, user: "User", payload: SessionCreate) -> SessionRead:
        """Create a new session with a fixed ordered list of questions resolved from filters"""
        available = await self.ai_client.health_check()
        if payload.auto_check and not available:
            raise ServiceError("AI service is unavailable, auto_check mode is not allowed")
        filters = payload.model_dump(
            exclude={"mode", "mix", "auto_check"},
            exclude_none=True,
            exclude_unset=True,
        )
        if payload.mode is SessionMode.REPEAT:
            filters["status"] = "review"
        if filters.get("module_id") is None:
            modules_filters = {k: v for k, v in filters.items() if k != "status"}
            modules_ids = [
                b.id for b in await self.module_repo.get_by_filters(modules_filters, user.id)
            ]
        else:
            modules_ids = [filters.get("module_id")]
        questions = []
        if modules_ids:
            filters["module_id"] = modules_ids.copy()
            questions = [q.id for q in await self.question_repo.get_by_filters(filters, user.id)]
        session_dict = payload.model_dump(exclude={"mix"})
        session_dict["user_id"] = user.id
        session_dict["id"] = generate_base_id()
        if payload.mix:
            random.shuffle(questions)
        session_dict["questions"] = questions
        orm = await self.repo.create(session_dict)
        schema = orm_to_schema(SessionRead, orm)
        return schema

    @service_handler
    async def update(self, user: "User", id: BaseIdType, payload: SessionUpdate) -> SessionRead:
        """Apply a partial update to the session and return the updated state"""
        data = payload.model_dump(exclude_none=True, exclude_unset=True)
        orm = await self.repo.update(id, data, user.id)
        schema = orm_to_schema(SessionRead, orm)
        return schema

    @service_handler
    async def finish(self, user: "User", id: BaseIdType) -> SessionFinishResult:
        """Mark the session as completed and return a summary of results"""
        session = await self.repo.get_by_id(id, user.id)
        items = await self.repo.get_items_by_session(id, user.id)
        if session.auto_check:
            last_item = next((i for i in items if i.question_id == session.questions[-1]), None)
            if last_item is None or last_item.result is None:
                raise ServiceError("Session evaluation is not complete yet")
        known_count = sum(1 for i in items if i.result == QuestionStatus.KNOWN)
        unknown_count = sum(1 for i in items if i.result == QuestionStatus.UNKNOWN)
        repeat_count = sum(1 for i in items if i.result == QuestionStatus.REPEAT)
        total = len(items)
        await self.repo.update(
            id, {"status": SessionStatus.COMPLETED, "completed_at": datetime.now()}
        )
        return SessionFinishResult(
            id=session.id,
            roadmap_id=session.roadmap_id,
            module_id=session.module_id,
            mode=SessionMode(session.mode),
            auto_check=session.auto_check,
            total=total,
            known_count=known_count,
            unknown_count=unknown_count,
            repeat_count=repeat_count,
            accuracy_percentage=round(known_count / total * 100, 2) if total else 0,
            items=orms_to_schemas(SessionItemRead, items),
        )

    @service_handler
    async def delete(self, user: "User", id: BaseIdType) -> None:
        """Delete the session"""
        await self.repo.delete(id, user.id)
