from dyapi.implementations.builders.model import ModelBuilder
from dyapi.interfaces.builders.crud import ICRUDBuilder


class TestAPIBuilder:
    def test_cruds(self, api_builder):
        assert isinstance(api_builder.cruds["Test"], ICRUDBuilder)
        assert isinstance(api_builder.cruds["Test2"], ICRUDBuilder)

    def test_models(self, api_builder):
        assert isinstance(api_builder.models["Test"], ModelBuilder)
        assert isinstance(api_builder.models["Test2"], ModelBuilder)

    def test_router(self, api_builder):
        router = api_builder.router
        assert len(router.routes) == 10
        assert router.routes[0].path == "/Test/"
        assert router.routes[0].tags == ["tag1"]
