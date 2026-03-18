import contextlib

import httpx

from app.schemas.ai import ConceptContext, EvaluateAnswerResponse


class AIClient:
    def __init__(self) -> None:
        self.base_url = "http://127.0.0.1:9090/api/openai"
        self.timeout = 60

    async def health_check(self) -> bool:
        """Check whether the AI service is reachable and healthy."""
        async with httpx.AsyncClient(timeout=5) as client:
            with contextlib.suppress(httpx.ConnectError, httpx.TimeoutException):
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        return False

    async def distribute(self, category: str, context: str, content: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/distribute",
                json={"category": category, "context": context, "content": content},
            )
            response.raise_for_status()
            return response.json()["content"]

    async def chat(self, context: str, content: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat",
                json={"context": context, "content": content},
            )
            response.raise_for_status()
            return response.json()["response"]

    async def generate(self, target: str, context: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json={"target": target, "context": context},
            )
            response.raise_for_status()
            return response.json()["content"]

    async def evaluate_answer(
        self, question: str, correct_answer: str, answer: str, hint: bool, concepts: list[ConceptContext]
    ) -> EvaluateAnswerResponse:
        """Send an answer to the AI service for evaluation and return the result."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/evaluate",
                json={
                    "question": question,
                    "correct_answer": correct_answer,
                    "answer": answer,
                    "hint": hint,
                    "cards": [c.model_dump() for c in concepts],
                },
            )
            response.raise_for_status()
            return EvaluateAnswerResponse.model_validate(response.json())
