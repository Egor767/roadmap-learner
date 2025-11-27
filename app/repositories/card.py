from typing import TYPE_CHECKING
from sqlalchemy import (
    select,
    insert,
    update,
    delete,
)

from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.repositories import BaseRepository
from app.models import Card

if TYPE_CHECKING:
    from app.core.types import BaseIdType


class CardRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Card]:
        stmt = select(Card)
        result = await self.session.execute(stmt)
        cards = list(result.scalars().all())
        return cards

    @repository_handler
    async def get_by_id(self, card_id: "BaseIdType") -> Card | None:
        stmt = select(Card).where(Card.id == card_id)
        result = await self.session.execute(stmt)
        card = result.scalar_one_or_none()
        return card

    @repository_handler
    async def get_by_filters(
        self,
        filters: dict,
    ) -> list[Card]:
        stmt = select(Card)
        for field_name, value in filters.items():
            if value is not None:
                column = getattr(Card, field_name, None)
                if column is not None:
                    if isinstance(value, list):
                        stmt = stmt.where(column.in_(value))
                    else:
                        stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        cards = list(result.scalars().all())
        return cards

    @repository_handler
    async def create(self, card_data: dict) -> Card | None:
        async with transaction_manager(self.session):
            stmt = insert(Card).values(**card_data).returning(Card)
            result = await self.session.execute(stmt)
            card = result.scalar_one_or_none()
            return card

    @repository_handler
    async def delete(
        self,
        card_id: "BaseIdType",
    ) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Card).where(Card.id == card_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update(
        self,
        card_id: "BaseIdType",
        card_data: dict,
    ) -> Card | None:
        async with transaction_manager(self.session):
            stmt = (
                update(Card)
                .where(Card.id == card_id)
                .values(**card_data)
                .returning(Card)
            )
            result = await self.session.execute(stmt)
            card = result.scalar_one_or_none()
            return card
