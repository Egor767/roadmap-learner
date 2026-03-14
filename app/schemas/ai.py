from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class ChatRequest(BaseModel):
    context: str = Field(default="", max_length=5_000)
    content: str = Field(..., min_length=1, max_length=10_000)


class ChatResponse(BaseModel):
    response: str


class BlockDistributeRequest(BaseModel):
    roadmap_id: BaseIdType
    text: str = Field(..., min_length=1, max_length=10_000)


class LoadBlock(BaseModel):
    title: str


class BlockDistributeResponse(BaseModel):
    blocks: list[LoadBlock]


class BlockInfo(BaseModel):
    id: BaseIdType
    title: str
    model_config = ConfigDict(from_attributes=True)


class QuestionDistributeRequest(BaseModel):
    roadmap_id: BaseIdType
    text: str = Field(..., min_length=1, max_length=10_000)


class QuestionDistributionItem(BaseModel):
    block: BlockInfo
    questions: list[str]


class QuestionDistributeResponse(BaseModel):
    distribution: list[QuestionDistributionItem]
    undefined: list[str] = []


class GenerateTarget(str, Enum):
    blocks = "blocks"
    cards = "cards"
    questions = "questions"


class GenerateRequest(BaseModel):
    target: GenerateTarget = GenerateTarget.blocks
    roadmap_id: BaseIdType | None = None
    block_id: BaseIdType | None = None
    question_id: BaseIdType | None = None


class GenerateResponse(BaseModel):
    items: list[str]
