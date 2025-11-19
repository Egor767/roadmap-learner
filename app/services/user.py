from core.handlers import service_handler
from core.logging import user_service_logger as logger
from repositories import UserRepository
from schemas.user import UserRead, UserFilters


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    @service_handler
    async def get_all_users(self) -> list[UserRead]:
        users = await self.repo.get_all()
        validated_users = [UserRead.model_validate(user) for user in users]
        logger.info(
            "Successful get all users, count: %r",
            len(validated_users),
        )
        return validated_users

    @service_handler
    async def get_users_by_filters(self, filters: UserFilters) -> list[UserRead]:
        users = await self.repo.get_by_filters(filters)
        validated_users = [UserRead.model_validate(user) for user in users]
        logger.info(
            "Retrieved %r users with filters: %r",
            len(validated_users),
            filters,
        )
        return validated_users
