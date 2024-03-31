from functools import cached_property
from typing import Type

from dyapi.entities.config import Config, ConfigField
from dyapi.interfaces.builders.model import IModelBuilder
from pydantic import BaseModel, create_model


class ModelBuilder(IModelBuilder):
    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    def create_model(
        name: str,
        fields: list[ConfigField],
        optional: bool = False,
    ) -> Type[BaseModel]:
        return create_model(  # type: ignore
            name,
            **{
                field.name: (field.type | None, None) if optional else (field.type, ...)
                for field in fields
            },
        )

    @cached_property
    def path(self) -> Type[BaseModel]:
        return self.create_model(
            f"PathModel{self.config.name}", self.config.path_fields
        )

    @cached_property
    def query(self) -> Type[BaseModel]:
        return self.create_model(
            f"QueryModel{self.config.name}",
            self.config.path_fields,
            optional=True,
        )

    @cached_property
    def body(self) -> Type[BaseModel]:
        return self.create_model(
            f"BodyModel{self.config.name}", self.config.body_fields
        )

    @cached_property
    def entity(self) -> Type[BaseModel]:
        return self.create_model(f"EntityModel{self.config.name}", self.config.fields)
