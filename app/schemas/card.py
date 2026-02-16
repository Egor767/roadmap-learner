from datetime import datetime
from enum import Enum
from typing import Annotated, List

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class BaseCard(BaseModel):
    term: str
    definition: str


class CardCreate(BaseCard):
    example: str | None = None
    comment: str | None = None
    block_id: BaseIdType


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
    user_id: BaseIdType
    example: str | None = None
    comment: str | None = None
    status: CardStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CardFilters(BaseModel):
    user_id: BaseIdType | None = None
    term: str | None = None
    definition: str | None = None
    example: str | None = None
    comment: str | None = None
    status: CardStatus | None = None
