import time

from redis.asyncio import Redis
from redis.exceptions import RedisError
from redis.typing import KeyT

from app.core.config import settings


class CacheHelper:
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
        return time.time() >= self._disabled_until

    def _trip(self):
        self._disabled_until = time.time() + self._cooldown

    async def get(self, key: KeyT):
        if not self._available():
            return None
        try:
            return await self.redis.get(key)
        except RedisError:
            self._trip()
            return None

    async def set(self, key: KeyT, value: KeyT, ttl: int = settings.cache.default_ttl):
        if not self._available():
            return
        try:
            await self.redis.set(key, value, ex=ttl)
        except RedisError:
            self._trip()

    async def delete(self, *keys: KeyT):
        if not self._available():
            return
        try:
            await self.redis.delete(*keys)
        except RedisError:
            self._trip()

    async def close(self):
        await self.redis.close()
