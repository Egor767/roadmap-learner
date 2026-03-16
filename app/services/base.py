from abc import ABC

from app.repositories import BaseEntityRepository


class BaseService(ABC):
    def __init__(self, repository: BaseEntityRepository):
        self.repository = repository
