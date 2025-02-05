from .jsonconfig import JSONWrapConfig
from .core import WrapConfig, FileWrapConfig, ValueToSectionError, ExpectingSectionError
from .inmemory import InMemoryConfig

__all__ = [
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

__version__ = "0.2.1"
