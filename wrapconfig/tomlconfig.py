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
        with open(self.path, "r", encoding="utf-8") as f:
            data = toml.load(f)
            self.set_data(data)

    def save(self) -> None:
        """Save the current configuration to the TOML file."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        dump = toml.dumps(self._data)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(dump)
