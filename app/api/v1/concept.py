from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.custom_types import BaseIdType
from app.core.dependencies.services import get_concept_service
from app.core.handlers import router_handler
from app.schemas.concept import (
    ConceptCreate,
    ConceptFilters,
    ConceptRead,
    ConceptUpdate,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services import ConceptService


router = APIRouter(
    prefix=settings.api.v1.concepts,
    tags=["Concepts"],
)


# -------------------------------------- GET ----------------------------------------------
@router.get("/filters", name="concepts:filter_concepts", response_model=list[ConceptRead])
@router_handler
async def get_concepts(
    filters: Annotated[ConceptFilters, Depends()],
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ConceptService", Depends(get_concept_service)],
) -> list[ConceptRead]:
    return await service.get_by_filters(user, filters)


@router.get("/{id}", name="concepts:concept", response_model=ConceptRead)
@router_handler
async def get_concept(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ConceptService", Depends(get_concept_service)],
) -> ConceptRead:
    return await service.get_by_id(user, id)


# -------------------------------------- CREATE --------------------------------------
@router.post("", name="concepts:create_concept", response_model=ConceptRead)
@router_handler
async def create_concept(
    payload: ConceptCreate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ConceptService", Depends(get_concept_service)],
) -> ConceptRead:
    return await service.create(user, payload)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{id}", name="concepts:patch_concept", response_model=ConceptRead)
@router_handler
async def update_concept(
    id: BaseIdType,
    payload: ConceptUpdate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ConceptService", Depends(get_concept_service)],
) -> ConceptRead:
    return await service.update(user, id, payload)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{id}", name="concepts:delete_concept")
@router_handler
async def delete_concept(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["ConceptService", Depends(get_concept_service)],
) -> None:
    await service.delete(user, id)
