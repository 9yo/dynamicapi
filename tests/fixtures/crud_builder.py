from unittest.mock import MagicMock

import pytest

from dyapi.implementations.builders.crud import CRUDBuilder
from dyapi.implementations.builders.endpoint import EndpointBuilder
from dyapi.implementations.builders.model import ModelBuilder
from dyapi.interfaces.storages import IStorageManager


# Create a test instance of CRUDBuilder
@pytest.fixture
def crud_builder(
    configs
):
    return CRUDBuilder(
        config=configs[0],
        storage_manager=MagicMock(spec=IStorageManager),
        endpoint_builder=EndpointBuilder,
        model_builder=ModelBuilder,
    )
