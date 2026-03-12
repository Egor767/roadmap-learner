from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType
from app.schemas.block import BaseBlock, BlockRead


class BlockDistributeRequest(BaseModel):
    roadmap_id: BaseIdType
    text: str = Field(..., min_length=1, max_length=10_000)


class LoadBlock(BaseModel):
    text: str


class BlockDistributeResponse(BaseModel):
    loading_blocks: list[LoadBlock]


class BlockConfirmItem(BaseBlock):
    pass


class BlockConfirmRequest(BaseModel):
    roadmap_id: BaseIdType
    blocks: list[BlockConfirmItem] = Field(..., min_length=1, max_length=20)


class BlockConfirmResponse(BaseModel):
    created: list[BlockRead]


class BlockInfo(BaseModel):
    id: BaseIdType
    title: str

    model_config = ConfigDict(from_attributes=True)


class QuestionDistributeRequest(BaseModel):
    raw_text: str = Field(..., min_length=1, max_length=10_000)


class QuestionDistributeResponse(BaseModel):
    blocks: list[BlockInfo]
    distribution: dict[str, list[str]]


class QuestionConfirmItem(BaseModel):
    question: str = Field(..., min_length=1)
    answer: str = ""


class QuestionConfirmRequest(BaseModel):
    distribution: dict[BaseIdType, list[QuestionConfirmItem]] = Field(..., min_length=1)


class QuestionConfirmResponse(BaseModel):
    created_questions: int
