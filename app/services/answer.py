from typing import TYPE_CHECKING

from fastapi import BackgroundTasks

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.models import User
from app.schemas.ai import ConceptContext, EvaluateAnswerResponse
from app.schemas.session import SessionItemCreate
from app.shared.generate_id import generate_base_id

if TYPE_CHECKING:
    from app.clients.ai import AIClient
    from app.repositories import (
        ConceptRepository,
        QuestionRepository,
        SessionRepository,
    )


class AnswerService:
    """Service for submitting and evaluating answers within a session"""

    def __init__(
        self,
        repo: "SessionRepository",
        question_repo: "QuestionRepository",
        concept_repo: "ConceptRepository",
        ai_client: "AIClient",
    ):
        self.repo = repo
        self.question_repo = question_repo
        self.concept_repo = concept_repo
        self.ai_client = ai_client

    @service_handler
    async def submit_answer(
        self,
        user: "User",
        session: BaseIdType,
        data: SessionItemCreate,
        background_tasks: BackgroundTasks,
    ) -> None:
        """Record the user's answer for a question within a session"""
        orm = await self.repo.get_by_id(session, user.id)
        item = await self.repo.create_item(
            {
                "id": generate_base_id(),
                "session_id": session,
                "question_id": data.question_id,
                "answer": data.answer,
                "hint": data.hint,
                "result": None if orm.auto_check else data.result,
            }
        )
        if orm.auto_check:
            background_tasks.add_task(
                self._evaluate_answer,
                item.id,
                user.id,
            )
        else:
            await self.question_repo.update_status(data.question_id, data.result, user.id)

    async def _evaluate_answer(self, item: BaseIdType, user: BaseIdType) -> None:
        """Evaluate a submitted answer using AI and persist the result"""
        session_item = await self.repo.get_item_by_id(item)
        question = await self.question_repo.get_by_id(session_item.question_id, user)
        concepts = await self.concept_repo.get_by_question(session_item.question_id, user)
        evaluation: EvaluateAnswerResponse = await self.ai_client.evaluate_answer(
            question=question.question,
            correct_answer=question.answer,
            answer=session_item.answer,
            hint=session_item.hint,
            concepts=[ConceptContext(term=c.term, definition=c.definition) for c in concepts],
        )
        await self.repo.update_item(item, {"result": evaluation.result, "note": evaluation.note})
        await self.question_repo.update_status(session_item.question_id, evaluation.result, user)
