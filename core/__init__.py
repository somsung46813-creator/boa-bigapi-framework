"""BOA Framework Core Module

Core foundation and base classes for the BOA (BIG O API) framework.
"""

from .base import BaseComponent, BaseWorkflow, BaseProcessor
from .config import Config, ConfigManager
from .exceptions import (
    BOAException,
    ConfigurationError,
    ProcessingError,
    SecurityError,
    SessionError,
    PacketError
)

__all__ = [
    'BaseComponent',
    'BaseWorkflow',
    'BaseProcessor',
    'Config',
    'ConfigManager',
    'BOAException',
    'ConfigurationError',
    'ProcessingError',
    'SecurityError',
    'SessionError',
    'PacketError'
]

__version__ = '1.0.0'
