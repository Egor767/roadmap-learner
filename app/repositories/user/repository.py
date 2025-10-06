from app.repositories.user.interface import IUserRepository
from app.schemas.user import UserCreateModel, UserBaseModel


class UserRepository(IUserRepository):
    def __init(self, session):
        self.session = session

    async def create_user(self, user_create_model: UserCreateModel) -> UserBaseModel:
        ...

    async def get_user_by_id(self, uid: int) -> UserBaseModel:
        ...
