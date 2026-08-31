"""Custom exceptions for BOA Framework."""


class BOAException(Exception):
    """Base exception for all BOA Framework exceptions."""
    pass


class ConfigurationError(BOAException):
    """Raised when configuration is invalid."""
    pass


class ProcessingError(BOAException):
    """Raised during data processing errors."""
    pass


class SecurityError(BOAException):
    """Raised when security operations fail."""
    pass


class SessionError(BOAException):
    """Raised for session management errors."""
    pass


class PacketError(BOAException):
    """Raised for packet assembly/parsing errors."""
    pass


class GridError(BOAException):
    """Raised for grid computation errors."""
    pass


class ControllerError(BOAException):
    """Raised for controller routing errors."""
    pass


class GPUError(BOAException):
    """Raised for GPU processing errors."""
    pass
