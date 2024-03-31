from abc import ABC, abstractmethod
from functools import cached_property

from dyapi.entities.config import Config
from dyapi.interfaces.builders.crud import ICRUDBuilder
from dyapi.interfaces.builders.model import IModelBuilder
from dyapi.interfaces.storages import IStorageManager
from fastapi import APIRouter


class IAPIBuilder(ABC):
    @abstractmethod
    def __init__(
        self,
        configs: list[Config],
        storage: IStorageManager,
        crud_builder: ICRUDBuilder,
    ): ...

    @cached_property
    @abstractmethod
    def router(self) -> APIRouter: ...

    @cached_property
    @abstractmethod
    def models(self) -> dict[str, IModelBuilder]: ...

    @cached_property
    @abstractmethod
    def cruds(self) -> dict[str, ICRUDBuilder]: ...
