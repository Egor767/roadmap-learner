import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_block_service
from app.core.handlers import router_handler
from app.schemas.block import BlockResponse, BlockCreate, BlockUpdate, BlockFilters
from app.services.block.service import BlockService

router = APIRouter(prefix="/blocks", tags=["blocks"])


# -------------------------------------- GET ----------------------------------------------
@router.get("/",
            response_model=List[BlockResponse],
            status_code=status.HTTP_200_OK)
@router_handler
async def get_all_blocks(
    block_service: BlockService = Depends(get_block_service)
):
    return await block_service.get_all_blocks()

