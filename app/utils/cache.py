import logging

from app.core.config import settings

logger = logging.getLogger("CACHE-LOGGER")


def get_cache_key(*args: str) -> str:
    cfg = settings.cache
    return ":".join((cfg.prefix, cfg.version, *args))


def is_single_parent_filter(filters: dict, parent: str) -> bool:
    return set(filters.keys()) == {parent}


# def cached(
#     redis: any,
#     ttl: int = 300,
#     namespace: str = "cache",
#     key_maker: Optional[Callable] = None,
#     cache_empty: bool = True,
# ):
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         async def wrapper(self, *args, **kwargs) -> Any:
#             # Автоматический ключ
#             func_key = f"{func.__module__}.{func.__name__}"
#             key_args = hash((args, frozenset(kwargs.items())))
#             cache_key = f"{namespace}:{func_key}:{key_args}"
#
#             cached_data = await redis.get(cache_key)
#             if cached_data:
#                 logger.info("Cache HIT: %s", cache_key)
#                 return json.loads(cached_data)
#
#             result = await func(self, *args, **kwargs)
#
#             if cache_empty or result:
#                 await redis.set(cache_key, json.dumps(result), ex=ttl)
#                 logger.info("Cache SET: %s", cache_key)
#
#             return result
#
#         return wrapper
#
#     return decorator
