from unittest.mock import MagicMock

import pytest
from dyapi.implementations.builders.endpoint import EndpointBuilder
from dyapi.interfaces.storages import IStorage


@pytest.fixture
def endpoint_builder(model_builder):
    return EndpointBuilder(
        model=model_builder,
        storage=MagicMock(spec=IStorage),
    )
