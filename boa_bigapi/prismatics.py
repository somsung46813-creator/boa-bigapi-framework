"""Backend-neutral Prismatics operation facade."""

from typing import Any, Protocol


class ComputeBackend(Protocol):
    """Minimal execution contract required by Prismatics."""

    def execute(self, operations: list[tuple[str, Any]]) -> Any:
        """Execute an ordered operation list."""
        ...


class Prismatics:
    """Compose pitch, roll, index and scatter operations for a backend."""

    def __init__(self, backend: ComputeBackend | type[ComputeBackend]):
        self.backend = backend() if isinstance(backend, type) else backend
        self.operations: list[tuple[str, Any]] = []

    def pitch(self, rotation_angle: float) -> "Prismatics":
        self.operations.append(("pitch", rotation_angle))
        return self

    def roll(self, rotation_angle: float) -> "Prismatics":
        self.operations.append(("roll", rotation_angle))
        return self

    def index(self, mapping: Any) -> "Prismatics":
        self.operations.append(("index", mapping))
        return self

    def scatter(self, data_points: Any) -> "Prismatics":
        self.operations.append(("scatter", data_points))
        return self

    def compute(self) -> Any:
        return self.backend.execute(list(self.operations))
