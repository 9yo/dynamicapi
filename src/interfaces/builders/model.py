from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

from src.entities.config import Config


class IModelBuilder(ABC):
    @classmethod
    @abstractmethod
    def build_path(cls, config: Config) -> Type[BaseModel]: ...

    @classmethod
    @abstractmethod
    def build_optional_path(cls, config: Config) -> Type[BaseModel]: ...

    @classmethod
    @abstractmethod
    def build_body(cls, config: Config) -> Type[BaseModel]: ...

    @classmethod
    @abstractmethod
    def build_entity(cls, config: Config) -> Type[BaseModel]: ...
