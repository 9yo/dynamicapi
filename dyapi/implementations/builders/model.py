from functools import cached_property
from typing import Type

from dyapi.entities.config import Config, ConfigField
from dyapi.interfaces.builders.model import IModelBuilder
from pydantic import BaseModel, create_model
from sqlalchemy.orm import DeclarativeBase


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


class SQLAlchemyModelSchemaBuilder:
    def __init__(
        self,
        model: Type[DeclarativeBase],
    ):
        self.model = model

    @cached_property
    def base(self) -> Type[BaseModel]:
        return create_model(  # type: ignore
            self.model.__name__ + "Schema",
            **{
                key: (
                    (value.type.python_type | None, None)
                    if value.nullable
                    else (value.type.python_type, ...)
                )
                for key, value in self.model.__table__.columns.items()
            },
        )

    @cached_property
    def path(self) -> Type[BaseModel]:
        return create_model(  # type: ignore
            self.model.__name__ + "SchemaIdentifier",
            **{
                key: (
                    (value.type.python_type | None, None)
                    if value.nullable
                    else (value.type.python_type, ...)
                )
                for key, value in self.model.__table__.columns.items()
                if value.primary_key
            },
        )

    @cached_property
    def filter(self) -> Type[BaseModel]:
        return create_model(  # type: ignore
            self.model.__name__ + "FilterSchemaIdentifier",
            **{
                key: (value.type.python_type | None, None)
                for key, value in self.model.__table__.columns.items()
            },
        )

    @cached_property
    def update(self) -> Type[BaseModel]:
        return create_model(  # type: ignore
            self.model.__name__ + "UpdateSchema",
            **{
                key: (value.type.python_type | None, None)
                for key, value in self.model.__table__.columns.items()
                if not value.primary_key
            },
        )
