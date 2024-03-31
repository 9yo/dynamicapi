from typing import AsyncContextManager, Callable

from sqlalchemy import Column, Float, Integer, MetaData, String, Table, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession

from dyapi.entities.config import Config, ConfigField
from dyapi.interfaces.storages import IStorage, IStorageManager
from .base import PostgresEngineStorage, PostgresSessionStorage

__all__ = ["PostgresEngineStorageManager"]


class PostgresStorageManager:
    @staticmethod
    def generate_column(field: ConfigField) -> Column:
        if field.type == str:
            return Column(field.name, String)
        if field.type == int:
            return Column(field.name, Integer)
        if field.type == float:
            return Column(field.name, Float)
        raise ValueError(f"Unknown type {field.type}")


class PostgresEngineStorageManager(IStorageManager, PostgresStorageManager):
    def __init__(
        self,
        pg_engine: AsyncEngine,
        metadata: MetaData,
    ):
        self.pg_engine = pg_engine
        self.metadata = metadata

    def build_table(self, config: Config) -> Table:
        return Table(
            config.name,
            self.metadata,
            *[self.generate_column(field) for field in config.fields],
            UniqueConstraint(
                *[field.name for field in config.path_fields],
            ),
        )

    def storage(self, config: Config) -> IStorage:
        return PostgresEngineStorage(
            pg_engine=self.pg_engine,
            table=self.build_table(config),
        )


class PostgresSessionStorageManager(IStorageManager, PostgresStorageManager):
    def __init__(
        self,
        get_session: Callable[[], AsyncSession],
        metadata: MetaData,
    ):
        self.get_session = get_session
        self.metadata = metadata

    def build_table(self, config: Config) -> Table:
        return Table(
            config.name,
            self.metadata,
            *[self.generate_column(field) for field in config.fields],
            UniqueConstraint(
                *[field.name for field in config.path_fields],
            ),
        )

    def storage(self, config: Config) -> IStorage:
        return PostgresSessionStorage(
            get_session=self.get_session,
            table=self.build_table(config),
        )
