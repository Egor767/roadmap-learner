from sqlalchemy import (
    select,
    insert,
    update,
    delete,
)

from app.core.custom_exceptions import EntityNotFoundError
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.repositories import BaseRepository
from app.models import Card, Block, Roadmap
from app.core.custom_types import BaseIdType


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
            .join(Block, Card.block_id == Block.id)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Card.id == card_id, Roadmap.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        card = result.scalar_one_or_none()
        if card is None:
            raise EntityNotFoundError(Card, card_id)
        return card

    @repository_handler
    async def get_by_filters(self, filters: dict, user_id: BaseIdType) -> list[Card]:
        stmt = (
            select(Card)
            .join(Block, Card.block_id == Block.id)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Roadmap.user_id == user_id)
        )
        for field_name, value in filters.items():
            column = getattr(Card, field_name, None)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        cards = list(result.scalars().all())
        return cards

    @repository_handler
    async def create(self, card_data: dict) -> Card:
        async with transaction_manager(self.session):
            stmt = insert(Card).values(**card_data).returning(Card)
            result = await self.session.execute(stmt)
            card = result.scalar_one()
            return card

    @repository_handler
    async def update(
        self, card_id: BaseIdType, card_data: dict, user_id: BaseIdType
    ) -> Card:
        async with transaction_manager(self.session):
            allowed_block_ids = (
                select(Block.id).join(Roadmap).where(Roadmap.user_id == user_id)
            )

            stmt = (
                update(Card)
                .where(Card.id == card_id, Card.block_id.in_(allowed_block_ids))
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
                    Card.block_id.in_(
                        select(Block.id).join(Roadmap).where(Roadmap.user_id == user_id)
                    ),
                )
                .returning(Card)
            )
            result = await self.session.execute(stmt)
            card = result.scalar_one_or_none()
            if card is None:
                raise EntityNotFoundError(Card, card_id)
            return card
