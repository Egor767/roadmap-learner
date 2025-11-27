from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.core.logging import user_service_logger as logger
from app.utils.mappers.orm_to_models import user_orm_to_model

if TYPE_CHECKING:
    from app.services import AccessService
    from app.repositories import UserRepository
    from app.schemas.user import UserRead, UserFilters
    from app.models import User


class UserService:
    def __init__(
        self,
        repo: "UserRepository",
        access_service: "AccessService",
    ):
        self.repo = repo
        self.access = access_service

    @service_handler
    async def get_all(self) -> list["UserRead"]:
        db_users = await self.repo.get_all()
        if len(db_users) == 0:
            logger.warning("Users not found in DB")
            return []

        validated_users = [await user_orm_to_model(user) for user in db_users]

        return validated_users

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: "UserFilters",
    ) -> list["UserRead"]:
        filters_dict = filters.model_dump()
        accessed_filters = await self.access.filter_users_for_user(
            current_user,
            filters_dict,
        )

        db_users = await self.repo.get_by_filters(accessed_filters)
        if len(db_users) == 0:
            logger.warning("Users with filters(%r) not found", filters)
            return []

        validated_users = [await user_orm_to_model(user) for user in db_users]

        return validated_users
