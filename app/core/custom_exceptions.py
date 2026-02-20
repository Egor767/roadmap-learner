from app.core.custom_types import BaseIdType
from app.models import Base


class RepositoryError(Exception):
    pass


class EntityNotFoundError(RepositoryError):
    def __init__(self, entity: type[Base], entity_id: BaseIdType):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} with id={entity_id} not found")


class EntityConflictError(RepositoryError):
    def __init__(self, message: str = "Entity conflict occurred"):
        super().__init__(message)


class PersistenceError(RepositoryError):
    def __init__(self, message: str = "Persistence layer error"):
        super().__init__(message)
