from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.core.types import BaseIDType


class BlockCreate(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int


class BlockUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    status: Optional[str] = None


class BlockInDB(BaseModel):
    id: BaseIDType
    roadmap_id: BaseIDType
    title: str
    description: Optional[str] = None
    order_index: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlockResponse(BlockInDB): ...


class BlockStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class BlockFilters:
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BlockStatus] = None
