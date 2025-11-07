from typing import List

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.core.types import BaseIDType
from app.models.postgres.roadmap import Roadmap
from app.schemas.roadmap import RoadMapInDB, RoadMapFilters


def map_to_schema(db_user: Roadmap) -> RoadMapInDB:
    return RoadMapInDB.model_validate(db_user)


class RoadmapRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @repository_handler
    async def get_all_roadmaps(self) -> List[RoadMapInDB]:
        stmt = select(Roadmap)
        result = await self.session.execute(stmt)
        db_roadmaps = result.scalars().all()
        return [map_to_schema(roadmap) for roadmap in db_roadmaps]

    @repository_handler
    async def get_user_roadmap(
        self, user_id: BaseIDType, roadmap_id: BaseIDType
    ) -> RoadMapInDB:
        stmt = select(Roadmap).where(
            Roadmap.id == roadmap_id, Roadmap.user_id == user_id
        )
        result = await self.session.execute(stmt)
        roadmap = result.scalar_one_or_none()
        return map_to_schema(roadmap) if roadmap else None

    @repository_handler
    async def get_user_roadmaps(
        self, user_id: BaseIDType, filters: RoadMapFilters
    ) -> List[RoadMapInDB]:
        stmt = select(Roadmap).where(Roadmap.user_id == user_id)

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
    async def create_roadmap(self, roadmap_data: dict) -> RoadMapInDB:
        async with transaction_manager(self.session):
            stmt = insert(Roadmap).values(**roadmap_data).returning(Roadmap)
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one()
            return map_to_schema(db_roadmap)

    @repository_handler
    async def delete_roadmap(self, user_id: BaseIDType, roadmap_id: BaseIDType) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Roadmap).where(
                Roadmap.id == roadmap_id, Roadmap.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update_roadmap(
        self, user_id: BaseIDType, roadmap_id: BaseIDType, roadmap_data: dict
    ) -> RoadMapInDB:
        async with transaction_manager(self.session):
            stmt = (
                update(Roadmap)
                .where(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
                .values(**roadmap_data)
                .returning(Roadmap)
            )
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one_or_none()
            return map_to_schema(db_roadmap) if db_roadmap else None
