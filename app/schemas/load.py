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
    text: str = Field(..., min_length=1, max_length=10_000)


class QuestionDistributeResponse(BaseModel):
    blocks: list[BlockInfo]
    distribution: dict[BaseIdType, list[BaseQuestion]]


class QuestionConfirmRequest(BaseModel):
    distribution: dict[BaseIdType, list[BaseQuestion]]
