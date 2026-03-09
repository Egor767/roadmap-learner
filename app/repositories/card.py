from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import Card, Roadmap
from app.repositories import BaseRepository


class CardRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Card]:
        stmt = select(Card)
        result = await self.session.execute(stmt)
        cards = list(result.scalars().all())
        return cards

    @repository_handler
    async def get_by_id(self, card_id: BaseIdType, user_id: BaseIdType) -> Card:
        stmt = (
            select(Card)
            .join(Roadmap, Card.roadmap_id == Roadmap.id)
            .where(Card.id == card_id, Roadmap.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        card = result.scalar_one_or_none()
        if card is None:
            raise EntityNotFoundError(Card, card_id)
        return card

    @repository_handler
    async def get_by_filters(self, filters: dict, user_id: BaseIdType) -> list[Card]:
        stmt = select(Card).join(Roadmap, Card.roadmap_id == Roadmap.id).where(Roadmap.user_id == user_id)
        for field_name, value in filters.items():
            column = getattr(Card, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        cards = list(result.scalars().all())
        return cards

    @repository_handler
    async def create(self, card_data: dict, user_id: BaseIdType) -> Card:
        async with transaction_manager(self.session):
            roadmap_check_stmt = select(Roadmap.id).where(
                Roadmap.id == card_data.get("roadmap_id"), Roadmap.user_id == user_id
            )
            result = await self.session.execute(roadmap_check_stmt)
            if result.scalar_one_or_none() is None:
                raise EntityNotFoundError(Card, card_data.get("roadmap_id"))

            stmt = insert(Card).values(**card_data).returning(Card)
            result = await self.session.execute(stmt)
            card = result.scalar_one()
            return card

    @repository_handler
    async def update(self, card_id: BaseIdType, card_data: dict, user_id: BaseIdType) -> Card:
        async with transaction_manager(self.session):
            stmt = (
                update(Card)
                .where(
                    Card.id == card_id,
                    Card.roadmap_id.in_(select(Roadmap.id).where(Roadmap.user_id == user_id)),
                )
                .values(**card_data)
                .returning(Card)
            )
            result = await self.session.execute(stmt)
            card = result.scalar_one_or_none()
            if card is None:
                raise EntityNotFoundError(Card, card_id)
            return card

    @repository_handler
    async def delete(self, card_id: BaseIdType, user_id: BaseIdType) -> Card:
        async with transaction_manager(self.session):
            stmt = (
                delete(Card)
                .where(
                    Card.id == card_id,
                    Card.roadmap_id.in_(select(Roadmap.id).where(Roadmap.user_id == user_id)),
                )
                .returning(Card)
            )
            result = await self.session.execute(stmt)
            card = result.scalar_one_or_none()
            if card is None:
                raise EntityNotFoundError(Card, card_id)
            return card
