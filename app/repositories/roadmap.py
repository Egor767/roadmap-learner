from sqlalchemy import select, insert, update, delete

from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.core.types import BaseIdType
from app.models import Roadmap
from app.repositories import BaseRepository
from app.schemas.roadmap import RoadmapRead, RoadmapFilters


def map_to_schema(db_user: Roadmap | None) -> RoadmapRead | None:
    if db_user:
        return RoadmapRead.model_validate(db_user)
    return


class RoadmapRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[RoadmapRead] | list[None]:
        stmt = select(Roadmap)
        result = await self.session.execute(stmt)
        db_roadmaps = result.scalars().all()
        return [map_to_schema(roadmap) for roadmap in db_roadmaps]

    @repository_handler
    async def get_by_id(self, roadmap_id: BaseIdType) -> RoadmapRead | None:
        stmt = select(Roadmap).where(Roadmap.id == roadmap_id)
        result = await self.session.execute(stmt)
        db_roadmap = result.scalar_one_or_none()
        return map_to_schema(db_roadmap)

    @repository_handler
    async def get_by_filters(
        self,
        filters: dict,
    ) -> list[RoadmapRead] | list[None]:
        stmt = select(Roadmap)

        for field_name, value in filters.items():
            if value is not None:
                column = getattr(Roadmap, field_name, None)
                if column is not None:
                    stmt = stmt.where(column == value)

        result = await self.session.execute(stmt)
        db_roadmaps = result.scalars().all()
        return [map_to_schema(roadmap) for roadmap in db_roadmaps]

    @repository_handler
    async def create(self, roadmap_data: dict) -> RoadmapRead | None:
        async with transaction_manager(self.session):
            stmt = insert(Roadmap).values(**roadmap_data).returning(Roadmap)
            result = await self.session.execute(stmt)
            db_roadmap = result.scalar_one_or_none()
            return map_to_schema(db_roadmap)

    @repository_handler
    async def delete(self, roadmap_id: BaseIdType) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Roadmap).where(Roadmap.id == roadmap_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update(
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
