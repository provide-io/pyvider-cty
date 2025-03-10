import unittest

from pyvider.exceptions import ValidationError
from pyvider.cty import TFBool, TFMap, TFNumber, TFString


class TestTFMapType(unittest.TestCase):
    def setUp(self):
        self.string_map = TFMap(key_type=TFString(), value_type=TFString())
        self.number_map = TFMap(key_type=TFString(), value_type=TFNumber())
        self.bool_map = TFMap(key_type=TFString(), value_type=TFBool())

    # -------------------- VALIDATION TESTS --------------------
    def test_validate_valid_string_map(self):
        valid = {"name": "pyvider"}
        validated = self.string_map.validate(valid)
        assert validated == {"name": "pyvider"}

    def test_validate_valid_number_map(self):
        valid = {"count": 3, "max_retries": 5}
        self.number_map.validate(valid)
        self.assertEqual(valid["count"], 3)

    def test_validate_valid_bool_map(self):
        valid = {"is_active": True, "is_deleted": False}
        self.bool_map.validate(valid)
        self.assertEqual(valid["is_active"], True)

    def test_validate_invalid_key_type(self):
        invalid = {123: "invalid_key"}
        with self.assertRaises(ValidationError):
            self.string_map.validate(invalid)

    def test_validate_invalid_value_type(self):
        invalid = {"key": 42}
        with self.assertRaises(ValidationError):
            self.string_map.validate(invalid)

    def test_validate_empty_map(self):
        empty = {}
        self.string_map.validate(empty)
        self.assertEqual(len(empty), 0)

    def test_validate_nested_map(self):
        nested_map = TFMap(key_type=TFString(), value_type=self.string_map)
        valid = {"config": {"filename": "test.txt"}}
        nested_map.validate(valid)
        self.assertEqual(valid["config"]["filename"], "test.txt")

    def test_validate_nested_map_invalid(self):
        nested_map = TFMap(key_type=TFString(), value_type=self.string_map)
        invalid = {"config": {"filename": 123}}
        with self.assertRaises(ValidationError):
            nested_map.validate(invalid)

    # -------------------- EQUALITY AND COMPARISON TESTS --------------------
    def test_map_equality(self):
        map1 = TFMap(key_type=TFString(), value_type=TFNumber())
        map2 = TFMap(key_type=TFString(), value_type=TFNumber())
        self.assertTrue(map1.equal(map2))

    def test_map_inequality(self):
        map1 = TFMap(key_type=TFString(), value_type=TFNumber())
        map2 = TFMap(key_type=TFString(), value_type=TFString())
        self.assertFalse(map1.equal(map2))

    # -------------------- EDGE CASES --------------------
    def test_large_map(self):
        large_map = {str(i): i for i in range(1000)}
        self.number_map.validate(large_map)
        self.assertEqual(len(large_map), 1000)

    def test_map_with_none(self):
        invalid = {"key": None}
        with self.assertRaises(ValidationError):
            self.string_map.validate(invalid)

    def test_unhashable_key(self):
        invalid = {{"nested": "key"}: "value"}  # dict key is unhashable
        with self.assertRaises(ValidationError):
            self.string_map.validate(invalid)

    def test_map_with_nested_lists(self):
        tf_map = TFMap(value_type=TFString())
        nested_data = {"key1": ["item1", "item2"], "key2": ["item3"]}

        validated = tf_map.validate(nested_data)
        assert validated == {
            "key1": ["item1", "item2"],
            "key2": ["item3"]
        }

    def test_map_with_incompatible_nested(self):
        nested_map = TFMap(key_type=TFString(), value_type=self.string_map)
        invalid = {"nested": {"key": 42}}  # Key type valid, value type invalid
        with self.assertRaises(ValidationError):
            nested_map.validate(invalid)

    def test_validate_invalid_bool_map(self):
        invalid = {"is_active": TFNumber(1)}  # Incorrect type for boolean field
        with self.assertRaises(ValidationError) as excinfo:
            self.bool_map.validate(invalid)

        assert "Expected TFBool" in str(excinfo.exception)

if __name__ == "__main__":
    unittest.main()

