from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.clients import AIClient
from app.services import (
    AIService,
    AnswerService,
    ConceptService,
    ModuleService,
    QuestionService,
    RoadmapService,
    SessionService,
    UserService,
)

from .cache import get_cache
from .clients import get_ai_client
from .repositories import (
    get_concept_repository,
    get_module_repository,
    get_question_repository,
    get_roadmap_repository,
    get_session_repository,
    get_user_repository,
    get_verify_repository,
)

if TYPE_CHECKING:
    from cache import CacheHelper

    from app.repositories import (
        ConceptRepository,
        ModuleRepository,
        QuestionRepository,
        RoadmapRepository,
        SessionRepository,
        UserRepository,
        VerifyRepository,
    )


def get_user_service(
    user_repo: Annotated["UserRepository", Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repo)


def get_roadmap_service(
    repo: Annotated["RoadmapRepository", Depends(get_roadmap_repository)],
    verify: Annotated["VerifyRepository", Depends(get_verify_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> RoadmapService:
    return RoadmapService(repo, verify, cache)


def get_module_service(
    repo: Annotated["ModuleRepository", Depends(get_module_repository)],
    verify: Annotated["VerifyRepository", Depends(get_verify_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> ModuleService:
    return ModuleService(repo, verify, cache)


def get_concept_service(
    repo: Annotated["ConceptRepository", Depends(get_concept_repository)],
    verify: Annotated["VerifyRepository", Depends(get_verify_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> ConceptService:
    return ConceptService(repo, verify, cache)


def get_question_service(
    repo: Annotated["QuestionRepository", Depends(get_question_repository)],
    verify: Annotated["VerifyRepository", Depends(get_verify_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> QuestionService:
    return QuestionService(repo, verify, cache)


def get_ai_service(
    ai_client: Annotated["AIClient", Depends(get_ai_client)],
    roadmap_repo: Annotated["RoadmapRepository", Depends(get_roadmap_repository)],
    module_repo: Annotated["ModuleRepository", Depends(get_module_repository)],
    question_repo: Annotated["QuestionRepository", Depends(get_question_repository)],
) -> AIService:
    return AIService(ai_client, roadmap_repo, module_repo, question_repo)


def get_answer_service(
    repo: Annotated["SessionRepository", Depends(get_session_repository)],
    question_repo: Annotated["QuestionRepository", Depends(get_question_repository)],
    concept_repo: Annotated["ConceptRepository", Depends(get_concept_repository)],
    ai_client: Annotated["AIClient", Depends(get_ai_client)],
) -> AnswerService:
    return AnswerService(repo, question_repo, concept_repo, ai_client)


def get_session_service(
    repo: Annotated["SessionRepository", Depends(get_session_repository)],
    verify: Annotated["VerifyRepository", Depends(get_verify_repository)],
    module_repo: Annotated["ModuleRepository", Depends(get_module_repository)],
    question_repo: Annotated["QuestionRepository", Depends(get_question_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> SessionService:
    return SessionService(repo, verify, module_repo, question_repo, cache)
