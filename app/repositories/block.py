from sqlalchemy import select, insert, update, delete

from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.core.types import BaseIdType
from app.models import Block
from app.repositories import BaseRepository
from app.schemas.block import BlockRead, BlockFilters


def map_to_schema(db_block: Block | None) -> BlockRead | None:
    if db_block:
        return BlockRead.model_validate(db_block)
    return


class BlockRepository(BaseRepository):
    @repository_handler
    async def get_by_id(self, block_id: BaseIdType) -> BlockRead:
        stmt = select(Block).where(Block.id == block_id)

        result = await self.session.execute(stmt)
        db_block = result.scalar_one_or_none()

        return map_to_schema(db_block)

    @repository_handler
    async def get_all(self) -> list[BlockRead]:
        stmt = select(Block)

        result = await self.session.execute(stmt)
        db_blocks = result.scalars().all()

        return [map_to_schema(block) for block in db_blocks]

    @repository_handler
    async def get_by_parent(
        self,
        roadmap_id: BaseIdType,
        block_id: BaseIdType,
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
    async def get_by_filters(
        self,
        filters: BlockFilters,
    ) -> list[BlockRead] | list[None]:
        stmt = select(Block)

        for field_name, value in vars(filters).items():
            if value is not None:
                column = getattr(Block, field_name, None)
                if column is not None:
                    stmt = stmt.where(column == value)

        result = await self.session.execute(stmt)
        db_blocks = result.scalars().all()

        return [map_to_schema(block) for block in db_blocks]

    @repository_handler
    async def create(self, block_data: dict) -> BlockRead:
        async with transaction_manager(self.session):
            stmt = insert(Block).values(**block_data).returning(Block)

            result = await self.session.execute(stmt)
            db_block = result.scalar_one_or_none()

            return map_to_schema(db_block)

    @repository_handler
    async def delete(
        self,
        roadmap_id: BaseIdType,
        block_id: BaseIdType,
    ) -> bool:
        async with transaction_manager(self.session):
            stmt = (
                delete(Block)
                .where(Block.id == block_id)
                .where(Block.roadmap_id == roadmap_id)
            )

            result = await self.session.execute(stmt)

            return result.rowcount > 0

    @repository_handler
    async def update(
        self,
        block_id: BaseIdType,
        block_data: dict,
    ) -> BlockRead:
        async with transaction_manager(self.session):
            stmt = (
                update(Block)
                .where(Block.id == block_id)
                .values(**block_data)
                .returning(Block)
            )

            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one_or_none()

            return map_to_schema(db_roadmap)
