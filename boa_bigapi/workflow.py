"""Framework-level workflow abstractions."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from .context import BOAContext


class Workflow(ABC):
    """Minimal contract shared by executable BOA workflows."""
