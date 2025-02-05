from .jsonconfig import JSONWrapConfig
from .core import WrapConfig, FileWrapConfig, ValueToSectionError, ExpectingSectionError
from .inmemory import InMemoryConfig
from ._read import create_config

__all__ = [
    "create_config",
    "JSONWrapConfig",
    "WrapConfig",
    "InMemoryConfig",
    "FileWrapConfig",
    "ValueToSectionError",
    "ExpectingSectionError",
]

# YAML support is optional
try:
    from .yamlconf import YAMLWrapConfig

    __all__.append("YAMLWrapConfig")
except (ImportError, ModuleNotFoundError):
    pass

# TOML support is optional
try:
    from .tomlconfig import TOMLWrapConfig

    __all__.append("TOMLWrapConfig")
except (ImportError, ModuleNotFoundError):
    pass

__version__ = "0.2.2"
