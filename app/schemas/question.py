from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class QuestionStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    REVIEW = "review"


class BaseQuestion(BaseModel):
    question: str = Field(..., max_length=500)
    answer: str

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseQuestion):
    order_index: float
    block_id: BaseIdType


class QuestionUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    order_index: float | None = None
    status: QuestionStatus | None = None


class QuestionRead(BaseQuestion):
    id: BaseIdType
    block_id: BaseIdType
    order_index: float
    status: QuestionStatus
    created_at: datetime
    updated_at: datetime


class QuestionFilters(BaseModel):
    block_id: BaseIdType | None = None
    status: QuestionStatus | None = None
    order_index: float | None = None
