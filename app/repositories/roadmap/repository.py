import uuid
from contextlib import asynccontextmanager
from typing import List

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.handlers import repository_handler
from app.models.postgres.roadmap import RoadMap
from app.repositories.roadmap.interface import IRoadMapRepository
from app.schemas.roadmap import RoadMapInDB, RoadMapFilters


def map_to_schema(db_user: RoadMap) -> RoadMapInDB:
    return RoadMapInDB.model_validate(db_user)


class RoadMapRepository(IRoadMapRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def _transaction(self):
        try:
            yield
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    @repository_handler
    async def get_all_roadmaps(self) -> List[RoadMapInDB]:
        stmt = select(RoadMap)
        result = await self.session.execute(stmt)
        db_roadmaps = result.scalars().all()
        return [map_to_schema(roadmap) for roadmap in db_roadmaps]

    @repository_handler
    async def get_user_roadmap(self, user_id: uuid.UUID, roadmap_id: uuid.UUID) -> RoadMapInDB:
        stmt = select(RoadMap).where(
            RoadMap.road_id == roadmap_id,
            RoadMap.user_id == user_id
        )
        result = await self.session.execute(stmt)
        roadmap = result.scalar_one_or_none()
        return map_to_schema(roadmap) if roadmap else None

    @repository_handler
    async def get_user_roadmaps(self, user_id: uuid.UUID, filters: RoadMapFilters) -> List[RoadMapInDB]:
        stmt = select(RoadMap).where(RoadMap.user_id == user_id)

        if filters.title:
            stmt = stmt.where(RoadMap.title == filters.title)
        if filters.description:
            stmt = stmt.where(RoadMap.description == filters.description)
        if filters.status:
            stmt = stmt.where(RoadMap.status == filters.status)

        result = await self.session.execute(stmt)
        db_roadmaps = result.scalars().all()
        return [map_to_schema(roadmap) for roadmap in db_roadmaps]

    @repository_handler
    async def create_roadmap(self, roadmap_data: dict) -> RoadMapInDB:
        async with self._transaction():
            stmt = insert(RoadMap).values(**roadmap_data).returning(RoadMap)
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one()
            return map_to_schema(db_roadmap)

    @repository_handler
    async def delete_roadmap(self, user_id: uuid.UUID, roadmap_id: uuid.UUID) -> bool:
        async with self._transaction():
            stmt = delete(RoadMap).where(
                RoadMap.road_id == roadmap_id,
                RoadMap.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update_roadmap(self, user_id: uuid.UUID, roadmap_id: uuid.UUID, roadmap_data: dict) -> RoadMapInDB:
        async with self._transaction():
            stmt = (
                update(RoadMap)
                .where(
                    RoadMap.road_id == roadmap_id,
                    RoadMap.user_id == user_id
                )
                .values(**roadmap_data)
                .returning(RoadMap)
            )
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one_or_none()
            return map_to_schema(db_roadmap) if db_roadmap else None

