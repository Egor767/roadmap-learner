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
@router.get("", name="modules:all_modules", response_model=list[ModuleRead])
@router_handler
async def get_all_modules(
    module_service: Annotated["ModuleService", Depends(get_module_service)],
) -> list[ModuleRead]:
    return await module_service.get_all()


@router.get("/filters", name="modules:filter_modules", response_model=list[ModuleRead])
@router_handler
async def get_modules(
    filters: Annotated[ModuleFilters, Depends()],
    current_user: Annotated["User", Depends(current_active_user)],
    module_service: Annotated["ModuleService", Depends(get_module_service)],
) -> list[ModuleRead]:
    return await module_service.get_by_filters(current_user, filters)


@router.get("/{module_id}", name="modules:module", response_model=ModuleRead)
@router_handler
async def get_module(
    module_id: BaseIdType,
    current_user: Annotated["User", Depends(current_active_user)],
    module_service: Annotated["ModuleService", Depends(get_module_service)],
) -> ModuleRead:
    return await module_service.get_by_id(current_user, module_id)


# -------------------------------------- CREATE --------------------------------------
@router.post("", name="modules:create_module", response_model=ModuleRead)
@router_handler
async def create_module(
    module_create_data: ModuleCreate,
    current_user: Annotated["User", Depends(current_active_user)],
    module_service: Annotated["ModuleService", Depends(get_module_service)],
) -> ModuleRead:
    return await module_service.create(current_user, module_create_data)


@router.post("/batch", name="modules:create_batch_modules", response_model=list[ModuleRead])
@router_handler
async def confirm_modules(
    body: ModuleConfirmRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    module_service: Annotated["ModuleService", Depends(get_module_service)],
) -> list[ModuleRead]:
    return await module_service.create_multiple(current_user, body)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{module_id}", name="modules:patch_module", response_model=ModuleRead)
@router_handler
async def update_module(
    module_id: BaseIdType,
    module_update_data: ModuleUpdate,
    current_user: Annotated["User", Depends(current_active_user)],
    module_service: Annotated["ModuleService", Depends(get_module_service)],
) -> ModuleRead:
    return await module_service.update(current_user, module_id, module_update_data)


@router.patch("/{module_id}/move", name="modules:move_module", response_model=ModuleRead)
@router_handler
async def move_module(
    module_id: BaseIdType,
    move_data: ModuleMove,
    current_user: Annotated["User", Depends(current_active_user)],
    module_service: Annotated["ModuleService", Depends(get_module_service)],
) -> ModuleRead:
    return await module_service.move(current_user, module_id, move_data)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{module_id}", name="modules:delete_module")
@router_handler
async def delete_module(
    module_id: BaseIdType,
    current_user: Annotated["User", Depends(current_active_user)],
    module_service: Annotated["ModuleService", Depends(get_module_service)],
) -> None:
    await module_service.delete(current_user, module_id)
