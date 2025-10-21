import uuid
from typing import List

from app.core.handlers import service_handler
from app.repositories.block.interface import IBlockRepository
from app.schemas.block import BlockCreate, BlockResponse, BlockUpdate, BlockFilters
from app.core.logging import roadmap_service_logger as logger


class BlockService:
    def __init__(self, repo: IBlockRepository):
        self.repo = repo

    @service_handler
    async def get_all_blocks(self) -> List[BlockResponse]:
        blocks = await self.repo.get_all_blocks()
        validated_blocks = [BlockResponse.model_validate(block) for block in blocks]
        logger.info(f"Successful get all blocks, count: {len(validated_blocks)}")
        return validated_blocks

