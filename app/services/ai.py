import json
from collections import defaultdict
from typing import TYPE_CHECKING

from app.clients.ai import AIClient
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
    GenerateTarget,
    LoadModule,
    ModuleDistributeRequest,
    ModuleDistributeResponse,
    ModuleInfo,
    QuestionDistributeRequest,
    QuestionDistributeResponse,
    QuestionDistributionItem,
)
from app.schemas.module import ModuleFilters, ModuleRead
from app.schemas.question import QuestionRead
from app.schemas.roadmap import RoadmapRead
from app.utils.mappers.orm_to_schema import orm_list_to_schemas, orm_to_schema

if TYPE_CHECKING:
    from app.models import User
    from app.repositories.module import ModuleRepository
    from app.repositories.question import QuestionRepository
    from app.repositories.roadmap import RoadmapRepository


def _build_question_distribution_context(modules: list["ModuleRead"]) -> str:
    """Build context string for AI question distribution prompt."""
    return "\n".join(f"- {module.id}: {module.title} — {module.description or 'no description'}" for module in modules)


def _parse_ordered_topics(raw: str) -> list[LoadModule]:
    """Parse AI response into ordered list of module topics."""
    try:
        data = json.loads(raw.strip())
        if not isinstance(data, list):
            raise ValueError("expected a list")
        topics = [str(item).strip() for item in data if str(item).strip()]
    except (json.JSONDecodeError, ValueError):
        topics = [line.strip() for line in raw.splitlines() if line.strip()]

    return [LoadModule(title=topic) for topic in topics]


def _parse_distribution(raw: str, modules: list["ModuleRead"]) -> dict[str, list[str]]:
    """Parse AI response into question distribution mapping by module id."""
    valid_ids = {str(m.id) for m in modules}

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


def _build_module_context(roadmap: "RoadmapRead", module: "ModuleRead") -> str:
    """Build context string from roadmap and module data."""
    return (
        f"Roadmap: {roadmap.title}. Description: {roadmap.description or ''}."
        f"Module: {module.title}. Description: {module.description or ''}."
    )


def _build_question_context(roadmap: "RoadmapRead", module: "ModuleRead", question: "QuestionRead") -> str:
    """Build context string from roadmap, module and question data."""
    return (
        f"Roadmap: {roadmap.title}. Description: {roadmap.description or ''}."
        f"Module: {module.title}. Description: {module.description or ''}."
        f"Question: {question.question}. Description: {question.answer or ''}."
    )


class AIService:
    """Service for AI-powered operations: chat, distribution, and generation."""

    def __init__(
        self,
        ai_client: AIClient,
        roadmap_repo: "RoadmapRepository",
        module_repo: "ModuleRepository",
        question_repo: "QuestionRepository",
    ):
        self.ai_client = ai_client
        self.roadmap_repo = roadmap_repo
        self.module_repo = module_repo
        self.question_repo = question_repo

    async def chat(self, current_user: "User", request: ChatRequest) -> ChatResponse:
        """Send a message to AI with optional context."""
        response = await self.ai_client.chat(request.context, request.content)
        return ChatResponse(response=response)

    async def distribute_modules(
        self, current_user: "User", request: ModuleDistributeRequest
    ) -> ModuleDistributeResponse:
        """Ask AI to distribute raw text into ordered module topics."""
        roadmap_orm = await self.roadmap_repo.get_by_id(request.roadmap_id)
        roadmap = orm_to_schema(RoadmapRead, roadmap_orm)
        context = _build_roadmap_context(roadmap)

        response = await self.ai_client.distribute("blocks", context, request.text)
        modules = _parse_ordered_topics(response)

        return ModuleDistributeResponse(modules=modules)

    async def distribute_questions(
        self, current_user: "User", request: QuestionDistributeRequest
    ) -> QuestionDistributeResponse:
        """Ask AI to distribute raw text questions across existing modules."""
        filters = ModuleFilters(roadmap_id=request.roadmap_id)
        filters_dict = filters.model_dump(exclude_none=True, exclude_unset=True)

        modules_orm = await self.module_repo.get_by_filters(filters_dict, current_user.id)
        modules = orm_list_to_schemas(ModuleRead, modules_orm)

        if not modules:
            raise ValueError("Роадмап не содержит модулей")

        context = _build_question_distribution_context(modules)
        response = await self.ai_client.distribute("questions", context, request.text)
        raw_distribution = _parse_distribution(response, modules)

        distribution = [
            QuestionDistributionItem(
                module=ModuleInfo.model_validate(module),
                questions=raw_distribution.get(str(module.id), []),
            )
            for module in modules
            if str(module.id) in raw_distribution
        ]

        return QuestionDistributeResponse(
            distribution=distribution,
            undefined=raw_distribution.get("undefined", []),
        )

    async def generate_entities(self, current_user: "User", request: GenerateRequest) -> GenerateResponse:
        """Generate entities (modules, questions, or concepts) using AI for a given target."""
        context = await self._build_generate_context(current_user, request)
        raw = await self.ai_client.generate(request.target.value, context)
        items = _parse_generated_items(raw)
        return GenerateResponse(items=items)

    async def _build_generate_context(self, current_user: "User", request: GenerateRequest) -> str:
        """Build AI generation context based on target type."""
        if request.target == GenerateTarget.modules:
            if not request.roadmap_id:
                raise ValueError("roadmap_id обязателен для генерации модулей")

            roadmap_orm = await self.roadmap_repo.get_by_id(request.roadmap_id)
            roadmap = orm_to_schema(RoadmapRead, roadmap_orm)

            return _build_roadmap_context(roadmap)

        if request.target == GenerateTarget.questions:
            if not request.module_id:
                raise ValueError("module_id обязателен для генерации вопросов")

            module_orm = await self.module_repo.get_by_id(request.module_id)
            module = orm_to_schema(ModuleRead, module_orm)

            roadmap_orm = await self.roadmap_repo.get_by_id(module.roadmap_id)
            roadmap = orm_to_schema(RoadmapRead, roadmap_orm)

            return _build_module_context(roadmap, module)

        if not request.question_id:
            raise ValueError("question_id обязателен для генерации концептов")

        question_orm = await self.question_repo.get_by_id(request.question_id)
        question = orm_to_schema(QuestionRead, question_orm)

        module_orm = await self.module_repo.get_by_id(question.module_id)
        module = orm_to_schema(ModuleRead, module_orm)

        roadmap_orm = await self.roadmap_repo.get_by_id(module.roadmap_id)
        roadmap = orm_to_schema(RoadmapRead, roadmap_orm)

        return _build_question_context(roadmap, module, question)
