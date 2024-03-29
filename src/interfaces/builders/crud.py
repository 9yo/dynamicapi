from abc import ABC, abstractmethod
from typing import Type

from fastapi import APIRouter

from src.entities.config import Config
from src.interfaces.builders.endpoint import IEndpointBuilder
from src.interfaces.builders.model import IModelBuilder
from src.interfaces.storages import IStorageManager


class ICRUDBuilder(ABC):
    def __init__(
        self,
        config: Config,
        storage_manager: IStorageManager,
        endpoint_builder: Type[IEndpointBuilder],
        model_builder: Type[IModelBuilder],
    ): ...

    @property
    @abstractmethod
    def router(self) -> APIRouter: ...
