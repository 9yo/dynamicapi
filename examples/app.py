from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from sqlalchemy import URL, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from dyapi.implementations.builders.api import APIBuilder
from dyapi.implementations.storages.postgres.manager import PostgresStorageManager

from .config import configs

__all__ = ["metadata"]

metadata = MetaData()


def get_postgres_engine() -> AsyncEngine:
    engine = create_async_engine(
        url=URL.create(
            drivername="postgresql+asyncpg",
            username="postgres",
            password="postgres",
            host="localhost",
            port=5432,
            database="postgres",
        )
    )
    return engine


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    engine = get_postgres_engine()
    storage_manager = PostgresStorageManager(pg_engine=engine, metadata=metadata)

    example_router = APIBuilder(configs=configs, storage_manager=storage_manager).router

    app.state.postgres_engine = engine

    app.include_router(example_router)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    await app.state.postgres_engine.dispose()


application = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run("examples.app:application", host="0.0.0.0", port=8000, reload=True)
