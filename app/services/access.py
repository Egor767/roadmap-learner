import logging

from core.handlers import service_handler
from core.types import BaseIdType
from models import User
from repositories import RoadmapRepository
from schemas.roadmap import RoadmapRead

logger = logging.getLogger("AccessService-Logger")


class AccessService:
    def __init__(self, roadmap_repo: RoadmapRepository):
        self.roadmap_repo = roadmap_repo

    @service_handler
    async def ensure_roadmap_exists(self, roadmap_id: BaseIdType) -> RoadmapRead:
        logger.info("HELLO FROM AccessService.ensure_roadmap_exists")
        roadmap = await self.roadmap_repo.get_roadmap_by_id(roadmap_id)
        if not roadmap:
            logger.warning("Roadmap(id=%r) not found", roadmap_id)
            raise ValueError("Roadmap not found")
        return roadmap

    @service_handler
    async def ensure_user_can_access_roadmap(
        self,
        user: User,
        roadmap_id: BaseIdType,
    ) -> RoadmapRead:
        logger.info("HELLO FROM AccessService.ensure_user_can_access_roadmap")
        roadmap = await self.ensure_roadmap_exists(roadmap_id)
        if not user.is_superuser and roadmap.user_id != user.id:
            logger.warning(
                "Access denied to Roadmap(id=%r) for User(id=%r)",
                roadmap_id,
                user.id,
            )
            raise PermissionError("Access denied")
        return roadmap

    @service_handler
    async def ensure_user_can_modify_roadmap(
        self,
        user: User,
        roadmap_id: BaseIdType,
    ) -> RoadmapRead:
        """
        Проверяет права на модификацию roadmap (update/delete).
        """
        roadmap = await self.ensure_roadmap_exists(roadmap_id)
        if not user.is_superuser and roadmap.user_id != user.id:
            logger.warning(
                "Modification denied to Roadmap(id=%r) by User(id=%r)",
                roadmap_id,
                user.id,
            )
            raise PermissionError("Modification denied")
        return roadmap

    @service_handler
    async def filter_roadmaps_for_user(
        self,
        user: User,
        roadmaps: list[RoadmapRead],
    ) -> list[RoadmapRead]:
        """
        Фильтрует список roadmap, оставляя только те, к которым есть доступ.
        Суперпользователь видит все roadmap.
        """
        if user.is_superuser:
            return roadmaps
        return [r for r in roadmaps if r.user_id == user.id]
