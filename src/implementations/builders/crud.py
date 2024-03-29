from typing import Type

from fastapi import APIRouter

from src.entities.config import Config
from src.entities.endpoint_settings import EndpointSettings
from src.entities.model_settings import ModelSettings
from src.interfaces.builders.crud import ICRUDBuilder
from src.interfaces.builders.endpoint import IEndpointBuilder
from src.interfaces.builders.model import IModelBuilder
from src.interfaces.storages import IStorageManager


class CRUDBuilder(ICRUDBuilder):
    def __init__(
        self,
        config: Config,
        storage_manager: IStorageManager,
        endpoint_builder: Type[IEndpointBuilder],
        model_builder: Type[IModelBuilder],
    ):
        self.model = ModelSettings(
            path=model_builder.build_path(config),
            body=model_builder.build_body(config),
            entity=model_builder.build_entity(config),
            optional_path=model_builder.build_optional_path(config),
        )
        self.settings = EndpointSettings(
            config=config,
            model=self.model,
            storage=storage_manager.get_storage(config=config, settings=self.model),
        )
        self.api_tags = config.api_tags
        self.endpoint_builder = endpoint_builder

    def generate_path_from_fields(self, fields: list[str]) -> str:
        return "/".join(["{" + field + "}" for field in fields])

    @property
    def router(self) -> APIRouter:
        router = APIRouter(tags=self.api_tags)

        path: str = self.generate_path_from_fields(
            [field.name for field in self.settings.config.path_fields]
        )
        router.add_api_route(
            "/",
            self.endpoint_builder.create_endpoint(settings=self.settings),
            methods=["POST"],
        )

        router.add_api_route(
            f"/{path}",
            self.endpoint_builder.get_endpoint(settings=self.settings),
            methods=["GET"],
        )

        router.add_api_route(
            f"/{path}",
            self.endpoint_builder.update_endpoint(settings=self.settings),
            methods=["PUT"],
        )

        router.add_api_route(
            f"/{path}",
            self.endpoint_builder.delete_endpoint(settings=self.settings),
            methods=["DELETE"],
        )

        router.add_api_route(
            "/",
            self.endpoint_builder.list_endpoint(settings=self.settings),
            methods=["GET"],
        )
        return router
