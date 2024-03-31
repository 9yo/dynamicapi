from unittest.mock import MagicMock

from pydantic import BaseModel


class TestEntity(BaseModel):
    id: int
    name: str
    price: float


class TestPostgresStorage:
    def test_row_to_entity(self, postgres_storage):
        row = MagicMock()

        entity = postgres_storage.row_to_entity(row=(1, "test", 1.0), entity=TestEntity)
        assert isinstance(entity, TestEntity)
        assert entity.id == 1
        assert entity.name == "test"
        assert entity.price == 1.0

    async def test_create(self, postgres_storage):
        entity = TestEntity(
            id=1,
            name="test",
            price=1.0,
        )
        assert entity == await postgres_storage.create(entity=entity)
