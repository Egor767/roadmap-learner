import logging

from app.core.config import settings

logger = logging.getLogger("CACHE-LOGGER")


def get_cache_key(*args: str) -> str:
    cfg = settings.cache
    return ":".join((cfg.prefix, cfg.version, *args))


def is_single_parent_filter(filters: dict, parent: str) -> bool:
    return set(filters.keys()) == {parent}
