import logging

import httpx

logger = logging.getLogger("Request-Logger")


async def get_block_by_id(
    token: str,
    block_id: str,
) -> dict:
    url = f"http://localhost:8080/api/v1/blocks/{block_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
        )
        return response.json()


async def get_blocks_by_filters(
    token: str,
    filters: dict,
) -> list[dict]:
    url = "http://localhost:8080/api/v1/blocks/filters"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    params = filters.copy()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
            params=params,
        )
        return response.json()


async def get_questions_by_filters(
    token: str,
    filters: dict,
) -> list[dict]:
    url = "http://localhost:8080/api/v1/questions/filters"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    params = filters.copy()
    params.pop("roadmap_id")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
            params=params,
        )

        return response.json()
