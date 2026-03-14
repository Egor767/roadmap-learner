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

if TYPE_CHECKING:
    from app.models import User
    from app.services import BlockService, CardService, QuestionService, RoadmapService


def _build_question_distribution_context(blocks: list["BlockRead"]) -> str:
    return "\n".join(f"- {block.id}: {block.title} — {block.description or 'no description'}" for block in blocks)


def _parse_ordered_topics(raw: str) -> list[LoadBlock]:
    try:
        data = json.loads(raw.strip())
        if not isinstance(data, list):
            raise ValueError("expected a list")
        topics = [str(item).strip() for item in data if str(item).strip()]
    except (json.JSONDecodeError, ValueError):
        topics = [line.strip() for line in raw.splitlines() if line.strip()]

    return [LoadBlock(title=topic) for topic in topics]


def _parse_distribution(raw: str, blocks: list["BlockRead"]) -> dict[str, list[str]]:
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
    try:
        data = json.loads(raw.strip())
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]
    except (json.JSONDecodeError, ValueError):
        pass
    return [line.strip() for line in raw.splitlines() if line.strip()]


class AIService:
    def __init__(
        self,
        ai_client: AIClient,
        roadmap_service: "RoadmapService",
        block_service: "BlockService",
        question_service: "QuestionService",
        card_service: "CardService",
    ):
        self.ai_client = ai_client
        self.roadmap_service = roadmap_service
        self.block_service = block_service
        self.question_service = question_service
        self.card_service = card_service

    async def chat(self, current_user: "User", request: ChatRequest) -> ChatResponse:
        response = await self.ai_client.chat(request.context, request.content)
        return ChatResponse(response=response)

    async def distribute_blocks(self, current_user: "User", request: BlockDistributeRequest) -> BlockDistributeResponse:
        roadmap = await self.roadmap_service.get_by_id(current_user, request.roadmap_id)
        context = f"Roadmap title: {roadmap.title}. Roadmap Description: {roadmap.description}"

        response = await self.ai_client.distribute("blocks", context, request.text)
        blocks = _parse_ordered_topics(response)

        return BlockDistributeResponse(blocks=blocks)

    async def distribute_questions(
        self, current_user: "User", request: QuestionDistributeRequest
    ) -> QuestionDistributeResponse:
        filters = BlockFilters(roadmap_id=request.roadmap_id)
        blocks: list[BlockRead] = await self.block_service.get_by_filters(current_user, filters)

        if not blocks:
            raise ValueError("Роадмап не содержит блоков")

        context = _build_question_distribution_context(blocks)
        response = await self.ai_client.distribute("questions", context, request.text)
        raw_distribution = _parse_distribution(response, blocks)

        return QuestionDistributeResponse(
            distribution=[
                QuestionDistributionItem(
                    block=BlockInfo.model_validate(block),
                    questions=raw_distribution.get(str(block.id), []),
                )
                for block in blocks
                if str(block.id) in raw_distribution
            ],
            undefined=raw_distribution.get("undefined", []),
        )

    async def generate_entities(self, current_user: "User", request: GenerateRequest) -> GenerateResponse:
        if request.target == GenerateTarget.blocks:
            if not request.roadmap_id:
                raise ValueError("roadmap_id обязателен для генерации блоков")
            roadmap = await self.roadmap_service.get_by_id(current_user, request.roadmap_id)
            context = f"Title: {roadmap.title}. Description: {roadmap.description or ''}."

        elif request.target == GenerateTarget.questions:
            if not request.block_id:
                raise ValueError("block_id обязателен для генерации вопросов")
            block = await self.block_service.get_by_id(current_user, request.block_id)
            roadmap = await self.roadmap_service.get_by_id(current_user, block.roadmap_id)
            context = (
                f"Roadmap: {roadmap.title}. Description: {roadmap.description or ''}."
                f"Block: {block.title}. Description: {block.description or ''}."
            )

        else:
            if not request.question_id:
                raise ValueError("question_id обязателен для генерации вопросов")
            question = await self.question_service.get_by_id(current_user, request.question_id)
            block = await self.block_service.get_by_id(current_user, question.block_id)
            roadmap = await self.roadmap_service.get_by_id(current_user, block.roadmap_id)
            context = (
                f"Roadmap: {roadmap.title}. Description: {roadmap.description or ''}."
                f"Block: {block.title}. Description: {block.description or ''}."
                f"Question: {question.question}. Description: {question.answer or ''}."
            )

        raw = await self.ai_client.generate(request.target.value, context)
        return GenerateResponse(items=_parse_generated_items(raw))
