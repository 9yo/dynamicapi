from unittest.mock import MagicMock

import pytest
from dyapi.implementations.storages.postgres.base import PostgresEngineStorage


@pytest.fixture
def postgres_storage():
    return PostgresEngineStorage(
        pg_engine=MagicMock(),
        table=MagicMock(),
    )
