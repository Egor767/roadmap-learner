from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType
from app.schemas.question import QuestionStatus


class ChatRequest(BaseModel):
    context: str = Field(default="", max_length=5_000)
    content: str = Field(..., min_length=1, max_length=10_000)


class ChatResponse(BaseModel):
    response: str


class ModuleDistributeRequest(BaseModel):
    roadmap_id: BaseIdType
    text: str = Field(..., min_length=1, max_length=10_000)


class LoadModule(BaseModel):
    title: str


class ModuleDistributeResponse(BaseModel):
    modules: list[LoadModule]


class ModuleInfo(BaseModel):
    id: BaseIdType
    title: str
    model_config = ConfigDict(from_attributes=True)


class QuestionDistributeRequest(BaseModel):
    roadmap_id: BaseIdType
    text: str = Field(..., min_length=1, max_length=10_000)


class QuestionDistributionItem(BaseModel):
    module: ModuleInfo
    questions: list[str]


class QuestionDistributeResponse(BaseModel):
    distribution: list[QuestionDistributionItem]
    undefined: list[str] = []


class GenerateTarget(str, Enum):
    modules = "modules"
    concepts = "concepts"
    questions = "questions"


class GenerateRequest(BaseModel):
    target: GenerateTarget = GenerateTarget.modules
    roadmap_id: BaseIdType | None = None
    module_id: BaseIdType | None = None
    question_id: BaseIdType | None = None


class GenerateResponse(BaseModel):
    items: list[str]


class ConceptContext(BaseModel):
    term: str
    definition: str


class EvaluateAnswerRequest(BaseModel):
    question: str
    correct_answer: str
    answer: str
    hint: bool
    concepts: list[ConceptContext]


class EvaluateAnswerResponse(BaseModel):
    result: QuestionStatus
    note: str
