# # Mock classes
# from unittest.mock import MagicMock, AsyncMock
#
# import pytest
# from pydantic import BaseModel
# from sqlalchemy.sql import Selectable
#
# from src.implementations.storages.postgres.base import PostgresStorage
#
#
# class MockConnection:
#     def __init__(self):
#         self.connection = AsyncMock()
#
#     async def __aenter__(self):
#         # Directly return the AsyncMock object
#         return self.connection
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         pass
#
#
# class MockAsyncEngine:
#     def begin(self):
#         # Return an instance of MockConnection
#         return MockConnection()
#
#
# class TestModel(BaseModel):
#     id: int
#     name: str
#
#
# # Setup for each test
# @pytest.fixture
# def mock_engine():
#     return MockAsyncEngine()
#
#
# @pytest.fixture
# def mock_table():
#     table = MagicMock()
#     table.insert.return_value = MagicMock()
#     table.select.return_value = MagicMock(spec=Selectable)
#     table.update.return_value = MagicMock()
#     table.delete.return_value = MagicMock()
#     return table
#
#
# @pytest.mark.asyncio
# async def test_create_success(mock_engine, mock_table):
#     storage = PostgresStorage(pg_engine=mock_engine, table=mock_table)
#     entity = TestModel(id=1, name='Test Name')
#
#     await storage.create(entity)
#
#     mock_table.insert.assert_called_once()
#     mock_table.insert().values.assert_called_once_with(entity.dict())
#
#
# @pytest.mark.asyncio
# async def test_create_failure(mock_engine, mock_table):
#     storage = PostgresStorage(pg_engine=mock_engine, table=mock_table)
#     entity = TestModel(id=1, name='Test Name')
#
#     mock_table.insert.return_value = MagicMock(side_effect=Exception('Test Error'))
#
#     with pytest.raises(Exception) as exc:
#         await storage.create(entity)
#
#     assert str(exc.value) == 'Test Error'
#
#
# @pytest.mark.asyncio
# async def test_get_success(mock_engine, mock_table):
#     storage = PostgresStorage(pg_engine=mock_engine, table=mock_table)
#     entity = TestModel(id=1, name='Test Name')
#
#     mock_table.select.return_value.fetchone.return_value = (1, 'Test Name')
#
#     result = await storage.get(entity, TestModel)
#
#     mock_table.select.assert_called_once()
#     mock_table.select().where.assert_called_once()
#     mock_table.select().where().fetchone.assert_called_once()
#     assert result.id == 1
#     assert result.name == 'Test Name'
#
#
# @pytest.mark.asyncio
# async def test_get_failure(mock_engine, mock_table):
#     storage = PostgresStorage(pg_engine=mock_engine, table=mock_table)
#     entity = TestModel(id=1, name='Test Name')
#
#     mock_table.select.return_value.fetchone.return_value = None
#
#     with pytest.raises(Exception) as exc:
#         await storage.get(entity, TestModel)
#
#     assert str(exc.value) == 'NotFoundError'
#
#
# @pytest.mark.asyncio
# async def test_update_success(mock_engine, mock_table):
#     storage = PostgresStorage(pg_engine=mock_engine, table=mock_table)
#     entity = TestModel(id=1, name='Test Name')
#
#     mock_table.update.return_value = MagicMock()
#
#     result = await storage.update(entity, entity, TestModel)
#
#     mock_table.update.assert_called_once()
#     mock_table.update().where.assert_called_once()
#     mock_table.update().where().values.assert_called_once()
#     assert result.id == 1
#     assert result.name == 'Test Name'
#
#
# @pytest.mark.asyncio
# async def test_update_failure(mock_engine, mock_table):
#     storage = PostgresStorage(pg_engine=mock_engine, table=mock_table)
#     entity = TestModel(id=1, name='Test Name')
#
#     mock_table.update.return_value = MagicMock(side_effect=Exception('Test Error'))
#
#     with pytest.raises(Exception) as exc:
#         await storage.update(entity, entity, TestModel)
#
#     assert str(exc.value) == 'Test Error'
#
#
# @pytest.mark.asyncio
# async def test_delete_success(mock_engine, mock_table):
#     storage = PostgresStorage(pg_engine=mock_engine, table=mock_table)
#     entity = TestModel(id=1, name='Test Name')
#
#     mock_table.delete.return_value = MagicMock()
#     mock_table.delete().where.return_value = MagicMock()
#
#     result = await storage.delete(entity)
#
#     mock_table.delete.assert_called_once()
#     mock_table.delete().where.assert_called_once()
#     assert result is True
#
#
# @pytest.mark.asyncio
# async def test_delete_failure(mock_engine, mock_table):
#     storage = PostgresStorage(pg_engine=mock_engine, table=mock_table)
#     entity = TestModel(id=1, name='Test Name')
#
#     mock_table.delete.return_value = MagicMock(side_effect=Exception('Test Error'))
#
#     with pytest.raises(Exception) as exc:
#         await storage.delete(entity)
#
#     assert str(exc.value) == 'Test Error'
