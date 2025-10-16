import uuid
from typing import Optional

from app.core.handlers import service_handler
from app.core.logging import user_service_logger as logger
from app.core.security import get_password_hash, verify_password
from app.repositories.user.interface import IUserRepository
from app.schemas.user import UserCreate, UserBase, UserInDB, UserResponse


class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    @service_handler
    async def create_user(self, user_create_model: UserCreate) -> UserResponse:
        # existing_user = await self.repo.get_user_by_email(user_create_model.email)
        # if existing_user:
        #     logger.warning(f"Attempt to create user with existing email: {user_create_model.email}")
        #     raise ValueError("User with this email already exists")

        hashed_password = get_password_hash(user_create_model.password)
        user_data = user_create_model.model_dump()
        user_data["password"] = hashed_password

        logger.info(f"Creating new user: {user_create_model.username}")
        created_user = await self.repo.create_user(UserCreate(**user_data))

        logger.info(f"User created successfully: {created_user.id}")
        return UserResponse.model_validate(created_user)

    @service_handler
    async def get_user_by_id(self, uid: uuid.UUID) -> UserBase:
        user = await self.repo.get_user_by_id(uid)
        if not user:
            logger.warning(f"User not found with id: {uid}")
            raise ValueError("User not found")

        logger.debug(f"Retrieved user by id: {uid}")
        return UserBase.model_validate(user)

    @service_handler
    async def get_user_by_email(self, email: str) -> Optional[UserBase]:
        user = await self.repo.get_user_by_email(email)
        if user:
            return UserBase.model_validate(user)
        return None

    @service_handler
    async def auth_user(self, email: str, password: str) -> Optional[UserBase]:
        user = await self.repo.get_user_by_email(email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Failed authentication attempt for user: {email}")
            return None

        logger.info(f"User authenticated successfully: {email}")
        return UserBase.model_validate(user)

    @service_handler
    async def delete_user(self, uid: uuid.UUID) -> bool:
        success = await self.repo.delete_user(uid)
        if success:
            logger.info(f"User deleted successfully: {uid}")
        else:
            logger.warning(f"User not found for deletion: {uid}")
        return success

