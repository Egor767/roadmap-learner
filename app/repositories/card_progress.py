from typing import TYPE_CHECKING

from sqlalchemy import (
    select,
)
from sqlalchemy.dialects.postgresql import insert

from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import UserCardProgress
from app.schemas.card import CardStatus

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserCardProgressRepository:
    def __init__(self, session: "AsyncSession") -> None:
        self.session = session

    @repository_handler
    async def get_status(self, user: BaseIdType, question: BaseIdType) -> CardStatus:
        stmt = select(UserCardProgress.status).where(
            UserCardProgress.user_id == user,
            UserCardProgress.card_id == question,
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none() or CardStatus.UNKNOWN
        return row

    @repository_handler
    async def get_statuses(self, user: BaseIdType, questions: list[BaseIdType]) -> dict[BaseIdType, CardStatus]:
        stmt = select(
            UserCardProgress.card_id,
            UserCardProgress.status,
        ).where(
            UserCardProgress.user_id == user,
            UserCardProgress.card_id.in_(questions),
        )
        result = await self.session.execute(stmt)
        found = {row.question_id: row.status for row in result.all()}
        data = {q: found.get(q, CardStatus.UNKNOWN) for q in questions}
        return data

    @repository_handler
    async def get_ids_by_status(self, user: BaseIdType, status: CardStatus) -> list[BaseIdType]:
        stmt = select(UserCardProgress.card_id).where(
            UserCardProgress.user_id == user,
            UserCardProgress.status == status,
        )
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def create(self, user: BaseIdType, question: BaseIdType):
        async with transaction_manager(self.session):
            stmt = insert(UserCardProgress).values(
                user_id=user,
                question_id=question,
                status=CardStatus.UNKNOWN,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def update(self, user: BaseIdType, question: BaseIdType, status: CardStatus):
        async with transaction_manager(self.session):
            stmt = (
                insert(UserCardProgress)
                .values(user_id=user, question_id=question, status=status)
                .on_conflict_do_update(
                    index_elements=["user_id", "question_id"],
                    set_={"status": status},
                )
            )
            await self.session.execute(stmt)
