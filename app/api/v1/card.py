from typing import List, Annotated

from fastapi import APIRouter, Depends, status

from core.config import settings
from core.dependencies import get_card_service
from core.handlers import router_handler
from core.types import BaseIdType
from schemas.card import CardResponse, CardCreate, CardUpdate, CardFilters
from services import CardService

router = APIRouter(
    prefix=settings.api.v1.cards,
    tags=["Cards"],
)


@router.get(
    "/all",
    response_model=List[CardResponse],
    status_code=status.HTTP_200_OK,
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
@router.get("/{card_id}", response_model=CardResponse)
@router_handler
async def get_block_card(
    user_id: BaseIdType,  # = Depends(get_current_user)
    block_id: BaseIdType,  # query param
    card_id: BaseIdType,
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.get_block_card(
        user_id,
        block_id,
        card_id,
    )


@router.get("/", response_model=List[CardResponse])
@router_handler
async def get_block_cards(
    user_id: BaseIdType,  # = Depends(get_current_user)
    block_id: BaseIdType,  # query param
    filters: Annotated[CardFilters, Depends()],
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.get_block_cards(
        user_id,
        block_id,
        filters,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "/",
    response_model=CardResponse,
    status_code=201,
)
@router_handler
async def create_card(
    user_id: BaseIdType,  # = Depends(get_current_user)
    block_id: BaseIdType,  # query param
    card_data: CardCreate,
    card_service: Annotated[CardService, Depends(get_card_service)],
):
    return await card_service.create_card(
        user_id,
        block_id,
        card_data,
    )


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{card_id}", status_code=204)
@router_handler
async def delete_card(
    user_id: BaseIdType,  # = Depends(get_current_user)
    block_id: BaseIdType,  # query param
    card_id: BaseIdType,
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    await card_service.delete_card(
        user_id,
        block_id,
        card_id,
    )


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{card_id}", response_model=CardResponse)
@router_handler
async def update_card(
    user_id: BaseIdType,  # = Depends(get_current_user)
    block_id: BaseIdType,  # query param
    card_id: BaseIdType,
    card_data: CardUpdate,
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.update_card(
        user_id,
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
    response_model=CardResponse,
)
@router_handler
async def get_card(
    user_id: BaseIdType,
    card_id: BaseIdType,
    card_service: Annotated[
        CardService,
        Depends(get_card_service),
    ],
):
    return await card_service.get_card(
        user_id,
        card_id,
    )
