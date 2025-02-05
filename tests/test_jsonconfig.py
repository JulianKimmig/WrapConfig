import unittest
from unittest.mock import patch, mock_open
import json


class TestJSONWrapConfig(unittest.TestCase):
    def setUp(self):
        # Setting up a dummy path for tests
        self.dummy_path = "dummy_path.json"
        self.data = {"key": "value"}

    def test_load_existing_file(self):
        from wrapconfig import JSONWrapConfig

        # Mock the open method to return a string of data
        m = mock_open(read_data=json.dumps(self.data))
        with patch("builtins.open", m):
            manager = JSONWrapConfig(self.dummy_path)
            manager.load()
            self.assertEqual(manager.data, self.data)

    def test_save_file(self):
        from wrapconfig import JSONWrapConfig

        with (
            patch.object(JSONWrapConfig, "_write_file") as mocked_write_file,
            patch("os.makedirs") as mocked_makedirs,
        ):
            manager = JSONWrapConfig(self.dummy_path, default_save=False)
            manager.set_data(self.data)
            manager.save()

            # We expect JSON dump to be created with default_flow_style=False.
            expected_dump = json.dumps(self.data, indent=4)

            mocked_write_file.assert_called_once_with(expected_dump)

    def test_save_file_existing_dir(self):
        from wrapconfig import JSONWrapConfig

        # Mock the open method and os methods
        m = mock_open(read_data=json.dumps(self.data))
        with (
            patch("builtins.open", m),
            patch("os.path.exists", return_value=True),  # Mock to return True
            patch(
                "os.makedirs",
            ) as mock_makedirs,
        ):
            manager = JSONWrapConfig(self.dummy_path)
            manager.set_data(self.data)
            manager.save()

            # Assert that os.makedirs was not called
            with self.assertRaises(AssertionError):
                manager.save()
                mock_makedirs.assert_called_once()
