from sqlalchemy import Column, Float, Integer, MetaData, String, Table, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncEngine

from dyapi.entities.config import Config, ConfigField
from dyapi.entities.model_settings import ModelSettings
from dyapi.interfaces.storages import IStorage, IStorageManager

from .base import PostgresStorage

__all__ = ["PostgresStorageManager"]


class PostgresStorageManager(IStorageManager):
    def __init__(
        self,
        pg_engine: AsyncEngine,
        metadata: MetaData,
    ):
        self.pg_engine = pg_engine
        self.metadata = metadata

    @staticmethod
    def generate_column(field: ConfigField) -> Column:
        if field.type == str:
            return Column(field.name, String)
        if field.type == int:
            return Column(field.name, Integer)
        if field.type == float:
            return Column(field.name, Float)
        raise ValueError(f"Unknown type {field.type}")

    def build_table(self, config: Config) -> Table:
        return Table(
            config.name,
            self.metadata,
            *[self.generate_column(field) for field in config.fields],
            UniqueConstraint(
                *[field.name for field in config.fields if field.location == "path"]
            ),
        )

    def get_storage(self, config: Config, settings: ModelSettings) -> IStorage:
        return PostgresStorage(
            pg_engine=self.pg_engine,
            table=self.build_table(config),
        )


#
