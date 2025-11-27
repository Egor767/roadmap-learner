from typing import TYPE_CHECKING
from sqlalchemy import (
    select,
    insert,
    update,
    delete,
)

from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.repositories import BaseRepository
from app.models import Block

if TYPE_CHECKING:
    from app.core.types import BaseIdType


class BlockRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Block]:
        stmt = select(Block)
        result = await self.session.execute(stmt)
        blocks = list(result.scalars().all())
        return blocks

    @repository_handler
    async def get_by_id(self, block_id: "BaseIdType") -> Block | None:
        stmt = select(Block).where(Block.id == block_id)
        result = await self.session.execute(stmt)
        block = result.scalar_one_or_none()
        return block

    @repository_handler
    async def get_by_filters(
        self,
        filters: dict,
    ) -> list[Block]:
        stmt = select(Block)
        for field_name, value in filters.items():
            if value is not None:
                column = getattr(Block, field_name, None)
                if column is not None:
                    if isinstance(value, list):
                        stmt = stmt.where(column.in_(value))
                    else:
                        stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        blocks = list(result.scalars().all())
        return blocks

    @repository_handler
    async def create(self, block_data: dict) -> Block | None:
        async with transaction_manager(self.session):
            stmt = insert(Block).values(**block_data).returning(Block)
            result = await self.session.execute(stmt)
            block = result.scalar_one_or_none()
            return block

    @repository_handler
    async def delete(self, block_id: "BaseIdType") -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Block).where(Block.id == block_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update(
        self,
        block_id: "BaseIdType",
        block_data: dict,
    ) -> Block | None:
        async with transaction_manager(self.session):
            stmt = (
                update(Block)
                .where(Block.id == block_id)
                .values(**block_data)
                .returning(Block)
            )
            result = await self.session.execute(stmt)
            block = result.scalar_one_or_none()
            return block
