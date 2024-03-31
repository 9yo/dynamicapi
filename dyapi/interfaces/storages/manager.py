from abc import ABC, abstractmethod

from dyapi.entities.config import Config
from dyapi.interfaces.storages.base import IStorage


class IStorageManager(ABC):
    @abstractmethod
    def storage(self, config: Config) -> IStorage: ...
