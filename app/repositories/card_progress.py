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
    async def get_status(self, user: BaseIdType, card: BaseIdType) -> CardStatus:
        stmt = select(UserCardProgress.status).where(
            UserCardProgress.user_id == user,
            UserCardProgress.card_id == card,
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none() or CardStatus.UNKNOWN
        return row

    @repository_handler
    async def get_statuses(self, user: BaseIdType, cards: list[BaseIdType]) -> dict[BaseIdType, CardStatus]:
        stmt = select(
            UserCardProgress.card_id,
            UserCardProgress.status,
        ).where(
            UserCardProgress.user_id == user,
            UserCardProgress.card_id.in_(cards),
        )
        result = await self.session.execute(stmt)
        found = {row.card_id: row.status for row in result.all()}
        data = {q: found.get(q, CardStatus.UNKNOWN) for q in cards}
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
    async def create(self, user: BaseIdType, card: BaseIdType):
        async with transaction_manager(self.session):
            stmt = insert(UserCardProgress).values(
                user_id=user,
                card_id=card,
                status=CardStatus.UNKNOWN,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def update(self, user: BaseIdType, card: BaseIdType, status: CardStatus):
        async with transaction_manager(self.session):
            stmt = (
                insert(UserCardProgress)
                .values(user_id=user, card_id=card, status=status)
                .on_conflict_do_update(
                    index_elements=["user_id", "card_id"],
                    set_={"status": status},
                )
            )
            await self.session.execute(stmt)
