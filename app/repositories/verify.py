from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.handlers import repository_handler
from app.models import Block, Card, Question, Roadmap

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class VerifyRepository:
    """Ownership verification repository for hierarchical resource access control"""

    def __init__(self, session: "AsyncSession"):
        self.session = session

    @repository_handler
    async def verify_roadmap(self, roadmap: BaseIdType, user: BaseIdType) -> Roadmap:
        """Verify that roadmap belongs to user and return it"""
        stmt = select(Roadmap).where(Roadmap.id == roadmap, Roadmap.user_id == user)
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Roadmap, roadmap)
        return row

    @repository_handler
    async def verify_block(self, block: BaseIdType, user: BaseIdType) -> Block:
        """Verify that block belongs to user through roadmap and return it."""
        stmt = (
            select(Block)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Block.id == block, Roadmap.user_id == user)
        )
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Block, block)
        return row

    @repository_handler
    async def verify_blocks(self, blocks: list[BaseIdType], user: BaseIdType) -> None:
        """Verify that all blocks belong to user through roadmap."""
        stmt = (
            select(Block.id)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Block.id.in_(blocks), Roadmap.user_id == user)
        )
        result = await self.session.execute(stmt)
        valid = {row[0] for row in result.fetchall()}
        missing = set(blocks) - valid
        if missing:
            raise EntityNotFoundError(Block, missing.pop())

    @repository_handler
    async def verify_question(self, question: BaseIdType, user: BaseIdType) -> Question:
        """Verify that question belongs to user through block and roadmap and return it"""
        stmt = (
            select(Question)
            .join(Block, Question.block_id == Block.id)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Question.id == question, Roadmap.user_id == user)
        )
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Question, question)
        return row

    @repository_handler
    async def verify_card(self, card: BaseIdType, user: BaseIdType) -> Card:
        """Verify that card belongs to user through roadmap and return it."""
        stmt = select(Card).join(Roadmap, Card.roadmap_id == Roadmap.id).where(Card.id == card, Roadmap.user_id == user)
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Card, card)
        return row
