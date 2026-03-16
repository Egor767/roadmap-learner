from typing import TYPE_CHECKING

from fastapi import BackgroundTasks

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.models import User
from app.schemas.ai import CardContext, EvaluateAnswerResponse
from app.schemas.session import SessionItemCreate
from app.shared.generate_id import generate_base_id

if TYPE_CHECKING:
    from app.clients.ai import AIClient
    from app.repositories import (
        CardRepository,
        QuestionRepository,
        SessionRepository,
    )


class AnswerService:
    """Service for submitting and evaluating answers within a session."""

    def __init__(
        self,
        repo: "SessionRepository",
        question_repo: "QuestionRepository",
        card_repo: "CardRepository",
        ai_client: "AIClient",
    ):
        self.repo = repo
        self.question_repo = question_repo
        self.card_repo = card_repo
        self.ai_client = ai_client

    @service_handler
    async def submit_answer(
        self, current_user: "User", session: BaseIdType, data: SessionItemCreate, background_tasks: BackgroundTasks
    ) -> BaseIdType | None:
        """Record the user's answer for a question within a session.

        In auto_check mode, schedules AI evaluation as a background task and does not
        immediately update progress. In manual mode, saves result and updates progress at once.
        Returns the ID of the next unanswered question, or None if the session is complete.
        """
        orm = await self.repo.get_by_id(session)
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
                current_user.id,
            )
        else:
            await self.question_repo.update_progress(current_user.id, data.question_id, data.result)
        next_question_id = await self._next(session, orm.questions)
        return next_question_id

    async def _next(self, session: BaseIdType, questions: list[BaseIdType]) -> BaseIdType | None:
        """Return the next unanswered question ID in the ordered questions list."""
        answered_ids = await self.repo.get_answered_ids(session)
        result = next((q for q in questions if q not in answered_ids), None)
        return result

    async def _evaluate_answer(self, item: BaseIdType, user: BaseIdType) -> None:
        """Evaluate a submitted answer using AI and persist the result.

        Fetches the session item, question, and linked term cards, sends them to the AI
        for evaluation, then updates the item result and the user's question progress.
        """
        session_item = await self.repo.get_item_by_id(item)
        question = await self.question_repo.get_by_id(session_item.question_id)
        cards = await self.card_repo.get_by_question(session_item.question_id)
        evaluation: EvaluateAnswerResponse = await self.ai_client.evaluate_answer(
            question=question.question,
            correct_answer=question.answer,
            answer=session_item.answer,
            hint=session_item.hint,
            cards=[CardContext(term=c.term, definition=c.definition) for c in cards],
        )
        await self.repo.update_item(item, {"result": evaluation.result, "note": evaluation.note})
        await self.question_repo.update_progress(user, session_item.question_id, evaluation.result)
