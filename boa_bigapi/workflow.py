"""Framework-level workflow abstractions."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from .context import BOAContext


class Workflow(ABC):
    """Minimal contract shared by executable BOA workflows."""

    @abstractmethod
    def execute(self, data: Any) -> Any:
        """Execute the workflow against input data."""
        raise NotImplementedError


class CPUWorkflow(Workflow):
    """Composable CPU pipeline facade."""

    DEFAULT_PIPELINE = (
        "View", "Data", "Grid", "Controller", "Secret", "Session",
        "Sequence", "Model", "Packet", "Frame", "Medium",
    )

    def __init__(self, components: Iterable[Any] | None = None):
        self.components: list[Any] = list(components or [])

    def use(self, component: Any) -> "CPUWorkflow":
        if not hasattr(component, "process"):
            raise TypeError("Workflow components must expose process(data)")
        self.components.append(component)
        return self

    def execute(self, data: Any) -> Any:
        context = data if isinstance(data, BOAContext) else BOAContext.create(data)
        current: Any = context
        for component in self.components:
            if isinstance(current, BOAContext):
                result = component.process(current.payload)
                current = current.replace(result)
            else:
                current = component.process(current)
        return current


class BOA:
    """Top-level facade separating CPU workflows from compute backends."""

    def __init__(self, workflow: Workflow | None = None, backend: Any = None):
        self.workflow = workflow or CPUWorkflow()
        self.backend = backend

    def execute(self, data: Any) -> Any:
        return self.workflow.execute(data)

    def compute(self, operation: Any) -> Any:
        if self.backend is None:
            raise RuntimeError("No compute backend configured")
        return self.backend.execute(operation)
