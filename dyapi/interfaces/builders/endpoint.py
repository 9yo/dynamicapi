from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Callable

from dyapi.interfaces.builders.model import IModelBuilder
from dyapi.interfaces.storages import IStorage


class IEndpointBuilder(ABC):
    @abstractmethod
    def __init__(self, model: IModelBuilder, storage: IStorage): ...

    @cached_property
    @abstractmethod
    def create(self) -> Callable[[Any], Any]:
        """
        Returns FastAPI endpoint for creating a new entity.
        :return:
        """
        pass

    @cached_property
    @abstractmethod
    def get(self) -> Callable[[Any], Any]:
        """
        Returns FastAPI endpoint for getting an entity.
        :return:
        """
        ...

    @cached_property
    @abstractmethod
    def update(self) -> Callable[[Any], Any]:
        """
        Returns FastAPI endpoint for updating an entity.
        :return:
        """
        ...

    @cached_property
    @abstractmethod
    def delete(self) -> Callable[[Any], Any]:
        """
        Returns FastAPI endpoint for deleting an entity.
        :return:
        """
        ...

    @cached_property
    @abstractmethod
    def list(self) -> Callable[[Any], Any]:
        """
        Returns FastAPI endpoint for listing entities.
        :return:
        """
        ...
