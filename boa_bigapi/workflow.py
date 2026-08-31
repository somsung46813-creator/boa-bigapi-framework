"""Framework-level workflow abstractions."""

from abc import ABC, abstractmethod
from typing import Any, Iterable

from .context import BOAContext


class Workflow(ABC):
    """Minimal contract shared by executable BOA workflows."""

    @abstractmethod
    def execute(self, data: Any) -> Any:
        raise NotImplementedError


class CPUWorkflow(Workflow):
    """Composable CPU pipeline using the canonical BOA context contract."""

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
        context = data if isinstance(data, BOAContext) else BOAContext(data)
        for component in self.components:
            result = component.process(context.payload)
            context = context.replace(result, stage=component.__class__.__name__)
        return context


class BOA:
    """Top-level facade separating workflow execution from compute backends."""

    def __init__(self, workflow: Workflow | None = None, backend: Any = None):
        self.workflow = workflow or CPUWorkflow()
        self.backend = backend

    def execute(self, data: Any) -> BOAContext | Any:
        return self.workflow.execute(data)

    def compute(self, operation: Any) -> Any:
        if self.backend is None:
            raise RuntimeError("No compute backend configured")
        return self.backend.execute(operation)
