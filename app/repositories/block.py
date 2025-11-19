from typing import List

from sqlalchemy import select, insert, update, delete

from core.db import transaction_manager
from core.handlers import repository_handler
from core.types import BaseIdType
from models import Block
from repositories import BaseRepository
from schemas.block import BlockRead, BlockFilters


def map_to_schema(db_block: Block | None) -> BlockRead | None:
    if db_block:
        return BlockRead.model_validate(db_block)
    return


class BlockRepository(BaseRepository):
    @repository_handler
    async def get_all_blocks(self) -> list[BlockRead]:
        stmt = select(Block)
        result = await self.session.execute(stmt)
        db_blocks = result.scalars().all()
        return [map_to_schema(block) for block in db_blocks]

    @repository_handler
    async def get_roadmap_block(
        self, roadmap_id: BaseIdType, block_id: BaseIdType
    ) -> BlockRead:
        stmt = (
            select(Block)
            .where(Block.id == block_id)
            .where(Block.roadmap_id == roadmap_id)
        )
        result = await self.session.execute(stmt)
        block = result.scalar_one_or_none()
        return map_to_schema(block)

    @repository_handler
    async def get_blocks(
        self,
        roadmap_id: BaseIdType,
        filters: BlockFilters,
    ) -> list[BlockRead]:
        stmt = select(Block).where(Block.roadmap_id == roadmap_id)

        if filters.title:
            stmt = stmt.where(Block.title == filters.title)
        if filters.description:
            stmt = stmt.where(Block.description == filters.description)
        if filters.status:
            stmt = stmt.where(Block.status == filters.status)

        result = await self.session.execute(stmt)
        db_blocks = result.scalars().all()
        return [map_to_schema(block) for block in db_blocks]

    @repository_handler
    async def get_block(self, block_id: BaseIdType) -> BlockRead:
        stmt = select(Block).where(Block.id == block_id)
        result = await self.session.execute(stmt)
        db_block = result.scalar_one_or_none()
        return map_to_schema(db_block)

    @repository_handler
    async def create_block(self, block_data: dict) -> BlockRead:
        async with transaction_manager(self.session):
            stmt = insert(Block).values(**block_data).returning(Block)
            result = await self.session.execute(stmt)
            db_block = result.scalar_one_or_none()
            return map_to_schema(db_block)

    @repository_handler
    async def delete_block(self, roadmap_id: BaseIdType, block_id: BaseIdType) -> bool:
        async with transaction_manager(self.session):
            stmt = (
                delete(Block)
                .where(Block.id == block_id)
                .where(Block.roadmap_id == roadmap_id)
            )
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update_block(
        self, roadmap_id: BaseIdType, block_id: BaseIdType, block_data: dict
    ) -> BlockRead:
        async with transaction_manager(self.session):
            stmt = (
                update(Block)
                .where(Block.id == block_id)
                .where(Block.roadmap_id == roadmap_id)
                .values(**block_data)
                .returning(Block)
            )
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one_or_none()
            return map_to_schema(db_roadmap)
