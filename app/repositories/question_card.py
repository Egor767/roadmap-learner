from typing import TYPE_CHECKING

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import QuestionCard

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class QuestionCardRepository:
    def __init__(self, session: "AsyncSession") -> None:
        self.session = session

    @repository_handler
    async def create(self, question: BaseIdType, card: BaseIdType) -> None:
        async with transaction_manager(self.session):
            stmt = insert(QuestionCard).values(
                question_id=question,
                card_id=card,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def delete(self, question: BaseIdType, card: BaseIdType) -> None:
        async with transaction_manager(self.session):
            stmt = delete(QuestionCard).where(
                question_id=question,
                card_id=card,
            )
            await self.session.execute(stmt)
