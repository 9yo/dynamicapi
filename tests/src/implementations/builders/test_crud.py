from unittest.mock import MagicMock

import pytest

from dyapi import Config
from dyapi.implementations.builders.crud import CRUDBuilder
from dyapi.implementations.builders.endpoint import EndpointBuilder
from dyapi.implementations.builders.model import ModelBuilder
from dyapi.interfaces.storages import IStorageManager


# Create a test instance of CRUDBuilder

class TestCRUDBuilder:
    def test_generate_path_from_fields(self):
        assert CRUDBuilder.generate_path_from_fields(["field1", "field2"]) == "{field1}/{field2}"

    def test_config(self, crud_builder):
        assert isinstance(crud_builder.config, Config)

    def test_model(self, crud_builder):
        assert isinstance(crud_builder.model, ModelBuilder)

    def test_endpoint(self, crud_builder):
        assert isinstance(crud_builder.endpoint, EndpointBuilder)

    def test_router(self, crud_builder):
        router = crud_builder.router
        assert len(router.routes) == 5
        assert router.routes[0].path == "/"
        assert router.routes[0].methods == {"POST"}
        assert router.routes[1].path == "/"
        assert router.routes[1].methods == {"GET"}
        assert router.routes[2].path == "/{field1}"
        assert router.routes[2].methods == {"GET"}
        assert router.routes[3].path == "/{field1}"
        assert router.routes[3].methods == {"PUT"}
        assert router.routes[4].path == "/{field1}"
        assert router.routes[4].methods == {"DELETE"}
