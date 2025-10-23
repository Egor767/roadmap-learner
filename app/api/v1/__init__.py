from fastapi import APIRouter

from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.roadmap import router as roadmap_router
from app.api.v1.endpoints.block import router as block_router
from app.api.v1.endpoints.card import router as card_router

main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(roadmap_router)
main_router.include_router(block_router)
main_router.include_router(card_router)

