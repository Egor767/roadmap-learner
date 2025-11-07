from typing import List

from app.core.handlers import service_handler
from app.core.logging import user_service_logger as logger
from app.core.security import get_password_hash
from app.core.types import BaseIDType
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserFilters, UserUpdate
from shared.generate_id import generate_base_id


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    @service_handler
    async def get_all_users(self) -> List[UserResponse]:
        users = await self.repo.get_all_users()
        validated_users = [UserResponse.model_validate(user) for user in users]
        logger.info(f"Successful get all users, count: {len(validated_users)}")
        return validated_users

    @service_handler
    async def get_user_by_id(self, user_id: BaseIDType) -> UserResponse:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User not found with id: {user_id}")
            raise ValueError("User not found")
        logger.info(f"Retrieved user by id: {user_id}")
        return UserResponse.model_validate(user)

    @service_handler
    async def get_users(self, filters: UserFilters) -> List[UserResponse]:
        users = await self.repo.get_users(filters)
        validated_users = [UserResponse.model_validate(user) for user in users]
        logger.info(f"Retrieved {len(validated_users)} users with filters: {filters}")
        return validated_users

    @service_handler
    async def create_user(self, user_create_model: UserCreate) -> UserResponse:
        existing_user = await self.repo.get_users(
            UserFilters(email=user_create_model.email)
        )
        if existing_user:
            logger.warning(
                f"Attempt to create user with existing email: {user_create_model.email}"
            )
            raise ValueError("User with this email already exists")

        hashed_password = get_password_hash(user_create_model.password)
        user_data = user_create_model.model_dump()
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
        user_data["id"] = await generate_base_id()

        logger.info(f"Creating new user: {user_create_model.username}")
        created_user = await self.repo.create_user(user_data)

        logger.info(f"User created successfully: {created_user.id}")
        return UserResponse.model_validate(created_user)

    @service_handler
    async def delete_user(
        self, current_user_id: BaseIDType, user_id: BaseIDType
    ) -> bool:
        # check roots

        success = await self.repo.delete_user(user_id)
        if success:
            logger.info(f"User deleted successfully: {user_id}")
        else:
            logger.warning(f"User not found for deletion: {user_id}")
        return success

    @service_handler
    async def update_user(
        self,
        current_user_id: BaseIDType,
        user_id: BaseIDType,
        user_update_model: UserUpdate,
    ) -> UserResponse:
        # check roots

        user_data = user_update_model.model_dump(exclude_unset=True)

        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

        logger.info(f"Updating user {user_id}: {user_data}")
        updated_user = await self.repo.update_user(user_id, user_data)

        if not updated_user:
            logger.warning(f"User not found for update: {user_id}")
            raise ValueError("User not found")

        logger.info(f"Successful updating user: {user_id}")
        return UserResponse.model_validate(updated_user)
