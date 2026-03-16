from typing import Literal

from sqlalchemy import (
    delete,
    func,
    insert,
    select,
    update,
)

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import Block, Roadmap
from app.repositories import BaseEntityRepository


class BlockRepository(BaseEntityRepository):
    """Repository for block data access"""

    @repository_handler
    async def get_all(self) -> list[Block]:
        """Return all blocks ordered by index"""
        stmt = select(Block).order_by(Block.order_index)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, block: BaseIdType) -> Block:
        """Return block by id"""
        stmt = select(Block).where(Block.id == block)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Block, block)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Block]:
        """Return blocks matching filters for user"""
        stmt = select(Block).join(Roadmap, Block.roadmap_id == Roadmap.id).where(Roadmap.user_id == user)
        for field_name, value in filters.items():
            column = getattr(Block, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Block.order_index)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def create(
        self,
        roadmap: BaseIdType,
        data: dict,
        position: Literal["start", "end"] = "end",
        previous: BaseIdType | None = None,
    ) -> Block:
        """Create block in roadmap at given position"""
        async with transaction_manager(self.session):
            if previous:
                after_stmt = select(Block.order_index).where(
                    Block.id == previous,
                    Block.roadmap_id == roadmap,
                )
                after_index = (await self.session.execute(after_stmt)).scalar_one_or_none()
                if after_index is None:
                    raise EntityNotFoundError(Block, previous)
                await self.session.execute(
                    update(Block)
                    .where(Block.roadmap_id == roadmap, Block.order_index > after_index)
                    .values(order_index=Block.order_index + 1)
                )
                data["order_index"] = after_index + 1
            elif position == "start":
                await self.session.execute(
                    update(Block).where(Block.roadmap_id == roadmap).values(order_index=Block.order_index + 1)
                )
                data["order_index"] = 0
            else:
                max_stmt = select(func.max(Block.order_index)).where(Block.roadmap_id == roadmap)
                max_index = (await self.session.execute(max_stmt)).scalar()
                data["order_index"] = (max_index + 1) if max_index is not None else 0
            stmt = insert(Block).values(**data).returning(Block)
            return (await self.session.execute(stmt)).scalar_one()

    @repository_handler
    async def update(self, block: BaseIdType, data: dict) -> Block:
        """Update block by id and return updated entity"""
        async with transaction_manager(self.session):
            stmt = update(Block).where(Block.id == block).values(**data).returning(Block)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Block, block)
            return row

    @repository_handler
    async def move(
        self, roadmap: BaseIdType, block: BaseIdType, previous: BaseIdType | None
    ) -> tuple[Block, list[BaseIdType]]:
        """Move block to new position within roadmap"""
        async with transaction_manager(self.session):
            stmt = select(Block).where(Block.id == block, Block.roadmap_id == roadmap)
            row = (await self.session.execute(stmt)).scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Block, block)
            old_index = row.order_index
            if previous is None:
                new_index = 0
            else:
                after_stmt = select(Block.order_index).where(
                    Block.id == previous,
                    Block.roadmap_id == roadmap,
                )
                after_index = (await self.session.execute(after_stmt)).scalar_one_or_none()
                if after_index is None:
                    raise EntityNotFoundError(Block, previous)
                new_index = after_index + 1 if after_index < old_index else after_index
            if new_index == old_index:
                return row, []
            if new_index < old_index:
                affected_stmt = select(Block.id).where(
                    Block.roadmap_id == roadmap,
                    Block.order_index >= new_index,
                    Block.order_index < old_index,
                    Block.id != block,
                )
                await self.session.execute(
                    update(Block)
                    .where(
                        Block.roadmap_id == roadmap,
                        Block.order_index >= new_index,
                        Block.order_index < old_index,
                        Block.id != block,
                    )
                    .values(order_index=Block.order_index + 1)
                )
            else:
                affected_stmt = select(Block.id).where(
                    Block.roadmap_id == roadmap,
                    Block.order_index > old_index,
                    Block.order_index <= new_index,
                    Block.id != block,
                )
                await self.session.execute(
                    update(Block)
                    .where(
                        Block.roadmap_id == roadmap,
                        Block.order_index > old_index,
                        Block.order_index <= new_index,
                        Block.id != block,
                    )
                    .values(order_index=Block.order_index - 1)
                )
            affected_ids = (await self.session.execute(affected_stmt)).scalars().all()
            result = await self.session.execute(
                update(Block).where(Block.id == block).values(order_index=new_index).returning(Block)
            )
            return result.scalar_one(), list(affected_ids)

    @repository_handler
    async def delete(self, block: BaseIdType) -> Block:
        """Delete block by id and return deleted entity"""
        async with transaction_manager(self.session):
            stmt = delete(Block).where(Block.id == block).returning(Block)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Block, block)
            return row

    @repository_handler
    async def create_multiple(self, roadmap_id: BaseIdType, data: list[dict]) -> list[Block]:
        """Create multiple blocks in roadmap"""
        async with transaction_manager(self.session):
            max_stmt = select(func.max(Block.order_index)).where(Block.roadmap_id == roadmap_id)
            max_index = (await self.session.execute(max_stmt)).scalar()
            start_index = (max_index + 1) if max_index is not None else 0
            for i, block in enumerate(data):
                block["order_index"] = start_index + i
            insert_stmt = insert(Block).values(data).returning(Block)
            result = await self.session.execute(insert_stmt)
            rows = list(result.scalars().all())
            return rows
