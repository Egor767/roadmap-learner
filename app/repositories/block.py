from sqlalchemy import (
    select,
    insert,
    update,
    delete,
)

from app.core.custom_exceptions import EntityNotFoundError
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.core.custom_types import BaseIdType
from app.repositories import BaseRepository
from app.models import Block, Roadmap


class BlockRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Block]:
        stmt = select(Block)
        result = await self.session.execute(stmt)
        blocks = list(result.scalars().all())
        return blocks

    @repository_handler
    async def get_by_id(self, block_id: BaseIdType, user_id: BaseIdType) -> Block:
        stmt = (
            select(Block)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Block.id == block_id, Roadmap.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        block = result.scalar_one_or_none()
        if block is None:
            raise EntityNotFoundError(Block, block_id)
        return block

    @repository_handler
    async def get_by_filters(self, filters: dict, user_id: BaseIdType) -> list[Block]:
        stmt = (
            select(Block)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Roadmap.user_id == user_id)
        )
        for field_name, value in filters.items():
            column = getattr(Block, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        blocks = list(result.scalars().all())
        return blocks

    @repository_handler
    async def create(self, block_data: dict) -> Block:
        async with transaction_manager(self.session):
            stmt = insert(Block).values(**block_data).returning(Block)
            result = await self.session.execute(stmt)
            block = result.scalar_one()
            return block

    @repository_handler
    async def update(
        self, block_id: BaseIdType, block_data: dict, user_id: BaseIdType
    ) -> Block:
        async with transaction_manager(self.session):
            stmt = (
                update(Block)
                .where(
                    Block.id == block_id,
                    Block.roadmap_id.in_(
                        select(Roadmap.id).where(Roadmap.user_id == user_id)
                    ),
                )
                .values(**block_data)
                .returning(Block)
            )
            result = await self.session.execute(stmt)
            block = result.scalar_one_or_none()
            if block is None:
                raise EntityNotFoundError(Block, block_id)
            return block

    @repository_handler
    async def delete(self, block_id: BaseIdType, user_id: BaseIdType) -> Block:
        async with transaction_manager(self.session):
            stmt = (
                delete(Block)
                .where(
                    Block.id == block_id,
                    Block.roadmap_id.in_(
                        select(Roadmap.id).where(Roadmap.user_id == user_id)
                    ),
                )
                .returning(Block)
            )
            result = await self.session.execute(stmt)
            block = result.scalar_one_or_none()
            if block is None:
                raise EntityNotFoundError(Block, block_id)
            return block
