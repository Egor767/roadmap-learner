from typing import List, Optional

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import transaction_manager
from core.handlers import repository_handler
from core.types import BaseIdType
from models import Card
from schemas.card import CardInDB, CardFilters


def map_to_schema(db_card: Optional[Card]) -> Optional[CardInDB]:
    if db_card:
        return CardInDB.model_validate(db_card)
    return


class CardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @repository_handler
    async def get_all_cards(self) -> List[CardInDB]:
        stmt = select(Card)
        result = await self.session.execute(stmt)
        db_cards = result.scalars().all()
        return [map_to_schema(card) for card in db_cards]

    @repository_handler
    async def get_card(self, card_id: BaseIdType) -> CardInDB:
        stmt = select(Card).where(Card.id == card_id)
        result = await self.session.execute(stmt)
        card = result.scalar_one_or_none()
        return map_to_schema(card)

    @repository_handler
    async def get_block_card(
        self, block_id: BaseIdType, card_id: BaseIdType
    ) -> CardInDB:
        stmt = select(Card).where(Card.id == card_id).where(Card.block_id == block_id)
        result = await self.session.execute(stmt)
        card = result.scalar_one_or_none()
        return map_to_schema(card)

    @repository_handler
    async def get_block_cards(
        self, block_id: BaseIdType, filters: CardFilters
    ) -> List[CardInDB]:
        stmt = select(Card).where(Card.block_id == block_id)

        if filters.term:
            stmt = stmt.where(Card.term == filters.term)
        if filters.definition:
            stmt = stmt.where(Card.definition == filters.definition)
        if filters.comment:
            stmt = stmt.where(Card.comment == filters.term)
        if filters.example:
            stmt = stmt.where(Card.example == filters.example)
        if filters.status:
            stmt = stmt.where(Card.status == filters.status)

        result = await self.session.execute(stmt)
        db_blocks = result.scalars().all()
        return [map_to_schema(block) for block in db_blocks]

    @repository_handler
    async def create_card(self, card_data: dict) -> CardInDB:
        async with transaction_manager(self.session):
            stmt = insert(Card).values(**card_data).returning(Card)
            result = await self.session.execute(stmt)
            db_card = result.scalar_one_or_none()
            return map_to_schema(db_card)

    @repository_handler
    async def delete_card(self, block_id: BaseIdType, card_id: BaseIdType) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Card).where(Card.block_id == block_id, Card.id == card_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update_card(
        self, block_id: BaseIdType, card_id: BaseIdType, card_data: dict
    ) -> CardInDB:
        async with transaction_manager(self.session):
            stmt = (
                update(Card)
                .where(Card.block_id == block_id, Card.id == card_id)
                .values(**card_data)
                .returning(Card)
            )
            result = await self.session.execute(stmt)
            db_card = result.scalar_one_or_none()
            return map_to_schema(db_card)
