import json
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.handlers import service_handler
from app.core.loggers import card_service_logger as logger
from app.shared.access import get_accessed_filters, user_can_read_entity
from app.shared.generate_id import generate_base_id
from app.utils.cache import is_single_parent_filter, get_cache_key
from app.utils.mappers.cache_to_model import card_cache_to_models
from app.utils.mappers.orm_to_models import card_orm_to_model

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from app.core.custom_types import BaseIdType
    from app.repositories import CardRepository
    from app.models import User
    from app.schemas.card import (
        CardRead,
        CardCreate,
        CardUpdate,
        CardFilters,
    )


class CardService:
    def __init__(self, repo: "CardRepository", redis: "Redis"):
        self.repo = repo
        self.redis = redis

    @service_handler
    async def get_all(self) -> list["CardRead"]:
        db_cards = await self.repo.get_all()
        if not db_cards:
            logger.warning("Cards not found in DB")
            return []

        validated_cards = [card_orm_to_model(db_card) for db_card in db_cards]
        return validated_cards

    @service_handler
    async def get_by_filters(
        self,
        current_user: "User",
        filters: "CardFilters",
        block_id: list["BaseIdType"] | None,
    ) -> list["CardRead"]:
        filters_dump = {
            **filters.model_dump(exclude_none=True, exclude_unset=True),
            "block_id": block_id,
        }
        filters_dict = {k: v for k, v in filters_dump.items() if v is not None}

        if is_single_parent_filter(filters_dict, "block_id"):
            key = get_cache_key(
                "cards",
                settings.cache.version,
                "user",
                str(current_user.id),
                "block",
                str(filters_dict["block_id"][0]),
                "list",
            )
            cached = await self.redis.get(key)
            if cached:
                return card_cache_to_models(cached)

        accessed_filters = get_accessed_filters(
            current_user,
            filters_dict,
        )
        db_cards = await self.repo.get_by_filters(accessed_filters)
        if not db_cards:
            logger.warning("Cards with filters(%r) not found", filters)
            return []

        validated_cards = [card_orm_to_model(db_card) for db_card in db_cards]
        if is_single_parent_filter(filters_dict, "block_id"):
            cache_data = json.dumps(
                [u.model_dump(mode="json") for u in validated_cards],
                default=str,
            )
            await self.redis.set(
                key,
                cache_data,
                ex=settings.cache.card_list_ttl,
            )

        return validated_cards

    @service_handler
    async def get_by_id(
        self, current_user: "User", card_id: "BaseIdType"
    ) -> "CardRead":
        key = get_cache_key(
            "cards",
            settings.cache.version,
            "user",
            str(current_user.id),
            "card",
            str(card_id),
            "detail",
        )
        cached = await self.redis.get(key)
        if cached:
            result_card = card_cache_to_models(cached)
            return result_card[0]

        db_card = await self.repo.get_by_id(card_id)
        if not db_card:
            logger.error("Card(%r) not found", card_id)
            raise ValueError("NOT_FOUND")

        validated_card = card_orm_to_model(db_card)
        user_can_read_entity(
            current_user,
            validated_card.model_dump(),
        )

        await self.redis.set(
            key,
            json.dumps([validated_card.model_dump(mode="json")]),
            ex=settings.cache.card_detail_ttl,
        )
        return validated_card

    @service_handler
    async def create(
        self, current_user: "User", card_create_data: "CardCreate"
    ) -> "CardRead":
        card_dict = card_create_data.model_dump(exclude_none=True, exclude_unset=True)
        card_dict["id"] = generate_base_id()
        card_dict["user_id"] = current_user.id

        created_card = await self.repo.create(card_dict)
        if not created_card:
            logger.error(
                "Card with params(%r) for User(id=%r) not created",
                card_create_data,
                current_user.id,
            )
            raise ValueError("OPERATION_FAILED")

        validated_created_card = card_orm_to_model(created_card)

        await self.redis.delete(
            get_cache_key(
                "cards",
                settings.cache.version,
                "user",
                str(current_user.id),
                "block",
                str(created_card.block_id),
                "list",
            ),
        )

        return validated_created_card

    @service_handler
    async def delete(self, current_user: "User", card_id: "BaseIdType") -> None:
        existed_card = await self.get_by_id(current_user, card_id)

        success = await self.repo.delete(card_id)
        if not success:
            logger.error("Deletion for Card(%r) FAILED", card_id)
            raise ValueError("OPERATION_FAILED")

        await self.redis.delete(
            get_cache_key(
                "cards",
                settings.cache.version,
                "user",
                str(current_user.id),
                "block",
                str(existed_card.block_id),
                "list",
            ),
            get_cache_key(
                "cards",
                settings.cache.version,
                "user",
                str(current_user.id),
                "card",
                str(card_id),
                "detail",
            ),
        )

    @service_handler
    async def update(
        self,
        current_user: "User",
        card_id: "BaseIdType",
        card_update_data: "CardUpdate",
    ) -> "CardRead":
        await self.get_by_id(current_user, card_id)

        card_dict = card_update_data.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        updated_card = await self.repo.update(
            card_id,
            card_dict,
        )
        if not updated_card:
            logger.warning("Failed to update Card(id=%r)", card_id)
            raise ValueError("OPERATION_FAILED")

        validated_updated_card = card_orm_to_model(updated_card)

        await self.redis.delete(
            get_cache_key(
                "cards",
                settings.cache.version,
                "user",
                str(current_user.id),
                "block",
                str(validated_updated_card.block_id),
                "list",
            ),
            get_cache_key(
                "cards",
                settings.cache.version,
                "user",
                str(current_user.id),
                "card",
                str(card_id),
                "detail",
            ),
        )

        return validated_updated_card
