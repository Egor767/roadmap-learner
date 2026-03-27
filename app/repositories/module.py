from typing import cast

from sqlalchemy import (
    and_,
    delete,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.engine import CursorResult

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import Module, Roadmap
from app.repositories import BaseEntityRepository


class ModuleRepository(BaseEntityRepository):
    """Repository for module data access"""

    @repository_handler
    async def get_all(self, user: BaseIdType) -> list[Module]:
        """Return all modules rdered by title verified against user through roadmap"""
        stmt = (
            select(Module)
            .join(Roadmap, Roadmap.id == Module.roadmap_id)
            .where(Roadmap.user_id == user)
            .order_by(Module.title)
        )
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, id: BaseIdType, user: BaseIdType) -> Module:
        """Return module by id verified against user through roadmap"""
        stmt = (
            select(Module)
            .join(Roadmap, Roadmap.id == Module.roadmap_id)
            .where(Module.id == id, Roadmap.user_id == user)
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Module, id)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Module]:
        """Return modules matching filters verified against user through roadmapr"""
        stmt = (
            select(Module)
            .join(Roadmap, Module.roadmap_id == Roadmap.id)
            .where(Roadmap.user_id == user)
        )
        for field, value in filters.items():
            column = getattr(Module, field)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Module.order_index)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    async def _index_for_previous(self, roadmap: BaseIdType, previous: BaseIdType) -> int:
        """Return order_index to place module after previous"""
        stmt = select(Module.order_index).where(
            Module.id == previous,
            Module.roadmap_id == roadmap,
        )
        result = await self.session.execute(stmt)
        index = result.scalar_one_or_none()
        if index is None:
            raise EntityNotFoundError(Module, previous)
        await self.session.execute(
            update(Module)
            .where(Module.roadmap_id == roadmap, Module.order_index > index)
            .values(order_index=Module.order_index + 1)
        )
        return index + 1

    async def _index_for_start(self, roadmap: BaseIdType) -> int:
        """Return order_index to place module at start"""
        await self.session.execute(
            update(Module)
            .where(Module.roadmap_id == roadmap)
            .values(order_index=Module.order_index + 1)
        )
        return 0

    async def _index_for_end(self, roadmap: BaseIdType) -> int:
        """Return order_index to place module at end"""
        stmt = select(func.max(Module.order_index)).where(Module.roadmap_id == roadmap)
        index = (await self.session.execute(stmt)).scalar()
        return (index + 1) if index is not None else 0

    async def _resolve_index(
        self, roadmap: BaseIdType, position: str, previous: BaseIdType | None
    ) -> int:
        """Return resolved order_index based on position and previous"""
        if previous:
            return await self._index_for_previous(roadmap, previous)
        if position == "start":
            return await self._index_for_start(roadmap)
        return await self._index_for_end(roadmap)

    @repository_handler
    async def create(self, data: dict) -> Module:
        """Create module in roadmap at given position verified against user through roadmap"""
        async with transaction_manager(self.session):
            roadmap_id = data["roadmap_id"]
            user_id = data.pop("user_id")
            previous = data.pop("previous", None)
            position = data.pop("position", "end")
            owned = (
                await self.session.execute(
                    select(Roadmap.id).where(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
                )
            ).scalar_one_or_none()
            if owned is None:
                raise EntityNotFoundError(Roadmap, roadmap_id)
            data["order_index"] = await self._resolve_index(roadmap_id, position, previous)
            stmt = insert(Module).values(**data).returning(Module)
            return (await self.session.execute(stmt)).scalar_one()

    @repository_handler
    async def update(self, module: BaseIdType, data: dict, user: BaseIdType) -> Module:
        """Update module by id verified against user and return updated entity"""
        async with transaction_manager(self.session):
            owned = select(Roadmap.id).where(Roadmap.user_id == user)
            stmt = (
                update(Module)
                .where(Module.id == module, Module.roadmap_id.in_(owned))
                .values(**data)
                .returning(Module)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Module, module)
            return row

    async def _locate(self, module: BaseIdType, user: BaseIdType) -> Module:
        """Return module verified against roadmap and user"""
        stmt = (
            select(Module)
            .join(Roadmap, Module.roadmap_id == Roadmap.id)
            .where(Module.id == module, Roadmap.user_id == user)
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Module, module)
        return row

    async def _resolve(self, roadmap: BaseIdType, previous: BaseIdType, origin: int) -> int:
        """Return target order index resolved from previous module position"""
        stmt = select(Module.order_index).where(
            Module.id == previous,
            Module.roadmap_id == roadmap,
        )
        index = (await self.session.execute(stmt)).scalar_one_or_none()
        if index is None:
            raise EntityNotFoundError(Module, previous)
        target = index + 1 if index < origin else index
        return target

    async def _shift(
        self, roadmap: BaseIdType, module: BaseIdType, low: int, high: int, delta: int
    ) -> None:
        """Shift order indices in [low, high] by delta"""
        condition = and_(
            Module.roadmap_id == roadmap,
            Module.order_index >= low,
            Module.order_index <= high,
            Module.id != module,
        )
        await self.session.execute(
            update(Module).where(condition).values(order_index=Module.order_index + delta)
        )

    @repository_handler
    async def move(
        self, module: BaseIdType, previous: BaseIdType | None, user: BaseIdType
    ) -> Module:
        """Move module to new position within roadmap verified against user"""
        async with transaction_manager(self.session):
            row = await self._locate(module, user)
            roadmap = row.roadmap_id
            origin = row.order_index
            target = 0 if previous is None else await self._resolve(roadmap, previous, origin)
            if target == origin:
                raise ValueError(f"Module {module} is already at the requested position")
            if target < origin:
                await self._shift(roadmap, module, target, origin - 1, 1)
            else:
                await self._shift(roadmap, module, origin + 1, target, -1)
            result = await self.session.execute(
                update(Module)
                .where(Module.id == module)
                .values(order_index=target)
                .returning(Module)
            )
            return result.scalar_one()

    @repository_handler
    async def delete(self, module: BaseIdType, user: BaseIdType) -> Module:
        """Delete module by id verified against user and return deleted entity"""
        async with transaction_manager(self.session):
            owned = select(Roadmap.id).where(Roadmap.user_id == user)
            stmt = (
                delete(Module)
                .where(Module.id == module, Module.roadmap_id.in_(owned))
                .returning(Module)
            )
            result = cast("CursorResult", await self.session.execute(stmt))
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Module, module)
            return row

    @repository_handler
    async def create_multiple(
        self, roadmap: BaseIdType, user: BaseIdType, data: list[dict]
    ) -> list[Module]:
        """Create multiple modules in roadmap verified against user"""
        async with transaction_manager(self.session):
            owned = select(Roadmap.id).where(Roadmap.id == roadmap, Roadmap.user_id == user)
            valid = (await self.session.execute(owned)).scalar_one_or_none()
            if valid is None:
                raise EntityNotFoundError(Roadmap, roadmap)
            stmt = select(func.max(Module.order_index)).where(Module.roadmap_id == roadmap)
            index = (await self.session.execute(stmt)).scalar()
            start = (index + 1) if index is not None else 0
            for i, module in enumerate(data):
                module["order_index"] = start + i
            result = await self.session.execute(insert(Module).values(data).returning(Module))
            rows = list(result.scalars().all())
            return rows
