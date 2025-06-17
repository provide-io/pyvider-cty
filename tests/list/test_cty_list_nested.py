#
# tests/list/test_cty_list_nested.py
#

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyNumber,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import CtyListValidationError


class TestCtyListWithNestedTypes:
    """Tests for CtyList with complex nested types."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())
        self.nested_list = CtyList(element_type=CtyList(element_type=CtyNumber()))


    def test_list_of_lists_of_strings(self) -> None:
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

        # Check that all elements are CtyValue objects containing CtyList objects
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyList) for item in result.value)

        # Check the contents of the first inner list
        assert len(result.value[0].value) == 2
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyString) for item in result.value[0].value)
        assert [item.value for item in result.value[0].value] == ["a", "b"]

        # Check the contents of the second inner list
        assert len(result.value[1].value) == 3
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyString) for item in result.value[1].value)
        assert [item.value for item in result.value[1].value] == ["c", "d", "e"]

        # Check the contents of the third inner list
        assert len(result.value[2].value) == 1
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyString) for item in result.value[2].value)
        assert [item.value for item in result.value[2].value] == ["f"]

    def test_complex_nesting(self) -> None:
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
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert len(result.value) == 3

        # Check first element (list of lists)
        assert len(result.value[0].value) == 2
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyList) for item in result.value[0].value)

        # Check first inner list
        assert len(result.value[0].value[0].value) == 2
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyNumber) for item in result.value[0].value[0].value)
        assert [item.value for item in result.value[0].value[0].value] == [1, 2]

        # Check second inner list
        assert len(result.value[0].value[1].value) == 2
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyNumber) for item in result.value[0].value[1].value)
        assert [item.value for item in result.value[0].value[1].value] == [3, 4]

        # Check second element (list with one list)
        assert len(result.value[1].value) == 1
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyList) for item in result.value[1].value)

        # Check inner list of second element
        assert len(result.value[1].value[0].value) == 3
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyNumber) for item in result.value[1].value[0].value)
        assert [item.value for item in result.value[1].value[0].value] == [5, 6, 7]

        # Check third element (empty list)
        assert len(result.value[2].value) == 0

    def test_cty_list_validate_nested_lists(self) -> None:
        """Test validation of nested lists."""
        # Create a list of lists
        self.nested_list = CtyList(element_type=self.string_list)
        data = [["a", "b"], ["c", "d", "e"]]

        # Validate
        result = self.nested_list.validate(data)

        # Assertions - proper type checking first
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert len(result.value) == 2

        # Check first inner list - should be a CtyValue containing a CtyList, not a direct CtyList
        assert isinstance(result.value[0], CtyValue)
        assert isinstance(result.value[0].type, CtyList)
        assert len(result.value[0].value) == 2
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyString) for item in result.value[0].value)
        assert [item.value for item in result.value[0].value] == ["a", "b"]

        # Check second inner list
        assert isinstance(result.value[1], CtyValue)
        assert isinstance(result.value[1].type, CtyList)
        assert len(result.value[1].value) == 3
        assert all(isinstance(item, CtyValue) and isinstance(item.type, CtyString) for item in result.value[1].value)
        assert [item.value for item in result.value[1].value] == ["c", "d", "e"]

    def test_validate_nested_list_with_errors(self) -> None:
        """Test validation of nested lists with errors."""
        # Create a list of lists with an error in the nested list
        self.nested_list = CtyList(element_type=self.number_list)
        data = [[1, 2], [3, "four", 5]]  # "four" is not a number

        # Validate
        with pytest.raises(CtyListValidationError):
            self.nested_list.validate(data)

# 🐍🏗️🧪
