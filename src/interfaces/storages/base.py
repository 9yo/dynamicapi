from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

from src.entities.pagination import PaginationEntity

__all__ = ("IStorage",)


class IStorage(ABC):
    @abstractmethod
    async def get(
        self, filter_: BaseModel, response_model: Type[BaseModel]
    ) -> BaseModel: ...

    @abstractmethod
    async def create(self, entity: BaseModel) -> BaseModel: ...

    @abstractmethod
    async def update(
        self, filter_: BaseModel, entity: BaseModel, response_model: Type[BaseModel]
    ) -> BaseModel: ...

    @abstractmethod
    async def delete(self, filter_: BaseModel) -> bool: ...

    @abstractmethod
    async def list(
        self,
        filter_: BaseModel,
        pagination: PaginationEntity,
        response_model: Type[BaseModel],
    ) -> list[BaseModel]: ...
