from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from dyapi.implementations.builders.api import ModelAPIBuilder
from fastapi import Depends, FastAPI, Request
from fastapi.security import HTTPBearer
from sqlalchemy import URL, Column, MetaData, String
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


class ProductModel(Base):
    """
    Product model.
    """

    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"ProductModel(id={self.id}, name={self.name}"


# schemas = SQLAlchemyModelSchemaBuilder(model=ProductModel)
#
# router = SQLAlchemyCRUDBuilder(
#     api_tags=["Product"],
#     api_prefix="/api/v1/product",
#     db_model=ProductModel,
#     db_session=get_db_session,
#     schema=schemas.base,
#     path_schema=schemas.path,
#     filter_schema=schemas.filter,
#     update_schema=schemas.update,
# )
security = HTTPBearer()


def authenticate(security_=Depends(security)):  # type: ignore
    pass


router = ModelAPIBuilder(
    api_tags=["Product"],
    api_prefix="/api/v1/product",
    model=ProductModel,
    db_session=get_db_session,
    dependencies=[Depends(authenticate)],
).router

application = FastAPI(lifespan=lifespan)
application.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "examples.app_models_from_table:application",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
