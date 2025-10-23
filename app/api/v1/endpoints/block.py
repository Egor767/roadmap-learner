import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_block_service
from app.core.handlers import router_handler
from app.schemas.block import BlockResponse, BlockCreate, BlockUpdate, BlockFilters
from app.services.block.service import BlockService

router = APIRouter(
    prefix="/roadmaps/{roadmap_id}/blocks",
    tags=["blocks"]
)


@router.get("/all", response_model=List[BlockResponse], status_code=status.HTTP_200_OK)
@router_handler
async def get_all_blocks(
    block_service: BlockService = Depends(get_block_service)
):
    return await block_service.get_all_blocks()


# -------------------------------------- GET ----------------------------------------------
@router.get("/{block_id}", response_model=BlockResponse)
@router_handler
async def get_roadmap_block(
    user_id: uuid.UUID,  # = Depends(get_current_user)
    roadmap_id: uuid.UUID,  # query param
    block_id: uuid.UUID,
    block_service: BlockService = Depends(get_block_service)
):
    return await block_service.get_roadmap_block(user_id, roadmap_id, block_id)


@router.get("/", response_model=List[BlockResponse])
@router_handler
async def get_roadmap_blocks(
    user_id: uuid.UUID,  # = Depends(get_current_user)
    roadmap_id: uuid.UUID,  # query param
    filters: BlockFilters = Depends(),
    block_service: BlockService = Depends(get_block_service)
):
    return await block_service.get_roadmap_blocks(user_id, roadmap_id, filters)


# -------------------------------------- CREATE --------------------------------------
@router.post("/", response_model=BlockResponse, status_code=201)
@router_handler
async def create_block(
    user_id: uuid.UUID,  # = Depends(get_current_user)
    roadmap_id: uuid.UUID,  # query param
    block_data: BlockCreate,
    block_service: BlockService = Depends(get_block_service)
):
    return await block_service.create_block(user_id, roadmap_id, block_data)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{block_id}", status_code=204)
@router_handler
async def delete_block(
    user_id: uuid.UUID,  # = Depends(get_current_user)
    road_id: uuid.UUID,  # query param
    block_id: uuid.UUID,
    block_service: BlockService = Depends(get_block_service)
):
    await block_service.delete_block(user_id, road_id, block_id)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{block_id}", response_model=BlockResponse)
@router_handler
async def update_block(
    user_id: uuid.UUID,  # = Depends(get_current_user)
    roadmap_id: uuid.UUID,  # query param
    block_id: uuid.UUID,
    block_data: BlockUpdate,
    block_service: BlockService = Depends(get_block_service)
):
    return await block_service.update_block(user_id, roadmap_id, block_id, block_data)