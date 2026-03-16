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
    @repository_handler
    async def get_all(self) -> list[Block]:
        stmt = select(Block).order_by(Block.order_index)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, block: BaseIdType, user: BaseIdType) -> Block:
        stmt = (
            select(Block)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Block.id == block, Roadmap.user_id == user)
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Block, block)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Block]:
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
        user: BaseIdType,
        position: Literal["start", "end"] = "end",
        previous: BaseIdType | None = None,
    ) -> Block:
        async with transaction_manager(self.session):
            sub_query = select(Roadmap.id).where(Roadmap.id == roadmap, Roadmap.user_id == user)
            if (await self.session.execute(sub_query)).scalar_one_or_none() is None:
                raise EntityNotFoundError(Roadmap, roadmap)
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
    async def update(self, block: BaseIdType, data: dict, user: BaseIdType) -> Block:
        async with transaction_manager(self.session):
            stmt = (
                update(Block)
                .where(
                    Block.id == block,
                    Block.roadmap_id.in_(select(Roadmap.id).where(Roadmap.user_id == user)),
                )
                .values(**data)
                .returning(Block)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Block, block)
            return row

    @repository_handler
    async def move(
        self, roadmap: BaseIdType, block: BaseIdType, previous: BaseIdType | None, user: BaseIdType
    ) -> Block:
        async with transaction_manager(self.session):
            stmt = select(Block).where(
                Block.id == block,
                Block.roadmap_id == roadmap,
                Block.roadmap_id.in_(select(Roadmap.id).where(Roadmap.user_id == user)),
            )
            row = (await self.session.execute(stmt)).scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Block, block)
            old_index = row.order_index
            if previous is None:
                new_index = 0
            else:
                stmt = select(Block.order_index).where(
                    Block.id == previous,
                    Block.roadmap_id == roadmap,
                )
                after_index = (await self.session.execute(stmt)).scalar_one_or_none()
                if after_index is None:
                    raise EntityNotFoundError(Block, previous)

                if after_index < old_index:
                    new_index = after_index + 1
                else:
                    new_index = after_index
            if new_index == old_index:
                return row
            if new_index < old_index:
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
            result = await self.session.execute(
                update(Block).where(Block.id == block).values(order_index=new_index).returning(Block)
            )
            row = result.scalar_one()
            return row

    @repository_handler
    async def delete(self, block: BaseIdType, user: BaseIdType) -> Block:
        async with transaction_manager(self.session):
            stmt = (
                delete(Block)
                .where(
                    Block.id == block,
                    Block.roadmap_id.in_(select(Roadmap.id).where(Roadmap.user_id == user)),
                )
                .returning(Block)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Block, block)
            return row

    @repository_handler
    async def create_multiple(self, roadmap_id: BaseIdType, data: list[dict], user: BaseIdType) -> list[Block]:
        async with transaction_manager(self.session):
            sub_query = select(Roadmap.id).where(
                Roadmap.id == roadmap_id,
                Roadmap.user_id == user,
            )
            if (await self.session.execute(sub_query)).scalar_one_or_none() is None:
                raise EntityNotFoundError(Roadmap, roadmap_id)
            max_stmt = select(func.max(Block.order_index)).where(
                Block.roadmap_id == roadmap_id,
            )
            max_index = (await self.session.execute(max_stmt)).scalar()
            start_index = (max_index + 1) if max_index is not None else 0
            for i, block in enumerate(data):
                block["order_index"] = start_index + i
            insert_stmt = insert(Block).values(data).returning(Block)
            result = await self.session.execute(insert_stmt)
            rows = list(result.scalars().all())
            return rows
