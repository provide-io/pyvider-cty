# tests/values/test_value_operations.py

import pytest
from decimal import Decimal

from pyvider.cty.ctypes import (
    CtyBool, CtyNumber, CtyString, CtyList, CtyMap, CtySet, CtyObject, CtyTuple
)
from pyvider.cty.values import CtyValue
from pyvider.cty.values.operations import (
    equals, add, subtract, multiply, divide, modulo, negate,
    get_attribute, get_element, length, contains, 
    concat_lists, merge_maps, slice_string, slice_list
)
from pyvider.cty.exceptions import CtyError, TypeMismatchError

class TestArithmeticOperations:
    """Test arithmetic operations."""
    
    def test_negate_number(self):
        """Test negating a number."""
        val = CtyValue(type_=CtyNumber(), value=Decimal("42"))
        result = negate(val)
        
        assert result.type == CtyNumber()
        assert result.value == Decimal("-42")
        
        # Negating zero
        val = CtyValue(type_=CtyNumber(), value=Decimal("0"))
        result = negate(val)
        
        assert result.type == CtyNumber()
        assert result.value == Decimal("0")

    def test_negate_bool(self):
        """Test negating a boolean."""
        val_true = CtyValue(type_=CtyBool(), value=True)
        val_false = CtyValue(type_=CtyBool(), value=False)
        
        result_true = negate(val_true)
        result_false = negate(val_false)
        
        assert result_true.type == CtyBool()
        assert result_false.type == CtyBool()
        assert result_true.value is False
        assert result_false.value is True

    def test_negate_null(self):
        """Test negating a null value."""
        val = CtyValue(type_=CtyNumber(), is_null=True)
        result = negate(val)
        
        assert result.type == CtyNumber()
        assert result.is_null is True

    def test_negate_unknown(self):
        """Test negating an unknown value."""
        val = CtyValue(type_=CtyNumber(), is_unknown=True)
        result = negate(val)
        
        assert result.type == CtyNumber()
        assert result.is_unknown is True

    def test_negate_invalid_type(self):
        """Test negating an invalid type."""
        val = CtyValue(type_=CtyString(), value="hello")
        
        with pytest.raises(TypeError):
            negate(val)

    def test_divide_numbers(self):
        """Test dividing two numbers."""
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("84"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("2"))
        
        result = divide(val1, val2)
        
        assert result.type == CtyNumber()
        assert result.value == Decimal("42")
        
        # Division with decimal result
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("1"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("3"))
        
        result = divide(val1, val2)
        
        assert result.type == CtyNumber()
        assert round(result.value, 4) == round(Decimal("0.3333"), 4)

    def test_divide_by_zero(self):
        """Test dividing by zero."""
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("42"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("0"))
        
        with pytest.raises(ValueError):
            divide(val1, val2)

    def test_divide_null(self):
        """Test dividing with a null value."""
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("42"))
        val2 = CtyValue(type_=CtyNumber(), is_null=True)
        
        result = divide(val1, val2)
        
        assert result.type == CtyNumber()
        assert result.is_null is True

    def test_divide_unknown(self):
        """Test dividing with an unknown value."""
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("42"))
        val2 = CtyValue(type_=CtyNumber(), is_unknown=True)
        
        result = divide(val1, val2)
        
        assert result.type == CtyNumber()
        assert result.is_unknown is True

    def test_divide_invalid_types(self):
        """Test dividing with invalid types."""
        val1 = CtyValue(type_=CtyString(), value="hello")
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("2"))
        
        with pytest.raises(TypeError):
            divide(val1, val2)

    def test_modulo(self):
        """Test modulo operation."""
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("43"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("10"))
        
        result = modulo(val1, val2)
        
        assert result.type == CtyNumber()
        assert result.value == Decimal("3")
        
        # Modulo with decimals
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("10.5"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("3.2"))
        
        result = modulo(val1, val2)
        
        assert result.type == CtyNumber()
        assert round(result.value, 1) == round(Decimal("0.9"), 1)

    def test_modulo_by_zero(self):
        """Test modulo by zero."""
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("42"))
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("0"))
        
        with pytest.raises(ValueError):
            modulo(val1, val2)

    def test_modulo_null(self):
        """Test modulo with a null value."""
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("42"))
        val2 = CtyValue(type_=CtyNumber(), is_null=True)
        
        result = modulo(val1, val2)
        
        assert result.type == CtyNumber()
        assert result.is_null is True

    def test_modulo_unknown(self):
        """Test modulo with an unknown value."""
        val1 = CtyValue(type_=CtyNumber(), value=Decimal("42"))
        val2 = CtyValue(type_=CtyNumber(), is_unknown=True)
        
        result = modulo(val1, val2)
        
        assert result.type == CtyNumber()
        assert result.is_unknown is True

    def test_modulo_invalid_types(self):
        """Test modulo with invalid types."""
        val1 = CtyValue(type_=CtyString(), value="hello")
        val2 = CtyValue(type_=CtyNumber(), value=Decimal("2"))
        
        with pytest.raises(TypeError):
            modulo(val1, val2)

class TestCollectionOperations:
    """Test collection operations."""
    
    def test_get_element_list(self):
        """Test getting an element from a list."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        index = CtyValue(type_=CtyNumber(), value=1)
        
        result = get_element(list_val, index)
        
        assert result.type == CtyString()
        assert result.value == "b"

    def test_get_element_map(self):
        """Test getting an element from a map."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_val = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        key = CtyValue(type_=CtyString(), value="b")
        
        result = get_element(map_val, key)
        
        assert result.type == CtyNumber()
        assert result.value == 2

    def test_get_element_tuple(self):
        """Test getting an element from a tuple."""
        tuple_type = CtyTuple(element_types=[CtyString(), CtyNumber(), CtyBool()])
        tuple_val = CtyValue(type_=tuple_type, value=("hello", 42, True))
        index = CtyValue(type_=CtyNumber(), value=1)
        
        result = get_element(tuple_val, index)
        
        assert result.type == CtyNumber()
        assert result.value == 42

    def test_get_element_out_of_bounds(self):
        """Test getting an element with an out-of-bounds index."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        index = CtyValue(type_=CtyNumber(), value=5)
        
        with pytest.raises(IndexError):
            get_element(list_val, index)

    def test_get_element_invalid_key(self):
        """Test getting an element with an invalid key."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_val = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        key = CtyValue(type_=CtyString(), value="c")
        
        with pytest.raises(KeyError):
            get_element(map_val, key)

    def test_get_element_null(self):
        """Test getting an element from a null collection."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, is_null=True)
        index = CtyValue(type_=CtyNumber(), value=0)
        
        result = get_element(list_val, index)
        
        assert result.type == CtyString()
        assert result.is_null is True

    def test_get_element_unknown(self):
        """Test getting an element from an unknown collection."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, is_unknown=True)
        index = CtyValue(type_=CtyNumber(), value=0)
        
        result = get_element(list_val, index)
        
        assert result.type == CtyString()
        assert result.is_unknown is True

    def test_get_element_null_index(self):
        """Test getting an element with a null index."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        index = CtyValue(type_=CtyNumber(), is_null=True)
        
        with pytest.raises(ValueError):
            get_element(list_val, index)

    def test_get_element_unknown_index(self):
        """Test getting an element with an unknown index."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        index = CtyValue(type_=CtyNumber(), is_unknown=True)
        
        result = get_element(list_val, index)
        
        assert result.type == CtyString()
        assert result.is_unknown is True

    def test_length_string(self):
        """Test getting the length of a string."""
        str_val = CtyValue(type_=CtyString(), value="hello")
        
        result = length(str_val)
        
        assert result.type == CtyNumber()
        assert result.value == 5

    def test_length_list(self):
        """Test getting the length of a list."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        
        result = length(list_val)
        
        assert result.type == CtyNumber()
        assert result.value == 3

    def test_length_map(self):
        """Test getting the length of a map."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_val = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        
        result = length(map_val)
        
        assert result.type == CtyNumber()
        assert result.value == 2

    def test_length_set(self):
        """Test getting the length of a set."""
        set_type = CtySet(element_type=CtyString())
        set_val = CtyValue(type_=set_type, value={"a", "b", "c"})
        
        result = length(set_val)
        
        assert result.type == CtyNumber()
        assert result.value == 3

    def test_length_tuple(self):
        """Test getting the length of a tuple."""
        tuple_type = CtyTuple(element_types=[CtyString(), CtyNumber(), CtyBool()])
        tuple_val = CtyValue(type_=tuple_type, value=("hello", 42, True))
        
        result = length(tuple_val)
        
        assert result.type == CtyNumber()
        assert result.value == 3

    def test_length_null(self):
        """Test getting the length of a null value."""
        str_val = CtyValue(type_=CtyString(), is_null=True)
        
        result = length(str_val)
        
        assert result.type == CtyNumber()
        assert result.is_null is True

    def test_length_unknown(self):
        """Test getting the length of an unknown value."""
        str_val = CtyValue(type_=CtyString(), is_unknown=True)
        
        result = length(str_val)
        
        assert result.type == CtyNumber()
        assert result.is_unknown is True

    def test_length_invalid_type(self):
        """Test getting the length of an invalid type."""
        val = CtyValue(type_=CtyNumber(), value=42)
        
        with pytest.raises(TypeError):
            length(val)

class TestContainsOperation:
    """Test contains operation."""
    
    def test_contains_string(self):
        """Test contains for strings."""
        str_val = CtyValue(type_=CtyString(), value="hello world")
        sub_val = CtyValue(type_=CtyString(), value="world")
        
        result = contains(str_val, sub_val)
        
        assert result.type == CtyBool()
        assert result.value is True
        
        # Not contained
        sub_val = CtyValue(type_=CtyString(), value="goodbye")
        
        result = contains(str_val, sub_val)
        
        assert result.type == CtyBool()
        assert result.value is False

    def test_contains_list(self):
        """Test contains for lists."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        item = CtyValue(type_=CtyString(), value="b")
        
        result = contains(list_val, item)
        
        assert result.type == CtyBool()
        assert result.value is True
        
        # Not contained
        item = CtyValue(type_=CtyString(), value="d")
        
        result = contains(list_val, item)
        
        assert result.type == CtyBool()
        assert result.value is False

    def test_contains_map(self):
        """Test contains for maps (key check)."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_val = CtyValue(type_=map_type, value={"a": 1, "b": 2})
        key = CtyValue(type_=CtyString(), value="b")
        
        result = contains(map_val, key)
        
        assert result.type == CtyBool()
        assert result.value is True
        
        # Not contained
        key = CtyValue(type_=CtyString(), value="c")
        
        result = contains(map_val, key)
        
        assert result.type == CtyBool()
        assert result.value is False

    def test_contains_set(self):
        """Test contains for sets."""
        set_type = CtySet(element_type=CtyString())
        set_val = CtyValue(type_=set_type, value={"a", "b", "c"})
        item = CtyValue(type_=CtyString(), value="b")
        
        result = contains(set_val, item)
        
        assert result.type == CtyBool()
        assert result.value is True
        
        # Not contained
        item = CtyValue(type_=CtyString(), value="d")
        
        result = contains(set_val, item)
        
        assert result.type == CtyBool()
        assert result.value is False

    def test_contains_type_mismatch(self):
        """Test contains with type mismatch."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        item = CtyValue(type_=CtyNumber(), value=1)
        
        result = contains(list_val, item)
        
        assert result.type == CtyBool()
        assert result.value is False

    def test_contains_null(self):
        """Test contains with null values."""
        str_val = CtyValue(type_=CtyString(), value="hello world")
        sub_val = CtyValue(type_=CtyString(), is_null=True)
        
        result = contains(str_val, sub_val)
        
        assert result.type == CtyBool()
        assert result.is_null is True
        
        # Null collection
        str_val = CtyValue(type_=CtyString(), is_null=True)
        sub_val = CtyValue(type_=CtyString(), value="world")
        
        result = contains(str_val, sub_val)
        
        assert result.type == CtyBool()
        assert result.is_null is True

    def test_contains_unknown(self):
        """Test contains with unknown values."""
        str_val = CtyValue(type_=CtyString(), value="hello world")
        sub_val = CtyValue(type_=CtyString(), is_unknown=True)
        
        result = contains(str_val, sub_val)
        
        assert result.type == CtyBool()
        assert result.is_unknown is True
        
        # Unknown collection
        str_val = CtyValue(type_=CtyString(), is_unknown=True)
        sub_val = CtyValue(type_=CtyString(), value="world")
        
        result = contains(str_val, sub_val)
        
        assert result.type == CtyBool()
        assert result.is_unknown is True

    def test_contains_invalid_type(self):
        """Test contains with invalid collection type."""
        val = CtyValue(type_=CtyNumber(), value=42)
        item = CtyValue(type_=CtyNumber(), value=1)
        
        with pytest.raises(TypeError):
            contains(val, item)

class TestObjectAttributeOperations:
    """Test operations on object attributes."""
    
    def test_get_attribute(self):
        """Test getting an attribute from an object."""
        obj_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber(),
            "active": CtyBool()
        })
        obj_val = CtyValue(type_=obj_type, value={
            "name": "Alice",
            "age": 30,
            "active": True
        })
        
        # Get attribute
        result = get_attribute(obj_val, "name")
        
        assert result.type == CtyString()
        assert result.value == "Alice"
        
        result = get_attribute(obj_val, "age")
        
        assert result.type == CtyNumber()
        assert result.value == 30
        
        result = get_attribute(obj_val, "active")
        
        assert result.type == CtyBool()
        assert result.value is True

    def test_get_attribute_missing(self):
        """Test getting a missing attribute."""
        obj_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        })
        obj_val = CtyValue(type_=obj_type, value={
            "name": "Alice"
            # age is missing
        })
        
        # Missing attribute should return null
        result = get_attribute(obj_val, "age")
        
        assert result.type == CtyNumber()
        assert result.is_null is True

    def test_get_attribute_unknown(self):
        """Test getting an attribute from an unknown object."""
        obj_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        })
        obj_val = CtyValue(type_=obj_type, is_unknown=True)
        
        # Attribute of unknown object is unknown
        result = get_attribute(obj_val, "name")
        
        assert result.type == CtyString()
        assert result.is_unknown is True

    def test_get_attribute_undefined(self):
        """Test getting an undefined attribute."""
        obj_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        })
        obj_val = CtyValue(type_=obj_type, value={
            "name": "Alice",
            "age": 30
        })
        
        # Undefined attribute raises error
        with pytest.raises(AttributeError):
            get_attribute(obj_val, "undefined")

    def test_get_attribute_invalid_type(self):
        """Test getting an attribute from a non-object."""
        val = CtyValue(type_=CtyString(), value="hello")
        
        with pytest.raises(TypeError):
            get_attribute(val, "length")

class TestConcatAndMergeOperations:
    """Test concatenation and merging operations."""
    
    def test_concat_lists(self):
        """Test concatenating lists."""
        list_type = CtyList(element_type=CtyString())
        list1 = CtyValue(type_=list_type, value=["a", "b"])
        list2 = CtyValue(type_=list_type, value=["c", "d"])
        list3 = CtyValue(type_=list_type, value=["e", "f"])
        
        result = concat_lists(list1, list2, list3)
        
        assert result.type == list_type
        assert result.value == ["a", "b", "c", "d", "e", "f"]

    def test_concat_lists_empty(self):
        """Test concatenating with empty lists."""
        list_type = CtyList(element_type=CtyString())
        list1 = CtyValue(type_=list_type, value=["a", "b"])
        list2 = CtyValue(type_=list_type, value=[])
        list3 = CtyValue(type_=list_type, value=["e", "f"])
        
        result = concat_lists(list1, list2, list3)
        
        assert result.type == list_type
        assert result.value == ["a", "b", "e", "f"]
        
        # No lists
        result = concat_lists()
        
        assert isinstance(result.type, CtyList)
        assert result.value == []

    def test_concat_lists_type_mismatch(self):
        """Test concatenating lists with type mismatch."""
        list_str_type = CtyList(element_type=CtyString())
        list_num_type = CtyList(element_type=CtyNumber())
        
        list1 = CtyValue(type_=list_str_type, value=["a", "b"])
        list2 = CtyValue(type_=list_num_type, value=[1, 2])
        
        with pytest.raises(ValueError):
            concat_lists(list1, list2)

    def test_concat_lists_null_unknown(self):
        """Test concatenating with null and unknown lists."""
        list_type = CtyList(element_type=CtyString())
        list1 = CtyValue(type_=list_type, value=["a", "b"])
        list_null = CtyValue(type_=list_type, is_null=True)
        list_unknown = CtyValue(type_=list_type, is_unknown=True)
        
        # Null lists are ignored
        result = concat_lists(list1, list_null)
        
        assert result.type == list_type
        assert result.value == ["a", "b"]
        
        # Unknown lists make the result unknown
        result = concat_lists(list1, list_unknown)
        
        assert result.type == list_type
        assert result.is_unknown is True
        
        # All null lists result in null
        result = concat_lists(list_null, list_null)
        
        assert result.type == list_type
        assert result.is_null is True

    def test_merge_maps(self):
        """Test merging maps."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        map1 = CtyValue(type_=map_type, value={"a": "A", "b": "B"})
        map2 = CtyValue(type_=map_type, value={"c": "C", "d": "D"})
        map3 = CtyValue(type_=map_type, value={"e": "E", "f": "F"})
        
        result = merge_maps(map1, map2, map3)
        
        assert result.type == map_type
        assert result.value == {
            "a": "A", "b": "B", "c": "C", "d": "D", "e": "E", "f": "F"
        }

    def test_merge_maps_overlapping(self):
        """Test merging maps with overlapping keys."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        map1 = CtyValue(type_=map_type, value={"a": "A", "b": "B"})
        map2 = CtyValue(type_=map_type, value={"b": "B2", "c": "C"})
        
        result = merge_maps(map1, map2)
        
        assert result.type == map_type
        assert result.value == {"a": "A", "b": "B2", "c": "C"}

    def test_merge_maps_empty(self):
        """Test merging with empty maps."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        map1 = CtyValue(type_=map_type, value={"a": "A", "b": "B"})
        map2 = CtyValue(type_=map_type, value={})
        map3 = CtyValue(type_=map_type, value={"e": "E", "f": "F"})
        
        result = merge_maps(map1, map2, map3)
        
        assert result.type == map_type
        assert result.value == {"a": "A", "b": "B", "e": "E", "f": "F"}
        
        # No maps
        result = merge_maps()
        
        assert isinstance(result.type, CtyMap)
        assert result.value == {}

    def test_merge_maps_type_mismatch(self):
        """Test merging maps with type mismatch."""
        map_str_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        map_num_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        
        map1 = CtyValue(type_=map_str_type, value={"a": "A", "b": "B"})
        map2 = CtyValue(type_=map_num_type, value={"c": 1, "d": 2})
        
        with pytest.raises(ValueError):
            merge_maps(map1, map2)

    def test_merge_maps_null_unknown(self):
        """Test merging with null and unknown maps."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        map1 = CtyValue(type_=map_type, value={"a": "A", "b": "B"})
        map_null = CtyValue(type_=map_type, is_null=True)
        map_unknown = CtyValue(type_=map_type, is_unknown=True)
        
        # Null maps are ignored
        result = merge_maps(map1, map_null)
        
        assert result.type == map_type
        assert result.value == {"a": "A", "b": "B"}
        
        # Unknown maps make the result unknown
        result = merge_maps(map1, map_unknown)
        
        assert result.type == map_type
        assert result.is_unknown is True
        
        # All null maps result in null
        result = merge_maps(map_null, map_null)
        
        assert result.type == map_type
        assert result.is_null is True

class TestSliceOperations:
    """Test slice operations."""
    
    def test_slice_string(self):
        """Test slicing a string."""
        str_val = CtyValue(type_=CtyString(), value="hello world")
        start = CtyValue(type_=CtyNumber(), value=0)
        end = CtyValue(type_=CtyNumber(), value=5)
        
        result = slice_string(str_val, start, end)
        
        assert result.type == CtyString()
        assert result.value == "hello"
        
        # Slice with just start
        result = slice_string(str_val, start)
        
        assert result.type == CtyString()
        assert result.value == "hello world"
        
        # Slice middle
        start = CtyValue(type_=CtyNumber(), value=6)
        end = CtyValue(type_=CtyNumber(), value=11)
        
        result = slice_string(str_val, start, end)
        
        assert result.type == CtyString()
        assert result.value == "world"

    def test_slice_string_bounds(self):
        """Test slicing a string with bounds checking."""
        str_val = CtyValue(type_=CtyString(), value="hello")
        
        # Start index out of bounds
        start = CtyValue(type_=CtyNumber(), value=10)
        
        with pytest.raises(IndexError):
            slice_string(str_val, start)
            
        # End index out of bounds
        start = CtyValue(type_=CtyNumber(), value=0)
        end = CtyValue(type_=CtyNumber(), value=10)
        
        with pytest.raises(IndexError):
            slice_string(str_val, start, end)
            
        # End before start
        start = CtyValue(type_=CtyNumber(), value=3)
        end = CtyValue(type_=CtyNumber(), value=1)
        
        with pytest.raises(IndexError):
            slice_string(str_val, start, end)

    def test_slice_string_null_unknown(self):
        """Test slicing with null and unknown values."""
        str_val = CtyValue(type_=CtyString(), value="hello")
        start = CtyValue(type_=CtyNumber(), value=0)
        end_null = CtyValue(type_=CtyNumber(), is_null=True)
        end_unknown = CtyValue(type_=CtyNumber(), is_unknown=True)
        
        # Null index
        result = slice_string(str_val, start, end_null)
        
        assert result.type == CtyString()
        assert result.is_null is True
        
        # Unknown index
        result = slice_string(str_val, start, end_unknown)
        
        assert result.type == CtyString()
        assert result.is_unknown is True
        
        # Null string
        str_null = CtyValue(type_=CtyString(), is_null=True)
        
        result = slice_string(str_null, start, end=None)
        
        assert result.type == CtyString()
        assert result.is_null is True
        
        # Unknown string
        str_unknown = CtyValue(type_=CtyString(), is_unknown=True)
        
        result = slice_string(str_unknown, start, end=None)
        
        assert result.type == CtyString()
        assert result.is_unknown is True

    def test_slice_string_invalid_types(self):
        """Test slicing with invalid types."""
        str_val = CtyValue(type_=CtyString(), value="hello")
        start = CtyValue(type_=CtyString(), value="0")  # Wrong type
        
        with pytest.raises(TypeError):
            slice_string(str_val, start)
            
        # Wrong value type
        val = CtyValue(type_=CtyNumber(), value=42)
        start = CtyValue(type_=CtyNumber(), value=0)
        
        with pytest.raises(TypeError):
            slice_string(val, start)

    def test_slice_list(self):
        """Test slicing a list."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c", "d", "e"])
        start = CtyValue(type_=CtyNumber(), value=1)
        end = CtyValue(type_=CtyNumber(), value=4)
        
        result = slice_list(list_val, start, end)
        
        assert result.type == list_type
        assert result.value == ["b", "c", "d"]
        
        # Slice with just start
        result = slice_list(list_val, start)
        
        assert result.type == list_type
        assert result.value == ["b", "c", "d", "e"]
        
        # Slice to empty list
        start = CtyValue(type_=CtyNumber(), value=2)
        end = CtyValue(type_=CtyNumber(), value=2)
        
        result = slice_list(list_val, start, end)
        
        assert result.type == list_type
        assert result.value == []

    def test_slice_list_bounds(self):
        """Test slicing a list with bounds checking."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        
        # Start index out of bounds
        start = CtyValue(type_=CtyNumber(), value=10)
        
        with pytest.raises(IndexError):
            slice_list(list_val, start)
            
        # End index out of bounds
        start = CtyValue(type_=CtyNumber(), value=0)
        end = CtyValue(type_=CtyNumber(), value=10)
        
        with pytest.raises(IndexError):
            slice_list(list_val, start, end)
            
        # End before start
        start = CtyValue(type_=CtyNumber(), value=2)
        end = CtyValue(type_=CtyNumber(), value=1)
        
        with pytest.raises(IndexError):
            slice_list(list_val, start, end)

    def test_slice_list_null_unknown(self):
        """Test slicing with null and unknown values."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        start = CtyValue(type_=CtyNumber(), value=0)
        end_null = CtyValue(type_=CtyNumber(), is_null=True)
        end_unknown = CtyValue(type_=CtyNumber(), is_unknown=True)
        
        # Null index
        result = slice_list(list_val, start, end_null)
        
        assert result.type == list_type
        assert result.is_null is True
        
        # Unknown index
        result = slice_list(list_val, start, end_unknown)
        
        assert result.type == list_type
        assert result.is_unknown is True
        
        # Null list
        list_null = CtyValue(type_=list_type, is_null=True)
        
        result = slice_list(list_null, start, end=None)
        
        assert result.type == list_type
        assert result.is_null is True
        
        # Unknown list
        list_unknown = CtyValue(type_=list_type, is_unknown=True)
        
        result = slice_list(list_unknown, start, end=None)
        
        assert result.type == list_type
        assert result.is_unknown is True

    def test_slice_list_invalid_types(self):
        """Test slicing with invalid types."""
        list_type = CtyList(element_type=CtyString())
        list_val = CtyValue(type_=list_type, value=["a", "b", "c"])
        start = CtyValue(type_=CtyString(), value="0")  # Wrong type
        
        with pytest.raises(TypeError):
            slice_list(list_val, start)
            
        # Wrong value type
        val = CtyValue(type_=CtyString(), value="hello")
        start = CtyValue(type_=CtyNumber(), value=0)
        
        with pytest.raises(TypeError):
            slice_list(val, start)
