from typing import TYPE_CHECKING

from app.core.handlers import service_handler
from app.core.logging import card_service_logger as logger
from app.schemas.card import CardRead, CardCreate, CardUpdate, CardFilters
from app.shared.generate_id import generate_base_id

if TYPE_CHECKING:
    from app.models import User
    from app.core.types import BaseIdType
    from app.repositories import CardRepository


class CardService:
    def __init__(self, repo: "CardRepository"):
        self.repo = repo

    @service_handler
    async def get_all_cards(self) -> list[CardRead] | list[None]:
        cards = await self.repo.get_all()
        return cards

    @service_handler
    async def get_card(
        self,
        user: "User",
        card_id: "BaseIdType",
    ) -> CardRead:
        # check roots

        card = await self.repo.get_by_id(card_id)
        if not card:
            logger.error(f"Card not found or access denied")
            raise ValueError("Card not found or access denied")

        return card

    @service_handler
    async def get_block_cards(
        self,
        user: "User",
        block_id: "BaseIdType",
        filters: CardFilters,
    ) -> list[CardRead] | list[None]:
        # check roots

        cards = await self.repo.get_by_filters(block_id, filters)

        logger.info(f"Successful get block cards, count: {len(cards)}")
        return cards

    @service_handler
    async def get_block_card(
        self,
        user: "User",
        block_id: "BaseIdType",
        card_id: "BaseIdType",
    ) -> CardRead:
        # check roots

        card = await self.repo.get_by_parent(block_id, card_id)
        if not card:
            logger.warning(f"Card not found or access denied")
            raise ValueError("Card not found or access denied")

        return card

    @service_handler
    async def create_card(
        self,
        user: "User",
        block_id: "BaseIdType",
        card_create_data: CardCreate,
    ) -> CardRead:
        # check roots

        card_data = card_create_data.model_dump()
        card_data["block_id"] = block_id
        card_data["id"] = await generate_base_id()

        logger.info(
            f"Creating new card: {card_create_data.term} "
            f"for block (block_id={card_data.get('block_id')}: "
            f"{card_data.get('block_data')}"
        )
        created_card = await self.repo.create(card_data)

        return created_card

    @service_handler
    async def delete_card(
        self,
        user: "User",
        block_id: "BaseIdType",
        card_id: "BaseIdType",
    ) -> None:
        # check roots

        success = await self.repo.delete(block_id, card_id)
        if not success:
            logger.warning(f"Card not found for deletion: {card_id}")

    @service_handler
    async def update_card(
        self,
        user: "User",
        block_id: "BaseIdType",
        card_id: "BaseIdType",
        card_update_data: CardUpdate,
    ) -> CardRead:
        # check roots

        card_data = card_update_data.model_dump(exclude_unset=True)

        updated_card = await self.repo.update(block_id, card_id, card_data)

        if not updated_card:
            logger.warning(f"Card not found for update: {card_id}")
            raise ValueError("Card not found")

        return updated_card
