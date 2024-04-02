from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from dyapi.implementations.builders.crud import SQLAlchemyCRUDBuilder
from fastapi import FastAPI, Request
from pydantic import BaseModel
from sqlalchemy import URL, Column, Float, Integer, MetaData, UniqueConstraint
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declarative_base

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


# @asynccontextmanager
async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    app.state.postgres_engine = get_postgres_engine()
    app.state.db_session_factory = async_sessionmaker(
        app.state.postgres_engine,
        expire_on_commit=False,
    )

    async with app.state.postgres_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    await app.state.postgres_engine.dispose()


Base: DeclarativeBase = declarative_base(metadata=metadata)


class MetricaModel(Base):
    """
    Extended model for metrics.
    """

    __tablename__ = "metrica_extended"
    product_id = Column(Integer, primary_key=True)
    category_id = Column(Integer)
    product_metrica_1 = Column(Float)
    product_category_constraint = UniqueConstraint("product_id", "category_id")
    product_metrica_2 = Column(Float)
    product_metrica_3 = Column(Float)


class MetricaModelSchema(BaseModel):
    product_id: int
    category_id: int
    product_metrica_1: float
    product_metrica_2: float
    product_metrica_3: float


class MetricaSchemaIdentifier(BaseModel):
    product_id: int
    category_id: int


class OptionalMetricaSchemaIdentifier(BaseModel):
    product_id: int | None = None
    category_id: int | None = None


class OptionalMetricaSchema(BaseModel):
    product_metrica_1: float | None = None
    product_metrica_2: float | None = None
    product_metrica_3: float | None = None


router = SQLAlchemyCRUDBuilder(
    api_tags=["Metrica"],
    api_prefix="/api/v1/metrica",
    db_model=MetricaModel,
    db_session=get_db_session,
    schema=MetricaModelSchema,
    path_schema=MetricaSchemaIdentifier,
    filter_schema=OptionalMetricaSchemaIdentifier,
    update_schema=OptionalMetricaSchema,
)

application = FastAPI(lifespan=lifespan)
application.include_router(router.router)

if __name__ == "__main__":
    uvicorn.run(
        "examples.app_models:application", host="0.0.0.0", port=8001, reload=True
    )
