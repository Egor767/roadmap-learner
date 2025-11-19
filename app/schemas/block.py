from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from core.types import BaseIdType


class BaseBlock(BaseModel):
    title: str
    description: str | None = None


class BlockCreate(BaseBlock):
    order_index: int
    roadmap_id: BaseIdType


class BlockStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class BlockUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: BlockStatus | None = None
    order_index: int | None = None
    roadmap_id: BaseIdType | None = None


class BlockRead(BaseBlock):
    id: BaseIdType
    roadmap_id: BaseIdType
    order_index: int
    status: BlockStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlockFilters:
    title: str | None = None
    description: str | None = None
    status: BlockStatus | None = None
    roadmap_id: BaseIdType | None = None
