import uuid
from typing import Optional, List
from abc import ABC, abstractmethod

from app.schemas.block import BlockInDB, BlockFilters


class IBlockRepository(ABC):
    @abstractmethod
    async def create_block(self, block_data: dict) -> BlockInDB:
        pass

    @abstractmethod
    async def get_all_blocks(self) -> List[BlockInDB]:
        pass

    @abstractmethod
    async def get_user_blocks(self, user_id: uuid.UUID) -> List[BlockInDB]:
        pass

    @abstractmethod
    async def get_user_block(self, user_id: uuid.UUID, block_id: uuid.UUID) -> Optional[BlockInDB]:
        pass

    @abstractmethod
    async def get_user_blocks_by_filters(self, user_id: uuid.UUID, filters: BlockFilters) -> List[BlockInDB]:
        pass

    @abstractmethod
    async def delete_block(self, user_id: uuid.UUID, block_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def update_roadmap(self, user_id: uuid.UUID, block_id: uuid.UUID, block_data: dict) -> Optional[BlockInDB]:
        pass

