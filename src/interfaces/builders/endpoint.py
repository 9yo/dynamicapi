from abc import ABC, abstractmethod
from typing import Any, Callable

from src.entities.endpoint_settings import EndpointSettings


class IEndpointBuilder(ABC):
    @staticmethod
    @abstractmethod
    def create_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

    @staticmethod
    @abstractmethod
    def get_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

    @staticmethod
    @abstractmethod
    def update_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

    @staticmethod
    @abstractmethod
    def delete_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...

    @staticmethod
    @abstractmethod
    def list_endpoint(settings: EndpointSettings) -> Callable[[Any], Any]: ...
