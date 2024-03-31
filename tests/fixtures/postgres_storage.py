from unittest.mock import MagicMock

import pytest

from dyapi.implementations.storages.postgres.base import PostgresStorage


@pytest.fixture
def postgres_storage():
    return PostgresStorage(
        pg_engine=MagicMock(),
        table=MagicMock(),
    )
