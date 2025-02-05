"""
YAML file–based configuration implementation.
"""

import os
import yaml
from .core import FileWrapConfig


class YAMLWrapConfig(FileWrapConfig):
    """
    A YAML-based configuration wrapper that reads from and writes to a YAML file.
    """

    def save(self) -> None:
        """Save the current configuration to a YAML file."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        dump = yaml.dump(self._data)
        self._write_file(dump)

    def load(self) -> None:
        """Load configuration data from the YAML file."""
        self.set_data(yaml.safe_load(self._read_file()))
