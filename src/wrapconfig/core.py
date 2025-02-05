"""
Core configuration classes and exceptions.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
import os
from typing import Any, Dict, Optional, Union
import tempfile
import logging

logger = logging.getLogger("wrapconfig")

# Type definitions
ConfigTypes = Union[str, float, int, bool]
ConfigData = Dict[str, Union[ConfigTypes, "ConfigData"]]

# Sentinel value used to detect an omitted value.
_NO_VALUE = object()


class ValueToSectionError(Exception):
    """Raised when attempting to overwrite a configuration section (dict) with a non-dict value."""


class ExpectingSectionError(Exception):
    """Raised when a nested section was expected but a non-dict value was found instead."""


class WrapConfig(ABC):
    """
    Abstract base class for configuration wrappers.

    Provides methods to set, get, update, fill, and clear configuration data.
    Subclasses must implement load() and save() to handle persistence.
    """

    def __init__(self, default_save: bool = True) -> None:
        self._config_data: ConfigData = {}
        self._default_save: bool = default_save

    @property
    def data(self) -> ConfigData:
        """Return a deep copy of the configuration data."""
        return deepcopy(self._data)

    @property
    def _data(self) -> ConfigData:
        """Internal access to the configuration data.
        This is used by subclasses to access the configuration data directly.
        """
        return self._config_data

    def set_data(self, data: ConfigData) -> None:
        """
        Replace the entire configuration with the provided data.
        """
        self.clear()
        self.update(data)

    @abstractmethod
    def load(self) -> None:
        """
        Load configuration from its resource.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def save(self) -> None:
        """
        Save configuration to its resource.
        Must be implemented by subclasses.
        """
        pass

    def clear(self, *keys):
        """clear config"""
        _datadict = self._data
        if len(keys) == 0:
            for key in list(self._data.keys()):
                del self._data[key]
            return

        keys = list(keys)
        lastkey = keys[-1]
        keys = keys[:-1]

        for key in keys:
            if key not in _datadict:
                raise KeyError(f"Key {key} not found in config.")
            _datadict = _datadict[key]

        if lastkey not in _datadict:
            raise KeyError(f"Key {lastkey} not found in config.")

        del _datadict[lastkey]

    def set(
        self,
        *keys: str,
        value: ConfigTypes = _NO_VALUE,
        save: Optional[bool] = None,
    ):
        """set config"""

        keys = list(keys)

        if value is _NO_VALUE:
            value = keys.pop(-1)
        if len(keys) == 0:
            raise ValueError("No keys provided")

        _datadict = self._data

        objectkey = keys.pop(-1)
        for _key in keys:
            if _key not in _datadict:
                _datadict[_key] = {}
            _datadict = _datadict[_key]
            if not isinstance(_datadict, dict):
                raise ExpectingSectionError(
                    f"Expected dict, got {type(_datadict)}, this might be the result of a key or subkey conflict, which is already a value."
                )

        if (
            objectkey in _datadict
            and isinstance(_datadict[objectkey], dict)
            and len(_datadict[objectkey]) > 0
        ):
            raise ValueToSectionError(
                f"Cannot overwrite section {objectkey} with a value."
            )
        _datadict[objectkey] = value
        if save is None:
            save = self._default_save

        if save:
            self.save()

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value using a nested key path.
        Returns the provided default if the key path is not found.
        """
        if not keys:
            return self.data

        _datadict = self._data
        if len(keys) > 1:
            for key in keys[:-1]:
                if key not in _datadict:
                    _datadict[key] = {}
                _datadict = _datadict[key]
                if not isinstance(_datadict, dict):
                    raise TypeError(
                        f"Expected dict, got {type(_datadict)}, this might be the result of a key or subkey conflict, which is already a value."
                    )

        return _datadict.get(keys[-1], default)

    def update(
        self,
        data: ConfigData,
        save: Optional[bool] = None,
    ):
        """Deeply update the configuration with the provided data.
        If a key is not present in the configuration, it will be added.
        If a key is present in the configuration, it will be updated.
        """

        def deep_update(target: ConfigData, source: ConfigData) -> ConfigData:
            for key, value in source.items():
                tv = target.get(key, {})
                if isinstance(value, dict) and isinstance(tv, dict):
                    target[key] = deep_update(tv, value)
                else:
                    target[key] = value
            return target

        deep_update(self._data, data)
        if save is None:
            save = self._default_save

        if save:
            self.save()

    def fill(self, data: ConfigData, save: Optional[bool] = None):
        """Deeply update the configuration with the provided data.
        If a key is not present in the configuration, it will be added.
        If a key is present in the configuration, it will not be updated.
        """

        def deep_update(target: ConfigData, source: ConfigData) -> ConfigData:
            for key, value in source.items():
                if isinstance(value, dict):
                    if key not in target:
                        target[key] = {}
                    elif not isinstance(target[key], dict):
                        continue
                    target[key] = deep_update(target[key], value)
                else:
                    if key not in target:
                        target[key] = value
            return target

        deep_update(self._data, data)

        if save is None:
            save = self._default_save

        if save:
            self.save()

    def __setitem__(self, key, value):
        if (
            key in self._data
            and isinstance(self._data[key], dict)
            and len(self._data[key]) > 0
        ):
            raise ValueToSectionError(f"Cannot overwrite section {key} with a value.")
        self.set(key, value=value)

    def __getitem__(self, key):
        if key not in self._data:
            self._data[key] = {}
        if isinstance(self._data[key], dict):
            return SubConfig(self, key)
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()


class SubConfigError(Exception):
    """Raised for operations that are not allowed on a SubConfig."""


class SubConfig(WrapConfig):
    """
    Represents a subsection of a parent configuration.

    The SubConfig delegates saving to the parent configuration.
    It does not support direct loading.
    """

    def __init__(self, parent: WrapConfig, key: str) -> None:
        super().__init__()
        self._parent = parent
        self._key = key

    @property
    def _default_save(self) -> bool:
        return self._parent._default_save

    @_default_save.setter
    def _default_save(self, value_: bool):
        pass  # only allow setting of default save on parent

    @property
    def _data(self) -> ConfigData:
        return self._parent._data[self._key]

    def load(self):
        raise SubConfigError("Cannot load a SubConfig.")

    def save(self):
        self._parent.save()

    def __repr__(self) -> str:
        return f"<SubConfig key={self._key} parent={self._parent}>"


class FileWrapConfig(WrapConfig):
    """WrapConfig that saves and loads from a file"""

    def __init__(self, path, default_save: bool = True) -> None:
        self._path = os.path.abspath(path)
        super().__init__(default_save)
        if os.path.exists(self.path):
            self.load()

    def _read_file(self) -> str:
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def _write_file(self, dump: str) -> None:
        """
        Atomically write the provided data to the file specified by self.path.

        This method writes the content to a temporary file located in the same
        directory as self.path. It then flushes, fsyncs, and atomically replaces
        the target file with the temporary file using os.replace. This ensures that
        the file is either fully written or not modified at all, thus preventing
        corruption.

        Parameters:
            dump (str): The string data to be written to the file.

        Raises:
            Exception: Re-raises any exception that occurs during the write process.
        """

        # Ensure the temporary file is created in the same directory as the target file.
        target_dir = os.path.dirname(os.path.abspath(self.path))
        temp_file_path = None

        try:
            # Create a temporary file in the target directory.
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8", dir=target_dir
            ) as tmp_file:
                temp_file_path = tmp_file.name
                tmp_file.write(dump)
                # Ensure data is flushed to disk.
                tmp_file.flush()
                os.fsync(tmp_file.fileno())

            # Atomically replace the destination file with the temporary file.
            os.replace(temp_file_path, self.path)

        except Exception as error:
            logger.exception("Error writing file atomically to %s", self.path)
            # Clean up the temporary file if it exists.
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as cleanup_error:
                    logger.warning(
                        "Failed to remove temporary file %s: %s",
                        temp_file_path,
                        cleanup_error,
                    )
            raise error

    @property
    def path(self):
        return self._path
