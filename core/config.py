"""Configuration management for BOA Framework."""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path


class Config:
    """Configuration holder for BOA Framework."""

    # CPU Workflow Configuration
    CPU_WORKERS = 4
    CPU_MAX_BATCH_SIZE = 1000
    CPU_TIMEOUT = 30.0
    
    # GPU Configuration
    GPU_DEVICE = 0
    GPU_MEMORY_MB = 2048
    GPU_BACKEND = 'vulkan'  # vulkan, opengl, webgl
    
    # Session Configuration
    SESSION_TIMEOUT = 3600  # 1 hour
    SESSION_PERSISTENT = True
    SESSION_STORAGE = '/tmp/boa_sessions'
    
    # Security Configuration
    SECURITY_ENCRYPTION = True
    SECURITY_KEY_SIZE = 256
    SECURITY_HASH_ALGORITHM = 'sha256'
    
    # Network Configuration
    NETWORK_PROTOCOL = 'tcp'  # tcp, udp, http
    NETWORK_HOST = '0.0.0.0'
    NETWORK_PORT = 8080
    NETWORK_BUFFER_SIZE = 65536
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = None
    
    # Framework Configuration
    FRAMEWORK_DEBUG = False
    FRAMEWORK_VERSION = '1.0.0'
    FRAMEWORK_NAME = 'BOA'

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {key: getattr(cls, key) for key in dir(cls) 
                if not key.startswith('_') and key.isupper()}

    @classmethod
    def update(cls, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
        """
        for key, value in config_dict.items():
            if key.isupper():
                setattr(cls, key, value)


class ConfigManager:
    """Manages configuration loading and management."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (JSON format)
        """
        self.config_file = config_file
        self.config = Config.to_dict()
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)

    def load_config(self, config_file: str) -> None:
        """Load configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                self.config.update(config_data)
                Config.update(config_data)
        except Exception as e:
            raise ValueError(f"Failed to load config file {config_file}: {e}")

    def save_config(self, config_file: str) -> None:
        """Save current configuration to JSON file.
        
        Args:
            config_file: Path to save configuration to
        """
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        if key.isupper():
            setattr(Config, key, value)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.
        
        Returns:
            Dictionary of all configuration
        """
        return self.config.copy()
