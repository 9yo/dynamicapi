from unittest.mock import AsyncMock, MagicMock

import pytest

from dyapi.entities.endpoint_settings import EndpointSettings
from dyapi.implementations.builders.endpoint import EndpointBuilder, NotFoundException, AlreadyExistsException
from dyapi.implementations.storages.exceptions import AlreadyExistsError, NotFoundError
from tests.src.implementations.builders.test_crud import entity_model

# Create a mock for the storage with AsyncMock
mock_storage = MagicMock()
mock_storage.create = AsyncMock()
mock_storage.get = AsyncMock()
mock_storage.update = AsyncMock()
mock_storage.delete = AsyncMock()
mock_storage.list = AsyncMock()

# Create a mock for EndpointSettings
mock_settings = MagicMock(spec=EndpointSettings)
mock_settings.storage = mock_storage

# Create a mock for the model attribute of EndpointSettings
mock_model = MagicMock()
mock_settings.model = mock_model

# Now assign entity_model to the sub-attributes of mock_model
mock_model.entity = entity_model
mock_model.path = entity_model
mock_model.body = entity_model


# Now continue with your test cases

# Test the create endpoint
@pytest.mark.asyncio
async def test_create_endpoint():
    # Setup
    mock_entity = MagicMock()
    mock_settings.storage.create.return_value = mock_entity
    create_endpoint = EndpointBuilder.create_endpoint(mock_settings)

    # Test success
    assert await create_endpoint(entity=mock_entity) == mock_entity

    # Test failure due to entity already exists
    mock_settings.storage.create.side_effect = AlreadyExistsError()
    with pytest.raises(AlreadyExistsException):
        await create_endpoint(entity=mock_entity)


# ... Similar tests for get_endpoint, update_endpoint, delete_endpoint, list_endpoint

# Example for testing get_endpoint
@pytest.mark.asyncio
async def test_get_endpoint():
    # Setup
    mock_entity = MagicMock()
    mock_settings.storage.get.return_value = mock_entity
    get_endpoint = EndpointBuilder.get_endpoint(mock_settings)

    # Test success
    assert await get_endpoint(path=mock_entity) == mock_entity

    # Test failure due to entity not found
    mock_settings.storage.get.side_effect = NotFoundError()
    with pytest.raises(NotFoundException):
        await get_endpoint(path=mock_entity)


# ... Continue with similar structure for the remaining endpoints

@pytest.mark.asyncio
async def test_update_endpoint():
    # Setup
    mock_entity = MagicMock()
    mock_settings.storage.update.return_value = mock_entity
    update_endpoint = EndpointBuilder.update_endpoint(mock_settings)

    # Test success
    assert await update_endpoint(path=mock_entity, body=mock_entity) == mock_entity

    # Test failure due to entity not found
    mock_settings.storage.update.side_effect = NotFoundError()
    with pytest.raises(NotFoundException):
        await update_endpoint(path=mock_entity, body=mock_entity)


@pytest.mark.asyncio
async def test_delete_endpoint():
    # Setup
    mock_entity = MagicMock()
    mock_settings.storage.delete.return_value = True
    delete_endpoint = EndpointBuilder.delete_endpoint(mock_settings)

    # Test success
    assert await delete_endpoint(path=mock_entity)

    # Test failure due to entity not found
    mock_settings.storage.delete.side_effect = NotFoundError()
    with pytest.raises(NotFoundException):
        await delete_endpoint(path=mock_entity)
