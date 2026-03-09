import json
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.card import (
    CardCreate,
    CardFilters,
    CardRead,
    CardUpdate,
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
    from app.repositories import CardRepository


class CardService:
    def __init__(self, repo: "CardRepository", cache: "CacheHelper"):
        self.repo = repo
        self.cache = cache

    @service_handler
    async def get_all(self) -> list[CardRead]:
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(CardRead, orm)
        return schema

    @service_handler
    async def get_by_filters(self, current_user: "User", filters: CardFilters) -> list[CardRead]:
        filters_dict = filters.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            key = get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "roadmap",
                str(filters_dict["roadmap_id"]),
                "list",
            )
            cache = await self.cache.get(key)
            if cache:
                return cache_to_schemas(CardRead, cache)

        orm = await self.repo.get_by_filters(filters_dict, current_user.id)

        schema = orm_list_to_schemas(CardRead, orm)

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in schema],
                default=str,
            )
            await self.cache.set(key, cache_data)

        return schema

    @service_handler
    async def get_by_id(self, current_user: "User", card_id: BaseIdType) -> CardRead:
        key = get_cache_key(
            "cards",
            "user",
            str(current_user.id),
            "card",
            str(card_id),
            "detail",
        )
        cache = await self.cache.get(key)
        if cache:
            result_card = cache_to_schema(CardRead, cache)
            return result_card

        orm = await self.repo.get_by_id(card_id, current_user.id)

        schema = orm_to_schema(CardRead, orm)

        await self.cache.set(
            key,
            json.dumps([schema.model_dump(mode="json")]),
        )

        return schema

    @service_handler
    async def create(self, current_user: "User", create_data: CardCreate) -> CardRead:
        data = create_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        data["id"] = generate_base_id()

        orm = await self.repo.create(data, current_user.id)

        schema = orm_to_schema(CardRead, orm)

        await self.cache.delete(
            get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "roadmap",
                str(schema.roadmap_id),
                "list",
            ),
        )

        return schema

    @service_handler
    async def update(self, current_user: "User", card_id: BaseIdType, update_data: CardUpdate) -> CardRead:
        card_dict = update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        orm = await self.repo.update(card_id, card_dict, current_user.id)

        schema = orm_to_schema(CardRead, orm)

        await self.cache.delete(
            get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "roadmap",
                str(schema.roadmap_id),
                "list",
            ),
            get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "card",
                str(card_id),
                "detail",
            ),
        )

        return schema

    @service_handler
    async def delete(
        self,
        current_user: "User",
        card_id: BaseIdType,
    ):
        orm = await self.repo.delete(card_id, current_user.id)

        await self.cache.delete(
            get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "roadmap",
                str(orm.roadmap_id),
                "list",
            ),
            get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "card",
                str(card_id),
                "detail",
            ),
        )
