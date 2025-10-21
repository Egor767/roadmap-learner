import uuid
from contextlib import asynccontextmanager
from typing import List

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.handlers import repository_handler
from app.models.postgres.block import Block
from app.repositories.block.interface import IBlockRepository
from app.schemas.block import BlockInDB, BlockFilters


def map_to_schema(db_user: Block) -> BlockInDB:
    return BlockInDB.model_validate(db_user)


class BlockRepository(IBlockRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def _transaction(self):
        try:
            yield
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    @repository_handler
    async def create_block(self, block_data: dict) -> BlockInDB:
        pass

    @repository_handler
    async def get_all_blocks(self) -> List[BlockInDB]:
        stmt = select(Block)
        result = await self.session.execute(stmt)
        db_blocks = result.scalars().all()
        return [map_to_schema(block) for block in db_blocks]

    @repository_handler
    async def get_user_blocks(self, user_id: uuid.UUID) -> List[BlockInDB]:
        ...

    @repository_handler
    async def get_user_block(self, user_id: uuid.UUID, block_id: uuid.UUID) -> BlockInDB:
        ...

    @repository_handler
    async def get_user_blocks_by_filters(self, user_id: uuid.UUID, filters: BlockFilters) -> List[BlockInDB]:
        ...

    @repository_handler
    async def delete_block(self, user_id: uuid.UUID, block_id: uuid.UUID) -> bool:
        ...

    @repository_handler
    async def update_roadmap(self, user_id: uuid.UUID, block_id: uuid.UUID, block_data: dict) -> BlockInDB:
        ...

