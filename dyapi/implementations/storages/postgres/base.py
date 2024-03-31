from typing import Any, Type

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from dyapi.entities.pagination import PaginationEntity
from dyapi.implementations.storages.exceptions import AlreadyExistsError, NotFoundError
from dyapi.interfaces.storages import IStorage

__all__ = ["PostgresStorage"]


class PostgresStorage(IStorage):
    def __init__(
        self,
        pg_engine: AsyncEngine,
        table: Table,
    ):
        self.pg_engine = pg_engine
        self.table = table

    def row_to_entity(self, row: tuple[Any], entity: Type[BaseModel]) -> BaseModel:
        return entity(**{key: row[i] for i, key in enumerate(entity.__fields__.keys())})  # type: ignore

    async def create(self, entity: BaseModel) -> BaseModel:
        async with self.pg_engine.begin() as conn:
            query = self.table.insert().values(entity.dict())
            try:
                await conn.execute(query)
            except IntegrityError as exc:
                if exc.orig.sqlstate == UniqueViolationError.sqlstate:
                    raise AlreadyExistsError from exc

        return entity

    async def get(
        self, filter_: BaseModel, response_model: Type[BaseModel]
    ) -> BaseModel:
        filter_stmnts = [
            getattr(self.table.c, key) == value for key, value in filter_.dict().items()
        ]
        async with self.pg_engine.begin() as conn:
            query = self.table.select().where(*filter_stmnts)
            result = await conn.execute(query)
            result = result.fetchone()
            if not result:
                raise NotFoundError
            return self.row_to_entity(result, response_model)

    async def update(
        self, filter_: BaseModel, entity: BaseModel, response_model: Type[BaseModel]
    ) -> BaseModel:
        filter_stmnts = [
            getattr(self.table.c, key) == value for key, value in filter_.dict().items()
        ]
        async with self.pg_engine.begin() as conn:
            query = self.table.update().where(*filter_stmnts).values(entity.dict())
            await conn.execute(query)
            await conn.commit()
            return await self.get(filter_, response_model)

    async def delete(self, filter_: BaseModel) -> bool:
        filter_stmnts = [
            getattr(self.table.c, key) == value for key, value in filter_.dict().items()
        ]
        async with self.pg_engine.begin() as conn:
            query = self.table.delete().where(*filter_stmnts)
            result = await conn.execute(query)
            return bool(result.rowcount)

    async def list(
        self,
        filter_: BaseModel,
        pagination: PaginationEntity,
        response_model: Type[BaseModel],
    ) -> list[BaseModel]:
        filter_stmnts = [
            getattr(self.table.c, key) == value
            for key, value in filter_.dict().items()
            if value is not None
        ]
        async with self.pg_engine.begin() as conn:
            query = (
                self.table.select()
                .where(*filter_stmnts)
                .limit(pagination.limit)
                .offset(pagination.offset)
            )
            result = await conn.execute(query)
            result = result.fetchall()
            return [self.row_to_entity(row, response_model) for row in result]
