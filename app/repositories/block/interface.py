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
    async def get_roadmap_block(self, road_id: uuid.UUID, block_id: uuid.UUID) -> Optional[BlockInDB]:
        pass

    @abstractmethod
    async def get_roadmap_blocks(self, road_id: uuid.UUID, filters: BlockFilters) -> List[BlockInDB]:
        pass

    @abstractmethod
    async def delete_block(self, roadmap_id: uuid.UUID, block_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def update_block(self, road_id: uuid.UUID, block_id: uuid.UUID, block_data: dict) -> Optional[BlockInDB]:
        pass

