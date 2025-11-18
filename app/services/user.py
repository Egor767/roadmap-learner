from typing import List

from core.handlers import service_handler
from core.logging import user_service_logger as logger
from repositories import UserRepository
from schemas.user import UserRead, UserFilters


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    @service_handler
    async def get_all_users(self) -> List[UserRead]:
        users = await self.repo.get_all_users()
        validated_users = [UserRead.model_validate(user) for user in users]
        logger.info(
            "Successful get all users, count: %r",
            len(validated_users),
        )
        return validated_users

    @service_handler
    async def get_users(self, filters: UserFilters) -> List[UserRead]:
        users = await self.repo.get_users(filters)
        validated_users = [UserRead.model_validate(user) for user in users]
        logger.info(
            "Retrieved %r users with filters: %r",
            len(validated_users),
            filters,
        )
        return validated_users
