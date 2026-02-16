import json
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.handlers import service_handler
from app.core.loggers import block_service_logger as logger
from app.shared.access import (
    user_can_read_entity,
    get_accessed_filters,
)
from app.shared.generate_id import generate_base_id
from app.utils.cache import get_cache_key, is_single_parent_filter
from app.utils.mappers.cache_to_model import block_cache_to_models
from app.utils.mappers.orm_to_models import block_orm_to_model

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from app.core.custom_types import BaseIdType
    from app.repositories.block import BlockRepository
    from app.models import User
    from app.schemas.block import (
        BlockCreate,
        BlockRead,
        BlockUpdate,
        BlockFilters,
    )


class BlockService:
    def __init__(self, repo: "BlockRepository", redis: "Redis"):
        self.repo = repo
        self.redis = redis

    @service_handler
    async def get_all(self) -> list["BlockRead"]:
        db_blocks = await self.repo.get_all()
        if not db_blocks:
            logger.warning("Blocks not found in DB")
            return []

        validated_blocks = [block_orm_to_model(db_block) for db_block in db_blocks]
        return validated_blocks

    @service_handler
    async def get_by_filters(
        self, current_user: "User", filters: "BlockFilters"
    ) -> list["BlockRead"]:
        filters_dict = filters.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            key = get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "roadmap",
                str(filters_dict["roadmap_id"]),
                "list",
            )
            cached = await self.redis.get(key)
            if cached:
                return block_cache_to_models(cached)

        accessed_filters = get_accessed_filters(current_user, filters_dict)
        db_blocks = await self.repo.get_by_filters(accessed_filters)
        if not db_blocks:
            logger.warning("Blocks with filters(%r) not found", filters)
            return []

        validated_blocks = [block_orm_to_model(db_block) for db_block in db_blocks]

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in validated_blocks], default=str
            )
            await self.redis.set(
                key,
                cache_data,
                ex=settings.cache.block_list_ttl,
            )

        return validated_blocks

    @service_handler
    async def get_by_id(
        self, current_user: "User", block_id: "BaseIdType"
    ) -> "BlockRead":
        key = get_cache_key(
            "blocks",
            settings.cache.version,
            "user",
            str(current_user.id),
            "block",
            str(block_id),
            "detail",
        )
        cached = await self.redis.get(key)
        if cached:
            cached_block = block_cache_to_models(cached)
            return cached_block[0]

        db_block = await self.repo.get_by_id(block_id)
        if not db_block:
            logger.error("Block(%r) not found", block_id)
            raise ValueError("NOT_FOUND")

        validated_block = block_orm_to_model(db_block)
        user_can_read_entity(
            current_user,
            validated_block.model_dump(),
        )

        await self.redis.set(
            key,
            json.dumps([validated_block.model_dump(mode="json")]),
            ex=settings.cache.block_detail_ttl,
        )
        return validated_block

    @service_handler
    async def create(
        self, current_user: "User", block_create_data: "BlockCreate"
    ) -> "BlockRead":
        block_dict = block_create_data.model_dump(exclude_none=True, exclude_unset=True)
        block_dict["id"] = generate_base_id()
        block_dict["user_id"] = current_user.id

        created_block = await self.repo.create(block_dict)
        if not created_block:
            logger.error(
                "Block with params(%r) for User(id=%r) not created",
                block_create_data,
                current_user.id,
            )
            raise ValueError("OPERATION_FAILED")

        validated_created_block = block_orm_to_model(created_block)

        await self.redis.delete(
            get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "roadmap",
                str(block_dict["roadmap_id"]),
                "list",
            )
        )

        return validated_created_block

    @service_handler
    async def delete(self, current_user: "User", block_id: "BaseIdType") -> None:
        existed_block = await self.get_by_id(current_user, block_id)

        success = await self.repo.delete(block_id)
        if not success:
            logger.error("Deletion for Block(%r) FAILED", block_id)
            raise ValueError("OPERATION_FAILED")

        await self.redis.delete(
            get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "roadmap",
                str(existed_block.roadmap_id),
                "list",
            ),
            get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "block",
                str(block_id),
                "detail",
            ),
        )

    @service_handler
    async def update(
        self,
        current_user: "User",
        block_id: "BaseIdType",
        block_update_data: "BlockUpdate",
    ) -> "BlockRead":
        await self.get_by_id(current_user, block_id)

        block_dict = block_update_data.model_dump(exclude_none=True, exclude_unset=True)
        updated_block = await self.repo.update(block_id, block_dict)
        if not updated_block:
            logger.error("Failed to update Block(id=%r)", block_id)
            raise ValueError("OPERATION_FAILED")

        validated_updated_block = block_orm_to_model(updated_block)

        await self.redis.delete(
            get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "roadmap",
                str(validated_updated_block.roadmap_id),
                "list",
            ),
            get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "block",
                str(block_id),
                "detail",
            ),
        )

        return validated_updated_block
