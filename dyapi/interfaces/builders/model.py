from abc import ABC, abstractmethod
from functools import cached_property
from typing import Type

from dyapi.entities.config import Config
from pydantic import BaseModel


class IModelBuilder(ABC):
    @abstractmethod
    def __init__(self, config: Config): ...

    @cached_property
    @abstractmethod
    def path(self) -> Type[BaseModel]:
        """
        Generates a Pydantic model for the path parameters of the endpoint.
        """
        ...

    @cached_property
    @abstractmethod
    def query(self) -> Type[BaseModel]:
        """
        Generates a Pydantic model for the optional path parameters of the endpoint.
        """
        ...

    @cached_property
    @abstractmethod
    def body(self) -> Type[BaseModel]:
        """
        Generates a Pydantic model for the body of the endpoint.
        """
        ...

    @cached_property
    @abstractmethod
    def entity(self) -> Type[BaseModel]:
        """
        Generates a Pydantic model for the entity of the endpoint.
        """
        ...
