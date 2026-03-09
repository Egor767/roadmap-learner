from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.core.custom_types import BaseIdType


class BaseSession(BaseModel):
    pass


class SessionMode(str, Enum):
    REVIEW = "review"
    EXAM = "exam"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionCreate(BaseSession):
    mode: SessionMode
    roadmap_id: BaseIdType
    block_id: BaseIdType | None = None
    mix: bool | None = False


class SessionUpdate(BaseModel):
    status: SessionStatus | None = None
    index: int | None = None
    correct_answers: int | None = None
    incorrect_answers: int | None = None
    review_answers: int | None = None


class SessionRead(BaseSession):
    id: BaseIdType
    user_id: BaseIdType
    roadmap_id: BaseIdType
    block_id: BaseIdType | None = None

    mode: SessionMode

    status: SessionStatus
    questions: list[BaseIdType] = []
    index: int

    correct_answers: int
    incorrect_answers: int
    review_answers: int

    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SessionFilters(BaseModel):
    mode: SessionMode | None = None
    roadmap_id: BaseIdType | None = None
    block_id: BaseIdType | None = None
    status: SessionStatus | None = None


class SessionCardsFilter(BaseModel):
    limit: int = 10
    offset: int = 0


class SessionResult(BaseModel):
    id: BaseIdType
    user_id: BaseIdType
    roadmap_id: BaseIdType
    block_id: BaseIdType | None = None
    mode: SessionMode
    total_answers: int
    correct_answers: int
    incorrect_answers: int
    review_answers: int
    accuracy_percentage: float
    completed_at: datetime
