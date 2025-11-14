from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from core.types import BaseIdType


class RoadMapCreate(BaseModel):
    title: str
    description: Optional[str] = None


class RoadMapUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class RoadMapInDB(BaseModel):
    id: BaseIdType
    user_id: BaseIdType
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoadMapResponse(RoadMapInDB): ...


class RoadMapStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class RoadMapFilters(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[RoadMapStatus] = None
