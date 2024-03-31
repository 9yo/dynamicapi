from pydantic import BaseModel

from dyapi.entities.config import Config
from dyapi.entities.model_settings import ModelSettings
from dyapi.interfaces.storages import IStorage


class EndpointSettings(BaseModel, arbitrary_types_allowed=True):
    model: ModelSettings
    storage: IStorage
    config: Config
