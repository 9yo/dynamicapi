from unittest.mock import MagicMock

import pytest
from dyapi import APIBuilder
from dyapi.implementations.builders.crud import CRUDBuilder
from dyapi.implementations.builders.model import ModelBuilder
from dyapi.interfaces.storages import IStorageManager


@pytest.fixture
def api_builder(configs):
    return APIBuilder(
        configs=configs,
        storage_manager=MagicMock(spec=IStorageManager),
        crud_builder=CRUDBuilder,
        model_builder=ModelBuilder,
    )
