from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.custom_types import BaseIdType
from app.core.enums import QuestionStatus


class BaseQuestion(BaseModel):
    question: str = Field(..., max_length=500)
    answer: str | None = None

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseQuestion):
    module_id: BaseIdType


class QuestionUpdate(BaseModel):
    question: str | None = Field(default=None, max_length=500)
    answer: str | None = None
    status: QuestionStatus | None = None

    @model_validator(mode="after")
    def validate(self) -> "QuestionUpdate":
        """Ensure at least one field is provided for update"""
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update")
        return self

    def dump(self) -> dict:
        """Return update data excluding unset and non-nullable null fields"""
        data = self.model_dump(exclude_unset=True)
        nullable = {"answer"}
        result = {k: v for k, v in data.items() if v is not None or k in nullable}
        return result


class QuestionRead(BaseQuestion):
    id: BaseIdType
    module_id: BaseIdType
    status: QuestionStatus = QuestionStatus.UNKNOWN
    created_at: datetime
    updated_at: datetime


class QuestionFilters(BaseModel):
    roadmap_id: BaseIdType | None = None
    module_id: BaseIdType | None = None
    status: QuestionStatus | None = None
    question: str | None = None


class QuestionConfirmItem(BaseModel):
    module_id: BaseIdType
    questions: list[BaseQuestion] = Field(..., min_length=1)


class QuestionConfirmRequest(BaseModel):
    items: list[QuestionConfirmItem] = Field(..., min_length=1, max_length=20)
