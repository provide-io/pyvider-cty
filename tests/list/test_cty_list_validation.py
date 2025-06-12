#
# tests/list/test_cty_list_validation.py
#

import pytest

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty import (
    CtyValue,
    CtyBool,
    CtyList,
    CtyNumber,
    CtyString,
    CtyTuple,
)

class TestCtyListValidation:
    """Advanced tests for the CtyList type to improve coverage."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())

    @pytest.mark.asyncio
    async def test_element_at_valid_index(self):
        """Test retrieving an element at a valid index."""
        # Create a list with strings
        list_obj = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="apple"), CtyString(value="banana"), CtyString(value="cherry")]
        )

        # Get element at index
        element = list_obj.element_at(list_obj, 1)

        # Check the value, not the wrapper type
        assert element.value == "banana"

    def test_post_init_validates_element_type(self):
        """Test that __post_init__ validates element_type is a CtyType."""
        # Try to create a CtyList with an invalid element_type
        with pytest.raises(CtyListValidationError, match="Expected CtyType for element_type"):
            CtyList(element_type="not_a_cty_type")

    def test_validate_tuple_as_list(self):
        """Test that validate accepts tuples and converts them to lists."""
        # Create a tuple of strings
        data = ("apple", "banana", "cherry")

        # Validate
        result = self.string_list.validate(data)

        # Assertions
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert len(result.value) == 3
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyString) for item in result.value)
        assert [item.value for item in result.value] == ["apple", "banana", "cherry"]

    def test_validate_none_raises_error(self):
        """Test that None is rejected with error (not converted to empty list)."""
        with pytest.raises(CtyListValidationError, match="Input to CtyList.validate cannot be None."):
            self.string_list.validate(None)

    def test_validate_invalid_container_type(self):
        """Test validation fails for non-list/tuple containers."""
        # Try to validate a dictionary
        with pytest.raises(CtyListValidationError, match="Expected list, tuple, or CtyValue list, got dict"):
            self.string_list.validate({"a": 1, "b": 2})

        # Try to validate a string (iterable but not list/tuple)
        with pytest.raises(CtyListValidationError, match="Expected list, tuple, or CtyValue list, got str"):
            self.string_list.validate("not_a_list")

    def test_validate_homogeneous_list(self):
        """Test validation of a homogeneous list."""
        # Create a list of numbers
        data = [1, 2, 3, 4, 5]

        # Validate
        result = self.number_list.validate(data)

        # Assertions
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert len(result.value) == 5
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyNumber) for item in result.value)
        assert [item.value for item in result.value] == [1, 2, 3, 4, 5]

    def test_validate_heterogeneous_list_fails(self):
        """Test validation fails for heterogeneous lists."""
        # Create a mixed list
        data = [1, "two", 3, True]

        # Validate against number list
        with pytest.raises(CtyListValidationError):
            self.number_list.validate(data)

    def test_element_at_invalid_index(self):
        """Test retrieving an element at an invalid index."""
        # Create and validate a list
        data = ["apple", "banana", "cherry"]
        validated = self.string_list.validate(data)

        with pytest.raises(IndexError) as exc:
            self.string_list.element_at(validated, 5)

    def test_cty_list_validate_empty_list(self):
        """Test validation of an empty list."""
        self.string_list = CtyList(element_type=CtyString())
        validated = self.string_list.validate([])

        # Test that we get back a CtyList
        assert isinstance(validated, CtyValue)
        assert isinstance(validated.type, CtyList)

        # Test that the value is an empty list
        assert validated.value == []

        # Test that the length is 0
        assert len(validated) == 0

    def test_cty_list_validate_success(self):
        """Test successful validation of a simple string list."""
        self.string_list = CtyList(element_type=CtyString())
        validated = self.string_list.validate(["apple", "banana", "cherry"])

        # Test that we get the list structure back
        assert len(validated) == 3
        assert validated[0].value == "apple"
        assert validated[1].value == "banana"
        assert validated[2].value == "cherry"

    def test_cty_list_validate_failure(self):
        """Test validation failure with mixed types."""
        self.string_list = CtyList(element_type=CtyString())

        # Second element is a number, not a string
        with pytest.raises(CtyListValidationError, match="List validation error: CtyList validation failed:\n - Item 1 \\('123'\\): String validation error: Value must be a string, got int"):
            self.string_list.validate(["apple", 123, "cherry"])


    def test_cty_list_validate_none(self):
        """Test validation of None, which should raise an error."""
        self.string_list = CtyList(element_type=CtyString())

        # None should raise an error, not return an empty list
        with pytest.raises(CtyListValidationError, match="Input to CtyList.validate cannot be None."):
            self.string_list.validate(None)

    def test_cty_list_invalid_element_type(self):
        """Test constructor with invalid element_type."""
        with pytest.raises(CtyListValidationError, match="Expected CtyType for element_type"):
            CtyList(element_type="invalid")  # Non-CtyType passed

    def test_cty_list_invalid_structure(self):
        """Test validation with non-list structure."""
        list_of_numbers = CtyList(element_type=CtyNumber())
        with pytest.raises(CtyListValidationError, match="Expected list, tuple, or CtyValue list, got str"):
            list_of_numbers.validate("not_a_list")  # String is not a valid list

    def test_cty_list_validate_none_in_list(self):
        """Test validation with None element in list."""
        self.string_list = CtyList(element_type=CtyString())

        # None element should cause validation failure
        with pytest.raises(CtyListValidationError, match="List validation error: CtyList validation failed:\n - Item 0 \\('None'\\): String validation error: String value cannot be None."):
            self.string_list.validate([None, "value"])

    def test_element_at_invalid_container(self):
        """Test element_at with an invalid container."""
        # Try to get element from non-list
        with pytest.raises(CtyListValidationError):
            self.string_list.element_at("not_a_list", 0)

    def test_usable_as_non_list_type(self):
        """Test usable_as with non-list type."""
        # Create a CtyString
        string_type = CtyString()

        # Test non-usability
        assert not self.string_list.usable_as(string_type)

# 🐍🏗️🧪
