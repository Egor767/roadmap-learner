import asyncio
import json
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.core.handlers import service_handler
from app.schemas.card import (
    CardCreate,
    CardFilters,
    CardRead,
    CardStatus,
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
    orm_list_to_schemas_statuses,
    orm_to_schema_status,
)

if TYPE_CHECKING:
    from app.core.cache import CacheHelper
    from app.models import User
    from app.repositories import CardRepository
    from app.repositories import UserCardProgressRepository as ProgressRepository


class CardService:
    def __init__(self, repo: "CardRepository", progress_repo: "ProgressRepository", cache: "CacheHelper"):
        self.repo = repo
        self.progress_repo = progress_repo
        self.cache = cache

    @service_handler
    async def get_all(self) -> list[CardRead]:
        orm = await self.repo.get_all()
        schema = orm_list_to_schemas(CardRead, orm)
        return schema

    @service_handler
    async def get_by_filters(self, current_user: "User", filters: CardFilters) -> list[CardRead]:
        filters_dump = filters.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        status_filter = filters_dump.pop("status", None)
        filters_dict = {
            **{k: v for k, v in filters_dump.items() if v is not None},
        }

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

        if status_filter is not None:
            allowed_ids = await self.progress_repo.get_ids_by_status(current_user.id, status_filter)
            filters_dict["id"] = allowed_ids

        orm = await self.repo.get_by_filters(filters_dict, current_user.id)

        statuses = await self.progress_repo.get_statuses(current_user.id, [q.id for q in orm])
        schemas = orm_list_to_schemas_statuses(CardRead, orm, statuses)

        if is_single_parent_filter(filters_dict, "roadmap_id"):
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in schemas],
                default=str,
            )
            await self.cache.set(key, cache_data)

        return schemas

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
        if cache := await self.cache.get(key):
            return cache_to_schema(CardRead, cache)

        card, status = await asyncio.gather(
            self.repo.get_by_id(card_id, current_user.id),
            self.progress_repo.get_status(current_user.id, card_id),
        )
        schema = orm_to_schema_status(CardRead, card, status)

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
        await self.progress_repo.create(current_user.id, orm.id)

        schema = orm_to_schema_status(CardRead, orm, CardStatus.UNKNOWN)

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
    async def update(
        self,
        current_user: "User",
        card_id: BaseIdType,
        update_data: CardUpdate,
    ) -> CardRead:
        data = update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        status = data.pop("status", None)

        tasks = []
        if data:
            tasks.append(self.repo.update(card_id, data, current_user.id))
        if status is not None:
            tasks.append(self.progress_repo.update(current_user.id, card_id, status))
        await asyncio.gather(*tasks)

        orm, final_status = await asyncio.gather(
            self.repo.get_by_id(card_id, current_user.id),
            self.progress_repo.get_status(current_user.id, card_id),
        )
        schema = orm_to_schema_status(CardRead, orm, final_status)

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
    async def delete(self, current_user: "User", card_id: BaseIdType):
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
