import unittest
from unittest.mock import patch, mock_open


class TestWrapConfig(unittest.TestCase):
    def setUp(self):
        from wrapconfig import WrapConfig

        class MockWrapConfig(WrapConfig):
            def load(self):
                pass  # No-op implementation

            def save(self):
                pass  # No-op implementation

        self.manager = MockWrapConfig()

    def test_set_and_save(self):
        with patch.object(self.manager, "save") as mock_save:
            self.manager.set("key", value="value")
            self.assertEqual(self.manager._data["key"], "value")
            mock_save.assert_called_once()

        with patch.object(self.manager, "save") as mock_save:
            self.manager["b"] = "c"
            self.assertEqual(self.manager._data["b"], "c")
            mock_save.assert_called_once()

    def test_set_withoutvalue(self):
        from wrapconfig import ValueToSectionError

        self.manager.set("key", "subkey1", "subkey2", "value")
        self.assertEqual(self.manager._data["key"]["subkey1"]["subkey2"], "value")

        with self.assertRaises(ValueToSectionError):
            self.manager.set("key", None)
        self.manager.clear("key")
        self.manager.set("key", None)
        self.assertEqual(self.manager._data["key"], None)

        with self.assertRaises(ValueError):
            self.manager.set("key")

    def test_set_with_subkeys(self):
        self.manager.set("key", "subkey1", "subkey2", value="value")
        self.assertEqual(self.manager._data["key"]["subkey1"]["subkey2"], "value")

    def test_set_without_autosave(self):
        with patch.object(self.manager, "save") as mock_save:
            self.manager = self.manager.__class__(default_save=False)
            self.manager.set("key", value="value")
            mock_save.assert_not_called()

    def test_set_with_save_override(self):
        with patch.object(self.manager, "save") as mock_save:
            self.manager.set("key", value="value", save=False)
            mock_save.assert_not_called()

    def test_set_error_handling(self):
        from wrapconfig import ExpectingSectionError

        self.manager._data["key"] = "value"
        with self.assertRaises(ExpectingSectionError):
            self.manager.set("key", "subkey", value="value2")

    def test_get_key(self):
        self.manager._data["key"] = "value"
        result = self.manager.get("key")
        self.assertEqual(result, "value")

    def test_get_subkeys(self):
        self.manager._data["key"] = {"subkey1": {"subkey2": "value"}}
        result = self.manager.get("key", "subkey1", "subkey2")
        self.assertEqual(result, "value")

    def test_get_default(self):
        result = self.manager.get("non_existent_key", default="default_val")
        self.assertEqual(result, "default_val")

    def test_get_no_key(self):
        result = self.manager.get()
        self.assertEqual(result, self.manager.data)

    def test_deep_new_key(self):
        result = self.manager.get("non_existent_key", "subkey1", "subkey2")
        self.assertEqual(result, None)
        self.assertEqual(self.manager.data, {"non_existent_key": {"subkey1": {}}})

    def test_get_error_handling(self):
        self.manager._data["key"] = "value"
        with self.assertRaises(TypeError):
            self.manager.get("key", "subkey")

    def test_update(self):
        initial_data = {"key1": "value1", "key2": {"subkey1": "value2"}}
        update_data = {"key2": {"subkey2": "value3"}, "key3": "value4"}
        self.manager.update(initial_data)
        self.manager.update(update_data)

        expected_data = {
            "key1": "value1",
            "key2": {"subkey1": "value2", "subkey2": "value3"},
            "key3": "value4",
        }
        self.assertEqual(self.manager._data, expected_data)

    def test_fill(self):
        initial_data = {"key1": "value1", "key2": {"subkey1": "value2"}}
        fill_data = {"key1": "value2", "key2": {"subkey2": "value3"}, "key3": "value4"}
        self.manager.update(initial_data)
        self.manager.fill(fill_data)

        expected_data = {
            "key1": "value1",
            "key2": {"subkey1": "value2", "subkey2": "value3"},
            "key3": "value4",
        }
        self.assertEqual(self.manager._data, expected_data)

        # conver no save in fill
        self.manager.fill(
            {
                "key4": {"subkey4": "value5"},
            },
            save=False,
        )
        expected_data.update({"key4": {"subkey4": "value5"}})

        self.assertEqual(self.manager._data, expected_data)

        self.manager.fill(
            {"key1": {"bad_value": "a"}},
        )

        self.assertEqual(self.manager._data, expected_data)

    def test_data_property(self):
        initial_data = {"key": "value"}
        self.manager.set_data(initial_data)
        data_copy = self.manager.data
        data_copy["key"] = "modified"

        self.assertEqual(self.manager._data["key"], "value")
        self.assertNotEqual(data_copy["key"], self.manager._data["key"])

    def test_clear(self):
        self.manager.set_data({"key": "value"})
        self.manager.clear()
        self.assertEqual(self.manager.data, {})
        self.manager.set_data({"key": {"subkey": "value"}})
        with self.assertRaises(KeyError):
            self.manager.clear("key", "subkey", "subkey2")
        with self.assertRaises(KeyError):
            self.manager.clear("key", "subkey1", "subkey2")
        self.manager.clear("key", "subkey")
        self.assertEqual(self.manager.data, {"key": {}})
        with self.assertRaises(KeyError):
            self.manager.clear("key", "subkey")

    def test_set_data(self):
        self.manager.set_data({"key": "value"})
        self.assertEqual(self.manager.data, {"key": "value"})

    def test_subconfig(self):
        from wrapconfig.core import SubConfig

        self.manager.set_data({"A": {"B": {"C": "value"}}})
        subc = self.manager["A"]
        self.assertIsInstance(subc, SubConfig)
        self.assertEqual(subc.data, {"B": {"C": "value"}})
        subc.set("D", "value2")
        self.assertEqual(self.manager.data, {"A": {"B": {"C": "value"}, "D": "value2"}})

    def test_direct_assignment(self):
        from wrapconfig import ValueToSectionError

        self.manager["level1"] = "value1"

        expected_data = {"level1": "value1"}
        self.assertEqual(self.manager._data, expected_data)

        self.manager["level2"]["level3"]["level4"] = "value3"
        expected_data.update({"level2": {"level3": {"level4": "value3"}}})
        self.assertEqual(self.manager._data, expected_data)

        # content thas is alreaady a section cannot be overwritten with a value
        with self.assertRaises(ValueToSectionError):
            self.manager["level2"]["level3"] = "value2"

    def test_abstract_methods(self):
        from wrapconfig import WrapConfig

        class DummyWrapConfig(WrapConfig):
            def load(self):
                super().load()

            def save(self):
                super().save()

        dummy = DummyWrapConfig()
        dummy.load()  # This will cover the abstract load method
        dummy.save()  # This will cover the abstract save method

    def test_load_method(self):
        from wrapconfig.core import SubConfigError

        self.manager.set_data({"key": {"subkey": "value"}})
        # Test that calling load method raises SubConfigError
        sub_config = self.manager["key"]
        with self.assertRaises(SubConfigError) as context:
            sub_config.load()
            # Check the error message
            self.assertEqual(str(context.exception), "Cannot load a SubConfig.")

    def test_repr_method(self):
        # Test the representation string
        self.manager.set_data({"key": {"subkey": "value"}})
        sub_config = self.manager["key"]
        expected_repr = f"<SubConfig key=key parent={self.manager}>"
        self.assertEqual(repr(sub_config), expected_repr)

    def test_direct_assinment_and_then_set(self):
        from wrapconfig import ValueToSectionError

        self.manager["level1"]
        self.manager["level1"] = "value1"

        expected_data = {"level1": "value1"}
        self.assertEqual(self.manager._data, expected_data)

    def test_iter(self):
        from wrapconfig import WrapConfig

        self.manager.set_data({"key": {"subkey": "value"}, "v": 1})
        d = dict(**self.manager)
        assert isinstance(d["key"], WrapConfig)
        assert d["v"] == 1
        assert d["key"]["subkey"] == "value"
