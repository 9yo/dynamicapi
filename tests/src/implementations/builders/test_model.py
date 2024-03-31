from dyapi import ConfigField
from pydantic import BaseModel


class TestModelBuilder:
    def test_create_model(self, model_builder):
        model = model_builder.create_model(
            "TestModel",
            fields=[
                ConfigField(
                    name="field1",
                    type=str,
                ),
            ],
        )
        assert issubclass(model, BaseModel)
        assert model.__name__ == "TestModel"
        assert model.model_fields["field1"].annotation == str

    def test_path_model(self, model_builder):
        model = model_builder.path
        assert issubclass(model, BaseModel)
        assert model.__name__.startswith("PathModel")
        assert model.model_fields["field1"].annotation == int

    def test_body_model(self, model_builder):
        model = model_builder.body
        assert issubclass(model, BaseModel)
        assert model.__name__.startswith("BodyModel")
        assert model.model_fields == {}

    def test_query_model(self, model_builder):
        model = model_builder.query
        assert issubclass(model, BaseModel)
        assert model.__name__.startswith("QueryModel")
        assert model.model_fields["field1"].annotation == int | None

    def test_entity_model(self, model_builder):
        model = model_builder.entity
        assert issubclass(model, BaseModel)
        assert model.__name__.startswith("EntityModel")
        assert model.model_fields["field1"].annotation == int
