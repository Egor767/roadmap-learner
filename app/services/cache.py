# from cache.asyncio import Redis
#
# from app.core.config import settings
# from app.core.loggers import cache_service_logger
#
#
# class CacheService:
#     def __init__(self, cache: "Redis"):
#         self.cache = cache
#
#     def get_cache_key(self, *args: str) -> str:
#         cfg = settings.cache
#         return ":".join((cfg.prefix, cfg.version, *args))
#
#     async def ping(self) -> bool:
#         try:
#             return await self.cache.ping()
#         except ConnectionError:
#             cache_service_logger.warning("Redis connection error")
#             return False
#
#     async def get(self, key):
#         if await self.ping():
#             return self.cache.get(key)
#         return None
#
#     async def set(self, key, value, ttl=settings.cache.default_ttl):
#         if await self.ping():
#             await self.cache.set(key, value, ex=ttl)
#         return None
#
#     async def delete(self, *keys):
#         if await self.ping():
#             await self.cache.delete(*keys)
#         return None
