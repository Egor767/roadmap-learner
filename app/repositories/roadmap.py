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
from app.repositories import BaseRepository


class RoadmapRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Roadmap]:
        stmt = select(Roadmap)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, roadmap: BaseIdType, user: BaseIdType) -> Roadmap:
        stmt = select(Roadmap).where(
            Roadmap.user_id == user,
            Roadmap.id == roadmap,
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Roadmap, roadmap)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Roadmap]:
        stmt = select(Roadmap).where(Roadmap.user_id == user)
        for field_name, value in filters.items():
            column = getattr(Roadmap, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def create(self, data: dict) -> Roadmap:
        async with transaction_manager(self.session):
            stmt = insert(Roadmap).values(**data).returning(Roadmap)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

    @repository_handler
    async def update(self, roadmap: BaseIdType, data: dict, user: BaseIdType) -> Roadmap:
        async with transaction_manager(self.session):
            stmt = (
                update(Roadmap).where(Roadmap.user_id == user, Roadmap.id == roadmap).values(**data).returning(Roadmap)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Roadmap, roadmap)
            return row

    @repository_handler
    async def delete(self, roadmap: BaseIdType, user: BaseIdType):
        async with transaction_manager(self.session):
            stmt = delete(Roadmap).where(Roadmap.user_id == user, Roadmap.id == roadmap)
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Roadmap, roadmap)
