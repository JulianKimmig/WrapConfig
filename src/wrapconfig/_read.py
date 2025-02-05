from pathlib import Path
from .core import FileWrapConfig
from .jsonconfig import JSONWrapConfig

# Optional imports for YAML and TOML support.
try:
    from wrapconfig.yamlconf import YAMLWrapConfig
except ImportError:
    YAMLWrapConfig = None

try:
    from wrapconfig.tomlconfig import TOMLWrapConfig
except ImportError:
    TOMLWrapConfig = None


def create_config(file_path: str, default_save: bool = True) -> FileWrapConfig:
    """
    Create and return a FileWrapConfig subclass instance based on the file extension.

    Supported file extensions:
      - .json : Returns a JSONWrapConfig
      - .yaml or .yml : Returns a YAMLWrapConfig (if available)
      - .toml : Returns a TOMLWrapConfig (if available)

    Parameters:
        file_path (str): The path to the configuration file.
        default_save (bool): Whether to use the default auto-save behavior.

    Returns:
        FileWrapConfig: An instance of a FileWrapConfig subclass appropriate for the file type.

    Raises:
        ValueError: If the file extension is not supported.
        ImportError: If the required optional dependency is not installed.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".json":
        return JSONWrapConfig(file_path, default_save=default_save)
    elif ext in (".yaml", ".yml"):
        if YAMLWrapConfig is None:
            raise ImportError(
                "YAMLWrapConfig is not available because pyyaml is not installed."
            )
        return YAMLWrapConfig(file_path, default_save=default_save)
    elif ext == ".toml":
        if TOMLWrapConfig is None:
            raise ImportError(
                "TOMLWrapConfig is not available because toml is not installed."
            )
        return TOMLWrapConfig(file_path, default_save=default_save)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
