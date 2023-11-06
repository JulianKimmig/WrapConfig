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

        # Mock the open method and os methods
        m = mock_open()
        with patch("builtins.open", m), patch(
            "os.path.exists", return_value=False
        ), patch("os.makedirs"):
            manager = JSONWrapConfig(self.dummy_path)
            manager.set_data(self.data)
            manager.save()
            written_data = "".join(m().write.call_args_list[-1][0])

            self.assertEqual(json.dumps(self.data, indent=4), written_data)

    def test_save_file_existing_dir(self):
        from wrapconfig import JSONWrapConfig

        # Mock the open method and os methods
        m = mock_open(read_data=json.dumps(self.data))
        with patch("builtins.open", m), patch(
            "os.path.exists", return_value=True  # Mock to return True
        ), patch(
            "os.makedirs",
        ) as mock_makedirs:
            manager = JSONWrapConfig(self.dummy_path)
            manager.set_data(self.data)
            manager.save()

            # Assert that os.makedirs was not called
            with self.assertRaises(AssertionError):
                manager.save()
                mock_makedirs.assert_called_once()
