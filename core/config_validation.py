"""Validation helpers for BOA Framework configuration."""

from typing import Any

from .exceptions import ConfigurationError


def validate_config_value(key: str, value: Any) -> None:
    """Validate bounded configuration values."""
    if key in {"CPU_WORKERS", "CPU_MAX_BATCH_SIZE"}:
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ConfigurationError(f"{key} must be a positive integer")
    elif key == "CPU_TIMEOUT":
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise ConfigurationError("CPU_TIMEOUT must be a positive number")
    elif key == "GPU_BACKEND" and value not in {"vulkan", "opengl", "webgl"}:
        raise ConfigurationError("GPU_BACKEND must be one of: vulkan, opengl, webgl")
    elif key == "NETWORK_PROTOCOL" and value not in {"tcp", "udp", "http"}:
        raise ConfigurationError("NETWORK_PROTOCOL must be one of: tcp, udp, http")
    elif key == "NETWORK_PORT":
        if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 65535:
            raise ConfigurationError("NETWORK_PORT must be an integer between 1 and 65535")
