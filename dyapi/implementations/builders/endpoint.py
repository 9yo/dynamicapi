from functools import cached_property
from typing import Any, Callable

from dyapi.entities.pagination import PaginationContainer, PaginationEntity
from dyapi.implementations.storages.exceptions import AlreadyExistsError, NotFoundError
from dyapi.interfaces.builders.endpoint import IEndpointBuilder
from dyapi.interfaces.builders.model import IModelBuilder
from dyapi.interfaces.storages import IStorage
from fastapi import Body, Depends, HTTPException


class NotFoundException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=404, detail=message)


class AlreadyExistsException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


class EndpointBuilder(IEndpointBuilder):
    def __init__(self, model: IModelBuilder, storage: IStorage):
        self.model = model
        self.storage = storage

    @cached_property
    def create(self) -> Callable[[Any], Any]:
        async def endpoint(
            entity: self.model.entity = Body(self.model.entity),  # type: ignore
        ) -> self.model.entity:  # type: ignore
            try:
                return await self.storage.create(entity=entity)
            except AlreadyExistsError:
                raise AlreadyExistsException(
                    message="Entity already exists",
                )

        return endpoint

    @cached_property
    def get(self) -> Callable[[Any], Any]:
        async def endpoint(
            path: self.model.path = Depends(self.model.path),  # type: ignore
        ) -> self.model.entity:  # type: ignore
            try:
                return await self.storage.get(
                    path,
                    response_model=self.model.entity,
                )
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )

        return endpoint

    @cached_property
    def update(self) -> Callable[[Any], Any]:
        async def endpoint(
            path: self.model.path = Depends(self.model.path),  # type: ignore
            body: self.model.body = Body(self.model.body),  # type: ignore
        ) -> self.model.entity:  # type: ignore
            try:
                return await self.storage.update(
                    filter_=path,
                    entity=body,
                    response_model=self.model.entity,
                )
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )

        return endpoint

    @cached_property
    def delete(self) -> Callable[[Any], Any]:
        async def endpoint(
            path: self.model.path = Depends(self.model.path),  # type: ignore
        ) -> bool:
            try:
                await self.storage.delete(path)
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )
            return True

        return endpoint

    @cached_property
    def list(self) -> Callable[[Any], Any]:
        async def endpoint(
            path: self.model.query = Depends(self.model.query),  # type: ignore
            pagination: PaginationEntity = Depends(PaginationEntity),
        ) -> PaginationContainer[self.model.entity]:  # type: ignore
            result, total = await self.storage.list(
                filter_=path,
                pagination=pagination,
                response_model=self.model.entity,
            )
            return PaginationContainer(
                data=result,
                total=total,
                pagination=pagination,
            )

        return endpoint
