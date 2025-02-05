"""
JSON file–based configuration implementation.
"""

from __future__ import annotations
import json
import os
from typing import Optional, Type
from .core import FileWrapConfig


class JSONWrapConfig(FileWrapConfig):
    """
    A JSON-based configuration wrapper that reads from and writes to a JSON file.
    """

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

    def load(self) -> None:
        """Load configuration data from the JSON file."""
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f, cls=self._decoder)
            self.set_data(data)

    def save(self) -> None:
        """Save the current configuration to the JSON file."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        dump = json.dumps(self._data, indent=4, cls=self._encoder)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(dump)
