from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer

from core.config import settings
from .auth import router as auth_router
from .block import (
    router as block_router,
    resource_router as block_resource_router,
)
from .card import (
    router as card_router,
    resource_router as card_resource_router,
)
from .roadmap import router as roadmap_router
from .session import router as session_manager_router
from .user import router as user_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)
router.include_router(auth_router)
router.include_router(user_router)

router.include_router(roadmap_router)
router.include_router(block_router)
router.include_router(block_resource_router)
router.include_router(card_router)
router.include_router(card_resource_router)
router.include_router(session_manager_router)
