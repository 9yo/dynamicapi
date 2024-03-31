import pytest
from dyapi import Config, ConfigField


@pytest.fixture
def configs():
    return [
        Config(
            name="Test",
            api_tags=["tag1"],
            fields=[
                ConfigField(name="field1", type=int, location="path"),
            ],
        ),
        Config(
            name="Test2",
            api_tags=["tag2"],
            fields=[
                ConfigField(name="field2", type=str, location="body"),
            ],
        ),
    ]
