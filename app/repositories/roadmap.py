from typing import List, Optional

from sqlalchemy import select, insert, update, delete

from core.db import transaction_manager
from core.handlers import repository_handler
from core.types import BaseIdType
from models import Roadmap
from repositories import BaseRepository
from schemas.roadmap import RoadmapRead, RoadmapFilters


def map_to_schema(db_user: Roadmap | None) -> RoadmapRead | None:
    if db_user:
        return RoadmapRead.model_validate(db_user)
    return


class RoadmapRepository(BaseRepository):
    @repository_handler
    async def get_all_roadmaps(self) -> list[RoadmapRead]:
        stmt = select(Roadmap)
        result = await self.session.execute(stmt)
        db_roadmaps = result.scalars().all()
        return [map_to_schema(roadmap) for roadmap in db_roadmaps]

    @repository_handler
    async def get_roadmap_by_id(self, roadmap_id: BaseIdType) -> RoadmapRead | None:
        stmt = select(Roadmap).where(Roadmap.id == roadmap_id)
        result = await self.session.execute(stmt)
        db_roadmap = result.scalar_one_or_none()
        return map_to_schema(db_roadmap)

    @repository_handler
    async def get_roadmaps(
        self,
        filters: RoadmapFilters,
    ) -> list[RoadmapRead] | list[None]:
        stmt = select(Roadmap)

        if filters.title:
            stmt = stmt.where(Roadmap.title == filters.title)
        if filters.description:
            stmt = stmt.where(Roadmap.description == filters.description)
        if filters.status:
            stmt = stmt.where(Roadmap.status == filters.status)

        result = await self.session.execute(stmt)
        db_roadmaps = result.scalars().all()
        return [map_to_schema(roadmap) for roadmap in db_roadmaps]

    @repository_handler
    async def create_roadmap(self, roadmap_data: dict) -> RoadmapRead | None:
        async with transaction_manager(self.session):
            stmt = insert(Roadmap).values(**roadmap_data).returning(Roadmap)
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one_or_none()
            return map_to_schema(db_roadmap)

    @repository_handler
    async def delete_roadmap(self, roadmap_id: BaseIdType) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Roadmap).where(Roadmap.id == roadmap_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update_roadmap(
        self,
        roadmap_id: BaseIdType,
        roadmap_data: dict,
    ) -> RoadmapRead | None:
        async with transaction_manager(self.session):
            stmt = (
                update(Roadmap)
                .where(Roadmap.id == roadmap_id)
                .values(**roadmap_data)
                .returning(Roadmap)
            )
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one_or_none()
            return map_to_schema(db_roadmap)
