from typing import Annotated, TYPE_CHECKING

from fastapi import APIRouter, Depends
from starlette import status

from core.authentication.fastapi_users import current_active_user
from core.config import settings
from core.dependencies.services import get_block_service
from core.handlers import router_handler
from core.types import BaseIdType
from schemas.block import (
    BlockRead,
    BlockCreate,
    BlockUpdate,
    BlockFilters,
)

if TYPE_CHECKING:
    from services import BlockService
    from models import User


router = APIRouter(
    prefix=settings.api.v1.blocks,
    tags=["Blocks"],
)


@router.get(
    "",
    name="blocks:all_blocks",
    response_model=list[BlockRead],
)
@router_handler
async def get_blocks(
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
):
    return await block_service.get_all_blocks()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/filters",
    name="blocks:filter_blocks",
    response_model=list[BlockRead],
)
@router_handler
async def get_blocks(
    filters: Annotated[
        BlockFilters,
        Depends(),
    ],
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
):
    return await block_service.get_blocks_by_filters(
        current_user,
        filters,
    )


@router.get(
    "/{block_id}",
    name="blocks:block",
    response_model=BlockRead,
)
@router_handler
async def get_roadmap_block(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,  # query param
    block_id: BaseIdType,
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
):
    return await block_service.get_roadmap_block_by_id(user_id, roadmap_id, block_id)


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "/",
    name="blocks:create_block",
    response_model=BlockRead,
)
@router_handler
async def create_block(
    block_data: BlockCreate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
):
    return await block_service.create_block(
        current_user,
        block_data,
    )


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{block_id}",
    name="blocks:delete_block",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def delete_block(
    user_id: BaseIdType,  # = Depends(get_current_user)
    road_id: BaseIdType,  # query param
    block_id: BaseIdType,
    block_service: Annotated[
        "BlockService",
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
    name="blocks:patch_block",
    response_model=BlockRead,
)
@router_handler
async def update_block(
    user_id: BaseIdType,  # = Depends(get_current_user)
    roadmap_id: BaseIdType,  # query param
    block_id: BaseIdType,
    block_data: BlockUpdate,
    block_service: Annotated[
        "BlockService",
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
    name="blocks:block",
    response_model=BlockRead,
)
@router_handler
async def get_block(
    user_id: BaseIdType,
    block_id: BaseIdType,
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
):
    return await block_service.get_block_by_id(
        user_id,
        block_id,
    )
