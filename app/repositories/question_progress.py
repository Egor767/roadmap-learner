from typing import TYPE_CHECKING

from sqlalchemy import (
    select,
)
from sqlalchemy.dialects.postgresql import insert

from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import UserQuestionProgress
from app.schemas.question import QuestionStatus

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserQuestionProgressRepository:
    def __init__(self, session: "AsyncSession") -> None:
        self.session = session

    @repository_handler
    async def get_status(self, user_id: BaseIdType, question_id: BaseIdType) -> QuestionStatus:
        stmt = select(UserQuestionProgress.status).where(
            UserQuestionProgress.user_id == user_id,
            UserQuestionProgress.question_id == question_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or QuestionStatus.UNKNOWN

    @repository_handler
    async def get_statuses(
        self, user_id: BaseIdType, question_ids: list[BaseIdType]
    ) -> dict[BaseIdType, QuestionStatus]:
        stmt = select(
            UserQuestionProgress.question_id,
            UserQuestionProgress.status,
        ).where(
            UserQuestionProgress.user_id == user_id,
            UserQuestionProgress.question_id.in_(question_ids),
        )
        result = await self.session.execute(stmt)
        found = {row.question_id: row.status for row in result.all()}
        return {qid: found.get(qid, QuestionStatus.UNKNOWN) for qid in question_ids}

    @repository_handler
    async def get_ids_by_status(self, user_id: BaseIdType, status: QuestionStatus) -> list[BaseIdType]:
        stmt = select(UserQuestionProgress.question_id).where(
            UserQuestionProgress.user_id == user_id,
            UserQuestionProgress.status == status,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def create(self, user_id: BaseIdType, question_id: BaseIdType):
        async with transaction_manager(self.session):
            stmt = insert(UserQuestionProgress).values(
                user_id=user_id,
                question_id=question_id,
                status=QuestionStatus.UNKNOWN,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def update(self, user_id: BaseIdType, question_id: BaseIdType, status: QuestionStatus):
        async with transaction_manager(self.session):
            stmt = (
                insert(UserQuestionProgress)
                .values(user_id=user_id, question_id=question_id, status=status)
                .on_conflict_do_update(
                    index_elements=["user_id", "question_id"],
                    set_={"status": status},
                )
            )
            await self.session.execute(stmt)
