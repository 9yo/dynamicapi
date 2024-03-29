from unittest.mock import MagicMock

import pytest
from fastapi import APIRouter

from src.entities.config import Config
from src.implementations.builders.api import APIBuilder
from src.interfaces.builders.crud import ICRUDBuilder
from src.interfaces.builders.model import IModelBuilder
from src.interfaces.storages import IStorageManager

# Mock dependencies
MockCRUDBuilder = MagicMock(spec=ICRUDBuilder)
MockEndpointBuilder = MagicMock(spec=IModelBuilder)
MockModelBuilder = MagicMock(spec=IModelBuilder)
MockStorageManager = MagicMock(spec=IStorageManager)

# Sample configuration
config1 = Config(name="TestEntity1", api_tags=["test1"], fields=[])
config2 = Config(name="TestEntity2", api_tags=["test2"], fields=[])


@pytest.fixture
def api_builder():
    return APIBuilder(
        configs=[config1, config2],
        storage_manager=MockStorageManager,
        crud_builder=MockCRUDBuilder,
        endpoint_builder=MockEndpointBuilder,
        model_builder=MockModelBuilder
    )


def test_api_builder_initialization(api_builder):
    assert api_builder.configs == [config1, config2]
    assert api_builder.storage_manager is MockStorageManager
    assert api_builder.crud_builder is MockCRUDBuilder
    assert api_builder.endpoint_builder is MockEndpointBuilder
    assert api_builder.model_builder is MockModelBuilder


def test_api_builder_router(api_builder):
    api_builder.crud_builder.router.return_value = APIRouter()
    router = api_builder.router
    assert isinstance(router, APIRouter)
    assert len(router.routes) == 0
    # Additional assertions can be made to verify route configurations
