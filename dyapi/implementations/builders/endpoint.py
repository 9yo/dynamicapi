from functools import cached_property
from typing import Any, AsyncGenerator, Callable, Type

from dyapi.entities.pagination import PaginationContainer, PaginationEntity
from dyapi.implementations.storages.exceptions import AlreadyExistsError, NotFoundError
from dyapi.implementations.storages.postgres.base import SQLAlchemyStorage
from dyapi.interfaces.builders.endpoint import IEndpointBuilder
from dyapi.interfaces.builders.model import IModelBuilder
from dyapi.interfaces.storages import IStorage
from fastapi import Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


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


class SQLAlchemyEndpointBuilder:
    def __init__(
        self,
        db_model: Type[DeclarativeBase],
        db_session: Callable[[Any], AsyncGenerator[Any, None]],
        schema: Type[BaseModel],
        path_schema: Type[BaseModel],
        filter_schema: Type[BaseModel],
        update_schema: Type[BaseModel],
    ):
        self.db_model = db_model
        self.db_session = db_session
        self.schema = schema
        self.path_schema = path_schema
        self.filter_schema = filter_schema
        self.update_schema = update_schema
        self.storage = SQLAlchemyStorage

    @cached_property
    def create(self) -> Callable[[Any], Any]:
        schema = self.schema

        async def endpoint(
            entity: schema = Body(schema),  # type: ignore
            session: AsyncSession = Depends(self.db_session),
        ) -> schema:  # type: ignore
            try:
                model = await self.storage.create(
                    session=session,
                    model=self.db_model(**entity.model_dump()),  # type: ignore
                )
            except AlreadyExistsError:
                raise AlreadyExistsException(message="Entity already exists")

            return schema(**model.__dict__)

        return endpoint

    @cached_property
    def upsert_many(self) -> Callable[[Any], Any]:
        schema = self.schema

        async def endpoint(
            entities: list[schema] = Body(...),  # type: ignore
            session: AsyncSession = Depends(self.db_session),
        ) -> list[schema]:  # type: ignore
            return await self.storage.upsert_many(
                session=session, model_type=self.db_model, entities=entities
            )

        return endpoint

    @cached_property
    def get(self) -> Callable[[Any], Any]:
        schema = self.schema

        async def endpoint(
            path: schema = Depends(self.path_schema),  # type: ignore
            session: AsyncSession = Depends(self.db_session),
        ) -> schema:  # type: ignore
            try:
                model = await self.storage.get(
                    session=session,
                    model_type=self.db_model,
                    filter_=path,
                )
            except NotFoundError:
                raise NotFoundException(message="Entity not found")
            return schema(**model.__dict__)

        return endpoint

    @cached_property
    def update(self) -> Callable[[Any], Any]:
        schema = self.schema

        async def endpoint(
            path: self.path_schema = Depends(self.path_schema),  # type: ignore
            body: self.update_schema = Body(self.update_schema),  # type: ignore
            session: AsyncSession = Depends(self.db_session),
        ) -> schema:  # type: ignore
            try:
                model = await self.storage.update(
                    session=session,
                    model_type=self.db_model,
                    filter_=path,
                    body=body,
                )
            except NotFoundError:
                raise NotFoundException(message="Entity not found")
            return schema(**model.__dict__)

        return endpoint

    @cached_property
    def delete(self) -> Callable[[Any], Any]:
        async def endpoint(
            path: self.path_schema = Depends(self.path_schema),  # type: ignore
            session: AsyncSession = Depends(self.db_session),
        ) -> bool:
            try:
                return await self.storage.delete(
                    session=session,
                    model_type=self.db_model,
                    filter_=path,
                )
            except NotFoundError:
                raise NotFoundException(message="Entity not found")

        return endpoint

    @cached_property
    def list(self) -> Callable[[Any], Any]:
        schema = self.schema

        async def endpoint(
            filter_: self.filter_schema = Depends(self.filter_schema),  # type: ignore
            pagination: PaginationEntity = Depends(PaginationEntity),
            session: AsyncSession = Depends(self.db_session),
        ) -> PaginationContainer[schema]:  # type: ignore
            data, total = await self.storage.list(
                session=session,
                model_type=self.db_model,
                filter_=filter_,
                pagination=pagination,
            )
            return PaginationContainer(
                data=[schema(**item.__dict__) for item in data],
                total=total,
                pagination=pagination,
            )

        return endpoint
