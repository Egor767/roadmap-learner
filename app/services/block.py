from typing import List

from core.handlers import service_handler
from core.logging import block_service_logger as logger
from core.types import BaseIdType
from models import User
from repositories import RoadmapRepository
from repositories.block import BlockRepository
from schemas.block import (
    BlockCreate,
    BlockRead,
    BlockUpdate,
    BlockFilters,
)
from shared.generate_id import generate_base_id


class BlockService:
    def __init__(self, repo: BlockRepository):
        self.repo = repo

    @service_handler
    async def get_all_blocks(self) -> list[BlockRead]:
        blocks = await self.repo.get_all_blocks()
        logger.info(
            "Successful get all blocks, count: %r",
            len(blocks),
        )
        return blocks

    @service_handler
    async def get_blocks(
        self,
        current_user: User,
        roadmap_id: BaseIdType,
        filters: BlockFilters,
    ) -> list[BlockRead]:
        # check roots

        blocks = await self.repo.get_blocks(roadmap_id, filters)
        validated_blocks = [BlockRead.model_validate(block) for block in blocks]
        logger.info(
            "Successful get roadmap blocks, count: %r",
            len(validated_blocks),
        )
        return validated_blocks

    @service_handler
    async def get_roadmap_block(
        self, user_id: BaseIdType, roadmap_id: BaseIdType, block_id: BaseIdType
    ) -> BlockRead:
        # check roots

        block = await self.repo.get_roadmap_block(roadmap_id, block_id)
        if not block:
            logger.warning("Block(%r) not found or access denied", block_id)
            raise ValueError("Block not found or access denied")
        logger.info("Successful get roadmap block")
        return BlockRead.model_validate(block)

    @service_handler
    async def get_block(self, user_id: BaseIdType, block_id: BaseIdType) -> BlockRead:
        # check roots

        block = await self.repo.get_block(block_id)
        if not block:
            logger.warning("Block(%r) not found or access denied", block_id)
            raise ValueError("Block not found or access denied")
        logger.info("Successful get block")
        return BlockRead.model_validate(block)

    @service_handler
    async def create_block(
        self,
        user_id: BaseIdType,
        roadmap_id: BaseIdType,
        block_create_data: BlockCreate,
    ) -> BlockRead:
        # check roots

        block_data = block_create_data.model_dump()
        block_data["roadmap_id"] = roadmap_id
        block_data["id"] = await generate_base_id()

        logger.info(
            "Creating new block: %r for roadmap (roadmap_id=%r): %r",
            block_create_data.title,
            block_data.get("roadmap_id"),
            block_data,
        )
        created_block = await self.repo.create_block(block_data)

        logger.info(
            "Block created successfully: %r",
            created_block.id,
        )
        return BlockRead.model_validate(created_block)

    @service_handler
    async def delete_block(
        self, user_id: BaseIdType, roadmap_id: BaseIdType, block_id: BaseIdType
    ):
        # check roots

        success = await self.repo.delete_block(roadmap_id, block_id)
        if success:
            logger.info("Block deleted successfully: %r", block_id)
        else:
            logger.warning("Block not found for deletion: %r", block_id)
        return success

    @service_handler
    async def update_block(
        self,
        user_id: BaseIdType,
        roadmap_id: BaseIdType,
        block_id: BaseIdType,
        block_update_data: BlockUpdate,
    ) -> BlockRead:
        # check roots

        block_data = block_update_data.model_dump(exclude_unset=True)
        logger.info(
            "Updating block %r: %r",
            block_id,
            block_data,
        )
        updated_block = await self.repo.update_block(roadmap_id, block_id, block_data)

        if not updated_block:
            logger.warning("Block(%r) not found or access denied", block_id)
            raise ValueError("Block not found or access denied")

        logger.info("Successful updating block: %r", block_id)
        return BlockRead.model_validate(updated_block)
