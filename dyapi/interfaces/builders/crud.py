from abc import ABC, abstractmethod
from functools import cached_property
from typing import Type

from dyapi.entities.config import Config
from dyapi.interfaces.builders.endpoint import IEndpointBuilder
from dyapi.interfaces.builders.model import IModelBuilder
from dyapi.interfaces.storages import IStorageManager
from fastapi import APIRouter


class ICRUDBuilder(ABC):
    def __init__(
        self,
        config: Config,
        storage_manager: IStorageManager,
        endpoint_builder: Type[IEndpointBuilder],
        model_builder: Type[IModelBuilder],
    ): ...

    @cached_property
    @abstractmethod
    def config(self) -> Config: ...

    @cached_property
    @abstractmethod
    def router(self) -> APIRouter: ...

    @cached_property
    @abstractmethod
    def model(self) -> IModelBuilder: ...

    @cached_property
    @abstractmethod
    def endpoint(self) -> IEndpointBuilder: ...
