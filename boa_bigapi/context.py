"""Canonical request/data contract for BOA pipeline execution."""

from dataclasses import dataclass, field
from time import time
from typing import Any
import uuid


@dataclass
class BOAContext:
    """Stable envelope passed between CPU stages and compute boundaries."""

    payload: Any
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def replace(self, payload: Any, **metadata: Any) -> "BOAContext":
        merged = {**self.metadata, **metadata}
        return BOAContext(payload=payload, request_id=self.request_id,
                          timestamp=self.timestamp, metadata=merged)
