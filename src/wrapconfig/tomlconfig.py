# ======================
# File: wrapconfig/tomlconfig.py
# ======================
"""
TOML file–based configuration implementation.
"""

import os
import toml
from .core import FileWrapConfig


class TOMLWrapConfig(FileWrapConfig):
    """
    A TOML-based configuration wrapper that reads from and writes to a TOML file.
    """

    def load(self) -> None:
        """Load configuration data from the TOML file."""
        self.set_data(toml.loads(self._read_file()))

    def save(self) -> None:
        """Save the current configuration to the TOML file."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        dump = toml.dumps(self._data)
        self._write_file(dump)
