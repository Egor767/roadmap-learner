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
        cards_orm = await self.repo.get_all()
        cards_schemas = orm_list_to_schemas(CardRead, cards_orm)
        return cards_schemas

    @service_handler
    async def get_by_filters(
        self, current_user: "User", filters: CardFilters, roadmap: list[BaseIdType]
    ) -> list[CardRead]:
        filters_dump = {
            **filters.model_dump(exclude_none=True, exclude_unset=True),
            "roadmap_id": roadmap,
        }
        filters_dict = {k: v for k, v in filters_dump.items() if v is not None}

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            key = get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "roadmap",
                str(filters_dict["roadmap_id"][0]),
                "list",
            )
            cache = await self.cache.get(key)
            if cache:
                return cache_to_schemas(CardRead, cache)

        cards_orm = await self.repo.get_by_filters(filters_dict, current_user.id)

        cards_schema = orm_list_to_schemas(CardRead, cards_orm)

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in cards_schema],
                default=str,
            )
            await self.cache.set(key, cache_data)

        return cards_schema

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

        cards_orm = await self.repo.get_by_id(card_id, current_user.id)

        cards_schema = orm_to_schema(CardRead, cards_orm)

        await self.cache.set(
            key,
            json.dumps([cards_schema.model_dump(mode="json")]),
        )

        return cards_schema

    @service_handler
    async def create(self, current_user: "User", card_create_data: CardCreate) -> CardRead:
        card_dict = card_create_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        card_dict["id"] = generate_base_id()

        card_orm = await self.repo.create(card_dict, current_user.id)

        card_schema = orm_to_schema(CardRead, card_orm)

        await self.cache.delete(
            get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "block",
                str(card_schema.block_id),
                "list",
            ),
        )

        return card_schema

    @service_handler
    async def update(self, current_user: "User", card_id: BaseIdType, card_update_data: CardUpdate) -> CardRead:
        card_dict = card_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        card_orm = await self.repo.update(card_id, card_dict, current_user.id)

        card_schema = orm_to_schema(CardRead, card_orm)

        await self.cache.delete(
            get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "roadmap",
                str(card_schema.roadmap_id),
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

        return card_schema

    @service_handler
    async def delete(
        self,
        current_user: "User",
        card_id: BaseIdType,
    ):
        card_orm = await self.repo.delete(card_id, current_user.id)

        await self.cache.delete(
            get_cache_key(
                "cards",
                "user",
                str(current_user.id),
                "roadmap",
                str(card_orm.roadmap_id),
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
