import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyString, CtyNumber, CtyList


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
        assert len(result.value) == 3

        # Check that all elements are CtyList objects
        assert all(isinstance(item, CtyList) for item in result.value)

        # Check the contents of the first inner list
        assert len(result.value[0].value) == 2
        assert all(isinstance(item, CtyString) for item in result.value[0].value)
        assert [item.value for item in result.value[0].value] == ["a", "b"]

        # Check the contents of the second inner list
        assert len(result.value[1].value) == 3
        assert all(isinstance(item, CtyString) for item in result.value[1].value)
        assert [item.value for item in result.value[1].value] == ["c", "d", "e"]

        # Check the contents of the third inner list
        assert len(result.value[2].value) == 1
        assert all(isinstance(item, CtyString) for item in result.value[2].value)
        assert [item.value for item in result.value[2].value] == ["f"]

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
        assert len(result.value) == 3

        # Check that all elements are CtyList objects
        assert all(isinstance(item, CtyList) for item in result.value)

        # Check the contents of the first inner list
        assert len(result.value[0].value) == 2
        assert all(isinstance(item, CtyString) for item in result.value[0].value)
        assert [item.value for item in result.value[0].value] == ["a", "b"]

        # Check that the second inner list is empty
        assert len(result.value[1].value) == 0

        # Check the contents of the third inner list
        assert len(result.value[2].value) == 2
        assert all(isinstance(item, CtyString) for item in result.value[2].value)
        assert [item.value for item in result.value[2].value] == ["c", "d"]

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
        assert len(result.value) == 3

        # Check first element (list of lists)
        assert len(result.value[0].value) == 2
        assert all(isinstance(item, CtyList) for item in result.value[0].value)

        # Check first inner list
        assert len(result.value[0].value[0].value) == 2
        assert all(isinstance(item, CtyNumber) for item in result.value[0].value[0].value)
        assert [item.value for item in result.value[0].value[0].value] == [1, 2]

        # Check second inner list
        assert len(result.value[0].value[1].value) == 2
        assert all(isinstance(item, CtyNumber) for item in result.value[0].value[1].value)
        assert [item.value for item in result.value[0].value[1].value] == [3, 4]

        # Check second element (list with one list)
        assert len(result.value[1].value) == 1
        assert all(isinstance(item, CtyList) for item in result.value[1].value)

        # Check inner list of second element
        assert len(result.value[1].value[0].value) == 3
        assert all(isinstance(item, CtyNumber) for item in result.value[1].value[0].value)
        assert [item.value for item in result.value[1].value[0].value] == [5, 6, 7]

        # Check third element (empty list)
        assert len(result.value[2].value) == 0

    def test_mixed_depth_list(self):
        """Test lists with mixed nesting depths (should fail)."""
        # Create a nested list
        string_list = CtyList(element_type=CtyString())

        # Create data with inconsistent depths
        data = ["single_item", ["nested", "items"]]

        # This should fail since the second element is a list, not a string
        with pytest.raises(ValidationError):
            string_list.validate(data)
