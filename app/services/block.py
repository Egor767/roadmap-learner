from typing import List

from app.core.handlers import service_handler
from app.core.types import BaseIDType
from app.repositories.block import BlockRepository
from app.schemas.block import BlockCreate, BlockResponse, BlockUpdate, BlockFilters
from app.core.logging import block_service_logger as logger
from shared.generate_id import generate_base_id


class BlockService:
    def __init__(self, repo: BlockRepository):
        self.repo = repo

    @service_handler
    async def get_all_blocks(self) -> List[BlockResponse]:
        blocks = await self.repo.get_all_blocks()
        validated_blocks = [BlockResponse.model_validate(block) for block in blocks]
        logger.info(f"Successful get all blocks, count: {len(validated_blocks)}")
        return validated_blocks

    @service_handler
    async def get_roadmap_blocks(
        self, user_id: BaseIDType, roadmap_id: BaseIDType, filters: BlockFilters
    ) -> List[BlockResponse]:
        # check roots

        blocks = await self.repo.get_roadmap_blocks(roadmap_id, filters)
        validated_blocks = [BlockResponse.model_validate(block) for block in blocks]
        logger.info(f"Successful get roadmap blocks, count: {len(validated_blocks)}")
        return validated_blocks

    @service_handler
    async def get_roadmap_block(
        self, user_id: BaseIDType, roadmap_id: BaseIDType, block_id: BaseIDType
    ) -> BlockResponse:
        # check roots

        block = await self.repo.get_roadmap_block(roadmap_id, block_id)
        if not block:
            logger.warning(f"Block not found or access denied")
            raise ValueError("Block not found or access denied")
        logger.info(f"Successful get roadmap block")
        return BlockResponse.model_validate(block)

    @service_handler
    async def get_block(
        self, user_id: BaseIDType, block_id: BaseIDType
    ) -> BlockResponse:
        # check roots

        block = await self.repo.get_block(block_id)
        if not block:
            logger.warning(f"Block not found or access denied")
            raise ValueError("Block not found or access denied")
        logger.info(f"Successful get block")
        return BlockResponse.model_validate(block)

    @service_handler
    async def create_block(
        self,
        user_id: BaseIDType,
        roadmap_id: BaseIDType,
        block_create_data: BlockCreate,
    ) -> BlockResponse:
        # check roots

        block_data = block_create_data.model_dump()
        block_data["roadmap_id"] = roadmap_id
        block_data["id"] = await generate_base_id()

        logger.info(
            f"Creating new block: {block_create_data.title} for roadmap (roadmap_id={block_data.get('roadmap_id')}): {block_data}"
        )
        created_block = await self.repo.create_block(block_data)

        logger.info(f"Block created successfully: {created_block.id}")
        return BlockResponse.model_validate(created_block)

    @service_handler
    async def delete_block(
        self, user_id: BaseIDType, roadmap_id: BaseIDType, block_id: BaseIDType
    ):
        # check roots

        success = await self.repo.delete_block(roadmap_id, block_id)
        if success:
            logger.info(f"Block deleted successfully: {block_id}")
        else:
            logger.warning(f"Block not found for deletion: {block_id}")
        return success

    @service_handler
    async def update_block(
        self,
        user_id: BaseIDType,
        roadmap_id: BaseIDType,
        block_id: BaseIDType,
        block_update_data: BlockUpdate,
    ) -> BlockResponse:
        # check roots

        block_data = block_update_data.model_dump(exclude_unset=True)
        logger.info(f"Updating block {block_id}: {block_data}")
        updated_block = await self.repo.update_block(roadmap_id, block_id, block_data)

        if not updated_block:
            logger.warning(f"Block not found for update: {block_id}")
            raise ValueError("Block not found")

        logger.info(f"Successful updating block: {block_id}")
        return BlockResponse.model_validate(updated_block)
