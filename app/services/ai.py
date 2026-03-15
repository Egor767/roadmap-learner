import json
from collections import defaultdict
from typing import TYPE_CHECKING

from app.clients.ai import AIClient
from app.schemas.ai import (
    BlockDistributeRequest,
    BlockDistributeResponse,
    BlockInfo,
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
    GenerateTarget,
    LoadBlock,
    QuestionDistributeRequest,
    QuestionDistributeResponse,
    QuestionDistributionItem,
)
from app.schemas.block import BlockFilters, BlockRead
from app.schemas.question import QuestionRead
from app.schemas.roadmap import RoadmapRead
from app.utils.mappers.orm_to_schema import orm_list_to_schemas, orm_to_schema

if TYPE_CHECKING:
    from app.models import User
    from app.repositories.block import BlockRepository
    from app.repositories.question import QuestionRepository
    from app.repositories.roadmap import RoadmapRepository


def _build_question_distribution_context(blocks: list["BlockRead"]) -> str:
    """Build context string for AI question distribution prompt."""
    return "\n".join(f"- {block.id}: {block.title} — {block.description or 'no description'}" for block in blocks)


def _parse_ordered_topics(raw: str) -> list[LoadBlock]:
    """Parse AI response into ordered list of block topics."""
    try:
        data = json.loads(raw.strip())
        if not isinstance(data, list):
            raise ValueError("expected a list")
        topics = [str(item).strip() for item in data if str(item).strip()]
    except (json.JSONDecodeError, ValueError):
        topics = [line.strip() for line in raw.splitlines() if line.strip()]

    return [LoadBlock(title=topic) for topic in topics]


def _parse_distribution(raw: str, blocks: list["BlockRead"]) -> dict[str, list[str]]:
    """Parse AI response into question distribution mapping by block id."""
    valid_ids = {str(b.id) for b in blocks}

    try:
        data = json.loads(raw.strip())
        if not isinstance(data, dict):
            raise ValueError("expected an object")
    except (json.JSONDecodeError, ValueError):
        return {}

    result: dict[str, list[str]] = defaultdict(list)
    seen: set[str] = set()

    for key, items in data.items():
        target = key if (key == "undefined" or key in valid_ids) else "undefined"
        for item in items:
            question = str(item).strip()
            if question and question not in seen:
                result[target].append(question)
                seen.add(question)

    return dict(result)


def _parse_generated_items(raw: str) -> list[str]:
    """Parse AI response into list of generated items."""
    try:
        data = json.loads(raw.strip())
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]
    except (json.JSONDecodeError, ValueError):
        pass
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _build_roadmap_context(roadmap: "RoadmapRead") -> str:
    """Build context string from roadmap data."""
    return f"Title: {roadmap.title}. Description: {roadmap.description or ''}."


def _build_block_context(roadmap: "RoadmapRead", block: "BlockRead") -> str:
    """Build context string from roadmap and block data."""
    return (
        f"Roadmap: {roadmap.title}. Description: {roadmap.description or ''}."
        f"Block: {block.title}. Description: {block.description or ''}."
    )


def _build_question_context(roadmap: "RoadmapRead", block: "BlockRead", question: "QuestionRead") -> str:
    """Build context string from roadmap, block and question data."""
    return (
        f"Roadmap: {roadmap.title}. Description: {roadmap.description or ''}."
        f"Block: {block.title}. Description: {block.description or ''}."
        f"Question: {question.question}. Description: {question.answer or ''}."
    )


class AIService:
    """Service for AI-powered operations: chat, distribution, and generation."""

    def __init__(
        self,
        ai_client: AIClient,
        roadmap_repo: "RoadmapRepository",
        block_repo: "BlockRepository",
        question_repo: "QuestionRepository",
    ):
        self.ai_client = ai_client
        self.roadmap_repo = roadmap_repo
        self.block_repo = block_repo
        self.question_repo = question_repo

    async def chat(self, current_user: "User", request: ChatRequest) -> ChatResponse:
        """Send a message to AI with optional context."""
        response = await self.ai_client.chat(request.context, request.content)
        return ChatResponse(response=response)

    async def distribute_blocks(self, current_user: "User", request: BlockDistributeRequest) -> BlockDistributeResponse:
        """Ask AI to distribute raw text into ordered block topics."""
        roadmap_orm = await self.roadmap_repo.get_by_id(request.roadmap_id, current_user.id)
        roadmap = orm_to_schema(RoadmapRead, roadmap_orm)
        context = _build_roadmap_context(roadmap)

        response = await self.ai_client.distribute("blocks", context, request.text)
        blocks = _parse_ordered_topics(response)

        return BlockDistributeResponse(blocks=blocks)

    async def distribute_questions(
        self, current_user: "User", request: QuestionDistributeRequest
    ) -> QuestionDistributeResponse:
        """Ask AI to distribute raw text questions across existing blocks."""
        filters = BlockFilters(roadmap_id=request.roadmap_id)
        filters_dict = filters.model_dump(exclude_none=True, exclude_unset=True)

        blocks_orm = await self.block_repo.get_by_filters(filters_dict, current_user.id)
        blocks = orm_list_to_schemas(BlockRead, blocks_orm)

        if not blocks:
            raise ValueError("Роадмап не содержит блоков")

        context = _build_question_distribution_context(blocks)
        response = await self.ai_client.distribute("questions", context, request.text)
        raw_distribution = _parse_distribution(response, blocks)

        distribution = [
            QuestionDistributionItem(
                block=BlockInfo.model_validate(block),
                questions=raw_distribution.get(str(block.id), []),
            )
            for block in blocks
            if str(block.id) in raw_distribution
        ]

        return QuestionDistributeResponse(
            distribution=distribution,
            undefined=raw_distribution.get("undefined", []),
        )

    async def generate_entities(self, current_user: "User", request: GenerateRequest) -> GenerateResponse:
        """Generate entities (blocks, questions, or cards) using AI for a given target."""
        context = await self._build_generate_context(current_user, request)
        raw = await self.ai_client.generate(request.target.value, context)
        items = _parse_generated_items(raw)
        return GenerateResponse(items=items)

    async def _build_generate_context(self, current_user: "User", request: GenerateRequest) -> str:
        """Build AI generation context based on target type."""
        if request.target == GenerateTarget.blocks:
            if not request.roadmap_id:
                raise ValueError("roadmap_id обязателен для генерации блоков")

            roadmap_orm = await self.roadmap_repo.get_by_id(request.roadmap_id, current_user.id)
            roadmap = orm_to_schema(RoadmapRead, roadmap_orm)

            return _build_roadmap_context(roadmap)

        if request.target == GenerateTarget.questions:
            if not request.block_id:
                raise ValueError("block_id обязателен для генерации вопросов")

            block_orm = await self.block_repo.get_by_id(request.block_id, current_user.id)
            block = orm_to_schema(BlockRead, block_orm)

            roadmap_orm = await self.roadmap_repo.get_by_id(block.roadmap_id, current_user.id)
            roadmap = orm_to_schema(RoadmapRead, roadmap_orm)

            return _build_block_context(roadmap, block)

        if not request.question_id:
            raise ValueError("question_id обязателен для генерации карточек")

        question_orm = await self.question_repo.get_by_id(request.question_id, current_user.id)
        question = orm_to_schema(QuestionRead, question_orm)

        block_orm = await self.block_repo.get_by_id(question.block_id, current_user.id)
        block = orm_to_schema(BlockRead, block_orm)

        roadmap_orm = await self.roadmap_repo.get_by_id(block.roadmap_id, current_user.id)
        roadmap = orm_to_schema(RoadmapRead, roadmap_orm)

        return _build_question_context(roadmap, block, question)
