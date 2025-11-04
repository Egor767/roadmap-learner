import uuid
from typing import List

from app.core.handlers import service_handler
from app.repositories.block.interface import IBlockRepository
from app.schemas.block import BlockCreate, BlockResponse, BlockUpdate, BlockFilters
from app.core.logging import block_service_logger as logger


class BlockService:
    def __init__(self, repo: IBlockRepository):
        self.repo = repo

    @service_handler
    async def get_all_blocks(self) -> List[BlockResponse]:
        blocks = await self.repo.get_all_blocks()
        validated_blocks = [BlockResponse.model_validate(block) for block in blocks]
        logger.info(f"Successful get all blocks, count: {len(validated_blocks)}")
        return validated_blocks

    @service_handler
    async def get_roadmap_blocks(self, user_id: uuid.UUID,
                                 road_id: uuid.UUID,
                                 filters: BlockFilters
                                 ) -> List[BlockResponse]:
        # check roots

        blocks = await self.repo.get_roadmap_blocks(road_id, filters)
        validated_blocks = [BlockResponse.model_validate(block) for block in blocks]
        logger.info(f"Successful get roadmap blocks, count: {len(validated_blocks)}")
        return validated_blocks

    @service_handler
    async def get_roadmap_block(self, user_id: uuid.UUID,
                                road_id: uuid.UUID,
                                block_id: uuid.UUID
                                ) -> BlockResponse:
        # check roots

        block = await self.repo.get_roadmap_block(road_id, block_id)
        if not block:
            logger.warning(f"Block not found or access denied")
            raise ValueError("Block not found or access denied")
        logger.info(f"Successful get roadmap block")
        return BlockResponse.model_validate(block)

    @service_handler
    async def get_block(self, user_id: uuid.UUID, block_id: uuid.UUID) -> BlockResponse:
        # check roots

        block = await self.repo.get_block(block_id)
        if not block:
            logger.warning(f"Block not found or access denied")
            raise ValueError("Block not found or access denied")
        logger.info(f"Successful get block")
        return BlockResponse.model_validate(block)

    @service_handler
    async def create_block(self, user_id: uuid.UUID,
                           road_id: uuid.UUID,
                           block_create_data: BlockCreate
                           ) -> BlockResponse:
        # check roots

        block_data = block_create_data.model_dump()
        block_data["road_id"] = road_id
        block_data["block_id"] = uuid.uuid4()

        logger.info(f"Creating new block: {block_create_data.title} for roadmap (roadmap_id={block_data.get('road_id')}): {block_data}")
        created_block = await self.repo.create_block(block_data)

        logger.info(f"Block created successfully: {created_block.block_id}")
        return BlockResponse.model_validate(created_block)

    @service_handler
    async def delete_block(self, user_id: uuid.UUID,
                           road_id: uuid.UUID,
                           block_id: uuid.UUID):
        # check roots

        success = await self.repo.delete_block(road_id, block_id)
        if success:
            logger.info(f"Block deleted successfully: {block_id}")
        else:
            logger.warning(f"Block not found for deletion: {block_id}")
        return success

    @service_handler
    async def update_block(self, user_id: uuid.UUID,
                           road_id: uuid.UUID,
                           block_id: uuid.UUID,
                           block_update_data: BlockUpdate
                           ) -> BlockResponse:
        # check roots

        block_data = block_update_data.model_dump(exclude_unset=True)
        logger.info(f"Updating block {block_id}: {block_data}")
        updated_block = await self.repo.update_block(road_id, block_id, block_data)

        if not updated_block:
            logger.warning(f"Block not found for update: {block_id}")
            raise ValueError("Block not found")

        logger.info(f"Successful updating block: {block_id}")
        return BlockResponse.model_validate(updated_block)
