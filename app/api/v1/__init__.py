from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import HTTPBearer

from app.core.config import settings

from .ai import router as ai_router
from .auth import router as auth_router
from .concept import router as concept_router
from .module import router as module_router
from .question import router as question_router
from .roadmap import router as roadmap_router
from .session import router as session_router
from .user import router as user_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)
router.include_router(auth_router)
router.include_router(user_router)

router.include_router(roadmap_router)
router.include_router(module_router)
router.include_router(question_router)
router.include_router(concept_router)
router.include_router(session_router)
router.include_router(ai_router)
