from functools import cached_property
from typing import Type

from fastapi import APIRouter

from dyapi.entities.config import Config
from dyapi.interfaces.builders.crud import ICRUDBuilder
from dyapi.interfaces.builders.endpoint import IEndpointBuilder
from dyapi.interfaces.builders.model import IModelBuilder
from dyapi.interfaces.storages import IStorageManager


class CRUDBuilder(ICRUDBuilder):
    def __init__(
        self,
        config: Config,
        storage_manager: IStorageManager,
        endpoint_builder: Type[IEndpointBuilder],
        model_builder: Type[IModelBuilder],
    ):
        self._config = config
        self._model = model_builder(config=config)
        self._endpoint = endpoint_builder(
            model=self.model,
            storage=storage_manager.storage(config=config),
        )

    @staticmethod
    def generate_path_from_fields(fields: list[str]) -> str:
        return "/".join(["{" + field + "}" for field in fields])

    @cached_property
    def config(self) -> Config:
        return self._config

    @cached_property
    def model(self) -> IModelBuilder:
        return self._model

    @cached_property
    def endpoint(self) -> IEndpointBuilder:
        return self._endpoint

    @cached_property
    def router(self) -> APIRouter:
        router = APIRouter()

        path: str = self.generate_path_from_fields(
            [field.name for field in self.config.path_fields]
        )
        router.add_api_route("/", self.endpoint.create, methods=["POST"])

        router.add_api_route("/", self.endpoint.list, methods=["GET"])

        router.add_api_route(f"/{path}", self.endpoint.get, methods=["GET"])

        router.add_api_route(f"/{path}", self.endpoint.update, methods=["PUT"])

        router.add_api_route(f"/{path}", self.endpoint.delete, methods=["DELETE"])

        return router
