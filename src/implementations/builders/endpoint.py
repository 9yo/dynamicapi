from typing import Any, Callable

from fastapi import Body, Depends, HTTPException

from src.entities.endpoint_settings import EndpointSettings
from src.entities.pagination import PaginationContainer, PaginationEntity
from src.implementations.storages.exceptions import AlreadyExistsError, NotFoundError
from src.interfaces.builders.endpoint import IEndpointBuilder


class NotFoundException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=404, detail=message)


class AlreadyExistsException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


class EndpointBuilder(IEndpointBuilder):
    @staticmethod
    def create_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            entity: settings.model.entity = Body(settings.model.entity),  # type: ignore
        ) -> settings.model.entity:  # type: ignore
            try:
                return await settings.storage.create(entity=entity)
            except AlreadyExistsError:
                raise AlreadyExistsException(
                    message="Entity already exists",
                )

        return endpoint

    @staticmethod
    def get_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            path: settings.model.path = Depends(settings.model.path),  # type: ignore
        ) -> settings.model.entity:  # type: ignore
            try:
                return await settings.storage.get(
                    path,
                    response_model=settings.model.entity,
                )
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )

        return endpoint

    @staticmethod
    def update_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            path: settings.model.path = Depends(settings.model.path),  # type: ignore
            body: settings.model.body = Body(settings.model.body),  # type: ignore
        ) -> settings.model.entity:  # type: ignore
            try:
                return await settings.storage.update(
                    filter_=path,
                    entity=body,
                    response_model=settings.model.entity,
                )
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )

        return endpoint

    @staticmethod
    def delete_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            path: settings.model.path = Depends(settings.model.path),  # type: ignore
        ) -> bool:
            try:
                await settings.storage.delete(path)
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )
            return True

        return endpoint

    @staticmethod
    def list_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            path: settings.model.optional_path = Depends(settings.model.optional_path),  # type: ignore
            pagination: PaginationEntity = Depends(PaginationEntity),
        ) -> PaginationContainer[settings.model.entity]:  # type: ignore
            result = await settings.storage.list(
                filter_=path,
                pagination=pagination,
                response_model=settings.model.entity,
            )
            return PaginationContainer(
                data=result,
                total=0,
                pagination=pagination,
            )

        return endpoint
