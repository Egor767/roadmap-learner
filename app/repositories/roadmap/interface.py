from abc import ABC, abstractmethod
import uuid
from typing import Optional, List

from app.schemas.roadmap import RoadMapInDB, RoadMapUpdate, RoadMapCreate


class IRoadMapRepository(ABC):

    @abstractmethod
    async def create_roadmap(self, create_data: RoadMapCreate) -> RoadMapInDB:
        ...

    @abstractmethod
    async def get_user_roadmaps(self, user_id: uuid.UUID) -> Optional[List[RoadMapInDB]]:
        ...

    @abstractmethod
    async def get_user_roadmap(self, user_id: uuid.UUID, roadmap_id: uuid.UUID) -> RoadMapInDB:
        ...

    @abstractmethod
    async def delete_roadmap(self, roadmap_id: uuid.UUID) -> bool:
        ...

    @abstractmethod
    async def update_roadmap(self, update_data: RoadMapUpdate) -> RoadMapInDB:
        ...
