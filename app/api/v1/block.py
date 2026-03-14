from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.custom_types import BaseIdType
from app.core.dependencies.services import get_block_service
from app.core.handlers import router_handler
from app.schemas.block import (
    BlockConfirmRequest,
    BlockCreate,
    BlockFilters,
    BlockMove,
    BlockRead,
    BlockUpdate,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services import BlockService


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
async def get_all_blocks(
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
) -> list[BlockRead]:
    return await block_service.get_all()


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
) -> list[BlockRead]:
    return await block_service.get_by_filters(
        current_user,
        filters,
    )


@router.get(
    "/{block_id}",
    name="blocks:block",
    response_model=BlockRead,
)
@router_handler
async def get_block(
    block_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
) -> BlockRead:
    return await block_service.get_by_id(
        current_user,
        block_id,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "",
    name="blocks:create_block",
    response_model=BlockRead,
)
@router_handler
async def create_block(
    block_create_data: BlockCreate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
) -> BlockRead:
    return await block_service.create(
        current_user,
        block_create_data,
    )


@router.post(
    "/batch",
    name="blocks:create_batch_blocks",
    response_model=list[BlockRead],
    status_code=status.HTTP_201_CREATED,
)
@router_handler
async def confirm_blocks(
    body: BlockConfirmRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    block_service: Annotated["BlockService", Depends(get_block_service)],
) -> list[BlockRead]:
    return await block_service.create_multiple(current_user, body)


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{block_id}",
    name="blocks:delete_block",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def delete_block(
    block_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
) -> None:
    await block_service.delete(
        current_user,
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
    block_id: BaseIdType,
    block_update_data: BlockUpdate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
) -> BlockRead:
    return await block_service.update(
        current_user,
        block_id,
        block_update_data,
    )


@router.patch(
    "/{block_id}/move",
    name="blocks:move_block",
    response_model=BlockRead,
)
@router_handler
async def move_block(
    block_id: BaseIdType,
    move_data: BlockMove,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    block_service: Annotated[
        "BlockService",
        Depends(get_block_service),
    ],
) -> BlockRead:
    return await block_service.move(
        current_user,
        block_id,
        move_data,
    )
