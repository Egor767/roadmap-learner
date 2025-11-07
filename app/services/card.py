from typing import List

from app.core.handlers import service_handler
from app.core.types import BaseIDType
from app.repositories.card import CardRepository
from app.schemas.card import CardCreate, CardResponse, CardUpdate, CardFilters
from app.core.logging import card_service_logger as logger
from shared.generate_id import generate_base_id


class CardService:
    def __init__(self, repo: CardRepository):
        self.repo = repo

    @service_handler
    async def get_all_cards(self) -> List[CardResponse]:
        cards = await self.repo.get_all_cards()
        validated_cards = [CardResponse.model_validate(card) for card in cards]
        logger.info(f"Successful get all cards, count: {len(validated_cards)}")
        return validated_cards

    @service_handler
    async def get_card(self, user_id: BaseIDType, card_id: BaseIDType) -> CardResponse:
        # check roots

        card = await self.repo.get_card(card_id)
        if not card:
            logger.warning(f"Card not found or access denied")
            raise ValueError("Card not found or access denied")
        logger.info(f"Successful get card")
        return CardResponse.model_validate(card)

    @service_handler
    async def get_block_cards(
        self, user_id: BaseIDType, block_id: BaseIDType, filters: CardFilters
    ) -> List[CardResponse]:
        # check roots

        cards = await self.repo.get_block_cards(block_id, filters)
        validated_cards = [CardResponse.model_validate(card) for card in cards]
        logger.info(f"Successful get block cards, count: {len(validated_cards)}")
        return validated_cards

    @service_handler
    async def get_block_card(
        self, user_id: BaseIDType, block_id: BaseIDType, card_id: BaseIDType
    ) -> CardResponse:
        # check roots

        card = await self.repo.get_block_card(block_id, card_id)
        if not card:
            logger.warning(f"Card not found or access denied")
            raise ValueError("Card not found or access denied")
        logger.info(f"Successful get block card")
        return CardResponse.model_validate(card)

    @service_handler
    async def create_card(
        self, user_id: BaseIDType, block_id: BaseIDType, card_create_data: CardCreate
    ) -> CardResponse:
        # check roots

        card_data = card_create_data.model_dump()
        card_data["block_id"] = block_id
        card_data["id"] = await generate_base_id()

        logger.info(
            f"Creating new card: {card_create_data.term} for block (block_id={card_data.get('block_id')}: {card_data.get('block_data')}"
        )
        created_card = await self.repo.create_card(card_data)

        logger.info(f"Card created successfully: {created_card.id}")
        return CardResponse.model_validate(created_card)

    @service_handler
    async def delete_card(
        self, user_id: BaseIDType, block_id: BaseIDType, card_id: BaseIDType
    ):
        # check roots

        success = await self.repo.delete_card(block_id, card_id)
        if success:
            logger.info(f"Card deleted successfully: {card_id}")
        else:
            logger.warning(f"Card not found for deletion: {card_id}")
        return success

    @service_handler
    async def update_card(
        self,
        user_id: BaseIDType,
        block_id: BaseIDType,
        card_id: BaseIDType,
        card_update_data: CardUpdate,
    ) -> CardResponse:
        # check roots

        card_data = card_update_data.model_dump(exclude_unset=True)
        logger.info(f"Updating card {card_id}: {card_data}")
        updated_card = await self.repo.update_card(block_id, card_id, card_data)

        if not updated_card:
            logger.warning(f"Card not found for update: {card_id}")
            raise ValueError("Card not found")

        logger.info(f"Successful updating card: {card_id}")
        return CardResponse.model_validate(updated_card)
