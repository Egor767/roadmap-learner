import uuid
from typing import Optional, List
from abc import ABC, abstractmethod

from app.schemas.roadmap import RoadMapInDB, RoadMapFilters


class IRoadMapRepository(ABC):
    @abstractmethod
    async def create_roadmap(self, roadmap_data: dict) -> RoadMapInDB:
        pass

    @abstractmethod
    async def get_all_roadmaps(self) -> List[RoadMapInDB]:
        pass

    @abstractmethod
    async def get_user_roadmap(
        self, user_id: uuid.UUID, roadmap_id: uuid.UUID
    ) -> Optional[RoadMapInDB]:
        pass

    @abstractmethod
    async def get_user_roadmaps(
        self, user_id: uuid.UUID, filters: RoadMapFilters
    ) -> List[RoadMapInDB]:
        pass

    @abstractmethod
    async def delete_roadmap(self, user_id: uuid.UUID, roadmap_id: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def update_roadmap(
        self, user_id: uuid.UUID, roadmap_id: uuid.UUID, roadmap_data: dict
    ) -> Optional[RoadMapInDB]:
        pass
