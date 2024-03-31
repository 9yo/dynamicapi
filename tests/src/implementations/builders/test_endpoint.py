# Now continue with your test cases
from typing import Callable
from unittest.mock import MagicMock

import pytest
from pydantic import create_model

from dyapi.entities.pagination import PaginationEntity
from dyapi.implementations.builders.endpoint import AlreadyExistsException, NotFoundException
from dyapi.implementations.storages.exceptions import AlreadyExistsError, NotFoundError


def raise_not_found_error(*args, **kwargs):
    raise NotFoundError


def raise_already_exists_exception(*args, **kwargs):
    raise AlreadyExistsError


class TestEndpointBuilder:
    async def test_create_endpoint(self, endpoint_builder):
        endpoint = endpoint_builder.create
        assert isinstance(endpoint, Callable)
        entity = MagicMock()
        entity = await endpoint(entity=entity)

        endpoint_builder.storage.create = raise_already_exists_exception
        with pytest.raises(AlreadyExistsException):
            await endpoint(entity=entity)

    async def test_get_endpoint(self, endpoint_builder):
        endpoint = endpoint_builder.get
        assert isinstance(endpoint, Callable)
        path = MagicMock()
        entity = await endpoint(path=path)

        endpoint_builder.storage.get = raise_not_found_error
        with pytest.raises(NotFoundException):
            await endpoint(path=path)

    async def test_update_endpoint(self, endpoint_builder):
        endpoint = endpoint_builder.update
        assert isinstance(endpoint, Callable)
        path = MagicMock()
        body = MagicMock()
        entity = await endpoint(path=path, body=body)

        endpoint_builder.storage.update = raise_not_found_error
        with pytest.raises(NotFoundException):
            await endpoint(path=path, body=body)

    async def test_delete_endpoint(self, endpoint_builder):
        endpoint = endpoint_builder.delete
        assert isinstance(endpoint, Callable)
        path = MagicMock()
        entity = await endpoint(path=path)

        endpoint_builder.storage.delete = raise_not_found_error
        with pytest.raises(NotFoundException):
            await endpoint(path=path)

    async def test_list_endpoint(self, endpoint_builder):
        endpoint = endpoint_builder.list
        assert isinstance(endpoint, Callable)
        model = create_model(
            "TestModel",
            field1=(str, ...)
        )
        endpoint_builder.storage.list.return_value = [model(
            field1="test"
        ), model(
            field1="test"
        )], 2
        container = await endpoint(
            path=MagicMock(),
            pagination=PaginationEntity(
                offset=0,
                limit=10,
            )
        )
        assert len(container.data) == 2
