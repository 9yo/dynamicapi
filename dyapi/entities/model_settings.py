from typing import Type

from pydantic import BaseModel


class ModelSettings(BaseModel, arbitrary_types_allowed=True):
    path: Type[BaseModel]
    optional_path: Type[BaseModel]
    body: Type[BaseModel]
    entity: Type[BaseModel]
