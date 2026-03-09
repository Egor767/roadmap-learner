from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import Block, Roadmap
from app.repositories import BaseRepository


class BlockRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Block]:
        stmt = select(Block)
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
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def create(self, data: dict, user: BaseIdType) -> Block:
        async with transaction_manager(self.session):
            roadmap_check_stmt = select(Roadmap.id).where(Roadmap.id == data.get("roadmap_id"), Roadmap.user_id == user)
            result = await self.session.execute(roadmap_check_stmt)
            if result.scalar_one_or_none() is None:
                raise EntityNotFoundError(Roadmap, data.get("roadmap_id"))

            stmt = insert(Block).values(**data).returning(Block)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

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
