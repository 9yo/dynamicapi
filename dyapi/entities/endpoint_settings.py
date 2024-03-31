from dyapi.entities.config import Config
from dyapi.entities.model_settings import ModelSettings
from dyapi.interfaces.storages import IStorage
from pydantic import BaseModel


class EndpointSettings(BaseModel, arbitrary_types_allowed=True):
    model: ModelSettings
    storage: IStorage
    config: Config
