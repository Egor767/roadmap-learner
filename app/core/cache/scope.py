from itertools import starmap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .helper import CacheHelper


class CacheScope:
    """Scoped cache for a specific entity namespace and user"""

    def __init__(self, cache: "CacheHelper", namespace: str, user_id: str):
        self._cache = cache
        self._namespace = namespace
        self._user_id = user_id

    def _build(self, *parts: str) -> str:
        """Build a full cache key from parts"""
        return ":".join([self._namespace, "user", self._user_id, *parts])

    async def get(self, *parts: str):
        """Get cached value by key parts"""
        return await self._cache.get(self._build(*parts))

    async def put(self, data: str, *parts: str) -> None:
        """Store value in cache by key parts"""
        await self._cache.set(self._build(*parts), data)

    async def drop(self, *keys: tuple[str, ...]) -> None:
        """Delete multiple cache entries by key part tuples"""
        built = list(starmap(self._build, keys))
        await self._cache.delete(*built)
