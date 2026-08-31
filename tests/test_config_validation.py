import pytest

from core.config import Config
from core.exceptions import ConfigurationError


@pytest.fixture(autouse=True)
def reset_config():
    Config.CPU_WORKERS = 4
    Config.CPU_MAX_BATCH_SIZE = 1000
    Config.CPU_TIMEOUT = 30.0
    Config.GPU_BACKEND = "vulkan"
    Config.NETWORK_PROTOCOL = "tcp"
    Config.NETWORK_PORT = 8080
    yield


def test_valid_configuration_values():
    Config.update({
        "CPU_WORKERS": 8,
        "CPU_MAX_BATCH_SIZE": 256,
        "CPU_TIMEOUT": 10.5,
        "GPU_BACKEND": "opengl",
        "NETWORK_PROTOCOL": "http",
        "NETWORK_PORT": 8443,
    })
    assert Config.CPU_WORKERS == 8
    assert Config.CPU_MAX_BATCH_SIZE == 256
    assert Config.CPU_TIMEOUT == 10.5
    assert Config.GPU_BACKEND == "opengl"
    assert Config.NETWORK_PROTOCOL == "http"
    assert Config.NETWORK_PORT == 8443


@pytest.mark.parametrize("key,value", [
    ("CPU_WORKERS", 0),
    ("CPU_WORKERS", -1),
    ("CPU_MAX_BATCH_SIZE", 0),
    ("CPU_TIMEOUT", 0),
    ("CPU_TIMEOUT", -1),
])
def test_invalid_cpu_values_raise_configuration_error(key, value):
    with pytest.raises(ConfigurationError):
        Config.update({key: value})


@pytest.mark.parametrize("value", ["cuda", "metal", ""])
def test_invalid_gpu_backend_raises_configuration_error(value):
    with pytest.raises(ConfigurationError):
        Config.update({"GPU_BACKEND": value})


@pytest.mark.parametrize("value", ["ftp", "icmp", ""])
def test_invalid_network_protocol_raises_configuration_error(value):
    with pytest.raises(ConfigurationError):
        Config.update({"NETWORK_PROTOCOL": value})


@pytest.mark.parametrize("value", [0, -1, 65536, 100000])
def test_invalid_network_port_raises_configuration_error(value):
    with pytest.raises(ConfigurationError):
        Config.update({"NETWORK_PORT": value})


def test_unknown_uppercase_key_preserves_existing_behavior():
    Config.update({"UNKNOWN_SETTING": "value"})
    assert Config.UNKNOWN_SETTING == "value"
