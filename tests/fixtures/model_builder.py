import pytest
from dyapi.implementations.builders.model import ModelBuilder


@pytest.fixture
def model_builder(configs):
    return ModelBuilder(configs[0])
