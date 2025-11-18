from fastapi_users import FastAPIUsers

from core.dependencies import get_user_manager, authentication_backend
from core.types import BaseIdType
from models import User

fastapi_users = FastAPIUsers[User, BaseIdType](
    get_user_manager,
    [authentication_backend],
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
