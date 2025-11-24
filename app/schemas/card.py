from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.core.types import BaseIdType


class BaseCard(BaseModel):
    term: str
    definition: str


class CardCreate(BaseCard):
    example: str | None = None
    comment: str | None = None


class CardStatus(str, Enum):
    UNKNOWN = "unknown"
    KNOWN = "known"
    REVIEW = "review"


class CardUpdate(BaseModel):
    term: str | None = None
    definition: str | None = None
    example: str | None = None
    comment: str | None = None
    status: CardStatus | None = None


class CardRead(BaseCard):
    id: BaseIdType
    block_id: BaseIdType
    example: str | None = None
    comment: str | None = None
    status: CardStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CardFilters(BaseModel):
    term: str | None = None
    definition: str | None = None
    example: str | None = None
    comment: str | None = None
    status: CardStatus | None = None
