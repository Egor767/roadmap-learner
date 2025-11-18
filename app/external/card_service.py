import os
from typing import Optional

import aiohttp

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080/api/v1.0")


async def get_card_from_service(
    user_id: str,
    card_id: str,
) -> Optional[dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/cards/{card_id}",
                params={"user_id": user_id},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None

    except Exception:
        return
