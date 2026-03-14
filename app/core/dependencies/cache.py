from fastapi import Request

from app.core.cache import CacheHelper


def get_cache(request: Request) -> CacheHelper:
    return request.app.state.cache
