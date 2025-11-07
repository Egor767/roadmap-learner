from typing import List

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.core.types import BaseIDType
from app.models.postgres.block import Block
from app.schemas.block import BlockInDB, BlockFilters


def map_to_schema(db_block: Block) -> BlockInDB:
    return BlockInDB.model_validate(db_block)


class BlockRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @repository_handler
    async def get_all_blocks(self) -> List[BlockInDB]:
        stmt = select(Block)
        result = await self.session.execute(stmt)
        db_blocks = result.scalars().all()
        return [map_to_schema(block) for block in db_blocks]

    @repository_handler
    async def get_roadmap_block(
        self, roadmap_id: BaseIDType, block_id: BaseIDType
    ) -> BlockInDB:
        stmt = select(Block).where(Block.id == block_id, Block.roadmap_id == roadmap_id)
        result = await self.session.execute(stmt)
        block = result.scalar_one_or_none()
        return map_to_schema(block) if block else None

    @repository_handler
    async def get_roadmap_blocks(
        self, roadmap_id: BaseIDType, filters: BlockFilters
    ) -> List[BlockInDB]:
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
    async def get_block(self, block_id: BaseIDType) -> BlockInDB:
        stmt = select(Block).where(Block.id == block_id)
        result = await self.session.execute(stmt)
        db_block = result.scalar_one_or_none()
        return map_to_schema(db_block) if db_block else None

    @repository_handler
    async def create_block(self, block_data: dict) -> BlockInDB:
        async with transaction_manager(self.session):
            stmt = insert(Block).values(**block_data).returning(Block)
            result = await self.session.execute(stmt)
            db_block = result.scalar_one()
            return map_to_schema(db_block)

    @repository_handler
    async def delete_block(self, roadmap_id: BaseIDType, block_id: BaseIDType) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Block).where(
                Block.roadmap_id == roadmap_id, Block.id == block_id
            )
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update_block(
        self, road_id: BaseIDType, block_id: BaseIDType, block_data: dict
    ) -> BlockInDB:
        async with transaction_manager(self.session):
            stmt = (
                update(Block)
                .where(Block.roadmap_id == road_id, Block.id == block_id)
                .values(**block_data)
                .returning(Block)
            )
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one_or_none()
            return map_to_schema(db_roadmap) if db_roadmap else None
