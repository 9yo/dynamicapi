The following text is a Git repository with code. The structure of the text are sections that begin with ----, followed by a single line containing the file path and file name, followed by a variable amount of lines containing the file contents. The text representing the Git repository ends when the symbols --END-- are encounted. Any further text beyond --END-- are meant to be interpreted as instructions using the aforementioned Git repository as context.
----
.gptignore
pyproject.toml
poetry.lock
.pre-commit-config.yaml
.editorconfig

----
.ruff_cache/.gitignore
*
----
.ruff_cache/CACHEDIR.TAG
Signature: 8a477f597d28d172789f06886806bc55
----
examples/__init__.py

----
examples/app.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from sqlalchemy import URL, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.implementations.builders.api import APIBuilder
from src.implementations.storages.postgres.manager import PostgresStorageManager

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

----
examples/config.py
from src.entities.config import Config, ConfigField

configs: list[Config] = [
    Config(
        name="Entity1",
        api_tags=["Entity1"],
        fields=[
            ConfigField(name="field_1", type=int, location="path"),
            ConfigField(name="field_2", type=int, location="body"),
            ConfigField(name="field_3", type=float, location="body"),
            ConfigField(name="field_e", type=float, location="body"),
        ],
    ),
]
# configs: list[Config] = [
#     Config(
#         name="ozon",
#         api_tags=["ozon"],
#         fields=[
#             ConfigField(name="product_id", type=int, location='path'),
#             ConfigField(name="category_id", type=int, location='path'),
#             ConfigField(name="sale_schema_fbo", type=float, location='body'),
#             ConfigField(name="sale_schema_fbs", type=float, location='body'),
#             ConfigField(name="sale_schema_rfbs", type=float, location='body'),
#
#         ]
#     ),
# ]

----
src/__init__.py

----
src/entities/__init__.py

----
src/entities/config.py
from typing import Any, Literal, Type

from pydantic import BaseModel


class ConfigField(BaseModel):
    name: str
    type: Type[Any]
    location: Literal["path", "body"] = "body"


class Config(BaseModel):
    name: str
    api_tags: list[str]
    fields: list[ConfigField]

    @property
    def path_fields(self) -> list[ConfigField]:
        return [field for field in self.fields if field.location == "path"]

    @property
    def body_fields(self) -> list[ConfigField]:
        return [field for field in self.fields if field.location == "body"]

----
src/entities/endpoint_settings.py
from pydantic import BaseModel

from src.entities.config import Config
from src.entities.model_settings import ModelSettings
from src.interfaces.storages import IStorage


class EndpointSettings(BaseModel, arbitrary_types_allowed=True):
    model: ModelSettings
    storage: IStorage
    config: Config

----
src/entities/model_settings.py
from typing import Type

from pydantic import BaseModel


class ModelSettings(BaseModel, arbitrary_types_allowed=True):
    path: Type[BaseModel]
    optional_path: Type[BaseModel]
    body: Type[BaseModel]
    entity: Type[BaseModel]

----
src/entities/pagination.py
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class PaginationEntity(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=1)


class PaginationContainer(BaseModel, Generic[T]):
    pagination: PaginationEntity
    data: list[T]
    total: int

----
src/implementations/__init__.py

----
src/implementations/builders/__init__.py

----
src/implementations/builders/api.py
from typing import Type

from fastapi import APIRouter

from src.entities.config import Config
from src.implementations.builders.crud import CRUDBuilder
from src.implementations.builders.endpoint import EndpointBuilder
from src.implementations.builders.model import ModelBuilder
from src.interfaces.builders.api import IAPIBuilder
from src.interfaces.builders.crud import ICRUDBuilder
from src.interfaces.builders.endpoint import IEndpointBuilder
from src.interfaces.builders.model import IModelBuilder
from src.interfaces.storages import IStorageManager


class APIBuilder(IAPIBuilder):
    def __init__(
        self,
        configs: list[Config],
        storage_manager: IStorageManager,
        crud_builder: Type[ICRUDBuilder] = CRUDBuilder,
        endpoint_builder: Type[IEndpointBuilder] = EndpointBuilder,
        model_builder: Type[IModelBuilder] = ModelBuilder,
    ):
        self.configs = configs
        self.storage_manager = storage_manager
        self.crud_builder = crud_builder
        self.endpoint_builder = endpoint_builder
        self.model_builder = model_builder

    @property
    def router(self) -> APIRouter:
        router = APIRouter()

        for config in self.configs:
            crud_router = self.crud_builder(
                config=config,
                storage_manager=self.storage_manager,
                endpoint_builder=self.endpoint_builder,
                model_builder=self.model_builder,
            ).router

            router.include_router(
                crud_router, prefix=f"/{config.name}", tags=config.api_tags
            )

        return router

----
src/implementations/builders/crud.py
from typing import Type

from fastapi import APIRouter

from src.entities.config import Config
from src.entities.endpoint_settings import EndpointSettings
from src.entities.model_settings import ModelSettings
from src.interfaces.builders.crud import ICRUDBuilder
from src.interfaces.builders.endpoint import IEndpointBuilder
from src.interfaces.builders.model import IModelBuilder
from src.interfaces.storages import IStorageManager


class CRUDBuilder(ICRUDBuilder):
    def __init__(
        self,
        config: Config,
        storage_manager: IStorageManager,
        endpoint_builder: Type[IEndpointBuilder],
        model_builder: Type[IModelBuilder],
    ):
        self.model = ModelSettings(
            path=model_builder.build_path(config),
            body=model_builder.build_body(config),
            entity=model_builder.build_entity(config),
            optional_path=model_builder.build_optional_path(config),
        )
        self.settings = EndpointSettings(
            config=config,
            model=self.model,
            storage=storage_manager.get_storage(config=config, settings=self.model),
        )
        self.api_tags = config.api_tags
        self.endpoint_builder = endpoint_builder

    def generate_path_from_fields(self, fields: list[str]) -> str:
        return "/".join(["{" + field + "}" for field in fields])

    @property
    def router(self) -> APIRouter:
        router = APIRouter(tags=self.api_tags)

        path: str = self.generate_path_from_fields(
            [field.name for field in self.settings.config.path_fields]
        )
        router.add_api_route(
            "/",
            self.endpoint_builder.create_endpoint(settings=self.settings),
            methods=["POST"],
        )

        router.add_api_route(
            f"/{path}",
            self.endpoint_builder.get_endpoint(settings=self.settings),
            methods=["GET"],
        )

        router.add_api_route(
            f"/{path}",
            self.endpoint_builder.update_endpoint(settings=self.settings),
            methods=["PUT"],
        )

        router.add_api_route(
            f"/{path}",
            self.endpoint_builder.delete_endpoint(settings=self.settings),
            methods=["DELETE"],
        )

        router.add_api_route(
            "/",
            self.endpoint_builder.list_endpoint(settings=self.settings),
            methods=["GET"],
        )
        return router

----
src/implementations/builders/endpoint.py
from typing import Any, Callable

from fastapi import Body, Depends, HTTPException

from src.entities.endpoint_settings import EndpointSettings
from src.entities.pagination import PaginationContainer, PaginationEntity
from src.implementations.storages.exceptions import AlreadyExistsError, NotFoundError
from src.interfaces.builders.endpoint import IEndpointBuilder


class NotFoundException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=404, detail=message)


class AlreadyExistsException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


class EndpointBuilder(IEndpointBuilder):
    @staticmethod
    def create_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            entity: settings.model.entity = Body(settings.model.entity),  # type: ignore
        ) -> settings.model.entity:  # type: ignore
            try:
                return await settings.storage.create(entity=entity)
            except AlreadyExistsError:
                raise AlreadyExistsException(
                    message="Entity already exists",
                )

        return endpoint

    @staticmethod
    def get_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            path: settings.model.path = Depends(settings.model.path),  # type: ignore
        ) -> settings.model.entity:  # type: ignore
            try:
                return await settings.storage.get(
                    path,
                    response_model=settings.model.entity,
                )
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )

        return endpoint

    @staticmethod
    def update_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            path: settings.model.path = Depends(settings.model.path),  # type: ignore
            body: settings.model.body = Body(settings.model.body),  # type: ignore
        ) -> settings.model.entity:  # type: ignore
            try:
                return await settings.storage.update(
                    filter_=path,
                    entity=body,
                    response_model=settings.model.entity,
                )
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )

        return endpoint

    @staticmethod
    def delete_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            path: settings.model.path = Depends(settings.model.path),  # type: ignore
        ) -> bool:
            try:
                await settings.storage.delete(path)
            except NotFoundError:
                raise NotFoundException(
                    message="Entity not found",
                )
            return True

        return endpoint

    @staticmethod
    def list_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]:
        async def endpoint(
            path: settings.model.optional_path = Depends(settings.model.optional_path),  # type: ignore
            pagination: PaginationEntity = Depends(PaginationEntity),
        ) -> PaginationContainer[settings.model.entity]:  # type: ignore
            result = await settings.storage.list(
                filter_=path,
                pagination=pagination,
                response_model=settings.model.entity,
            )
            return PaginationContainer(
                data=result,
                total=0,
                pagination=pagination,
            )

        return endpoint

----
src/implementations/builders/model.py
from typing import Type

from pydantic import BaseModel, create_model

from src.entities.config import Config, ConfigField
from src.interfaces.builders.model import IModelBuilder


class ModelBuilder(IModelBuilder):
    @staticmethod
    def create_model(
        name: str,
        fields: list[ConfigField],
        optional: bool = False,
    ) -> Type[BaseModel]:
        return create_model(  # type: ignore
            name,
            **{
                field.name: (field.type | None, None) if optional else (field.type, ...)
                for field in fields
            },
        )

    @classmethod
    def build_path(cls, config: Config) -> Type[BaseModel]:
        return cls.create_model(f"PathModel{config.name}", config.path_fields)

    @classmethod
    def build_optional_path(cls, config: Config) -> Type[BaseModel]:
        return cls.create_model(
            f"OptionalPathModel{config.name}", config.path_fields, optional=True
        )

    @classmethod
    def build_body(cls, config: Config) -> Type[BaseModel]:
        return cls.create_model(f"BodyModel{config.name}", config.body_fields)

    @classmethod
    def build_entity(cls, config: Config) -> Type[BaseModel]:
        return cls.create_model(f"EntityModel{config.name}", config.fields)

----
src/implementations/storages/__init__.py

----
src/implementations/storages/exceptions.py
__all__ = ["NotFoundError", "AlreadyExistsError"]


class NotFoundError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass

----
src/implementations/storages/postgres/__init__.py

----
src/implementations/storages/postgres/base.py
from typing import Any, Type

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from src.entities.pagination import PaginationEntity
from src.implementations.storages.exceptions import AlreadyExistsError, NotFoundError
from src.interfaces.storages import IStorage

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

----
src/implementations/storages/postgres/manager.py
from sqlalchemy import Column, Float, Integer, MetaData, String, Table, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncEngine

from src.entities.config import Config, ConfigField
from src.entities.model_settings import ModelSettings
from src.interfaces.storages import IStorage, IStorageManager

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

----
src/interfaces/__init__.py

----
src/interfaces/builders/__init__.py

----
src/interfaces/builders/api.py
from abc import ABC, abstractmethod

from fastapi import APIRouter

from src.entities.config import Config
from src.interfaces.builders.crud import ICRUDBuilder
from src.interfaces.storages import IStorageManager


class IAPIBuilder(ABC):
    @abstractmethod
    def __init__(
        self,
        configs: list[Config],
        storage: IStorageManager,
        crud_builder: ICRUDBuilder,
    ): ...

    @property
    @abstractmethod
    def router(self) -> list[APIRouter]: ...

----
src/interfaces/builders/crud.py
from abc import ABC, abstractmethod
from typing import Type

from fastapi import APIRouter

from src.entities.config import Config
from src.interfaces.builders.endpoint import IEndpointBuilder
from src.interfaces.builders.model import IModelBuilder
from src.interfaces.storages import IStorageManager


class ICRUDBuilder(ABC):
    def __init__(
        self,
        config: Config,
        storage_manager: IStorageManager,
        endpoint_builder: Type[IEndpointBuilder],
        model_builder: Type[IModelBuilder],
    ): ...

    @property
    @abstractmethod
    def router(self) -> APIRouter: ...

----
src/interfaces/builders/endpoint.py
from abc import ABC, abstractmethod
from typing import Any, Callable

from src.entities.endpoint_settings import EndpointSettings


class IEndpointBuilder(ABC):
    @staticmethod
    @abstractmethod
    def create_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

    @staticmethod
    @abstractmethod
    def get_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

    @staticmethod
    @abstractmethod
    def update_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

    @staticmethod
    @abstractmethod
    def delete_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

    @staticmethod
    @abstractmethod
    def list_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

----
src/interfaces/builders/model.py
from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

from src.entities.config import Config


class IModelBuilder(ABC):
    @classmethod
    @abstractmethod
    def build_path(cls, config: Config) -> Type[BaseModel]: ...

    @classmethod
    @abstractmethod
    def build_optional_path(cls, config: Config) -> Type[BaseModel]: ...

    @classmethod
    @abstractmethod
    def build_body(cls, config: Config) -> Type[BaseModel]: ...

    @classmethod
    @abstractmethod
    def build_entity(cls, config: Config) -> Type[BaseModel]: ...

----
src/interfaces/storages/__init__.py
from .base import IStorage
from .manager import IStorageManager

__all__ = [
    "IStorage",
    "IStorageManager",
]

----
src/interfaces/storages/base.py
from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

from src.entities.pagination import PaginationEntity

__all__ = ("IStorage",)


class IStorage(ABC):
    @abstractmethod
    async def get(
        self, filter_: BaseModel, response_model: Type[BaseModel]
    ) -> BaseModel: ...

    @abstractmethod
    async def create(self, entity: BaseModel) -> BaseModel: ...

    @abstractmethod
    async def update(
        self, filter_: BaseModel, entity: BaseModel, response_model: Type[BaseModel]
    ) -> BaseModel: ...

    @abstractmethod
    async def delete(self, filter_: BaseModel) -> bool: ...

    @abstractmethod
    async def list(
        self,
        filter_: BaseModel,
        pagination: PaginationEntity,
        response_model: Type[BaseModel],
    ) -> list[BaseModel]: ...

----
src/interfaces/storages/manager.py
from abc import ABC, abstractmethod

from src.entities.config import Config
from src.entities.model_settings import ModelSettings
from src.interfaces.storages.base import IStorage


class IStorageManager(ABC):
    @abstractmethod
    def get_storage(self, config: Config, settings: ModelSettings) -> IStorage: ...

--END--