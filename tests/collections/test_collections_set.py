#from attrs import define, evolve, field

import unittest

import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyBool, CtyNumber, CtySet, CtyString


class TestCtySetType(unittest.TestCase):
    def setUp(self):
        # Set up basic sets for testing
        self.string_set = CtySet(element_type=CtyString())
        self.number_set = CtySet(element_type=CtyNumber())
        self.bool_set = CtySet(element_type=CtyBool())

    # -------------------- VALIDATION TESTS --------------------
    def test_validate_valid_string_set(self):
        updated = self.string_set.validate({"one", "two", "three"})
        expected = {CtyString(value="one"), CtyString(value="two"), CtyString(value="three")}
        self.assertEqual(updated.value, expected)  # Compare CtyString instances

    def test_validate_invalid_string_set(self):
        with self.assertRaises(ValidationError):
            self.string_set.validate({"one", 42})  # Mixing int with str

    def test_validate_empty_set(self):
        updated = self.string_set.validate(set())
        self.assertEqual(updated.value, set())

    def test_validate_number_set(self):
        updated = self.number_set.validate({1, 2, 3.5})
        assert {x.value for x in updated.value} == {1, 2, 3.5}

    def test_validate_invalid_number_set(self):
        with self.assertRaises(ValidationError):
            self.number_set.validate({1, "two"})  # Mixing str with int

    def test_validate_non_iterable(self):
        tfset = CtySet(element_type=CtyString())
        with self.assertRaises(ValidationError, msg="Expected iterable, got int"):
            tfset.validate(123)

    # -------------------- EQUALITY TESTS --------------------
    def test_set_equality(self):
        set1 = self.string_set.validate({"one", "two"})
        set2 = self.string_set.validate({"two", "one"})  # Order doesn't matter
        self.assertEqual(set1, set2)


    def test_set_inequality(self):
        set1 = self.string_set.validate({"one", "two"})
        set2 = self.string_set.validate({"three"})
        self.assertNotEqual(set1, set2)

    def test_mixed_type_equality(self):
        str_set = self.string_set.validate({"one"})
        num_set = self.number_set.validate({1})
        self.assertNotEqual(str_set, num_set)

    # -------------------- OPERATIONAL TESTS --------------------
    def test_add_element_to_set(self):
        s = CtySet(element_type=CtyString())
        s.validate({"apple"})
        s.add("banana")
        assert s.value == {"apple", "banana"}, f"Expected set: {{'apple', 'banana'}}, got {s.value}"

    def test_add_element_to_set(self):
        tfset = CtySet(element_type=CtyString())
        tfset.add("apple")
        expected = {"apple"}
        self.assertEqual(set(tfset), expected)  # Ensure native conversion for comparison

    def test_remove_element_from_set(self):
        updated = self.string_set.validate({"one", "two"})
        evolved = updated.remove("two")

        # Debugging output
        print(f"Evolved Set: {evolved.value}")

        # Ensure "two" was removed
        self.assertNotIn(CtyString(value="two"), evolved.value)
        self.assertEqual(evolved.value, {CtyString(value="one")})

    def test_remove_non_existent_element(self):
        s = CtySet(element_type=CtyString())
        s.validate({"apple"})
        s.remove("orange")  # Remove non-existent element
        assert s.value == {"apple"} or s.value == set()

    # -------------------- EDGE CASES --------------------
    def test_nested_sets(self):
        s = CtySet(element_type=CtyString())
        with pytest.raises(ValidationError, match="Nested sets are not allowed"):
            s.validate({frozenset({"nested"})})  # Use frozenset to simulate nesting

    def test_set_with_none(self):
        with self.assertRaises(ValidationError):
            self.string_set.validate({None})  # None is not a valid string

    def test_large_set(self):
        large_set = {str(i) for i in range(1000)}
        updated = self.string_set.validate(large_set)
        self.assertEqual(len(updated.value), 1000)

    def test_mixed_type_equality(self):
        with self.assertRaises(ValidationError):
            self.string_set.validate({"one", 1})  # Intentionally mixing types

    def test_unhashable_items(self):
        with self.assertRaises(ValidationError):
            self.string_set.validate([{"unhashable": "dict"}])

if __name__ == "__main__":
    unittest.main()
