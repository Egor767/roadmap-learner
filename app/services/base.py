from abc import ABC

from app.repositories import BaseRepository


class BaseService(ABC):
    def __init__(self, repository: BaseRepository):
        self.repository = repository
