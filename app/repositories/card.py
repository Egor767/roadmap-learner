from sqlalchemy import select, insert, update, delete

from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.core.types import BaseIdType
from app.models import Card
from app.repositories import BaseRepository
from app.schemas.card import CardRead, CardFilters


def map_to_schema(db_card: Card | None) -> CardRead | None:
    if db_card:
        return CardRead.model_validate(db_card)
    return


class CardRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[CardRead] | list[None]:
        stmt = select(Card)
        result = await self.session.execute(stmt)
        db_cards = result.scalars().all()
        return [map_to_schema(card) for card in db_cards]

    @repository_handler
    async def get_by_id(self, card_id: BaseIdType) -> CardRead | None:
        stmt = select(Card).where(Card.id == card_id)
        result = await self.session.execute(stmt)
        card = result.scalar_one_or_none()
        return map_to_schema(card)

    @repository_handler
    async def get_by_parent(
        self,
        block_id: BaseIdType,
        card_id: BaseIdType,
    ) -> CardRead | None:
        stmt = select(Card).where(
            Card.id == card_id,
            Card.block_id == block_id,
        )
        result = await self.session.execute(stmt)
        card = result.scalar_one_or_none()
        return map_to_schema(card)

    @repository_handler
    async def get_by_filters(
        self,
        filters: CardFilters,
    ) -> list[CardRead] | list[None]:
        stmt = select(Card)

        for field_name, value in vars(filters).items():
            if value is not None:
                column = getattr(Card, field_name, None)
                if column is not None:
                    stmt = stmt.where(column == value)

        result = await self.session.execute(stmt)
        db_blocks = result.scalars().all()
        return [map_to_schema(block) for block in db_blocks]

    @repository_handler
    async def create(self, card_data: dict) -> CardRead | None:
        async with transaction_manager(self.session):
            stmt = insert(Card).values(**card_data).returning(Card)
            result = await self.session.execute(stmt)
            db_card = result.scalar_one_or_none()
            return map_to_schema(db_card)

    @repository_handler
    async def delete(
        self,
        card_id: BaseIdType,
    ) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Card).where(Card.id == card_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update(
        self,
        card_id: BaseIdType,
        card_data: dict,
    ) -> CardRead | None:
        async with transaction_manager(self.session):
            stmt = (
                update(Card)
                .where(Card.id == card_id)
                .values(**card_data)
                .returning(Card)
            )
            result = await self.session.execute(stmt)
            db_card = result.scalar_one_or_none()
            return map_to_schema(db_card)
