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
from app.utils.cache import is_single_parent_filter
from app.utils.mappers.cache_to_schema import (
    cache_to_schema,
    cache_to_schemas,
)
from app.utils.mappers.orm_to_schema import (
    orm_list_to_schemas,
    orm_to_schema,
)

if TYPE_CHECKING:
    from app.core.cache import CacheHelper, CacheScope
    from app.models import User
    from app.repositories import BlockRepository, VerifyRepository


class BlockService:
    """Service for block business logic"""

    def __init__(self, repo: "BlockRepository", verify: "VerifyRepository", cache: "CacheHelper"):
        self.repo = repo
        self.verify = verify
        self.cache = cache

    def _scope(self, current_user: "User") -> "CacheScope":
        """Return cache scope for current user"""
        return self.cache.scope("blocks", str(current_user.id))

    @service_handler
    async def get_all(self) -> list[BlockRead]:
        """Return all blocks"""
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(BlockRead, orm)
        return schema

    @service_handler
    async def get_by_filters(self, current_user: "User", filters: BlockFilters) -> list[BlockRead]:
        """Return blocks matching filters for current user"""
        filters_dict = filters.model_dump(exclude_none=True, exclude_unset=True)
        scope = self._scope(current_user)
        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cached = await scope.get("roadmap", str(filters_dict["roadmap_id"]), "list")
            if cached:
                return cache_to_schemas(BlockRead, cached)
        orm = await self.repo.get_by_filters(filters_dict, current_user.id)
        schema = orm_list_to_schemas(BlockRead, orm)
        if is_single_parent_filter(filters_dict, "roadmap_id"):
            await scope.put(
                json.dumps([u.model_dump(mode="json") for u in schema], default=str),
                "roadmap",
                str(filters_dict["roadmap_id"]),
                "list",
            )
        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", block: BaseIdType) -> BlockRead:
        """Return block by id for current user"""
        scope = self._scope(current_user)
        cached = await scope.get("block", str(block), "detail")
        if cached:
            return cache_to_schema(BlockRead, cached)
        orm = await self.verify.verify_block(block, current_user.id)
        schema = orm_to_schema(BlockRead, orm)
        await scope.put(json.dumps([schema.model_dump(mode="json")]), "block", str(block), "detail")
        return schema

    @service_handler
    async def create(self, current_user: "User", data: BlockCreate) -> BlockRead:
        """Create new block for current user"""
        await self.verify.verify_roadmap(data.roadmap_id, current_user.id)
        block_dict = data.model_dump(exclude_none=True, exclude_unset=True)
        block_dict["id"] = generate_base_id()
        block_dict.pop("position", None)
        block_dict.pop("previous", None)
        orm = await self.repo.create(
            data.roadmap_id,
            block_dict,
            data.position,
            data.previous,
        )
        schema = orm_to_schema(BlockRead, orm)
        await self._scope(current_user).drop(("roadmap", str(schema.roadmap_id), "list"))
        return schema

    @service_handler
    async def update(self, current_user: "User", block: BaseIdType, data: BlockUpdate) -> BlockRead:
        """Update block for current user"""
        await self.verify.verify_block(block, current_user.id)
        block_dict = data.model_dump(exclude_none=True, exclude_unset=True)
        orm = await self.repo.update(block, block_dict)
        schema = orm_to_schema(BlockRead, orm)
        await self._scope(current_user).drop(
            ("roadmap", str(schema.roadmap_id), "list"),
            ("block", str(block), "detail"),
        )
        return schema

    @service_handler
    async def move(self, current_user: "User", block: BaseIdType, data: BlockMove) -> BlockRead:
        """Move block to new position for current user"""
        await self.verify.verify_roadmap(data.roadmap_id, current_user.id)
        orm, affected = await self.repo.move(data.roadmap_id, block, data.previous)
        schema = orm_to_schema(BlockRead, orm)
        scope = self._scope(current_user)
        await scope.drop(
            ("roadmap", str(schema.roadmap_id), "list"),
            ("block", str(block), "detail"),
            *[("block", str(affected_id), "detail") for affected_id in affected],
        )
        return schema

    @service_handler
    async def delete(self, current_user: "User", block: BaseIdType) -> None:
        """Delete block for current user"""
        orm = await self.verify.verify_block(block, current_user.id)
        await self.repo.delete(block)
        await self._scope(current_user).drop(
            ("roadmap", str(orm.roadmap_id), "list"),
            ("block", str(block), "detail"),
        )

    @service_handler
    async def create_multiple(self, current_user: "User", request: "BlockConfirmRequest") -> list[BlockRead]:
        """Create multiple blocks for current user"""
        await self.verify.verify_roadmap(request.roadmap_id, current_user.id)
        blocks_dict = [block.model_dump(exclude_none=True, exclude_unset=True) for block in request.blocks]
        for block in blocks_dict:
            block["id"] = generate_base_id()
            block["roadmap_id"] = request.roadmap_id
        orm = await self.repo.create_multiple(request.roadmap_id, blocks_dict)
        schema = orm_list_to_schemas(BlockRead, orm)
        await self._scope(current_user).drop(("roadmap", str(request.roadmap_id), "list"))
        return schema
