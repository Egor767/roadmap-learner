from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.custom_types import BaseIdType
from app.core.dependencies.services import get_module_service
from app.core.handlers import router_handler
from app.schemas.module import (
    ModuleConfirmRequest,
    ModuleCreate,
    ModuleFilters,
    ModuleMove,
    ModuleRead,
    ModuleUpdate,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services import ModuleService


router = APIRouter(
    prefix=settings.api.v1.modules,
    tags=["Modules"],
)


# -------------------------------------- GET ----------------------------------------------
@router.get("/filters", name="modules:filter_modules", response_model=list[ModuleRead])
@router_handler
async def get_modules(
    filters: Annotated[ModuleFilters, Depends()],
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ModuleService", Depends(get_module_service)],
) -> list[ModuleRead]:
    return await service.get_by_filters(user, filters)


@router.get("/{id}", name="modules:module", response_model=ModuleRead)
@router_handler
async def get_module(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ModuleService", Depends(get_module_service)],
) -> ModuleRead:
    return await service.get_by_id(user, id)


# -------------------------------------- CREATE --------------------------------------
@router.post("", name="modules:create_module", response_model=ModuleRead)
@router_handler
async def create_module(
    payload: ModuleCreate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ModuleService", Depends(get_module_service)],
) -> ModuleRead:
    return await service.create(user, payload)


@router.post("/batch", name="modules:create_modules", response_model=list[ModuleRead])
@router_handler
async def confirm_modules(
    payload: ModuleConfirmRequest,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ModuleService", Depends(get_module_service)],
) -> list[ModuleRead]:
    return await service.create_multiple(user, payload)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{id}", name="modules:patch_module", response_model=ModuleRead)
@router_handler
async def update_module(
    id: BaseIdType,
    payload: ModuleUpdate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ModuleService", Depends(get_module_service)],
) -> ModuleRead:
    return await service.update(user, id, payload)


@router.patch("/{id}/move", name="modules:move_module", response_model=ModuleRead)
@router_handler
async def move_module(
    id: BaseIdType,
    payload: ModuleMove,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ModuleService", Depends(get_module_service)],
) -> ModuleRead:
    return await service.move(user, id, payload)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{id}", name="modules:delete_module")
@router_handler
async def delete_module(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ModuleService", Depends(get_module_service)],
) -> None:
    await service.delete(user, id)
