import uuid
from typing import Optional, List

from app.core.handlers import service_handler
from app.core.logging import user_service_logger as logger
from app.core.security import get_password_hash, verify_password
from app.repositories.user.interface import IUserRepository
from app.schemas.user import UserCreate, UserBase, UserResponse, UserFilters


class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    @service_handler
    async def create_user(self, user_create_model: UserCreate) -> UserResponse:
        existing_user = await self.repo.get_users_by_filters(
            UserFilters(
                email=user_create_model.email
            ))
        if existing_user:
            logger.warning(f"Attempt to create user with existing email: {user_create_model.email}")
            raise ValueError("User with this email already exists")

        hashed_password = get_password_hash(user_create_model.password)
        user_data = user_create_model.model_dump()
        user_data["password"] = hashed_password

        logger.info(f"Creating new user: {user_create_model.username}")
        created_user = await self.repo.create_user(UserCreate(**user_data))

        logger.info(f"User created successfully: {created_user.id}")
        return UserResponse.model_validate(created_user)

    @service_handler
    async def get_all_users(self) -> List[UserResponse]:
        users = await self.repo.get_all_users()
        if not users:
            logger.warning(f"No users in db")
            raise ValueError("No users in db")

        validated_users = [UserResponse.model_validate(user) for user in users]
        logger.info(f"Successful get all users")
        return validated_users

    @service_handler
    async def get_user_by_id(self, uid: uuid.UUID) -> UserResponse:
        user = await self.repo.get_user_by_id(uid)
        if not user:
            logger.warning(f"User not found with id: {uid}")
            raise ValueError("User not found")

        logger.info(f"Retrieved user by id: {uid}")
        return UserResponse.model_validate(user)

    @service_handler
    async def get_users_by_filters(self, filters: UserFilters) -> List[UserResponse]:
        users = await self.repo.get_users_by_filters(filters)
        if not users:
            logger.warning(f"Users not found with filters: {filters}")
            raise ValueError("Users not found")

        validated_users = [UserResponse.model_validate(user) for user in users]
        logger.info(f"Retrieved users with filters: {filters}")
        return validated_users

    @service_handler
    async def delete_user(self, uid: uuid.UUID) -> bool:
        success = await self.repo.delete_user(uid)
        if success:
            logger.info(f"User deleted successfully: {uid}")
        else:
            logger.warning(f"User not found for deletion: {uid}")
        return success

    @service_handler
    async def auth_user(self, email: str, password: str) -> Optional[UserBase]:
        user = await self.repo.get_users_by_filters(UserFilters(email=email))[0]
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Failed authentication attempt for user: {email}")
            return None

        logger.info(f"User authenticated successfully: {email}")
        return UserBase.model_validate(user)