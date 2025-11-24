from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.dependencies.services import get_card_service
from app.core.handlers import router_handler
from app.core.types import BaseIdType
from app.models import User
from app.schemas.card import CardRead, CardCreate, CardUpdate, CardFilters
from app.services import CardService

router = APIRouter(
    prefix=settings.api.v1.cards,
    tags=["Cards"],
)


@router.get(
    "/",
    name="cards:all_cards",
    response_model=list[CardRead],
)
@router_handler
async def get_all_blocks(
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.get_all_cards()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/{card_id}",
    name="cards:filter_cards",
    response_model=CardRead,
)
@router_handler
async def get_block_card(
    card_id: BaseIdType,
    block_id: BaseIdType,  # query param
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.get_block_card(
        current_user,
        block_id,
        card_id,
    )


@router.get(
    "/",
    name="cards:all_cards",
    response_model=list[CardRead],
)
@router_handler
async def get_block_cards(
    block_id: BaseIdType,  # query param
    filters: Annotated[
        CardFilters,
        Depends(),
    ],
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.get_block_cards(
        current_user,
        block_id,
        filters,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "/",
    name="cards:create_card",
    response_model=CardRead,
)
@router_handler
async def create_card(
    block_id: BaseIdType,
    card_data: CardCreate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.create_card(
        current_user,
        block_id,
        card_data,
    )


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{card_id}",
    name="cards:delete_card",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def delete_card(
    block_id: BaseIdType,  # query param
    card_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    await card_service.delete_card(
        current_user,
        block_id,
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
    block_id: BaseIdType,  # query param
    card_id: BaseIdType,
    card_data: CardUpdate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.update_card(
        current_user,
        block_id,
        card_id,
        card_data,
    )


# -------------------------------------- RESOURCE ROUTER --------------------------------------
resource_router = APIRouter(
    prefix=settings.api.v1.cards_resource,
    tags=["Cards Resources"],
)


@resource_router.get(
    "/{card_id}",
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
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.get_card(
        current_user,
        card_id,
    )
