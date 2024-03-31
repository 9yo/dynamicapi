from abc import ABC, abstractmethod

from fastapi import APIRouter

from dyapi.entities.config import Config
from dyapi.interfaces.builders.crud import ICRUDBuilder
from dyapi.interfaces.storages import IStorageManager


class IAPIBuilder(ABC):
    @abstractmethod
    def __init__(
        self,
        configs: list[Config],
        storage: IStorageManager,
        crud_builder: ICRUDBuilder,
    ): ...

    @property
    @abstractmethod
    def router(self) -> list[APIRouter]: ...
