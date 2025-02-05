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
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(dump)

    def load(self) -> None:
        """Load configuration data from the YAML file."""
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.set_data(data)
