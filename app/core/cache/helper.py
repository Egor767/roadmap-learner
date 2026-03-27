import time

from redis.asyncio import Redis
from redis.exceptions import RedisError
from redis.typing import KeyT

from app.core.config import settings

from .scope import CacheScope


class CacheHelper:
    """Redis cache helper with circuit breaker"""

    def __init__(self, url: str):
        self.redis = Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
            retry_on_timeout=False,
        )
        self._disabled_until = 0
        self._cooldown = 5

    def _available(self) -> bool:
        """Check if cache is currently available"""
        return time.time() >= self._disabled_until

    def _trip(self):
        """Disable cache for cooldown period"""
        self._disabled_until = time.time() + self._cooldown

    def scope(self, namespace: str, user_id: str) -> CacheScope:
        """Return a scoped cache for the given namespace and user"""
        return CacheScope(self, namespace, user_id)

    async def scan(self, pattern: str) -> None:
        """Delete all keys matching pattern"""
        if not self._available():
            return
        try:
            keys = [key async for key in self.redis.scan_iter(pattern)]
            if keys:
                await self.redis.delete(*keys)
        except RedisError:
            self._trip()

    async def get(self, key: KeyT):
        """Get value from cache by key"""
        if not self._available():
            return None
        try:
            return await self.redis.get(key)
        except RedisError:
            self._trip()
            return None

    async def set(self, key: KeyT, value: KeyT, ttl: int = settings.cache.default_ttl):
        """Set value in cache with ttl"""
        if not self._available():
            return
        try:
            await self.redis.set(key, value, ex=ttl)
        except RedisError:
            self._trip()

    async def delete(self, *keys: KeyT):
        """Delete one or more keys from cache"""
        if not self._available():
            return
        try:
            await self.redis.delete(*keys)
        except RedisError:
            self._trip()

    async def close(self):
        """Close Redis connection"""
        await self.redis.close()
