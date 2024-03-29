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
