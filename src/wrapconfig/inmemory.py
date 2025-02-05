"""
In-memory configuration implementation.
"""

from .core import WrapConfig, ConfigData


class InMemoryConfig(WrapConfig):
    """
    An in-memory configuration that does not persist to disk.

    The configuration is backed up internally to simulate saving and loading.
    """

    def __init__(self, default_save: bool = True) -> None:
        super().__init__(default_save=default_save)
        self._backup: ConfigData = {}

    def save(self) -> None:
        """Simulate saving by storing a backup of the current configuration."""
        self._backup = self.data

    def load(self) -> None:
        """Restore configuration from the in-memory backup."""
        self.set_data(self._backup)
