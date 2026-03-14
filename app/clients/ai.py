import httpx


class AIClient:
    def __init__(self) -> None:
        self.base_url = "http://127.0.0.1:9090/api/openai"
        self.timeout = 30

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
