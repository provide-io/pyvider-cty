

import pytest
import unittest

from pyvider.cty.exceptions import PyviderError, ValidationError
from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString

class TestCtyListAdvanced(unittest.TestCase):
    """Advanced tests for the CtyList type to improve coverage."""

    def setUp(self):
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())

    def test_post_init_validates_element_type(self):
        """Test that __post_init__ validates element_type is a CtyType."""
        # Correct test - PyviderError was expected
        with self.assertRaises(ValidationError) as cm:
            CtyList(element_type="not_a_cty_type")

        # Verify error message contains expected text
        self.assertIn("Expected CtyType", str(cm.exception))

    def test_validate_tuple_as_list(self):
        data = ("apple", "banana", "cherry")
        result = self.string_list.validate(data)
        self.assertIsInstance(result, CtyList)
        self.assertEqual(len(result.value), 3)
        for i, item in enumerate(result.value):
            self.assertIsInstance(item, CtyString)
            self.assertEqual(item.value, data[i])

    def test_validate_none_raises_error(self):
        """Test that None raises ValidationError (not converted to empty list)."""
        with pytest.raises(ValidationError) as cm:
            self.string_list.validate(None)


    def test_validate_invalid_container_type(self):
        """Test validation fails for non-list/tuple containers."""
        with self.assertRaises(ValidationError) as cm:
            self.string_list.validate({"a": 1, "b": 2})

        # Check for expected error message
        self.assertIn("Expected list or tuple", str(cm.exception))

    def test_validate_homogeneous_list(self):
        """Test validation of a homogeneous list."""
        # Create a list of numbers
        data = [1, 2, 3, 4, 5]

        # Validate
        result = self.number_list.validate(data)

        # Assertions
        assert isinstance(result, CtyList)
        assert len(result.value) == 5
        assert all(isinstance(item, CtyNumber) for item in result.value)
        assert [item.value for item in result.value] == [1, 2, 3, 4, 5]


    def test_validate_heterogeneous_list_fails(self):
        """Test validation fails for heterogeneous lists."""
        # Create a mixed list
        data = [1, "two", 3, True]

        # Validate against number list
        with self.assertRaises(ValidationError):
            self.number_list.validate(data)

    def test_validate_nested_lists(self):
        """Test validation of nested lists."""
        # Create a list of lists
        nested_list_type = CtyList(element_type=self.string_list)
        data = [["a", "b"], ["c", "d", "e"]]

        # Validate
        result = nested_list_type.validate(data)

        # Assertions - proper type checking first
        assert isinstance(result, CtyList)
        assert len(result.value) == 2

        # Check first inner list
        assert isinstance(result.value[0], CtyList)
        assert len(result.value[0].value) == 2
        assert all(isinstance(item, CtyString) for item in result.value[0].value)
        assert [item.value for item in result.value[0].value] == ["a", "b"]

        # Check second inner list
        assert isinstance(result.value[1], CtyList)
        assert len(result.value[1].value) == 3
        assert all(isinstance(item, CtyString) for item in result.value[1].value)
        assert [item.value for item in result.value[1].value] == ["c", "d", "e"]

    def test_validate_nested_list_with_errors(self):
        """Test validation of nested lists with errors."""
        # Create a list of lists with an error in the nested list
        nested_list_type = CtyList(element_type=self.number_list)
        data = [[1, 2], [3, "four", 5]]  # "four" is not a number

        # Validate
        with self.assertRaises(ValidationError):
            nested_list_type.validate(data)

    def test_element_at_valid_index(self):
        """Test retrieving an element at a valid index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)

        # Get element at index
        element = self.string_list.element_at(validated, 1)

        # Assertions - verify type first, then value
        self.assertIsInstance(element, CtyString)
        self.assertEqual(element.value, "banana")

    def test_element_at_invalid_index(self):
        """Test retrieving an element at an invalid index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)

        # Try to get element at invalid index
        with self.assertRaises(IndexError):
            self.string_list.element_at(validated, 5)

    def test_element_at_negative_index(self):
        """Test retrieving an element at a negative index."""
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)

        element = self.string_list.element_at(validated, -1)

        self.assertIsInstance(element, CtyString)
        self.assertEqual(element.value, "cherry")


    def test_element_at_invalid_container(self):
        """Test element_at with an invalid container."""
        # Try to get element from non-list
        with self.assertRaises(ValidationError):
            self.string_list.element_at("not_a_list", 0)

    def test_equal_same_element_type(self):
        """Test equality with same element type."""
        # Create another string list
        other_string_list = CtyList(element_type=CtyString())

        # Test equality
        self.assertTrue(self.string_list.equal(other_string_list))

    def test_equal_different_element_type(self):
        """Test equality with different element type."""
        # Test inequality
        self.assertFalse(self.string_list.equal(self.number_list))

    def test_equal_non_list_type(self):
        """Test equality with non-list type."""
        # Create a CtyString
        string_type = CtyString()

        # Test inequality
        self.assertFalse(self.string_list.equal(string_type))

    def test_usable_as_same_type(self):
        """Test usable_as with same type."""
        # Create another string list
        other_string_list = CtyList(element_type=CtyString())

        # Test usability
        self.assertTrue(self.string_list.usable_as(other_string_list))

    def test_usable_as_different_type(self):
        """Test usable_as with different type."""
        # Test non-usability
        self.assertFalse(self.string_list.usable_as(self.number_list))

    def test_usable_as_non_list_type(self):
        """Test usable_as with non-list type."""
        # Create a CtyString
        string_type = CtyString()

        # Test non-usability
        self.assertFalse(self.string_list.usable_as(string_type))

    def test_string_representation(self):
        """Test string representation of CtyList."""
        # Create a list type
        list_type = CtyList(element_type=CtyString())

        # Test string representation
        self.assertEqual(str(list_type), "list(CtyString)")

    def test_string_representation_complex(self):
        """Test string representation of complex CtyList."""
        # Create a nested list type
        nested_list = CtyList(element_type=CtyList(element_type=CtyNumber()))

        # Test string representation
        self.assertEqual(str(nested_list), "list(list(CtyNumber))")

    def test_list_equality_operator(self):
        """Test the __eq__ operator."""
        # Create two identical list types
        list1 = CtyList(element_type=CtyString())
        list2 = CtyList(element_type=CtyString())

        # Test equality
        self.assertEqual(list1, list2)

    def test_list_inequality_operator(self):
        """Test inequality with different element types."""
        # Test inequality
        self.assertNotEqual(self.string_list, self.number_list)

    def test_repr_representation(self):
        """Test __repr__ representation."""
        # Test repr
        self.assertEqual(repr(self.string_list), "CtyList(element_type=CtyString())")
