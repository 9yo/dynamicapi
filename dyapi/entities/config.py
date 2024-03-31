from typing import Any, Literal, Type

from pydantic import BaseModel


class ConfigField(BaseModel):
    name: str
    type: Type[Any]
    location: Literal["path", "body"] = "body"


class Config(BaseModel):
    name: str
    api_tags: list[str]
    fields: list[ConfigField]

    @property
    def path_fields(self) -> list[ConfigField]:
        return [field for field in self.fields if field.location == "path"]

    @property
    def body_fields(self) -> list[ConfigField]:
        return [field for field in self.fields if field.location == "body"]
