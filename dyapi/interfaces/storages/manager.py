from abc import ABC, abstractmethod

from dyapi.entities.config import Config
from dyapi.entities.model_settings import ModelSettings
from dyapi.interfaces.storages.base import IStorage


class IStorageManager(ABC):
    @abstractmethod
    def get_storage(self, config: Config, settings: ModelSettings) -> IStorage: ...
