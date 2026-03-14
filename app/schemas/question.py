from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.custom_types import BaseIdType


class QuestionStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    REPEAT = "repeat"


class BaseQuestion(BaseModel):
    question: str = Field(..., max_length=500)
    answer: str | None = None

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseQuestion):
    block_id: BaseIdType
    position: Literal["start", "end"] | None = None
    previous: BaseIdType | None = None

    @model_validator(mode="after")
    def validate_position(self):
        if self.position is not None and self.previous is not None:
            raise ValueError("Нельзя одновременно указывать position и previous")

        if self.position is None and self.previous is None:
            self.position = "end"

        return self


class QuestionUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    order_index: int | None = None
    status: QuestionStatus | None = None


class QuestionMove(BaseModel):
    block_id: BaseIdType
    previous: BaseIdType | None = None


class QuestionRead(BaseQuestion):
    id: BaseIdType
    block_id: BaseIdType
    order_index: int
    status: QuestionStatus = QuestionStatus.UNKNOWN
    created_at: datetime
    updated_at: datetime


class QuestionFilters(BaseModel):
    roadmap_id: BaseIdType | None = None
    status: QuestionStatus | None = None
    order_index: int | None = None
    question: str | None = None


class QuestionConfirmItem(BaseModel):
    block_id: BaseIdType
    questions: list[BaseQuestion] = Field(..., min_length=1)


class QuestionConfirmRequest(BaseModel):
    items: list[QuestionConfirmItem] = Field(..., min_length=1, max_length=20)
