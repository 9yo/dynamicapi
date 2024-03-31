from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from dyapi import APIBuilder
from dyapi.implementations.storages.postgres.manager import (
    PostgresSessionStorageManager,
)
from fastapi import FastAPI
from sqlalchemy import URL, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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


engine = get_postgres_engine()
get_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    app.state.postgres_engine = engine

    storage_manager = PostgresSessionStorageManager(
        get_session=get_session, metadata=metadata
    )

    api_builder = APIBuilder(configs=configs, storage_manager=storage_manager)
    example_router = api_builder.router

    application.include_router(example_router)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    await app.state.postgres_engine.dispose()


application = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(
        "examples.app_session:application", host="0.0.0.0", port=8001, reload=True
    )
