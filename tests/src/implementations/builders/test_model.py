from pydantic import BaseModel

from dyapi.entities.config import Config, ConfigField
from dyapi.implementations.builders.model import ModelBuilder

# Sample ConfigField and Config objects for testing
test_field_1 = ConfigField(name="field1", type=int, location="path")
test_field_2 = ConfigField(name="field2", type=str, location="body")
test_config = Config(name="Test", api_tags=["tag1"], fields=[test_field_1, test_field_2])


def test_create_model():
    TestModel = ModelBuilder.create_model("TestModel", [test_field_1, test_field_2], optional=False)
    assert issubclass(TestModel, BaseModel)
    assert "field1" in TestModel.__fields__
    assert "field2" in TestModel.__fields__


def test_build_path():
    PathModel = ModelBuilder.build_path(test_config)
    assert issubclass(PathModel, BaseModel)
    assert "field1" in PathModel.__fields__


def test_build_optional_path():
    OptionalPathModel = ModelBuilder.build_optional_path(test_config)
    assert issubclass(OptionalPathModel, BaseModel)
    assert "field1" in OptionalPathModel.__fields__


def test_build_body():
    BodyModel = ModelBuilder.build_body(test_config)
    assert issubclass(BodyModel, BaseModel)
    assert "field2" in BodyModel.__fields__


def test_build_entity():
    EntityModel = ModelBuilder.build_entity(test_config)
    assert issubclass(EntityModel, BaseModel)
    assert "field1" in EntityModel.__fields__
    assert "field2" in EntityModel.__fields__
