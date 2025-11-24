from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.core.logging import block_service_logger as logger
from app.core.types import BaseIdType
from app.shared.generate_id import generate_base_id

if TYPE_CHECKING:
    from app.services import AccessService
    from app.models import User
    from app.repositories.block import BlockRepository
    from app.schemas.block import (
        BlockCreate,
        BlockRead,
        BlockUpdate,
        BlockFilters,
    )


class BlockService:
    def __init__(
        self,
        repo: "BlockRepository",
        access_service: "AccessService",
    ):
        self.repo = repo
        self.access = access_service

    @service_handler
    async def get_all_blocks(self) -> list["BlockRead"] | list[None]:
        blocks = await self.repo.get_all()
        if not blocks:
            logger.warning("Blocks not found in DB")
            return []

        return blocks

    @service_handler
    async def get_blocks_by_filters(
        self,
        current_user: "User",
        filters: "BlockFilters",
    ) -> list["BlockRead"] | list[None]:

        blocks = await self.repo.get_by_filters(filters)
        if not blocks:
            logger.warning("Blocks with filters(%r) not found", filters)
            return []

        filtered_blocks = await self.access.filter_blocks_for_user(current_user, blocks)

        return filtered_blocks

    @service_handler
    async def get_roadmap_block_by_id(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
        block_id: "BaseIdType",
    ) -> "BlockRead":
        # check roots

        block = await self.repo.get_by_parent(roadmap_id, block_id)
        if not block:
            logger.warning("Block(%r) not found or access denied", block_id)
            raise ValueError("Block not found or access denied")

        return block

    @service_handler
    async def get_block_by_id(
        self,
        current_user: "User",
        block_id: "BaseIdType",
    ) -> "BlockRead":
        # check roots

        block = await self.repo.get_by_id(block_id)
        if not block:
            logger.warning("Block(%r) not found or access denied", block_id)
            raise ValueError("Block not found or access denied")

        return block

    @service_handler
    async def create_block(
        self,
        current_user: "User",
        block_create_data: "BlockCreate",
    ) -> "BlockRead":

        block_data = block_create_data.model_dump()
        block_data["id"] = await generate_base_id()

        created_block = await self.repo.create(block_data)
        if not created_block:
            logger.error(
                "Block with params(%r) for User(id=%r) not created",
                created_block,
                current_user.id,
            )
            raise ValueError("Creation failed")

        return created_block

    @service_handler
    async def delete_block(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
        block_id: "BaseIdType",
    ):
        # check roots

        success = await self.repo.delete(roadmap_id, block_id)
        if success:
            logger.info("Block deleted successfully: %r", block_id)
        else:
            logger.warning("Block not found for deletion: %r", block_id)
        return success

    @service_handler
    async def update_block(
        self,
        current_user: "User",
        roadmap_id: "BaseIdType",
        block_id: "BaseIdType",
        block_update_data: "BlockUpdate",
    ) -> "BlockRead":
        # check roots

        block_data = block_update_data.model_dump(exclude_unset=True)
        logger.info(
            "Updating block %r: %r",
            block_id,
            block_data,
        )
        # TODO убрал roadmap_id из update() надо проверку принадлежности сделать
        updated_block = await self.repo.update(block_id, block_data)

        if not updated_block:
            logger.warning("Block(%r) not found or access denied", block_id)
            raise ValueError("Block not found or access denied")

        return updated_block
