import json
from collections import defaultdict
from typing import TYPE_CHECKING

from app.clients.ai import AIClient
from app.core.custom_types import BaseIdType
from app.schemas.block import BlockFilters, BlockRead
from app.schemas.load import (
    BlockConfirmRequest,
    BlockDistributeRequest,
    BlockDistributeResponse,
    BlockInfo,
    LoadBlock,
    QuestionDistributeResponse,
)
from app.schemas.question import QuestionRead

if TYPE_CHECKING:
    from app.models import User
    from app.services import BlockService, CardService, QuestionService, RoadmapService


def _build_question_distribution_context(blocks: list["BlockRead"]) -> str:
    context = "\n".join(f"- {block.id}: {block.title} — {block.description or 'no description'}" for block in blocks)
    return context


# ── PARSERS ───────────────────────────────────────────────────────────────────


def _parse_ordered_topics(raw: str) -> list[LoadBlock]:
    """
    Expects a JSON array of strings from the LLM.
    Falls back to newline-splitting if JSON is malformed.
    """
    try:
        data = json.loads(raw.strip())
        if not isinstance(data, list):
            raise ValueError("expected a list")
        topics = [str(item).strip() for item in data if str(item).strip()]
    except (json.JSONDecodeError, ValueError):
        topics = [line.strip() for line in raw.splitlines() if line.strip()]

    return [LoadBlock(title=topic) for i, topic in enumerate(topics)]


def _parse_distribution(raw: str, blocks: list["BlockRead"]) -> dict[str, list[str]]:
    """
    Expects a JSON object from the LLM:
        { block_id | "undefined": [question_str, ...] }

    Guarantees:
    - Only valid block IDs or "undefined" as keys (hallucinated IDs → "undefined")
    - No duplicate questions across buckets
    - Falls back to empty dict on total parse failure (user distributes manually)
    """
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


# ── SERVICE ───────────────────────────────────────────────────────────────────


class LoadService:
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

    async def distribute_blocks(
        self,
        current_user: "User",
        request: BlockDistributeRequest,
    ) -> BlockDistributeResponse:
        roadmap = await self.roadmap_service.get_by_id(
            current_user,
            request.roadmap_id,
        )

        context = f"Roadmap title: {roadmap.title}. Roadmap Description: {roadmap.description}"

        response = await self.ai_client.distribute("blocks", context, request.text)
        blocks = _parse_ordered_topics(response)

        return BlockDistributeResponse(blocks=blocks)

    async def confirm_blocks(
        self,
        current_user: "User",
        request: BlockConfirmRequest,
    ):
        return await self.block_service.create_multiple(current_user, request)

    async def distribute_questions(
        self,
        current_user: "User",
        roadmap_id: BaseIdType,
        text: str,
    ) -> QuestionDistributeResponse:
        filters = BlockFilters(roadmap_id=roadmap_id)
        blocks: list[BlockRead] = await self.block_service.get_by_filters(
            current_user,
            filters,
        )

        if len(blocks) == 0:
            raise ValueError

        context = _build_question_distribution_context(blocks)
        response = await self.ai_client.distribute("questions", context, text)
        distribution = _parse_distribution(response, blocks)

        return QuestionDistributeResponse(
            blocks=[BlockInfo.model_validate(b) for b in blocks],
            distribution=distribution,
        )

    async def confirm_questions(
        self,
        current_user: "User",
        roadmap_id: BaseIdType,
        distribution: dict[BaseIdType, list[QuestionRead]],
    ):
        return await self.question_service.create_multiple(
            current_user,
            roadmap_id,
            distribution,
        )
