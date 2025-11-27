from typing import Annotated, TYPE_CHECKING

from fastapi import APIRouter, Depends
from starlette import status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.dependencies.services import get_card_service
from app.core.handlers import router_handler
from app.core.types import BaseIdType
from app.schemas.card import (
    CardRead,
    CardCreate,
    CardUpdate,
    CardFilters,
)

if TYPE_CHECKING:
    from app.services import CardService
    from app.models import User


router = APIRouter(
    prefix=settings.api.v1.cards,
    tags=["Cards"],
)


@router.get(
    "",
    name="cards:all_cards",
    response_model=list[CardRead],
)
@router_handler
async def get_all_cards(
    card_service: Annotated[
        "CardService",
        Depends(get_card_service),
    ],
) -> list[CardRead]:
    return await card_service.get_all()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/filters",
    name="cards:filter_cards",
    response_model=list[CardRead],
)
@router_handler
async def get_cards(
    filters: Annotated[
        CardFilters,
        Depends(),
    ],
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        "CardService",
        Depends(get_card_service),
    ],
) -> list[CardRead]:
    return await card_service.get_by_filters(
        current_user,
        filters,
    )


@router.get(
    "/{card_id}",
    name="cards:card",
    response_model=CardRead,
)
@router_handler
async def get_card(
    card_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        "CardService",
        Depends(get_card_service),
    ],
) -> CardRead:
    return await card_service.get_by_id(
        current_user,
        card_id,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "/",
    name="cards:create_card",
    response_model=CardRead,
)
@router_handler
async def create_card(
    card_create_data: CardCreate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        "CardService",
        Depends(get_card_service),
    ],
) -> CardRead:
    return await card_service.create(
        current_user,
        card_create_data,
    )


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{card_id}",
    name="cards:delete_card",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def delete_card(
    card_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        "CardService",
        Depends(get_card_service),
    ],
) -> None:
    await card_service.delete(
        current_user,
        card_id,
    )


# -------------------------------------- UPDATE --------------------------------------
@router.patch(
    "/{card_id}",
    name="cards:patch_card",
    response_model=CardRead,
)
@router_handler
async def update_card(
    card_id: BaseIdType,
    card_update_data: CardUpdate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        "CardService",
        Depends(get_card_service),
    ],
) -> CardRead:
    return await card_service.update(
        current_user,
        card_id,
        card_update_data,
    )
