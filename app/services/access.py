import logging

from models import User
from schemas.roadmap import RoadmapRead

logger = logging.getLogger("AccessService-Logger")


class AccessService:
    @staticmethod
    def filter_roadmaps_for_user(
        user: User,
        roadmaps: list[RoadmapRead],
    ) -> list[RoadmapRead]:

        if user.is_superuser:
            return roadmaps

        return [r for r in roadmaps if r.user_id == user.id]

    @staticmethod
    def ensure_can_view_roadmap(
        user: User,
        roadmap: RoadmapRead,
    ) -> None:
        if user.is_superuser:
            return

        if roadmap.user_id != user.id:
            logger.error(
                "Access denied to Roadmap(id=%r) for User(id=%r)",
                roadmap.id,
                user.id,
            )
            raise PermissionError("Access denied")
