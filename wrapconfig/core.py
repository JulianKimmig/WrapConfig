from abc import ABC, abstractmethod
from typing import Any, Union, Optional, Dict
from copy import deepcopy
import os

ConfigTypes = Union[str, float, int, bool]


ConfigData = Dict[str, Union[ConfigTypes, "ConfigData"]]

nonetype = object()


class ValueToSectionError(Exception):
    """Exception raised when trying to overwrite a section with a value."""


class ExpectingSectionError(Exception):
    """Exception raised expectin a section, but got something else."""


class WrapConfig(ABC):
    def __init__(self, default_save: bool = True) -> None:
        super().__init__()
        self._truedata: ConfigData = {}
        self._default_save = default_save

    @property
    def data(self) -> ConfigData:
        return deepcopy(self._data)

    @property
    def _data(self) -> ConfigData:
        return self._truedata

    def set_data(self, data: ConfigData):
        self.clear()
        self.update(data)

    @abstractmethod
    def load(self):
        """load config from resource"""
        ...

    @abstractmethod
    def save(self):
        """save config to resource"""
        ...

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
        value: ConfigTypes = nonetype,
        save: Optional[bool] = None,
    ):
        """set config"""

        keys = list(keys)

        if value is nonetype:
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

    def get(self, *keys: str, default: ConfigTypes = None) -> Any:
        """get config value recursively with default value"""
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

        def deep_update(target: ConfigData, source: ConfigData) -> None:
            """Helper function to recursively update a dictionary."""
            for key, value in source.items():
                if isinstance(value, dict):
                    target[key] = deep_update(target.get(key, {}), value)
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

        def deep_update(target: ConfigData, source: ConfigData) -> None:
            """Helper function to recursively update a dictionary."""
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
    """Exception raised when trying to call a method on a SubConfig which is not allowed."""


class SubConfig(WrapConfig):
    def __init__(
        self,
        parent: WrapConfig,
        key: str,
    ) -> None:
        super().__init__()
        self._parent = parent
        self._key = key

    @property
    def _default_save(self) -> ConfigData:
        return self._parent._default_save

    @_default_save.setter
    def _default_save(self, value: ConfigData):
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

    @property
    def path(self):
        return self._path
