from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.core.logging import user_service_logger as logger
from app.repositories import UserRepository
from app.schemas.user import UserRead, UserFilters

if TYPE_CHECKING:
    from app.models import User
    from app.services import AccessService


class UserService:
    def __init__(
        self,
        repo: UserRepository,
        access_service: "AccessService",
    ):
        self.repo = repo
        self.access = access_service

    @service_handler
    async def get_all_users(self) -> list[UserRead] | list[None]:
        users = await self.repo.get_all()

        if not users:
            logger.warning("Users not found in DB")
            return []

        return users

    @service_handler
    async def get_users_by_filters(
        self,
        current_user: "User",
        filters: UserFilters,
    ) -> list[UserRead] | list[None]:
        users = await self.repo.get_by_filters(filters)

        if not users:
            logger.warning("Users with filters(%r) not found", filters)
            return []
            # or:
            # logger.error("Roadmaps with filters(%r) not found", filters)
            # raise ValueError("Roadmaps not found")
            # and current_func() -> list[RoadmapRead]

        filtered_users = await self.access.filter_users_for_user(
            current_user,
            users,
        )

        return filtered_users
