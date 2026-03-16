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
from app.models import Roadmap
from app.repositories import BaseEntityRepository


class RoadmapRepository(BaseEntityRepository):
    """Repository for roadmap data access"""

    @repository_handler
    async def get_all(self) -> list[Roadmap]:
        """Return all roadmaps ordered by title"""
        stmt = select(Roadmap).order_by(Roadmap.title)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, roadmap: BaseIdType) -> Roadmap:
        """Return roadmap by id"""
        stmt = select(Roadmap).where(Roadmap.id == roadmap)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Roadmap, roadmap)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Roadmap]:
        """Return roadmaps matching filters for user"""
        stmt = select(Roadmap).where(Roadmap.user_id == user)
        for field_name, value in filters.items():
            column = getattr(Roadmap, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Roadmap.title)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def create(self, data: dict) -> Roadmap:
        """Create and return new roadmap"""
        async with transaction_manager(self.session):
            stmt = insert(Roadmap).values(**data).returning(Roadmap)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

    @repository_handler
    async def update(self, roadmap: BaseIdType, data: dict) -> Roadmap:
        """Update roadmap by id and return updated entity"""
        async with transaction_manager(self.session):
            stmt = update(Roadmap).where(Roadmap.id == roadmap).values(**data).returning(Roadmap)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Roadmap, roadmap)
            return row

    @repository_handler
    async def delete(self, roadmap: BaseIdType) -> None:
        """Delete roadmap by id"""
        async with transaction_manager(self.session):
            stmt = delete(Roadmap).where(Roadmap.id == roadmap)
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Roadmap, roadmap)
