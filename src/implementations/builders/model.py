from typing import Type

from pydantic import BaseModel, create_model

from src.entities.config import Config, ConfigField
from src.interfaces.builders.model import IModelBuilder


class ModelBuilder(IModelBuilder):
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

    @classmethod
    def build_path(cls, config: Config) -> Type[BaseModel]:
        return cls.create_model(f"PathModel{config.name}", config.path_fields)

    @classmethod
    def build_optional_path(cls, config: Config) -> Type[BaseModel]:
        return cls.create_model(
            f"OptionalPathModel{config.name}", config.path_fields, optional=True
        )

    @classmethod
    def build_body(cls, config: Config) -> Type[BaseModel]:
        return cls.create_model(f"BodyModel{config.name}", config.body_fields)

    @classmethod
    def build_entity(cls, config: Config) -> Type[BaseModel]:
        return cls.create_model(f"EntityModel{config.name}", config.fields)
