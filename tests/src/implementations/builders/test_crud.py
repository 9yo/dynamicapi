from unittest.mock import Mock

import pytest
from fastapi import APIRouter
from pydantic import create_model

from dyapi.entities.config import Config
from dyapi.implementations.builders.crud import CRUDBuilder
from dyapi.interfaces.storages import IStorageManager, IStorage

# Mock dependencies
MockEndpointBuilder = Mock()
MockModelBuilder = Mock()
MockStorageManager = Mock(spec=IStorageManager)

path_model = create_model("PathModel", id=(int, ...))
body_model = create_model("BodyModel", name=(str, ...), age=(int, ...))
entity_model = create_model("EntityModel", id=(int, ...), name=(str, ...), age=(int, ...))
optional_path_model = create_model("OptionalPathModel", id=(int | None, ...))

# Setting up the mock model builder to return mock model settings
MockModelBuilder.build_path.return_value = path_model
MockModelBuilder.build_body.return_value = body_model
MockModelBuilder.build_entity.return_value = entity_model
MockModelBuilder.build_optional_path.return_value = optional_path_model

MockStorageManager.get_storage.return_value = Mock(spec=IStorage)

# Sample configuration
config = Config(name="TestEntity", api_tags=["test"], fields=[])


# Create a test instance of CRUDBuilder
@pytest.fixture
def crud_builder():
    return CRUDBuilder(
        config=config,
        storage_manager=MockStorageManager,
        endpoint_builder=MockEndpointBuilder,
        model_builder=MockModelBuilder
    )


def test_crud_builder_initialization(crud_builder):
    assert crud_builder.api_tags == config.api_tags
    assert crud_builder.settings.config == config
    # Add more assertions related to the initialization


def test_generate_path_from_fields(crud_builder):
    fields = ["id", "name"]
    expected_path = "{id}/{name}"
    assert crud_builder.generate_path_from_fields(fields) == expected_path


def test_crud_builder_router(crud_builder):
    router = crud_builder.router
    assert isinstance(router, APIRouter)
    # Verify that the correct number of routes have been added
    assert len(router.routes) == 5
    # Further assertions can be made to check the specific endpoints and methods
