import uuid
from contextlib import asynccontextmanager
from typing import Optional, List

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgres.roadmap import RoadMap
from app.repositories.roadmap.interface import IRoadMapRepository
from app.schemas.roadmap import RoadMapInDB, RoadMapCreate, RoadMapUpdate


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

    async def create_roadmap(self, roadmap: RoadMapCreate) -> RoadMapInDB:
        async with self._transaction():
            roadmap_data = roadmap.model_dump()
            stmt = insert(RoadMap).values(**roadmap_data).returning(RoadMap)
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one()

            return map_to_schema(db_roadmap)

    async def get_user_roadmaps(self, user_id: uuid.UUID) -> Optional[List[RoadMapInDB]]:
        stmt = select(RoadMap).where(RoadMap.user_id == user_id)
        result = await self.session.execute(stmt)
        db_roadmaps = result.scalars().all()

        if not db_roadmaps:
            return
        return [map_to_schema(roadmap) for roadmap in db_roadmaps]

    async def get_user_roadmap(self, user_id: uuid.UUID, roadmap_id: uuid.UUID) -> Optional[RoadMapInDB]:
        stmt = select(RoadMap).where(
            RoadMap.road_id == roadmap_id,
            RoadMap.user_id == user_id
        )
        result = await self.session.execute(stmt)
        roadmap = result.scalar_one_or_none()

        if not roadmap:
            return
        return map_to_schema(roadmap)

    async def delete_roadmap(self, roadmap_id: uuid.UUID) -> bool:
        ...

    async def update_roadmap(self, update_data: RoadMapUpdate) -> RoadMapInDB:
        ...

