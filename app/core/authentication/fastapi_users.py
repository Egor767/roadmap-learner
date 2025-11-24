from fastapi_users import FastAPIUsers

from app.core.dependencies import authentication_backend
from app.core.dependencies.users import get_user_manager
from app.core.types import BaseIdType
from app.models import User

fastapi_users = FastAPIUsers[User, BaseIdType](
    get_user_manager,
    [authentication_backend],
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
