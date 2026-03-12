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
    QuestionConfirmItem,
    QuestionDistributeResponse,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services import BlockService, CardService, QuestionService, RoadmapService


# ── PROMPTS ───────────────────────────────────────────────────────────────────
# Each builder returns (context, content):
#   context → system instructions, sent as "role: system"
#   content → user data, sent as "role: user"


def _build_block_order_prompt(request: str, roadmap: str) -> tuple[str, str]:
    context = (
        "You are helping organize learning topics into a logical study progression. "
        "The user will send a raw list of topics in any format (numbered, bulleted, comma-separated, etc.). "
        "Extract the topics, clean them, then return ONLY a JSON array of strings in the exact same order as the input. "
        "Cleaning rules: remove numbering and bullet prefixes, remove duplicate punctuation (e.g. '??' → '?'), "
        "strip leading and trailing whitespace, capitalize the first letter of each topic. "
        "Do not reorder. No explanation. No markdown. Just the JSON array."
    )
    content = f'Roadmap: "{roadmap}"\nRaw input:\n{request}'
    return context, content


def _build_question_distribution_prompt(
    request: str,
    blocks: list["BlockRead"],
) -> tuple[str, str]:
    context = (
        "You assign learning questions to the most relevant block. "
        "The user will send a raw list of questions in any format (numbered, bulleted, inline, etc.). "
        'Extract the questions, clean them, then assign each to the most relevant block ID or to "undefined". '
        'Return ONLY a JSON object where keys are block IDs (as strings) or "undefined", '
        "values are arrays of cleaned question strings. "
        "Every extracted question must appear exactly once. "
        "No explanation. No markdown. Just the JSON object."
    )
    blocks_context = "\n".join(
        f"- {block.id}: {block.title} — {block.description or 'no description'}" for block in blocks
    )
    content = f"Blocks:\n{blocks_context}\n\nRaw input:\n{request}"
    return context, content


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

    return [LoadBlock(text=topic) for i, topic in enumerate(topics)]


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

        context, content = _build_block_order_prompt(
            request.text,
            roadmap.title + roadmap.description,
        )
        response = await self.ai_client.distribute(context, content)
        blocks = _parse_ordered_topics(response)

        return BlockDistributeResponse(loading_blocks=blocks)

    async def confirm_blocks(
        self,
        current_user: "User",
        request: BlockConfirmRequest,
    ):
        return await self.block_service.create_multiple(current_user, request.roadmap_id, request.blocks)

    async def distribute_questions(
        self,
        current_user: "User",
        roadmap_id: BaseIdType,
        raw_text: str,
    ) -> QuestionDistributeResponse:
        filters = BlockFilters(roadmap_id=roadmap_id)
        blocks: list[BlockRead] = await self.block_service.get_by_filters(
            current_user,
            filters,
        )

        if len(blocks) == 0:
            raise ValueError

        context, content = _build_question_distribution_prompt(raw_text, blocks)
        response = await self.ai_client.distribute(context, content)
        distribution = _parse_distribution(response, blocks)

        return QuestionDistributeResponse(
            blocks=[BlockInfo.model_validate(b) for b in blocks],
            distribution=distribution,
        )

    async def confirm_questions(
        self,
        current_user: "User",
        roadmap_id: BaseIdType,
        distribution: dict[BaseIdType, list[QuestionConfirmItem]],
    ):
        return await self.question_service.create_multiple(
            current_user,
            roadmap_id,
            distribution,
        )
