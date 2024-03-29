from abc import ABC, abstractmethod

from src.entities.config import Config
from src.entities.model_settings import ModelSettings
from src.interfaces.storages.base import IStorage


class IStorageManager(ABC):
    @abstractmethod
    def get_storage(self, config: Config, settings: ModelSettings) -> IStorage: ...
