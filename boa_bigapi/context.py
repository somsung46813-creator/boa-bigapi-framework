"""Canonical request/data contract for BOA pipeline execution."""

import uuid
from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass
class BOAContext:
    """Stable envelope passed between CPU stages and compute boundaries."""

    payload: Any
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, payload: Any, metadata: dict[str, Any] | None = None) -> "BOAContext":
        """Create a context envelope for a new workflow request."""
        return cls(payload=payload, metadata=dict(metadata or {}))

    def replace(self, payload: Any, **metadata: Any) -> "BOAContext":
        """Create a new context while preserving request identity and merging metadata."""
        merged = {**self.metadata, **metadata}
        return BOAContext(
            payload=payload,
            request_id=self.request_id,
            timestamp=self.timestamp,
            metadata=merged,
        )
