from sqlalchemy import delete, insert, select, update

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import Roadmap
from app.repositories import BaseEntityRepository


class RoadmapRepository(BaseEntityRepository):
    """Repository for roadmap data access"""

    @repository_handler
    async def get_all(self, user: BaseIdType) -> list[Roadmap]:
        """Return all roadmaps ordered by title verified against user"""
        stmt = select(Roadmap).where(Roadmap.user_id == user).order_by(Roadmap.title)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, id: BaseIdType, user: BaseIdType) -> Roadmap:
        """Return roadmap by id verified against user"""
        stmt = select(Roadmap).where(Roadmap.id == id, Roadmap.user_id == user)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Roadmap, id)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Roadmap]:
        """Return roadmaps matching filters ordered by title verified against user"""
        stmt = select(Roadmap).where(Roadmap.user_id == user)
        for field, value in filters.items():
            column = getattr(Roadmap, field)
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
    async def update(self, id: BaseIdType, data: dict, user: BaseIdType) -> Roadmap:
        """Update roadmap by id verified against user and return updated"""
        async with transaction_manager(self.session):
            stmt = (
                update(Roadmap)
                .where(Roadmap.id == id, Roadmap.user_id == user)
                .values(**data)
                .returning(Roadmap)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Roadmap, id)
            return row

    @repository_handler
    async def delete(self, id: BaseIdType, user: BaseIdType) -> None:
        """Delete roadmap by id verified against user"""
        async with transaction_manager(self.session):
            stmt = delete(Roadmap).where(Roadmap.id == id, Roadmap.user_id == user)
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Roadmap, id)
