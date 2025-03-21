
# tests/list/test_cty_collections_list_improve.py

import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyTuple

class TestCtyListAdvanced:
    """Advanced tests for the CtyList type to improve coverage."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())

    def test_post_init_validates_element_type(self):
        """Test that __post_init__ validates element_type is a CtyType."""
        # Try to create a CtyList with an invalid element_type
        with pytest.raises(ValidationError, match="Expected CtyType for element_type"):
            CtyList(element_type="not_a_cty_type")

    def test_validate_tuple_as_list(self):
        """Test that validate accepts tuples and converts them to lists."""
        # Create a tuple of strings
        data = ("apple", "banana", "cherry")

        # Validate
        result = self.string_list.validate(data)

        # Assertions
        assert isinstance(result, CtyList)
        assert result.value == ["apple", "banana", "cherry"]

    def test_validate_none_becomes_empty_list(self):
        """Test that None is treated as an empty list."""
        # Validate None
        result = self.string_list.validate(None)

        # Assertions
        assert isinstance(result, CtyList)
        assert result.value == []

    def test_validate_invalid_container_type(self):
        """Test validation fails for non-list/tuple containers."""
        # Try to validate a dictionary
        with pytest.raises(ValidationError):
            self.string_list.validate({"a": 1, "b": 2})

        # Try to validate a string (iterable but not list/tuple)
        with pytest.raises(ValidationError):
            self.string_list.validate("not_a_list")

    def test_validate_homogeneous_list(self):
        """Test validation of a homogeneous list."""
        # Create a list of numbers
        data = [1, 2, 3, 4, 5]

        # Validate
        result = self.number_list.validate(data)

        # Assertions
        assert isinstance(result, CtyList)
        assert result.value == [1, 2, 3, 4, 5]

    def test_validate_heterogeneous_list_fails(self):
        """Test validation fails for heterogeneous lists."""
        # Create a mixed list
        data = [1, "two", 3, True]

        # Validate against number list
        with pytest.raises(ValidationError):
            self.number_list.validate(data)

    def test_validate_nested_lists(self):
        """Test validation of nested lists."""
        # Create a list of lists
        nested_list_type = CtyList(element_type=self.string_list)
        data = [["a", "b"], ["c", "d", "e"]]

        # Validate
        result = nested_list_type.validate(data)

        # Assertions
        assert isinstance(result, CtyList)
        assert isinstance(result[0], CtyList)
        assert isinstance(result[1], CtyList)
        assert result[0].value == ["a", "b"]
        assert result[1].value == ["c", "d", "e"]

    def test_validate_nested_list_with_errors(self):
        """Test validation of nested lists with errors."""
        # Create a list of lists with an error in the nested list
        nested_list_type = CtyList(element_type=self.number_list)
        data = [[1, 2], [3, "four", 5]]  # "four" is not a number

        # Validate
        with pytest.raises(ValidationError):
            nested_list_type.validate(data)

    def test_element_at_valid_index(self):
        """Test retrieving an element at a valid index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)

        # Get element at index
        element = self.string_list.element_at(validated, 1)

        # Assertions
        assert element == "banana"

    def test_element_at_invalid_index(self):
        """Test retrieving an element at an invalid index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)

        # Try to get element at invalid index
        with pytest.raises(IndexError):
            self.string_list.element_at(validated, 5)

    def test_element_at_negative_index(self):
        """Test retrieving an element at a negative index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)

        # Get element at negative index
        element = self.string_list.element_at(validated, -1)

        # Assertions
        assert element == "cherry"

    def test_element_at_invalid_container(self):
        """Test element_at with an invalid container."""
        # Try to get element from non-list
        with pytest.raises(ValidationError):
            self.string_list.element_at("not_a_list", 0)

    def test_equal_same_element_type(self):
        """Test equality with same element type."""
        # Create another string list
        other_string_list = CtyList(element_type=CtyString())

        # Test equality
        assert self.string_list.equal(other_string_list)

    def test_equal_different_element_type(self):
        """Test equality with different element type."""
        # Test inequality
        assert not self.string_list.equal(self.number_list)

    def test_equal_non_list_type(self):
        """Test equality with non-list type."""
        # Create a CtyString
        string_type = CtyString()

        # Test inequality
        assert not self.string_list.equal(string_type)

    def test_usable_as_same_type(self):
        """Test usable_as with same type."""
        # Create another string list
        other_string_list = CtyList(element_type=CtyString())

        # Test usability
        assert self.string_list.usable_as(other_string_list)

    def test_usable_as_different_type(self):
        """Test usable_as with different type."""
        # Test non-usability
        assert not self.string_list.usable_as(self.number_list)

    def test_usable_as_non_list_type(self):
        """Test usable_as with non-list type."""
        # Create a CtyString
        string_type = CtyString()

        # Test non-usability
        assert not self.string_list.usable_as(string_type)

    def test_string_representation(self):
        """Test string representation of CtyList."""
        # Create a list type
        list_type = CtyList(element_type=CtyString())

        # Test string representation
        assert str(list_type) == "list(CtyString)"

    def test_string_representation_complex(self):
        """Test string representation of complex CtyList."""
        # Create a nested list type
        nested_list = CtyList(element_type=CtyList(element_type=CtyNumber()))

        # Test string representation
        assert str(nested_list) == "list(list(CtyNumber))"

    def test_list_equality_operator(self):
        """Test the __eq__ operator."""
        # Create two identical list types
        list1 = CtyList(element_type=CtyString())
        list2 = CtyList(element_type=CtyString())

        # Test equality
        assert list1 == list2

    def test_list_inequality_operator(self):
        """Test inequality with different element types."""
        # Test inequality
        assert self.string_list != self.number_list

    def test_repr_representation(self):
        """Test __repr__ representation."""
        # Test repr
        assert "CtyList" in repr(self.string_list)
        assert "element_type" in repr(self.string_list)


class TestCtyListWithNestedTypes:
    """Tests for CtyList with complex nested types."""

    def test_list_of_lists_of_strings(self):
        """Test a list of lists of strings."""
        # Create a nested list type
        list_of_strings = CtyList(element_type=CtyString())
        list_of_lists = CtyList(element_type=list_of_strings)

        # Create data
        data = [["a", "b"], ["c", "d", "e"], ["f"]]

        # Validate
        result = list_of_lists.validate(data)

        # Assertions
        assert isinstance(result, CtyList)
        assert len(result) == 3
        assert all(isinstance(item, CtyList) for item in result)
        assert result[0].value == ["a", "b"]
        assert result[1].value == ["c", "d", "e"]
        assert result[2].value == ["f"]

    def test_empty_list_elements(self):
        """Test a list with empty list elements."""
        # Create a nested list type
        list_of_strings = CtyList(element_type=CtyString())
        list_of_lists = CtyList(element_type=list_of_strings)

        # Create data with an empty list
        data = [["a", "b"], [], ["c", "d"]]

        # Validate
        result = list_of_lists.validate(data)

        # Assertions
        assert isinstance(result, CtyList)
        assert len(result) == 3
        assert all(isinstance(item, CtyList) for item in result)
        assert result[0].value == ["a", "b"]
        assert result[1].value == []
        assert result[2].value == ["c", "d"]

    def test_complex_nesting(self):
        """Test complex nested list structures."""
        # Create a complex nested structure: List of List of List of Number
        inner_list = CtyList(element_type=CtyNumber())
        middle_list = CtyList(element_type=inner_list)
        outer_list = CtyList(element_type=middle_list)

        # Create test data
        data = [
            [[1, 2], [3, 4]],
            [[5, 6, 7]],
            []
        ]

        # Validate
        result = outer_list.validate(data)

        # Assertions
        assert isinstance(result, CtyList)
        assert len(result) == 3
        assert all(isinstance(item, CtyList) for item in result)
        assert isinstance(result[0][0], CtyList)
        assert isinstance(result[1][0], CtyList)
        assert result[0][0].value == [1, 2]
        assert result[1][0].value == [5, 6, 7]
        assert len(result[2]) == 0

    def test_mixed_depth_list(self):
        """Test lists with mixed nesting depths (should fail)."""
        # Create a nested list
        string_list = CtyList(element_type=CtyString())

        # Create data with inconsistent depths
        data = ["single_item", ["nested", "items"]]

        # This should fail since the second element is a list, not a string
        with pytest.raises(ValidationError):
            string_list.validate(data)

    def test_list_access_methods(self):
        """Test advanced list access methods."""
        # Create a list
        string_list = CtyList(element_type=CtyString(), value=["a", "b", "c", "d", "e"])

        # Test slicing
        sliced = string_list[1:4]
        assert isinstance(sliced, CtyList)
        assert sliced.value == ["b", "c", "d"]

        # Test slice method
        sliced = string_list.slice(1, 4)
        assert isinstance(sliced, CtyList)
        assert sliced.value == ["b", "c", "d"]

        # Test negative slicing
        sliced = string_list[-3:]
        assert isinstance(sliced, CtyList)
        assert sliced.value == ["c", "d", "e"]

    def test_list_concat_method(self):
        """Test concatenation of lists."""
        # Create two lists
        list1 = CtyList(element_type=CtyString(), value=["a", "b"])
        list2 = CtyList(element_type=CtyString(), value=["c", "d"])

        # Test concat method
        result = list1.concat(list2)
        assert isinstance(result, CtyList)
        assert result.value == ["a", "b", "c", "d"]

        # Test with incompatible element types
        number_list = CtyList(element_type=CtyNumber(), value=[1, 2])
        with pytest.raises(ValidationError):
            list1.concat(number_list)

    def test_list_contains_method(self):
        """Test the contains method."""
        # Create a list
        string_list = CtyList(element_type=CtyString(), value=["a", "b", "c"])

        # Test contains with valid values
        assert string_list.contains("a") is True
        assert string_list.contains("d") is False

        # Test contains with invalid type (should return False, not raise)
        assert string_list.contains(123) is False
