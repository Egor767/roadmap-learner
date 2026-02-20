from sqlalchemy import (
    select,
    insert,
    update,
    delete,
)

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.repositories import BaseRepository
from app.models import Roadmap


class RoadmapRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Roadmap]:
        stmt = select(Roadmap)
        result = await self.session.execute(stmt)
        roadmaps = list(result.scalars().all())
        return roadmaps

    @repository_handler
    async def get_by_id(self, roadmap_id: BaseIdType, user_id: BaseIdType) -> Roadmap:
        stmt = select(Roadmap).where(
            Roadmap.user_id == user_id,
            Roadmap.id == roadmap_id,
        )
        result = await self.session.execute(stmt)
        roadmap = result.scalar_one_or_none()
        if roadmap is None:
            raise EntityNotFoundError(Roadmap, roadmap_id)
        return roadmap

    @repository_handler
    async def get_by_filters(self, filters: dict, user_id: BaseIdType) -> list[Roadmap]:
        stmt = select(Roadmap).where(Roadmap.user_id == user_id)
        for field_name, value in filters.items():
            column = getattr(Roadmap, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        roadmaps = list(result.scalars().all())
        return roadmaps

    @repository_handler
    async def create(self, roadmap_data: dict) -> Roadmap:
        async with transaction_manager(self.session):
            stmt = insert(Roadmap).values(**roadmap_data).returning(Roadmap)
            result = await self.session.execute(stmt)
            roadmap = result.scalar_one()
            return roadmap

    @repository_handler
    async def update(
        self,
        roadmap_id: BaseIdType,
        roadmap_data: dict,
        user_id: BaseIdType,
    ) -> Roadmap:
        async with transaction_manager(self.session):
            stmt = (
                update(Roadmap)
                .where(Roadmap.user_id == user_id, Roadmap.id == roadmap_id)
                .values(**roadmap_data)
                .returning(Roadmap)
            )
            result = await self.session.execute(stmt)
            roadmap = result.scalar_one_or_none()
            if roadmap is None:
                raise EntityNotFoundError(Roadmap, roadmap_id)
            return roadmap

    @repository_handler
    async def delete(self, roadmap_id: BaseIdType, user_id: BaseIdType):
        async with transaction_manager(self.session):
            stmt = delete(Roadmap).where(
                Roadmap.user_id == user_id, Roadmap.id == roadmap_id
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Roadmap, roadmap_id)
