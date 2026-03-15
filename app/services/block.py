import json
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.block import (
    BlockConfirmRequest,
    BlockCreate,
    BlockFilters,
    BlockMove,
    BlockRead,
    BlockUpdate,
)
from app.shared.generate_id import generate_base_id
from app.utils.cache import get_cache_key, is_single_parent_filter
from app.utils.mappers.cache_to_schema import (
    cache_to_schema,
    cache_to_schemas,
)
from app.utils.mappers.orm_to_schema import (
    orm_list_to_schemas,
    orm_to_schema,
)

if TYPE_CHECKING:
    from app.core.cache import CacheHelper
    from app.models import User
    from app.repositories.block import BlockRepository


class BlockService:
    def __init__(self, repo: "BlockRepository", cache: "CacheHelper"):
        self.repo = repo
        self.cache = cache

    @service_handler
    async def get_all(self) -> list[BlockRead]:
        orm = await self.repo.get_all()
        schemas = orm_list_to_schemas(BlockRead, orm)
        return schemas

    @service_handler
    async def get_by_filters(self, current_user: "User", filters: BlockFilters) -> list[BlockRead]:
        filters_dict = filters.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            key = get_cache_key(
                "blocks", "user", str(current_user.id), "roadmap", str(filters_dict["roadmap_id"]), "list"
            )
            cache = await self.cache.get(key)
            if cache:
                return cache_to_schemas(BlockRead, cache)

        orm = await self.repo.get_by_filters(filters_dict, current_user.id)

        schema = orm_list_to_schemas(BlockRead, orm)

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in schema],
                default=str,
            )
            await self.cache.set(key, cache_data)

        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", block_id: BaseIdType) -> BlockRead:
        key = get_cache_key("blocks", "user", str(current_user.id), "block", str(block_id), "detail")
        cache = await self.cache.get(key)
        if cache:
            return cache_to_schema(BlockRead, cache)

        orm = await self.repo.get_by_id(block_id, current_user.id)

        schema = orm_to_schema(BlockRead, orm)

        await self.cache.set(
            key,
            json.dumps([schema.model_dump(mode="json")]),
        )

        return schema

    @service_handler
    async def create(self, current_user: "User", block_create_data: BlockCreate) -> BlockRead:
        block_dict = block_create_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        block_dict["id"] = generate_base_id()

        block_dict.pop("position", None)
        block_dict.pop("previous", None)

        orm = await self.repo.create(
            block_create_data.roadmap_id,
            block_dict,
            current_user.id,
            block_create_data.position,
            block_create_data.previous,
        )

        schema = orm_to_schema(BlockRead, orm)

        await self.cache.delete(
            get_cache_key("blocks", "user", str(current_user.id), "roadmap", str(schema.roadmap_id), "list")
        )

        return schema

    @service_handler
    async def update(self, current_user: "User", block_id: BaseIdType, block_update_data: BlockUpdate) -> BlockRead:
        block_dict = block_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        orm = await self.repo.update(block_id, block_dict, current_user.id)

        schema = orm_to_schema(BlockRead, orm)

        await self.cache.delete(
            get_cache_key("blocks", "user", str(current_user.id), "roadmap", str(schema.roadmap_id), "list"),
            get_cache_key("blocks", "user", str(current_user.id), "block", str(block_id), "detail"),
        )

        return schema

    @service_handler
    async def move(
        self,
        current_user: "User",
        block_id: BaseIdType,
        move_data: BlockMove,
    ) -> BlockRead:
        orm = await self.repo.move(
            move_data.roadmap_id,
            block_id,
            move_data.previous,
            current_user.id,
        )

        schema = orm_to_schema(BlockRead, orm)

        await self.cache.delete(
            get_cache_key("blocks", "user", str(current_user.id), "roadmap", str(schema.roadmap_id), "list"),
            get_cache_key("blocks", "user", str(current_user.id), "block", str(block_id), "detail"),
        )

        return schema

    @service_handler
    async def delete(self, current_user: "User", block_id: BaseIdType):
        orm = await self.repo.delete(block_id, current_user.id)

        await self.cache.delete(
            get_cache_key("blocks", "user", str(current_user.id), "roadmap", str(orm.roadmap_id), "list"),
            get_cache_key("blocks", "user", str(current_user.id), "block", str(block_id), "detail"),
        )

    @service_handler
    async def create_multiple(self, current_user: "User", request: "BlockConfirmRequest") -> list[BlockRead]:
        blocks_dict = [block.model_dump(exclude_none=True, exclude_unset=True) for block in request.blocks]

        for block in blocks_dict:
            block["id"] = generate_base_id()
            block["roadmap_id"] = request.roadmap_id

        orm = await self.repo.create_multiple(request.roadmap_id, blocks_dict, current_user.id)

        schema = orm_list_to_schemas(BlockRead, orm)

        await self.cache.delete(
            get_cache_key("blocks", "user", str(current_user.id), "roadmap", str(request.roadmap_id), "list")
        )

        return schema
