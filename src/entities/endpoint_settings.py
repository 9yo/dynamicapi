from pydantic import BaseModel

from src.entities.config import Config
from src.entities.model_settings import ModelSettings
from src.interfaces.storages import IStorage


class EndpointSettings(BaseModel, arbitrary_types_allowed=True):
    model: ModelSettings
    storage: IStorage
    config: Config
