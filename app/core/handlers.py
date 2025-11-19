import logging
from functools import wraps

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def router_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    return wrapper


def service_handler(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                f"Service error in {func.__name__}: {str(e)}",
                exc_info=True,
            )
            raise ValueError(f"Service operation failed: {str(e)}")

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                f"Service error in {func.__name__}: {str(e)}",
                exc_info=True,
            )
            raise ValueError(f"Service operation failed: {str(e)}")

    return async_wrapper if func.__code__.co_flags & 0x80 else sync_wrapper


def repository_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(
                f"Database error in {func.__name__}: {str(e)}",
                exc_info=True,
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in {func.__name__}: {str(e)}",
                exc_info=True,
            )
            raise

    return wrapper
