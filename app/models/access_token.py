from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable

from app.core.types import BaseIdType
from .base import Base
from .mixins import UserRelationMixin


class AccessToken(UserRelationMixin, Base, SQLAlchemyBaseAccessTokenTable[BaseIdType]):
    # _user_back_populates = "tokens"

    def __str__(self):
        return f"{self.__class__.__name__}(token={self.token}, user={self.user_id!r})"

    def __repr__(self):
        return str(self)
