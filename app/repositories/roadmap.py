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
from app.models import Roadmap

if TYPE_CHECKING:
    from app.core.types import BaseIdType


class RoadmapRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Roadmap]:
        stmt = select(Roadmap)
        result = await self.session.execute(stmt)
        roadmaps = list(result.scalars().all())
        return roadmaps

    @repository_handler
    async def get_by_id(self, roadmap_id: "BaseIdType") -> Roadmap | None:
        stmt = select(Roadmap).where(Roadmap.id == roadmap_id)
        result = await self.session.execute(stmt)
        roadmap = result.scalar_one_or_none()
        return roadmap

    @repository_handler
    async def get_by_filters(
        self,
        filters: dict,
    ) -> list[Roadmap]:
        stmt = select(Roadmap)

        for field_name, value in filters.items():
            if value is not None:
                column = getattr(Roadmap, field_name, None)
                if column is not None:
                    stmt = stmt.where(column == value)

        result = await self.session.execute(stmt)
        roadmaps = list(result.scalars().all())
        return roadmaps

    @repository_handler
    async def create(self, roadmap_data: dict) -> Roadmap | None:
        async with transaction_manager(self.session):
            stmt = insert(Roadmap).values(**roadmap_data).returning(Roadmap)
            result = await self.session.execute(stmt)
            roadmap = result.scalar_one_or_none()
            return roadmap

    @repository_handler
    async def delete(self, roadmap_id: "BaseIdType") -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Roadmap).where(Roadmap.id == roadmap_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update(
        self,
        roadmap_id: "BaseIdType",
        roadmap_data: dict,
    ) -> Roadmap | None:
        async with transaction_manager(self.session):
            stmt = (
                update(Roadmap)
                .where(Roadmap.id == roadmap_id)
                .values(**roadmap_data)
                .returning(Roadmap)
            )
            result = await self.session.execute(stmt)
            roadmap = result.scalar_one_or_none()
            return roadmap
