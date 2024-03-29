from abc import ABC, abstractmethod

from fastapi import APIRouter

from src.entities.config import Config
from src.interfaces.builders.crud import ICRUDBuilder
from src.interfaces.storages import IStorageManager


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
