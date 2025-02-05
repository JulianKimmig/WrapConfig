# ======================
# File: tests/test_tomlconfig.py
# ======================
import unittest
from unittest.mock import patch, mock_open
import toml


class TestTOMLWrapConfig(unittest.TestCase):
    def setUp(self):
        self.dummy_path = "dummy_path.toml"
        self.data = {"key": "value"}

    def test_load_existing_file(self):
        from wrapconfig import TOMLWrapConfig

        # Create a mock that returns the TOML dump of self.data
        m = mock_open(read_data=toml.dumps(self.data))
        with patch("builtins.open", m):
            manager = TOMLWrapConfig(self.dummy_path)
            manager.load()
            self.assertEqual(manager.data, self.data)

    def test_save_file(self):
        from wrapconfig import TOMLWrapConfig

        with (
            patch.object(TOMLWrapConfig, "_write_file") as mocked_write_file,
            patch("os.makedirs") as mocked_makedirs,
        ):
            manager = TOMLWrapConfig(self.dummy_path, default_save=False)
            manager.set_data(self.data)
            manager.save()

            # We expect TOML dump to be created with default_flow_style=False.
            expected_dump = toml.dumps(self.data)

            mocked_write_file.assert_called_once_with(expected_dump)


if __name__ == "__main__":
    unittest.main()
