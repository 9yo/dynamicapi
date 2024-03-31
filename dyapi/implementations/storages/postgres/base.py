from typing import Any, Callable, Type

from asyncpg import UniqueViolationError
from dyapi.entities.pagination import PaginationEntity
from dyapi.implementations.storages.exceptions import AlreadyExistsError, NotFoundError
from dyapi.interfaces.storages import IStorage
from pydantic import BaseModel
from sqlalchemy import Table, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

__all__ = ["PostgresEngineStorage"]


class PostgresStorage:
    def row_to_entity(self, row: tuple[Any], entity: Type[BaseModel]) -> BaseModel:
        return entity(**{key: row[i] for i, key in enumerate(entity.__fields__.keys())})  # type: ignore


class PostgresEngineStorage(IStorage, PostgresStorage):
    def __init__(
        self,
        pg_engine: AsyncEngine,
        table: Table,
    ):
        self.pg_engine = pg_engine
        self.table = table

    async def execute_query(self, query: Any) -> Any:
        async with self.pg_engine.begin() as conn:
            result = await conn.execute(query)
            conn.commit()
            return result

    async def create(self, entity: BaseModel) -> BaseModel:
        query = self.table.insert().values(entity.dict())
        try:
            await self.execute_query(query)
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
        query = self.table.select().where(*filter_stmnts)
        result = await self.execute_query(query)
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
        query = self.table.update().where(*filter_stmnts).values(entity.dict())
        await self.execute_query(query)
        return await self.get(filter_, response_model)

    async def delete(self, filter_: BaseModel) -> bool:
        filter_stmnts = [
            getattr(self.table.c, key) == value for key, value in filter_.dict().items()
        ]
        query = self.table.delete().where(*filter_stmnts)
        result = await self.execute_query(query)
        return bool(result.rowcount)

    async def list(
        self,
        filter_: BaseModel,
        pagination: PaginationEntity,
        response_model: Type[BaseModel],
    ) -> tuple[list[BaseModel], int]:
        filter_stmnts = [
            getattr(self.table.c, key) == value
            for key, value in filter_.dict().items()
            if value is not None
        ]
        query = (
            self.table.select()
            .where(*filter_stmnts)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        total_count_query = (
            select(func.count()).select_from(self.table).where(*filter_stmnts)
        )

        result = await self.execute_query(query)
        result = result.fetchall()

        total_count = await self.execute_query(total_count_query)

        return [
            self.row_to_entity(row, response_model) for row in result
        ], total_count.fetchone()[0]


class PostgresSessionStorage(PostgresEngineStorage):
    def __init__(
        self,
        get_session: Callable[[], AsyncSession],
        table: Table,
    ):
        self.get_session = get_session
        self.table = table

    async def execute_query(self, query: Any) -> Any:
        session = self.get_session()
        async with session.begin():
            return await session.execute(query)
