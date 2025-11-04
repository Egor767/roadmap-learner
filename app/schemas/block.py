from enum import Enum

from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional


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
    block_id: uuid.UUID
    road_id: uuid.UUID
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


class BlockFilters(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BlockStatus] = None
