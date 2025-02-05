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

        m = mock_open()
        with (
            patch("builtins.open", m),
            patch("os.path.exists", return_value=False),
            patch("os.makedirs"),
        ):
            manager = TOMLWrapConfig(self.dummy_path, default_save=False)
            manager.set_data(self.data)
            manager.save()
            # Get the written data from the mock
            written_calls = m().write.call_args_list
            written_data = "".join(call_arg[0][0] for call_arg in written_calls)
            self.assertEqual(toml.dumps(self.data), written_data)


if __name__ == "__main__":
    unittest.main()
