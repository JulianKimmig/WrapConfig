import os
import sys
import types

PINLINED_DEFAULT_PACKAGE = 'wrapconfig'
PINLINER_MODULE_NAME = 'pinliner_loader'
loader_version = '0.2.0'

FORCE_EXC_HOOK = None

inliner_importer_code = '''
import imp
import marshal
import os
import struct
import sys
import types


class InlinerImporter(object):
    version = '%(loader_version)s'
    def __init__(self, data, datafile, set_excepthook=True):
        self.data = data
        self.datafile = datafile
        if set_excepthook:
            sys.excepthook = self.excepthook

    @staticmethod
    def excepthook(type, value, traceback):
        import traceback as tb
        tb.print_exception(type, value, traceback)

    def find_module(self, fullname, path):
        module = fullname in self.data
        if module:
            return self

    def get_source(self, fullname):
        __, start, end, ts = self.data[fullname]
        with open(self.datafile) as datafile:
            datafile.seek(start)
            code = datafile.read(end - start)
        return code

    def get_code(self, fullname, filename):
        py_ts = self.data[fullname][3]
        try:
            with open(fullname + '.pyc', 'rb') as pyc:
                pyc_magic = pyc.read(4)
                pyc_ts = struct.unpack('<I', pyc.read(4))[0]
                if pyc_magic == imp.get_magic() and pyc_ts == py_ts:
                    return marshal.load(pyc)
        except:
            pass

        code = self.get_source(fullname)
        compiled_code = compile(code, filename, 'exec')

        try:
            with open(fullname + '.pyc', 'wb') as pyc:
                pyc.write(imp.get_magic())
                pyc.write(struct.pack('<I', py_ts))
                marshal.dump(compiled_code, pyc)
        except:
            pass
        return compiled_code

    def load_module(self, fullname):
        # If the module it's already in there we'll reload but won't remove the
        # entry if we fail
        exists = fullname in sys.modules

        module = types.ModuleType(fullname)
        module.__loader__ = self

        is_package = self.data[fullname][0]
        path = fullname.replace('.', os.path.sep)
        if is_package:
            module.__package__ = fullname
            module.__file__ = os.path.join(path, '__init__.py')
            module.__path__ = [path]
        else:
            module.__package__ = fullname.rsplit('.', 1)[0]
            module.__file__ = path + '.py'

        sys.modules[fullname] = module

        try:
            compiled_code = self.get_code(fullname, module.__file__)
            exec compiled_code in module.__dict__
        except:
            if not exists:
                del sys.modules[fullname]
            raise

        return module
''' % {'loader_version': loader_version}

'''
from abc import ABC, abstractmethod
from typing import Any, Union, Optional, Dict
from copy import deepcopy
import os

ConfigTypes = Union[str, float, int, bool]


ConfigData = Dict[str, Union[ConfigTypes, "ConfigData"]]


class WrapConfig(ABC):
    def __init__(self, default_save: bool = True) -> None:
        super().__init__()
        self._data: ConfigData = {}
        self._default_save = default_save

    @property
    def data(self) -> ConfigData:
        return deepcopy(self._data)

    @abstractmethod
    def load(self):
        """load config from resource"""
        ...

    @abstractmethod
    def save(self):
        """save config to resource"""
        ...

    def set(
        self,
        key: str,
        *subkeys: str,
        value: ConfigTypes,
        save: Optional[bool] = None,
    ):
        """set config"""
        if key not in self._data:
            self._data[key] = {}

        _datadict = self._data
        _key = key
        if not isinstance(_datadict, dict):
            raise TypeError(
                f"Expected dict, got {type(_datadict)}, this might be the result of a key or subkey conflict, which is already a value."
            )
        for subkey in subkeys:
            if subkey not in _datadict[_key]:
                _datadict[_key][subkey] = {}
            _datadict = _datadict[_key]
            _key = subkey
            if not isinstance(_datadict, dict):
                raise TypeError(
                    f"Expected dict, got {type(_datadict)}, this might be the result of a key or subkey conflict, which is already a value."
                )

        _datadict[_key] = value
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

    def update(self, data: ConfigData):
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

        self._data = deep_update(self._data, data)

    def fill(self, data: ConfigData, save: Optional[bool] = None):
        """Deeply update the configuration with the provided data.
        If a key is not present in the configuration, it will be added.
        If a key is present in the configuration, it will not be updated.
        """

        def deep_update(target: ConfigData, source: ConfigData) -> None:
            """Helper function to recursively update a dictionary."""
            for key, value in source.items():
                print(key, value)
                if isinstance(value, dict):
                    if key not in target:
                        target[key] = {}
                    elif not isinstance(target[key], dict):
                        raise TypeError(
                            f"Expected dict, got {type(target[key])}, this might be the result of a key or subkey conflict, which is already a value."
                        )
                    target[key] = deep_update(target[key], value)
                else:
                    if key not in target:
                        target[key] = value
            return target

        self._data = deep_update(self._data, data)

        if save is None:
            save = self._default_save

        if save:
            self.save()


class FileWrapConfig(WrapConfig):
    """WrapConfig that saves and loads from a file"""

    def __init__(self, path, default_save: bool = True) -> None:
        self._path = path
        super().__init__(default_save)
        if os.path.exists(self.path):
            self.load()
        if self._data is None:
            self._data = {}

    @property
    def path(self):
        return self._path
from .core import WrapConfig


class InMemoryConfig(WrapConfig):
    def __init__(self, *args, **kwargs) -> None:
        self._backup = {}
        super().__init__(*args, **kwargs)

    def save(self):
        self._backup = self.data

    def load(self):
        self._data = self._backup
from __future__ import annotations
from typing import Type, Optional
from .core import FileWrapConfig

import json
import os


class JSONWrapConfig(FileWrapConfig):
    def __init__(
        self,
        path: str,
        default_save: bool = True,
        encoder: Optional[Type[json.JSONEncoder]] = None,
        decoder: Optional[Type[json.JSONDecoder]] = None,
    ) -> None:
        self._encoder = encoder
        self._decoder = decoder

        super().__init__(path=path, default_save=default_save)

    def load(self):
        with open(self.path, "r") as f:
            self._data = json.load(f, cls=self._decoder)

    def save(self):
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

        dump = json.dumps(self._data, indent=4, cls=self._encoder)
        with open(self.path, "w") as f:
            f.write(dump)
from typing import Optional, Type
import os
from .core import FileWrapConfig
import yaml


class YAMLWrapConfig(FileWrapConfig):
    def save(self):
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

        dump = yaml.dump(self._data)
        with open(self.path, "w") as f:
            f.write(dump)

    def load(self):
        with open(self.path, "r") as f:
            self._data = yaml.safe_load(f)
from .jsonconfig import JSONWrapConfig
from .core import WrapConfig, FileWrapConfig
from .inmemory import InMemoryConfig

__all__ = [
    "JSONWrapConfig",
    "WrapConfig",
    "InMemoryConfig",
    "FileWrapConfig",
]

# YAML support is optional
try:
    from .yamlconf import YAMLWrapConfig

    __all__.append("YAMLWrapConfig")
except (ImportError, ModuleNotFoundError):
    pass

__version__ = "0.1.5"
'''


inliner_packages = {
    "wrapconfig.core": [
        0, 2888, 7881, 1697034120],
    "wrapconfig.inmemory": [
        0, 7881, 8185, 1697034120],
    "wrapconfig.jsonconfig": [
        0, 8185, 9109, 1697034120],
    "wrapconfig.yamlconf": [
        0, 9109, 9593, 1697034120],
    "wrapconfig": [
        1, 9593, 10020, 1697038653]
}


def prepare_package():
    # Loader's module name changes withh each major version to be able to have
    # different loaders working at the same time.
    module_name = PINLINER_MODULE_NAME + '_' + loader_version.split('.')[0]

    # If the loader code is not already loaded we create a specific module for
    # it.  We need to do it this way so that the functions in there are not
    # compiled with a reference to this module's global dictionary in
    # __globals__.
    module = sys.modules.get(module_name)
    if not module:
        module = types.ModuleType(module_name)
        module.__package__ = ''
        module.__file__ = module_name + '.py'
        exec inliner_importer_code in module.__dict__
        sys.modules[module_name] = module

    # We cannot use __file__ directly because on the second run __file__ will
    # be the compiled file (.pyc) and that's not the file we want to read.
    filename = os.path.splitext(__file__)[0] + '.py'

    # Add our own finder and loader for this specific package if it's not
    # already there.
    # This must be done before we initialize the package, as it may import
    # packages and modules contained in the package itself.
    for finder in sys.meta_path:
        if (isinstance(finder, module.InlinerImporter) and
                finder.data == inliner_packages):
            importer = finder
    else:
        # If we haven't forced the setting of the uncaught exception handler
        # we replace it only if it hasn't been replace yet, this is because
        # CPython default handler does not use traceback or even linecache, so
        # it never calls get_source method to get the code, but for example
        # iPython does, so we don't need to replace the handler.
        if FORCE_EXC_HOOK is None:
            set_excepthook = sys.__excepthook__ == sys.excepthook
        else:
            set_excepthook = FORCE_EXC_HOOK

        importer = module.InlinerImporter(inliner_packages, filename,
                                          set_excepthook)
        sys.meta_path.append(importer)

    __, start, end, ts = inliner_packages[PINLINED_DEFAULT_PACKAGE]
    with open(filename) as datafile:
        datafile.seek(start)
        code = datafile.read(end - start)

    # We need everything to be local variables before we clear the global dict
    def_package = PINLINED_DEFAULT_PACKAGE
    name = __name__
    filename = def_package + '/__init__.py'
    compiled_code = compile(code, filename, 'exec')

    # Prepare globals to execute __init__ code
    globals().clear()
    # If we've been called directly we cannot set __path__
    if name != '__main__':
        globals()['__path__'] = [def_package]
    else:
        def_package = None
    globals().update(__file__=filename,
                     __package__=def_package,
                     __name__=name,
                     __loader__=importer)


    exec compiled_code


# Prepare loader's module and populate this namespace only with package's
# __init__
prepare_package()
