from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class BlockStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class BaseBlock(BaseModel):
    title: str = Field(..., max_length=75)
    description: str | None = Field(default=None, max_length=300)

    model_config = ConfigDict(from_attributes=True)


class BlockCreate(BaseBlock):
    order_index: float
    roadmap_id: BaseIdType


class BlockUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=75)
    description: str | None = Field(default=None, max_length=300)
    status: BlockStatus | None = None
    order_index: float | None = None
    roadmap_id: BaseIdType | None = None


class BlockRead(BaseBlock):
    id: BaseIdType
    roadmap_id: BaseIdType
    order_index: float
    status: BlockStatus
    created_at: datetime
    updated_at: datetime


class BlockFilters(BaseModel):
    roadmap_id: BaseIdType | None = None
    title: str | None = None
    description: str | None = None
    status: BlockStatus | None = None
    order_index: float | None = None
