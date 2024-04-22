from functools import cached_property
from typing import Dict, Type

from dyapi.entities.config import Config
from dyapi.implementations.builders.crud import CRUDBuilder, SQLAlchemyCRUDBuilder
from dyapi.implementations.builders.endpoint import EndpointBuilder
from dyapi.implementations.builders.model import (
    ModelBuilder,
    SQLAlchemyModelSchemaBuilder,
)
from dyapi.interfaces.builders.api import IAPIBuilder
from dyapi.interfaces.builders.crud import ICRUDBuilder
from dyapi.interfaces.builders.endpoint import IEndpointBuilder
from dyapi.interfaces.builders.model import IModelBuilder
from dyapi.interfaces.storages import IStorageManager
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class APIBuilder(IAPIBuilder):
    def __init__(
        self,
        configs: list[Config],
        storage_manager: IStorageManager,
        crud_builder: Type[ICRUDBuilder] = CRUDBuilder,
        endpoint_builder: Type[IEndpointBuilder] = EndpointBuilder,
        model_builder: Type[IModelBuilder] = ModelBuilder,
    ):
        self.configs = configs
        self.storage_manager = storage_manager
        self.crud_builder = crud_builder
        self.endpoint_builder = endpoint_builder
        self.model_builder = model_builder

    @cached_property
    def cruds(self) -> Dict[str, ICRUDBuilder]:
        return {
            config.name: self.crud_builder(
                config=config,
                storage_manager=self.storage_manager,
                endpoint_builder=self.endpoint_builder,
                model_builder=self.model_builder,
            )
            for config in self.configs
        }

    @cached_property
    def models(self) -> Dict[str, IModelBuilder]:
        return {
            config.name: self.model_builder(config=config) for config in self.configs
        }

    @cached_property
    def router(self) -> APIRouter:
        router = APIRouter()

        for builder in self.cruds.values():
            router.include_router(
                router=builder.router,
                prefix=f"/{builder.config.name}",
                tags=builder.config.api_tags,
            )

        return router


class ModelAPIBuilder:
    def __init__(
        self,
        model: DeclarativeBase,
        db_session: AsyncSession,
        api_prefix: str = "",
        api_tags: list[str] | None = None,
        dependencies: list[Depends] | None = None,
    ):
        self.model = model
        self.models = SQLAlchemyModelSchemaBuilder(model=model)
        self.api_prefix = api_prefix
        self.api_tags = api_tags or []
        self.db_session = db_session
        self.dependencies = dependencies or []

    @cached_property
    def router(self) -> APIRouter:
        return SQLAlchemyCRUDBuilder(
            api_prefix=self.api_prefix,
            api_tags=self.api_tags,
            schema=self.models.base,
            update_schema=self.models.update,
            path_schema=self.models.path,
            filter_schema=self.models.filter,
            db_model=self.model,
            db_session=self.db_session,
            dependencies=self.dependencies,
        ).router
