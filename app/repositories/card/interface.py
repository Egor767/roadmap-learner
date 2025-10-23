import uuid
from typing import Optional, List
from abc import ABC, abstractmethod

from app.schemas.card import CardInDB, CardFilters


class ICardRepository(ABC):
    @abstractmethod
    async def create_card(self, card_data: dict) -> CardInDB:
        pass

    @abstractmethod
    async def get_all_cards(self) -> List[CardInDB]:
        pass

    @abstractmethod
    async def get_block_card(self, block_id: uuid.UUID, card_id: uuid.UUID) -> Optional[CardInDB]:
        pass

    @abstractmethod
    async def get_block_cards(self, block_id: uuid.UUID, filters: CardFilters) -> List[CardInDB]:
        pass

    @abstractmethod
    async def delete_card(self, block_id: uuid.UUID, card_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def update_card(self, block_id: uuid.UUID, card_id: uuid.UUID, card_data: dict) -> Optional[CardInDB]:
        pass

