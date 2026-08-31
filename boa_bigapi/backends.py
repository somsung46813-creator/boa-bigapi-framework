"""Abstract contracts for compute and transport implementations."""

from abc import ABC, abstractmethod
from typing import Any


class ComputeBackend(ABC):
    """Backend-neutral compute contract."""

    @abstractmethod
    def execute(self, operation: Any) -> Any:
        raise NotImplementedError


class Transport(ABC):
    """Backend-neutral transport contract."""

    @abstractmethod
    def send(self, packet: Any, destination: str | None = None) -> Any:
        raise NotImplementedError

    @abstractmethod
    def receive(self, source: str | None = None) -> Any:
        raise NotImplementedError
