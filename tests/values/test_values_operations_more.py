
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

from pyvider.cty.values.operations import (
    equals, add, subtract, multiply, divide, modulo, negate,
    get_attribute, get_element, length, contains, concat_lists,
    merge_maps, slice_string, slice_list
)
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtySet, CtyObject, CtyTuple
)
from pyvider.cty.values.base import CtyValue
from pyvider.cty.exceptions import CtyError, TypeMismatchError


class TestEqualsOperation:
    """Tests for the equals operation."""
    
    def test_equals_same_value(self):
        """Test equality of identical values."""
        # Create two identical string values
        val1 = CtyValue(type_=CtyString(), value="test")
        val2 = CtyValue(type_=CtyString(), value="test")
        
        # Compare
        result = equals(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyBool()
        assert result.value is True
    
    def test_equals_different_values(self):
        """Test equality of different values of same type."""
        # Create two different string values
        val1 = CtyValue(type_=CtyString(), value="test1")
        val2 = CtyValue(type_=CtyString(), value="test2")
        
        # Compare
        result = equals(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyBool()
        assert result.value is False
    
    def test_equals_different_types(self):
        """Test equality of values with different types."""
        # Create values of different types
        val1 = CtyValue(type_=CtyString(), value="123")
        val2 = CtyValue(type_=CtyNumber(), value=123)
        
        # Compare
        result = equals(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyBool()
        assert result.value is False
    
    def test_equals_null_values(self):
        """Test equality of null values."""
        # Create null values
        val1 = CtyValue(type_=CtyString(), is_null=True)
        val2 = CtyValue(type_=CtyString(), is_null=True)
        
        # Compare
        result = equals(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyBool()
        assert result.value is True
    
    def test_equals_unknown_values(self):
        """Test equality of unknown values returns unknown."""
        # Create unknown values
        val1 = CtyValue(type_=CtyString(), is_unknown=True)
        val2 = CtyValue(type_=CtyString(), value="test")
        
        # Compare
        result = equals(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyBool()
        assert result.is_known is False  # Result should be unknown
    
    def test_equals_list_values(self):
        """Test equality of list values."""
        # Create list values
        list_type = CtyList(element_type=CtyString())
        val1 = CtyValue(type_=list_type, value=["a", "b"])
        val2 = CtyValue(type_=list_type, value=["a", "b"])
        val3 = CtyValue(type_=list_type, value=["a", "c"])
        
        # Compare equal lists
        result = equals(val1, val2)
        assert result.value is True
        
        # Compare different lists
        result = equals(val1, val3)
        assert result.value is False
    
    def test_equals_map_values(self):
        """Test equality of map values."""
        # Create map values
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        val1 = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        val2 = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        val3 = CtyValue(type_=map_type, value={"a": 1, "b": 3})
        
        # Compare equal maps
        result = equals(val1, val2)
        assert result.value is True
        
        # Compare different maps
        result = equals(val1, val3)
        assert result.value is False


class TestArithmeticOperations:
    """Tests for arithmetic operations."""
    
    def test_add_numbers(self):
        """Test adding two numbers."""
        # Create number values
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("123"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("456"))
        
        # Add
        result = add(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == Decimal("579")
    
    def test_add_strings(self):
        """Test concatenating two strings."""
        # Create string values
        val1 = CtyValue(type_=CtyString(), value="Hello, ")
        val2 = CtyValue(type_=CtyString(), value="world!")
        
        # Add
        result = add(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyString()
        assert result.value == "Hello, world!"
    
    def test_add_lists(self):
        """Test concatenating two lists."""
        # Create list values
        list_type = CtyList(element_type=CtyString())
        val1 = CtyValue(type_=list_type, value=["a", "b"])
        val2 = CtyValue(type_=list_type, value=["c", "d"])
        
        # Add
        result = add(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == list_type
        assert result.value == ["a", "b", "c", "d"]
    
    def test_add_incompatible_types(self):
        """Test adding incompatible types raises error."""
        # Create values of different types
        val1 = CtyValue(type_=CtyString(), value="test")
        val2 = CtyValue(type_=CtyNumber(), value=123)
        
        # Add should raise TypeError
        with pytest.raises(TypeError):
            add(val1, val2)
    
    def test_add_unknown_values(self):
        """Test adding with unknown values returns unknown."""
        # Create an unknown value
        val1 = CtyValue(type_=CtyNumber(), value=123)
        val2 = CtyValue(type_=CtyNumber(), is_unknown=True)
        
        # Add
        result = add(val1, val2)
        
        # Verify result is unknown
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.is_known is False
    
    def test_add_null_values(self):
        """Test adding with null values returns null."""
        # Create a null value
        val1 = CtyValue(type_=CtyNumber(), value=123)
        val2 = CtyValue(type_=CtyNumber(), is_null=True)
        
        # Add
        result = add(val1, val2)
        
        # Verify result is null
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.is_null is True
    
    def test_subtract_numbers(self):
        """Test subtracting numbers."""
        # Create number values
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("456"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("123"))
        
        # Subtract
        result = subtract(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == Decimal("333")
    
    def test_subtract_incompatible_types(self):
        """Test subtracting incompatible types raises error."""
        # Create values of different types
        val1 = CtyValue(type_=CtyString(), value="test")
        val2 = CtyValue(type_=CtyNumber(), value=123)
        
        # Subtract should raise TypeError
        with pytest.raises(TypeError):
            subtract(val1, val2)
    
    def test_multiply_numbers(self):
        """Test multiplying numbers."""
        # Create number values
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("12"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("10"))
        
        # Multiply
        result = multiply(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == Decimal("120")
    
    def test_multiply_string_by_number(self):
        """Test repeating a string by multiplying with a number."""
        # Create values
        val1 = CtyValue(type_=CtyString(), value="abc")
        val2 = CtyValue(type_=CtyNumber(), value=3)
        
        # Multiply
        result = multiply(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyString()
        assert result.value == "abcabcabc"
    
    def test_multiply_list_by_number(self):
        """Test repeating a list by multiplying with a number."""
        # Create values
        list_type = CtyList(element_type=CtyString())
        val1 = CtyValue(type_=list_type, value=["a", "b"])
        val2 = CtyValue(type_=CtyNumber(), value=3)
        
        # Multiply
        result = multiply(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == list_type
        assert result.value == ["a", "b", "a", "b", "a", "b"]
    
    def test_divide_numbers(self):
        """Test dividing numbers."""
        # Create number values
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("120"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("10"))
        
        # Divide
        result = divide(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == Decimal("12")
    
    def test_divide_by_zero(self):
        """Test dividing by zero raises error."""
        # Create number values
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("120"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("0"))
        
        # Divide by zero should raise CtyError
        with pytest.raises(CtyError):
            divide(val1, val2)
    
    def test_modulo_numbers(self):
        """Test modulo operation."""
        # Create number values
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("10"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("3"))
        
        # Modulo
        result = modulo(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == Decimal("1")
    
    def test_negate_number(self):
        """Test negating a number."""
        # Create number value
        val = CtyValue(type_=CtyNumber(), value=Decimal("123"))
        
        # Negate
        result = negate(val)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == Decimal("-123")
    
    def test_negate_bool(self):
        """Test negating a boolean."""
        # Create boolean values
        val_true = CtyValue(type_=CtyBool(), value=True)
        val_false = CtyValue(type_=CtyBool(), value=False)
        
        # Negate
        result_true = negate(val_true)
        result_false = negate(val_false)
        
        # Verify results
        assert result_true.value is False
        assert result_false.value is True


class TestCollectionOperations:
    """Tests for collection operations."""
    
    def test_get_attribute(self):
        """Test getting an attribute from an object."""
        # Create object type and value
        obj_type = CtyObject({
            "name": CtyString(),
            "age": CtyNumber()
        })
        obj_value = CtyValue(type_=obj_type, value={
            "name": "John",
            "age": 30
        })
        
        # Get attribute
        result = get_attribute(obj_value, "name")
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyString()
        assert result.value == "John"
    
    def test_get_attribute_missing(self):
        """Test getting a missing attribute raises error."""
        # Create object type and value
        obj_type = CtyObject({
            "name": CtyString()
        })
        obj_value = CtyValue(type_=obj_type, value={
            "name": "John"
        })
        
        # Get non-existent attribute should raise AttributeError
        with pytest.raises(AttributeError):
            get_attribute(obj_value, "age")
    
    def test_get_element_list(self):
        """Test getting an element from a list."""
        # Create list value
        list_type = CtyList(element_type=CtyString())
        list_value = CtyValue(type_=list_type, value=["a", "b", "c"])
        
        # Create index
        index = CtyValue(type_=CtyNumber(), value=1)
        
        # Get element
        result = get_element(list_value, index)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyString()
        assert result.value == "b"
    
    def test_get_element_map(self):
        """Test getting an element from a map."""
        # Create map value
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_value = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        
        # Create key
        key = CtyValue(type_=CtyString(), value="b")
        
        # Get element
        result = get_element(map_value, key)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == 2
    
    def test_get_element_out_of_bounds(self):
        """Test getting an element with an out-of-bounds index raises error."""
        # Create list value
        list_type = CtyList(element_type=CtyString())
        list_value = CtyValue(type_=list_type, value=["a", "b", "c"])
        
        # Create out-of-bounds index
        index = CtyValue(type_=CtyNumber(), value=5)
        
        # Get element should raise IndexError
        with pytest.raises(IndexError):
            get_element(list_value, index)
    
    def test_length_string(self):
        """Test getting the length of a string."""
        # Create string value
        val = CtyValue(type_=CtyString(), value="hello")
        
        # Get length
        result = length(val)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == 5
    
    def test_length_list(self):
        """Test getting the length of a list."""
        # Create list value
        list_type = CtyList(element_type=CtyString())
        val = CtyValue(type_=list_type, value=["a", "b", "c"])
        
        # Get length
        result = length(val)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == 3
    
    def test_length_map(self):
        """Test getting the length of a map."""
        # Create map value
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        val = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        
        # Get length
        result = length(val)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyNumber()
        assert result.value == 2
    
    def test_contains_string(self):
        """Test checking if a string contains a substring."""
        # Create string values
        val = CtyValue(type_=CtyString(), value="hello world")
        item = CtyValue(type_=CtyString(), value="world")
        
        # Check containment
        result = contains(val, item)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyBool()
        assert result.value is True
    
    def test_contains_list(self):
        """Test checking if a list contains an item."""
        # Create list value
        list_type = CtyList(element_type=CtyString())
        val = CtyValue(type_=list_type, value=["a", "b", "c"])
        item = CtyValue(type_=CtyString(), value="b")
        
        # Check containment
        result = contains(val, item)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyBool()
        assert result.value is True
    
    def test_contains_map_key(self):
        """Test checking if a map contains a key."""
        # Create map value
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        val = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        key = CtyValue(type_=CtyString(), value="b")
        
        # Check containment
        result = contains(val, key)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyBool()
        assert result.value is True
    
    def test_concat_lists(self):
        """Test concatenating multiple lists."""
        # Create list values
        list_type = CtyList(element_type=CtyString())
        val1 = CtyValue(type_=list_type, value=["a", "b"])
        val2 = CtyValue(type_=list_type, value=["c", "d"])
        val3 = CtyValue(type_=list_type, value=["e"])
        
        # Concatenate
        result = concat_lists(val1, val2, val3)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == list_type
        assert result.value == ["a", "b", "c", "d", "e"]
    
    def test_concat_lists_empty(self):
        """Test concatenating no lists returns empty list."""
        # Concatenate no lists
        result = concat_lists()
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert result.value == []
    
    def test_merge_maps(self):
        """Test merging multiple maps."""
        # Create map values
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        val1 = CtyValue(type_=map_type, value={"a": "1", "b": "2"})
        val2 = CtyValue(type_=map_type, value={"b": "3", "c": "4"})  # b will override
        
        # Merge
        result = merge_maps(val1, val2)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == map_type
        assert result.value == {"a": "1", "b": "3", "c": "4"}
    
    def test_slice_string(self):
        """Test slicing a string."""
        # Create string value
        val = CtyValue(type_=CtyString(), value="hello world")
        
        # Create indices
        start = CtyValue(type_=CtyNumber(), value=6)
        end = CtyValue(type_=CtyNumber(), value=11)
        
        # Slice
        result = slice_string(val, start, end)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == CtyString()
        assert result.value == "world"
    
    def test_slice_list(self):
        """Test slicing a list."""
        # Create list value
        list_type = CtyList(element_type=CtyString())
        val = CtyValue(type_=list_type, value=["a", "b", "c", "d", "e"])
        
        # Create indices
        start = CtyValue(type_=CtyNumber(), value=1)
        end = CtyValue(type_=CtyNumber(), value=4)
        
        # Slice
        result = slice_list(val, start, end)
        
        # Verify result
        assert isinstance(result, CtyValue)
        assert result.type == list_type
        assert result.value == ["b", "c", "d"]
