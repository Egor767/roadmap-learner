from typing import List, Annotated

from fastapi import APIRouter, Depends, status

from core.config import settings
from core.dependencies import get_block_service
from core.handlers import router_handler
from core.types import BaseIdType
from schemas.block import BlockResponse, BlockCreate, BlockUpdate, BlockFilters
from services import BlockService

router = APIRouter(
    prefix=settings.api.v1.blocks,
    tags=["Blocks"],
)


@router.get(
    "/all",
    response_model=List[BlockResponse],
    status_code=status.HTTP_200_OK,
)
@router_handler
async def get_all_blocks(
    block_service: Annotated[
        BlockService,
        Depends(get_block_service),
    ],
):
    return await block_service.get_all_blocks()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/{block_id}",
    response_model=BlockResponse,
)
@router_handler
async def get_roadmap_block(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,  # query param
    block_id: BaseIdType,
    block_service: Annotated[
        BlockService,
        Depends(get_block_service),
    ],
):
    return await block_service.get_roadmap_block(
        user_id,
        roadmap_id,
        block_id,
    )


@router.get(
    "/",
    response_model=List[BlockResponse],
)
@router_handler
async def get_roadmap_blocks(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,  # query param
    filters: Annotated[
        BlockFilters,
        Depends(),
    ],
    block_service: Annotated[
        BlockService,
        Depends(get_block_service),
    ],
):
    return await block_service.get_roadmap_blocks(
        user_id,
        roadmap_id,
        filters,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "/",
    response_model=BlockResponse,
    status_code=201,
)
@router_handler
async def create_block(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,  # query param
    block_data: BlockCreate,
    block_service: Annotated[
        BlockService,
        Depends(get_block_service),
    ],
):
    return await block_service.create_block(
        user_id,
        roadmap_id,
        block_data,
    )


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{block_id}", status_code=204)
@router_handler
async def delete_block(
    user_id: BaseIdType,  # = Depends(get_current_user)
    road_id: BaseIdType,  # query param
    block_id: BaseIdType,
    block_service: Annotated[
        BlockService,
        Depends(get_block_service),
    ],
):
    await block_service.delete_block(
        user_id,
        road_id,
        block_id,
    )


# -------------------------------------- UPDATE --------------------------------------
@router.patch(
    "/{block_id}",
    response_model=BlockResponse,
)
@router_handler
async def update_block(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,  # query param
    block_id: BaseIdType,
    block_data: BlockUpdate,
    block_service: Annotated[
        BlockService,
        Depends(get_block_service),
    ],
):
    return await block_service.update_block(
        user_id,
        roadmap_id,
        block_id,
        block_data,
    )


# -------------------------------------- RESOURCE ROUTER --------------------------------------
resource_router = APIRouter(
    prefix=settings.api.v1.blocks_resource,
    tags=["Blocks Resources"],
)


@resource_router.get(
    "/{block_id}",
    response_model=BlockResponse,
)
@router_handler
async def get_block(
    user_id: BaseIdType,
    block_id: BaseIdType,
    block_service: Annotated[
        BlockService,
        Depends(get_block_service),
    ],
):
    return await block_service.get_block(
        user_id,
        block_id,
    )
