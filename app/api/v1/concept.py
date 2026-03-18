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
@router.get("", name="concepts:all_concepts", response_model=list[ConceptRead])
@router_handler
async def get_all_concepts(
    concept_service: Annotated["ConceptService", Depends(get_concept_service)],
) -> list[ConceptRead]:
    return await concept_service.get_all()


@router.get("/filters", name="concepts:filter_concepts", response_model=list[ConceptRead])
@router_handler
async def get_concepts(
    filters: Annotated[ConceptFilters, Depends()],
    current_user: Annotated["User", Depends(current_active_user)],
    concept_service: Annotated["ConceptService", Depends(get_concept_service)],
) -> list[ConceptRead]:
    return await concept_service.get_by_filters(current_user, filters)


@router.get("/{concept_id}", name="concepts:concept", response_model=ConceptRead)
@router_handler
async def get_concept(
    concept_id: BaseIdType,
    current_user: Annotated["User", Depends(current_active_user)],
    concept_service: Annotated["ConceptService", Depends(get_concept_service)],
) -> ConceptRead:
    return await concept_service.get_by_id(current_user, concept_id)


# -------------------------------------- CREATE --------------------------------------
@router.post("", name="concepts:create_concept", response_model=ConceptRead)
@router_handler
async def create_concept(
    concept_create_data: ConceptCreate,
    current_user: Annotated["User", Depends(current_active_user)],
    concept_service: Annotated["ConceptService", Depends(get_concept_service)],
) -> ConceptRead:
    return await concept_service.create(current_user, concept_create_data)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{concept_id}", name="concepts:patch_concept", response_model=ConceptRead)
@router_handler
async def update_concept(
    concept_id: BaseIdType,
    concept_update_data: ConceptUpdate,
    current_user: Annotated["User", Depends(current_active_user)],
    concept_service: Annotated["ConceptService", Depends(get_concept_service)],
) -> ConceptRead:
    return await concept_service.update(current_user, concept_id, concept_update_data)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{concept_id}", name="concepts:delete_concept")
@router_handler
async def delete_concept(
    concept_id: BaseIdType,
    current_user: Annotated["User", Depends(current_active_user)],
    concept_service: Annotated["ConceptService", Depends(get_concept_service)],
) -> None:
    await concept_service.delete(current_user, concept_id)
