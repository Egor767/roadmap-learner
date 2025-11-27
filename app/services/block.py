from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.core.logging import block_service_logger as logger
from app.shared.generate_id import generate_base_id
from app.utils.mappers.orm_to_models import block_orm_to_model

if TYPE_CHECKING:
    from app.core.types import BaseIdType
    from app.services import AccessService
    from app.repositories.block import BlockRepository
    from app.models import User
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
    async def get_all(self) -> list["BlockRead"]:
        db_blocks = await self.repo.get_all()
        if not db_blocks:
            logger.warning("Blocks not found in DB")
            return []

        validated_blocks = [
            await block_orm_to_model(db_block) for db_block in db_blocks
        ]

        return validated_blocks

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: "BlockFilters",
    ) -> list["BlockRead"]:
        filters_dict = filters.model_dump()
        accessed_filters = await self.access.filter_blocks_for_user(
            current_user,
            filters_dict,
        )

        db_blocks = await self.repo.get_by_filters(accessed_filters)
        if not db_blocks:
            logger.warning("Blocks with filters(%r) not found", filters)
            return []

        validated_blocks = [
            await block_orm_to_model(db_block) for db_block in db_blocks
        ]

        return validated_blocks

    @service_handler
    async def get_by_id(
        self,
        current_user: "User",
        block_id: "BaseIdType",
    ) -> "BlockRead":
        db_block = await self.repo.get_by_id(block_id)
        if not db_block:
            logger.warning("Block(%r) not found", block_id)
            raise ValueError("NOT_FOUND")

        validated_block = await block_orm_to_model(db_block)
        await self.access.ensure_can_view_block(
            current_user, validated_block.model_dump()
        )

        return validated_block

    @service_handler
    async def create(
        self,
        current_user: "User",
        block_create_data: "BlockCreate",
    ) -> "BlockRead":
        block_dict = block_create_data.model_dump()
        block_dict["id"] = await generate_base_id()

        await self.access.ensure_can_view_block(current_user, block_dict)

        created_block = await self.repo.create(block_dict)
        if not created_block:
            logger.error(
                "Block with params(%r) for User(id=%r) not created",
                block_create_data,
                current_user.id,
            )
            raise ValueError("OPERATION_FAILED")

        validated_created_block = await block_orm_to_model(created_block)

        return validated_created_block

    @service_handler
    async def delete(
        self,
        current_user: "User",
        block_id: "BaseIdType",
    ) -> None:
        await self.get_by_id(current_user, block_id)

        success = await self.repo.delete(block_id)
        if success:
            logger.info("Block deleted successfully: %r", block_id)
        else:
            logger.error("Deletion for Block(%r) FAILED", block_id)
            raise ValueError("OPERATION_FAILED")

    @service_handler
    async def update(
        self,
        current_user: "User",
        block_id: "BaseIdType",
        block_update_data: "BlockUpdate",
    ) -> "BlockRead":
        await self.get_by_id(current_user, block_id)

        block_dict = block_update_data.model_dump(exclude_unset=True)

        updated_block = await self.repo.update(block_id, block_dict)
        if not updated_block:
            logger.error("Failed to update Block(id=%r)", block_id)
            raise ValueError("OPERATION_FAILED")

        validated_updated_user = await block_orm_to_model(updated_block)

        return validated_updated_user
