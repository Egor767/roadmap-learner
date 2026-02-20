import json
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.handlers import service_handler
from app.shared.generate_id import generate_base_id
from app.utils.cache import get_cache_key, is_single_parent_filter
from app.utils.mappers.cache_to_schema import (
    cache_to_schema,
    cache_to_schemas,
)
from app.utils.mappers.orm_to_schema import (
    orms_to_schemas,
    orm_to_schema,
)
from app.core.custom_types import BaseIdType
from app.schemas.block import (
    BlockCreate,
    BlockRead,
    BlockUpdate,
    BlockFilters,
)

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from app.repositories.block import BlockRepository
    from app.models import User


class BlockService:
    def __init__(self, repo: "BlockRepository", redis: "Redis"):
        self.repo = repo
        self.redis = redis

    @service_handler
    async def get_all(self) -> list[BlockRead]:
        blocks_orm = await self.repo.get_all()
        blocks_schemas = orms_to_schemas(BlockRead, blocks_orm)
        return blocks_schemas

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: BlockFilters,
    ) -> list[BlockRead]:
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
            cache = await self.redis.get(key)
            if cache:
                return cache_to_schemas(BlockRead, cache)

        blocks_orm = await self.repo.get_by_filters(filters_dict, current_user.id)

        blocks_schema = orms_to_schemas(BlockRead, blocks_orm)

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in blocks_schema],
                default=str,
            )
            await self.redis.set(
                key,
                cache_data,
                ex=settings.cache.block_list_ttl,
            )

        return blocks_schema

    @service_handler
    async def get_by_id(
        self,
        current_user: "User",
        block_id: BaseIdType,
    ) -> BlockRead:
        key = get_cache_key(
            "blocks",
            settings.cache.version,
            "user",
            str(current_user.id),
            "block",
            str(block_id),
            "detail",
        )
        cache = await self.redis.get(key)
        if cache:
            return cache_to_schema(BlockRead, cache)

        block_orm = await self.repo.get_by_id(block_id, current_user.id)

        block_schema = orm_to_schema(BlockRead, block_orm)

        await self.redis.set(
            key,
            json.dumps([block_schema.model_dump(mode="json")]),
            ex=settings.cache.block_detail_ttl,
        )

        return block_schema

    @service_handler
    async def create(
        self,
        current_user: "User",
        block_create_data: BlockCreate,
    ) -> BlockRead:
        block_dict = block_create_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        block_dict["id"] = generate_base_id()
        block_dict["user_id"] = current_user.id

        block_orm = await self.repo.create(block_dict)

        block_schema = orm_to_schema(BlockRead, block_orm)

        await self.redis.delete(
            get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "roadmap",
                str(block_orm.roadmap_id),
                "list",
            )
        )

        return block_schema

    @service_handler
    async def delete(
        self,
        current_user: "User",
        block_id: BaseIdType,
    ):
        block_orm = await self.repo.delete(block_id, current_user.id)

        await self.redis.delete(
            get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "roadmap",
                str(block_orm.roadmap_id),
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
        block_id: BaseIdType,
        block_update_data: BlockUpdate,
    ) -> BlockRead:
        block_dict = block_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        block_orm = await self.repo.update(block_id, block_dict, current_user.id)

        block_schema = orm_to_schema(BlockRead, block_orm)

        await self.redis.delete(
            get_cache_key(
                "blocks",
                settings.cache.version,
                "user",
                str(current_user.id),
                "roadmap",
                str(block_schema.roadmap_id),
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

        return block_schema
