from typing import List

from core.handlers import service_handler
from core.logging import user_service_logger as logger
from core.security import get_password_hash
from core.types import BaseIdType
from repositories import UserRepository
from schemas.user import UserCreate, UserResponse, UserFilters, UserUpdate
from shared.generate_id import generate_base_id


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    @service_handler
    async def get_all_users(self) -> List[UserResponse]:
        users = await self.repo.get_all_users()
        validated_users = [UserResponse.model_validate(user) for user in users]
        logger.info(
            "Successful get all users, count: %r",
            len(validated_users),
        )
        return validated_users

    @service_handler
    async def get_user_by_id(self, user_id: BaseIdType) -> UserResponse:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            logger.warning("User not found with id: %r", user_id)
            raise ValueError("User not found")
        logger.info("Retrieved user by id: %r", user_id)
        return UserResponse.model_validate(user)

    @service_handler
    async def get_users(self, filters: UserFilters) -> List[UserResponse]:
        users = await self.repo.get_users(filters)
        validated_users = [UserResponse.model_validate(user) for user in users]
        logger.info(
            "Retrieved %r users with filters: %r",
            len(validated_users),
            filters,
        )
        return validated_users

    @service_handler
    async def create_user(self, user_create_model: UserCreate) -> UserResponse:
        existing_user = await self.repo.get_users(
            UserFilters(email=user_create_model.email)
        )
        if existing_user:
            logger.warning(
                "Attempt to create user with existing email: %r",
                user_create_model.email,
            )
            raise ValueError("User with this email already exists")

        hashed_password = get_password_hash(user_create_model.password)
        user_data = user_create_model.model_dump()
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
        user_data["id"] = await generate_base_id()

        logger.info("Creating new user: %r", user_create_model.username)
        created_user = await self.repo.create_user(user_data)

        logger.info("User created successfully: %r", created_user.id)
        return UserResponse.model_validate(created_user)

    @service_handler
    async def delete_user(
        self, current_user_id: BaseIdType, user_id: BaseIdType
    ) -> bool:
        # check roots

        success = await self.repo.delete_user(user_id)
        if success:
            logger.info("User deleted successfully: %r", user_id)
        else:
            logger.warning("User not found for deletion: %r", user_id)
        return success

    @service_handler
    async def update_user(
        self,
        current_user_id: BaseIdType,
        user_id: BaseIdType,
        user_update_model: UserUpdate,
    ) -> UserResponse:
        # check roots

        user_data = user_update_model.model_dump(exclude_unset=True)

        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

        logger.info(
            "Updating user %r: %r",
            user_id,
            user_data,
        )
        updated_user = await self.repo.update_user(user_id, user_data)

        if not updated_user:
            logger.warning("User not found for update: %r", user_id)
            raise ValueError("User not found")

        logger.info("Successful updating user: %r", user_id)
        return UserResponse.model_validate(updated_user)
