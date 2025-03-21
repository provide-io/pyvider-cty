
# tests/list/test_list_with_nested_types.py

import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyString, CtyNumber, CtyList, CtyTuple


class TestCtyListWithNestedTypes:
    """Tests for CtyList with complex nested types."""
    
    def test_list_of_tuples(self):
        """Test a list of tuples."""
        # Create a tuple type
        tuple_type = CtyTuple((str, int))
        
        # Create a list of tuples type
        list_of_tuples = CtyList(element_type=tuple_type)
        
        # Create data
        data = [("a", 1), ("b", 2), ("c", 3)]
        
        # Validate
        try:
            result = list_of_tuples.validate(data)
            # Check that values match
            assert len(result) == 3
            assert result[0] == ("a", 1)
            assert result[1] == ("b", 2)
            assert result[2] == ("c", 3)
        except Exception as e:
            pytest.fail(f"Validation raised exception: {e}")
    
    def test_list_of_tuples_invalid(self):
        """Test a list of tuples with invalid data."""
        # Create a tuple type
        tuple_type = CtyTuple((str, int))
        
        # Create a list of tuples type
        list_of_tuples = CtyList(element_type=tuple_type)
        
        # Create invalid data (wrong tuple structure)
        data = [("a", 1), ("b", "not_an_int"), ("c", 3)]
        
        # Validate
        with pytest.raises(ValidationError):
            list_of_tuples.validate(data)
    
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
        assert result == data
        assert len(result) == 3
        assert result[0] == ["a", "b"]
        assert result[1] == ["c", "d", "e"]
        assert result[2] == ["f"]
    
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
        assert result == data
        assert len(result) == 3
        assert result[1] == []
    
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
        assert result == data
        assert len(result) == 3
        assert result[0][0][0] == 1
        assert result[1][0][2] == 7
        assert result[2] == []
    
    def test_mixed_depth_list(self):
        """Test lists with mixed nesting depths."""
        # Create a nested list
        string_list = CtyList(element_type=CtyString())
        
        # Create data with inconsistent depths
        data = ["single_item", ["nested", "items"]]
        
        # This should fail since the second element is a list, not a string
        with pytest.raises(ValidationError):
            string_list.validate(data)
