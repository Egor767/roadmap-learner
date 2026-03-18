from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.core.custom_types import BaseIdType
from app.schemas.question import QuestionStatus


class SessionMode(str, Enum):
    REPEAT = "repeat"
    EXAM = "exam"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionCreate(BaseModel):
    mode: SessionMode
    roadmap_id: BaseIdType
    module_id: BaseIdType | None = None
    mix: bool = False
    auto_check: bool = False


class SessionUpdate(BaseModel):
    status: SessionStatus | None = None
    index: int | None = None
    correct_answers: int | None = None
    incorrect_answers: int | None = None
    repeat_answers: int | None = None


class SessionRead(BaseModel):
    id: BaseIdType
    user_id: BaseIdType
    roadmap_id: BaseIdType
    module_id: BaseIdType | None = None
    mode: SessionMode
    auto_check: bool
    status: SessionStatus
    questions: list[BaseIdType] = []
    index: int
    correct_answers: int
    incorrect_answers: int
    repeat_answers: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SessionFilters(BaseModel):
    mode: SessionMode | None = None
    roadmap_id: BaseIdType | None = None
    module_id: BaseIdType | None = None
    status: SessionStatus | None = None


class SessionQuestionFilter(BaseModel):
    limit: int = 10
    offset: int = 0


class SessionItemCreate(BaseModel):
    question_id: BaseIdType
    result: QuestionStatus | None = None
    answer: str | None = None
    hint: bool = False


class SessionItemRead(BaseModel):
    id: BaseIdType
    session_id: BaseIdType
    question_id: BaseIdType
    answer: str | None = None
    hint: bool
    result: QuestionStatus | None = None
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SessionFinishResult(BaseModel):
    id: BaseIdType
    roadmap_id: BaseIdType
    module_id: BaseIdType | None = None
    mode: SessionMode
    auto_check: bool
    total: int
    known_count: int
    unknown_count: int
    repeat_count: int
    accuracy_percentage: float
    items: list[SessionItemRead]
