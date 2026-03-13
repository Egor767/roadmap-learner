from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType
from app.schemas.block import BaseBlock
from app.schemas.question import BaseQuestion


class BlockDistributeRequest(BaseModel):
    roadmap_id: BaseIdType
    text: str = Field(..., min_length=1, max_length=10_000)


class LoadBlock(BaseModel):
    title: str


class BlockDistributeResponse(BaseModel):
    blocks: list[LoadBlock]


class BlockConfirmRequest(BaseModel):
    roadmap_id: BaseIdType
    blocks: list[BaseBlock] = Field(..., min_length=1, max_length=20)


# ── Questions ─────────────────────────────────────────────────────────────────


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


class QuestionConfirmItem(BaseModel):
    block_id: BaseIdType
    questions: list[BaseQuestion] = Field(..., min_length=1)


class QuestionConfirmRequest(BaseModel):
    items: list[QuestionConfirmItem] = Field(..., min_length=1, max_length=20)
