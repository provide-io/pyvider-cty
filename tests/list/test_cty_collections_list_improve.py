
# tests/list/test_cty_collections_list_improve.py

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


class TestCtyListAdvanced:
    """Advanced tests for the CtyList type to improve coverage."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())

    def test_element_at_negative_index(self):
        """Test retrieving an element at a negative index."""
        # Create a CtyList with CtyString values
        validated = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="apple"), CtyString(value="banana"), CtyString(value="cherry")]
        )

        # Get element at negative index
        element = self.string_list.element_at(validated, -1)

        # Assertions
        assert isinstance(element, CtyString)
        assert element.value == "cherry"


    def test_repr_representation(self):
        """Test __repr__ representation."""
        # Based on the actual implementation, adjust expectations
        repr_str = repr(self.string_list)
        assert "CtyList" in repr_str

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
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert len(result.value) == 3

        # Check that all elements are CtyList objects
        assert all(isinstance(item, CtyList) for item in result.value)

        # Check the contents of the first inner list
        assert len(result[0].value) == 2
        assert all(isinstance(item, CtyString) for item in result[0].value)
        assert [item.value for item in result[0].value] == ["a", "b"]

        # Check the contents of the second inner list
        assert len(result[1].value) == 3
        assert all(isinstance(item, CtyString) for item in result[1].value)
        assert [item.value for item in result[1].value] == ["c", "d", "e"]

        # Check the contents of the third inner list
        assert len(result[2].value) == 1
        assert all(isinstance(item, CtyString) for item in result[2].value)
        assert [item.value for item in result[2].value] == ["f"]

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
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert len(result.value) == 3

        # Check that all elements are CtyList objects
        assert all(isinstance(item, CtyList) for item in result.value)

        # Check the contents of the first inner list
        assert len(result[0].value) == 2
        assert all(isinstance(item, CtyString) for item in result[0].value)
        assert [item.value for item in result[0].value] == ["a", "b"]

        # Check that the second inner list is empty
        assert len(result[1].value) == 0

        # Check the contents of the third inner list
        assert len(result[2].value) == 2
        assert all(isinstance(item, CtyString) for item in result[2].value)
        assert [item.value for item in result[2].value] == ["c", "d"]

    def test_mixed_depth_list(self):
        """Test lists with mixed nesting depths (should fail)."""
        # Create a nested list
        self.string_list = CtyList(element_type=CtyString())

        # Create data with inconsistent depths
        data = ["single_item", ["nested", "items"]]

        # This should fail since the second element is a list, not a string
        with pytest.raises(CtyListValidationError):
            self.string_list.validate(data)

# 🐍🏗️🧪
