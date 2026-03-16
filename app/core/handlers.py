import logging
from functools import wraps

from asyncpg import ForeignKeyViolationError
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.custom_exceptions import (
    EntityConflictError,
    EntityNotFoundError,
    PersistenceError,
    RepositoryError,
    ServiceError,
)

logger = logging.getLogger(__name__)


def router_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except EntityNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        except EntityConflictError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        except (PersistenceError, ServiceError) as e:
            logger.error(f"Internal error in {func.__name__}: {e!s}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e!s}", exc_info=True)
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
        except (RepositoryError, ValueError):
            raise
        except Exception as e:
            logger.error(f"Service error in {func.__name__}: {e!s}", exc_info=True)
            raise ServiceError(str(e)) from e

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RepositoryError, ValueError):
            raise
        except Exception as e:
            logger.error(f"Service error in {func.__name__}: {e!s}", exc_info=True)
            raise ServiceError(str(e)) from e

    return async_wrapper if func.__code__.co_flags & 0x80 else sync_wrapper


def repository_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except EntityNotFoundError:
            raise
        except IntegrityError as e:
            if isinstance(e.orig, ForeignKeyViolationError):
                logger.error(f"ForeignKey violation in {func.__name__}: {e!s}", exc_info=True)
                raise EntityConflictError("Foreign key constraint violated") from e
            logger.error(f"IntegrityError in {func.__name__}: {e!s}", exc_info=True)
            raise EntityConflictError(str(e)) from e
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {e!s}", exc_info=True)
            raise PersistenceError(str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e!s}", exc_info=True)
            raise PersistenceError(str(e)) from e

    return wrapper
