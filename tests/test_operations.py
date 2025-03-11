
# tests/integration/cty/values/test_operations.py

"""
Integration tests for CTY value operations.

These tests verify the functionality of CTY value operations against real CTY 
types and values, ensuring that operations handle all possible value states
correctly (known, unknown, null) and follow the same semantics as Go-CTY.
"""

import pytest
from decimal import Decimal
from typing import Dict, List, Set

from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyDynamic, CtyTuple
from pyvider.cty.values.base import Value
from pyvider.cty.values.operations import (
    equals,
    add,
    subtract,
    multiply,
    divide,
    modulo,
    negate,
    get_attribute,
    get_element,
    length,
    contains,
    concat_lists,
    merge_maps,
    slice_string,
    slice_list
)
from pyvider.cty.exceptions import CtyError, TypeMismatchError


@pytest.mark.asyncio
async def test_equals_basic():
    """Test basic equality operations."""
    # String equality
    str1 = Value(CtyString(), "hello")
    str2 = Value(CtyString(), "hello")
    str3 = Value(CtyString(), "world")
    
    result = equals(str1, str2)
    assert result.is_known
    assert result.value is True
    
    result = equals(str1, str3)
    assert result.is_known
    assert result.value is False
    
    # Number equality
    num1 = Value(CtyNumber(), 42)
    num2 = Value(CtyNumber(), 42)
    num3 = Value(CtyNumber(), 43)
    
    result = equals(num1, num2)
    assert result.is_known
    assert result.value is True
    
    result = equals(num1, num3)
    assert result.is_known
    assert result.value is False
    
    # Bool equality
    bool1 = Value(CtyBool(), True)
    bool2 = Value(CtyBool(), True)
    bool3 = Value(CtyBool(), False)
    
    result = equals(bool1, bool2)
    assert result.is_known
    assert result.value is True
    
    result = equals(bool1, bool3)
    assert result.is_known
    assert result.value is False
    
    # Different types
    result = equals(str1, num1)
    assert result.is_known
    assert result.value is False


@pytest.mark.asyncio
async def test_equals_complex():
    """Test equality for complex types."""
    # List equality
    list1 = Value(CtyList(element_type=CtyString()), ["a", "b", "c"])
    list2 = Value(CtyList(element_type=CtyString()), ["a", "b", "c"])
    list3 = Value(CtyList(element_type=CtyString()), ["a", "b", "d"])
    list4 = Value(CtyList(element_type=CtyString()), ["a", "b"])
    
    result = equals(list1, list2)
    assert result.is_known
    assert result.value is True
    
    result = equals(list1, list3)
    assert result.is_known
    assert result.value is False
    
    result = equals(list1, list4)
    assert result.is_known
    assert result.value is False
    
    # Map equality
    map1 = Value(CtyMap(element_type=CtyNumber()), {"a": 1, "b": 2})
    map2 = Value(CtyMap(element_type=CtyNumber()), {"a": 1, "b": 2})
    map3 = Value(CtyMap(element_type=CtyNumber()), {"a": 1, "b": 3})
    map4 = Value(CtyMap(element_type=CtyNumber()), {"a": 1})
    
    result = equals(map1, map2)
    assert result.is_known
    assert result.value is True
    
    result = equals(map1, map3)
    assert result.is_known
    assert result.value is False
    
    result = equals(map1, map4)
    assert result.is_known
    assert result.value is False
    
    # Object equality
    obj_type = CtyObject(attribute_types={
        "name": CtyString(),
        "age": CtyNumber()
    })
    
    obj1 = Value(obj_type, {"name": "Alice", "age": 30})
    obj2 = Value(obj_type, {"name": "Alice", "age": 30})
    obj3 = Value(obj_type, {"name": "Bob", "age": 30})
    
    result = equals(obj1, obj2)
    assert result.is_known
    assert result.value is True
    
    result = equals(obj1, obj3)
    assert result.is_known
    assert result.value is False


@pytest.mark.asyncio
async def test_equals_null_unknown():
    """Test equality with null and unknown values."""
    # Null equality
    str1 = Value(CtyString(), "hello")
    str_null = Value.null(CtyString())
    
    result = equals(str_null, str_null)
    assert result.is_known
    assert result.value is True
    
    result = equals(str1, str_null)
    assert result.is_known
    assert result.value is False
    
    # Nulls of different types
    num_null = Value.null(CtyNumber())
    result = equals(str_null, num_null)
    assert result.is_known
    assert result.value is False
    
    # Unknown equality
    str_unknown = Value.unknown(CtyString())
    
    result = equals(str_unknown, str1)
    assert not result.is_known
    
    result = equals(str_unknown, str_unknown)
    assert not result.is_known
    
    # Unknown and null
    result = equals(str_unknown, str_null)
    assert not result.is_known


@pytest.mark.asyncio
async def test_add_numbers():
    """Test number addition."""
    num1 = Value(CtyNumber(), 40)
    num2 = Value(CtyNumber(), 2)
    
    result = add(num1, num2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 42
    
    # Decimal precision
    num3 = Value(CtyNumber(), Decimal("0.1"))
    num4 = Value(CtyNumber(), Decimal("0.2"))
    
    result = add(num3, num4)
    assert result.is_known
    assert not result.is_null
    assert result.value == Decimal("0.3")
    
    # Mixed numbers
    num5 = Value(CtyNumber(), 10)
    num6 = Value(CtyNumber(), Decimal("0.5"))
    
    result = add(num5, num6)
    assert result.is_known
    assert not result.is_null
    assert result.value == Decimal("10.5")


@pytest.mark.asyncio
async def test_add_strings():
    """Test string concatenation."""
    str1 = Value(CtyString(), "Hello, ")
    str2 = Value(CtyString(), "world!")
    
    result = add(str1, str2)
    assert result.is_known
    assert not result.is_null
    assert result.value == "Hello, world!"
    
    # Empty strings
    str3 = Value(CtyString(), "")
    
    result = add(str1, str3)
    assert result.is_known
    assert not result.is_null
    assert result.value == "Hello, "
    
    result = add(str3, str3)
    assert result.is_known
    assert not result.is_null
    assert result.value == ""


@pytest.mark.asyncio
async def test_add_lists():
    """Test list concatenation."""
    list1 = Value(CtyList(element_type=CtyString()), ["a", "b"])
    list2 = Value(CtyList(element_type=CtyString()), ["c", "d"])
    
    result = add(list1, list2)
    assert result.is_known
    assert not result.is_null
    assert result.value == ["a", "b", "c", "d"]
    
    # Empty lists
    list3 = Value(CtyList(element_type=CtyString()), [])
    
    result = add(list1, list3)
    assert result.is_known
    assert not result.is_null
    assert result.value == ["a", "b"]
    
    result = add(list3, list3)
    assert result.is_known
    assert not result.is_null
    assert result.value == []
    
    # Incompatible element types
    list4 = Value(CtyList(element_type=CtyNumber()), [1, 2])
    
    with pytest.raises(TypeMismatchError):
        add(list1, list4)


@pytest.mark.asyncio
async def test_add_null_unknown():
    """Test addition with null and unknown values."""
    # Null addition
    num1 = Value(CtyNumber(), 42)
    num_null = Value.null(CtyNumber())
    
    result = add(num1, num_null)
    assert result.is_null
    
    result = add(num_null, num_null)
    assert result.is_null
    
    # Unknown addition
    num_unknown = Value.unknown(CtyNumber())
    
    result = add(num1, num_unknown)
    assert not result.is_known
    
    result = add(num_unknown, num_unknown)
    assert not result.is_known
    
    # Mixed null and unknown
    result = add(num_null, num_unknown)
    assert not result.is_known


@pytest.mark.asyncio
async def test_add_type_errors():
    """Test addition with incompatible types."""
    num = Value(CtyNumber(), 42)
    str_val = Value(CtyString(), "hello")
    bool_val = Value(CtyBool(), True)
    
    with pytest.raises(TypeError):
        add(num, bool_val)
    
    with pytest.raises(TypeError):
        add(str_val, num)
    
    with pytest.raises(TypeError):
        add(str_val, bool_val)


@pytest.mark.asyncio
async def test_subtract():
    """Test subtraction operation."""
    num1 = Value(CtyNumber(), 50)
    num2 = Value(CtyNumber(), 8)
    
    result = subtract(num1, num2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 42
    
    # Decimal precision
    num3 = Value(CtyNumber(), Decimal("0.3"))
    num4 = Value(CtyNumber(), Decimal("0.1"))
    
    result = subtract(num3, num4)
    assert result.is_known
    assert not result.is_null
    assert result.value == Decimal("0.2")
    
    # Negative result
    result = subtract(num2, num1)
    assert result.is_known
    assert not result.is_null
    assert result.value == -42
    
    # Null and unknown
    num_null = Value.null(CtyNumber())
    num_unknown = Value.unknown(CtyNumber())
    
    result = subtract(num1, num_null)
    assert result.is_null
    
    result = subtract(num1, num_unknown)
    assert not result.is_known
    
    # Type error
    str_val = Value(CtyString(), "hello")
    
    with pytest.raises(TypeError):
        subtract(num1, str_val)


@pytest.mark.asyncio
async def test_multiply():
    """Test multiplication operation."""
    # Number multiplication
    num1 = Value(CtyNumber(), 6)
    num2 = Value(CtyNumber(), 7)
    
    result = multiply(num1, num2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 42
    
    # String repetition
    str_val = Value(CtyString(), "abc")
    count = Value(CtyNumber(), 3)
    
    result = multiply(str_val, count)
    assert result.is_known
    assert not result.is_null
    assert result.value == "abcabcabc"
    
    # List repetition
    list_val = Value(CtyList(element_type=CtyNumber()), [1, 2])
    
    result = multiply(list_val, count)
    assert result.is_known
    assert not result.is_null
    assert result.value == [1, 2, 1, 2, 1, 2]
    
    # Null and unknown
    num_null = Value.null(CtyNumber())
    num_unknown = Value.unknown(CtyNumber())
    
    result = multiply(num1, num_null)
    assert result.is_null
    
    result = multiply(str_val, num_unknown)
    assert not result.is_known
    
    # Type error
    bool_val = Value(CtyBool(), True)
    
    with pytest.raises(TypeError):
        multiply(num1, bool_val)
    
    with pytest.raises(TypeError):
        multiply(bool_val, count)
    
    # Negative count for string/list
    neg_count = Value(CtyNumber(), -1)
    
    with pytest.raises(ValueError):
        multiply(str_val, neg_count)
    
    with pytest.raises(ValueError):
        multiply(list_val, neg_count)


@pytest.mark.asyncio
async def test_divide():
    """Test division operation."""
    num1 = Value(CtyNumber(), 84)
    num2 = Value(CtyNumber(), 2)
    
    result = divide(num1, num2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 42
    
    # Decimal division
    num3 = Value(CtyNumber(), 1)
    num4 = Value(CtyNumber(), 3)
    
    result = divide(num3, num4)
    assert result.is_known
    assert not result.is_null
    assert round(result.value, 10) == round(Decimal("0.3333333333"), 10)
    
    # Division by zero
    zero = Value(CtyNumber(), 0)
    
    with pytest.raises(ValueError):
        divide(num1, zero)
    
    # Null and unknown
    num_null = Value.null(CtyNumber())
    num_unknown = Value.unknown(CtyNumber())
    
    result = divide(num1, num_null)
    assert result.is_null
    
    result = divide(num1, num_unknown)
    assert not result.is_known
    
    # Type error
    str_val = Value(CtyString(), "hello")
    
    with pytest.raises(TypeError):
        divide(num1, str_val)


@pytest.mark.asyncio
async def test_modulo():
    """Test modulo operation."""
    num1 = Value(CtyNumber(), 43)
    num2 = Value(CtyNumber(), 10)
    
    result = modulo(num1, num2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 3
    
    # Decimal modulo
    num3 = Value(CtyNumber(), Decimal("10.5"))
    num4 = Value(CtyNumber(), Decimal("2.5"))
    
    result = modulo(num3, num4)
    assert result.is_known
    assert not result.is_null
    assert result.value == Decimal("0.5")
    
    # Modulo by zero
    zero = Value(CtyNumber(), 0)
    
    with pytest.raises(ValueError):
        modulo(num1, zero)
    
    # Null and unknown
    num_null = Value.null(CtyNumber())
    num_unknown = Value.unknown(CtyNumber())
    
    result = modulo(num1, num_null)
    assert result.is_null
    
    result = modulo(num1, num_unknown)
    assert not result.is_known
    
    # Type error
    str_val = Value(CtyString(), "hello")
    
    with pytest.raises(TypeError):
        modulo(num1, str_val)


@pytest.mark.asyncio
async def test_negate():
    """Test negation operation."""
    # Number negation
    num1 = Value(CtyNumber(), 42)
    num2 = Value(CtyNumber(), -42)
    num3 = Value(CtyNumber(), 0)
    
    result = negate(num1)
    assert result.is_known
    assert not result.is_null
    assert result.value == -42
    
    result = negate(num2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 42
    
    result = negate(num3)
    assert result.is_known
    assert not result.is_null
    assert result.value == 0
    
    # Boolean negation
    bool1 = Value(CtyBool(), True)
    bool2 = Value(CtyBool(), False)
    
    result = negate(bool1)
    assert result.is_known
    assert not result.is_null
    assert result.value is False
    
    result = negate(bool2)
    assert result.is_known
    assert not result.is_null
    assert result.value is True
    
    # Null and unknown
    num_null = Value.null(CtyNumber())
    num_unknown = Value.unknown(CtyNumber())
    bool_null = Value.null(CtyBool())
    bool_unknown = Value.unknown(CtyBool())
    
    result = negate(num_null)
    assert result.is_null
    
    result = negate(num_unknown)
    assert not result.is_known
    
    result = negate(bool_null)
    assert result.is_null
    
    result = negate(bool_unknown)
    assert not result.is_known
    
    # Type error
    str_val = Value(CtyString(), "hello")
    
    with pytest.raises(TypeError):
        negate(str_val)


@pytest.mark.asyncio
async def test_get_attribute():
    """Test get_attribute operation."""
    # Create object type and value
    obj_type = CtyObject(attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool()
    })
    
    obj = Value(obj_type, {
        "name": "Alice",
        "age": 30,
        "active": True
    })
    
    # Get attributes
    result = get_attribute(obj, "name")
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyString)
    assert result.value == "Alice"
    
    result = get_attribute(obj, "age")
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyNumber)
    assert result.value == 30
    
    result = get_attribute(obj, "active")
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyBool)
    assert result.value is True
    
    # Missing attribute
    with pytest.raises(AttributeError):
        get_attribute(obj, "missing")
    
    # Object with missing attributes
    obj2 = Value(obj_type, {
        "name": "Bob",
        # age and active are missing
    })
    
    result = get_attribute(obj2, "name")
    assert result.is_known
    assert not result.is_null
    assert result.value == "Bob"
    
    result = get_attribute(obj2, "age")
    assert result.is_null
    assert isinstance(result.type, CtyNumber)
    
    # Null and unknown objects
    obj_null = Value.null(obj_type)
    obj_unknown = Value.unknown(obj_type)
    
    result = get_attribute(obj_null, "name")
    assert result.is_null
    assert isinstance(result.type, CtyString)
    
    result = get_attribute(obj_unknown, "name")
    assert not result.is_known
    assert isinstance(result.type, CtyString)
    
    # Type error
    str_val = Value(CtyString(), "hello")
    
    with pytest.raises(TypeError):
        get_attribute(str_val, "length")


@pytest.mark.asyncio
async def test_get_element():
    """Test get_element operation."""
    # List element access
    list_val = Value(CtyList(element_type=CtyString()), ["a", "b", "c"])
    
    result = get_element(list_val, Value(CtyNumber(), 0))
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyString)
    assert result.value == "a"
    
    result = get_element(list_val, Value(CtyNumber(), 2))
    assert result.is_known
    assert not result.is_null
    assert result.value == "c"
    
    # Index out of range
    with pytest.raises(IndexError):
        get_element(list_val, Value(CtyNumber(), 3))
    
    with pytest.raises(IndexError):
        get_element(list_val, Value(CtyNumber(), -1))
    
    # Map element access
    map_val = Value(CtyMap(element_type=CtyNumber()), {"a": 1, "b": 2, "c": 3})
    
    result = get_element(map_val, Value(CtyString(), "a"))
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyNumber)
    assert result.value == 1
    
    result = get_element(map_val, Value(CtyString(), "c"))
    assert result.is_known
    assert not result.is_null
    assert result.value == 3
    
    # Key not found
    with pytest.raises(KeyError):
        get_element(map_val, Value(CtyString(), "d"))
    
    # Tuple element access
    tuple_type = CtyTuple(element_types=[CtyString(), CtyNumber(), CtyBool()])
    tuple_val = Value(tuple_type, ("hello", 42, True))
    
    result = get_element(tuple_val, Value(CtyNumber(), 0))
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyString)
    assert result.value == "hello"
    
    result = get_element(tuple_val, Value(CtyNumber(), 1))
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyNumber)
    assert result.value == 42
    
    result = get_element(tuple_val, Value(CtyNumber(), 2))
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyBool)
    assert result.value is True
    
    # Index out of range
    with pytest.raises(IndexError):
        get_element(tuple_val, Value(CtyNumber(), 3))
    
    # Null and unknown collections
    list_null = Value.null(CtyList(element_type=CtyString()))
    list_unknown = Value.unknown(CtyList(element_type=CtyString()))
    index = Value(CtyNumber(), 0)
    
    result = get_element(list_null, index)
    assert result.is_null
    assert isinstance(result.type, CtyString)
    
    result = get_element(list_unknown, index)
    assert not result.is_known
    assert isinstance(result.type, CtyString)
    
    # Null and unknown indices
    index_null = Value.null(CtyNumber())
    index_unknown = Value.unknown(CtyNumber())
    
    with pytest.raises(ValueError):
        get_element(list_val, index_null)
    
    result = get_element(list_val, index_unknown)
    assert not result.is_known
    assert isinstance(result.type, CtyString)
    
    # Type errors
    str_val = Value(CtyString(), "hello")
    
    with pytest.raises(TypeError):
        get_element(str_val, index)
    
    with pytest.raises(TypeError):
        get_element(list_val, Value(CtyString(), "a"))


@pytest.mark.asyncio
async def test_length():
    """Test length operation."""
    # String length
    str1 = Value(CtyString(), "hello")
    str2 = Value(CtyString(), "")
    
    result = length(str1)
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyNumber)
    assert result.value == 5
    
    result = length(str2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 0
    
    # List length
    list1 = Value(CtyList(element_type=CtyString()), ["a", "b", "c"])
    list2 = Value(CtyList(element_type=CtyString()), [])
    
    result = length(list1)
    assert result.is_known
    assert not result.is_null
    assert result.value == 3
    
    result = length(list2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 0
    
    # Map length
    map1 = Value(CtyMap(element_type=CtyNumber()), {"a": 1, "b": 2})
    map2 = Value(CtyMap(element_type=CtyNumber()), {})
    
    result = length(map1)
    assert result.is_known
    assert not result.is_null
    assert result.value == 2
    
    result = length(map2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 0
    
    # Set length
    set1 = Value(CtySet(element_type=CtyString()), {"a", "b", "c"})
    set2 = Value(CtySet(element_type=CtyString()), set())
    
    result = length(set1)
    assert result.is_known
    assert not result.is_null
    assert result.value == 3
    
    result = length(set2)
    assert result.is_known
    assert not result.is_null
    assert result.value == 0
    
    # Tuple length
    tuple_type = CtyTuple(element_types=[CtyString(), CtyNumber(), CtyBool()])
    tuple_val = Value(tuple_type, ("hello", 42, True))
    
    result = length(tuple_val)
    assert result.is_known
    assert not result.is_null
    assert result.value == 3
    
    # Null and unknown collections
    str_null = Value.null(CtyString())
    str_unknown = Value.unknown(CtyString())
    
    result = length(str_null)
    assert result.is_null
    assert isinstance(result.type, CtyNumber)
    
    result = length(str_unknown)
    assert not result.is_known
    assert isinstance(result.type, CtyNumber)
    
    # Type error
    num_val = Value(CtyNumber(), 42)
    
    with pytest.raises(TypeError):
        length(num_val)


@pytest.mark.asyncio
async def test_contains():
    """Test contains operation."""
    # String containment
    str_val = Value(CtyString(), "hello world")
    
    result = contains(str_val, Value(CtyString(), "hello"))
    assert result.is_known
    assert not result.is_null
    assert result.value is True
    
    result = contains(str_val, Value(CtyString(), "goodbye"))
    assert result.is_known
    assert not result.is_null
    assert result.value is False
    
    # List containment
    list_val = Value(CtyList(element_type=CtyString()), ["a", "b", "c"])
    
    result = contains(list_val, Value(CtyString(), "a"))
    assert result.is_known
    assert not result.is_null
    assert result.value is True
    
    result = contains(list_val, Value(CtyString(), "d"))
    assert result.is_known
    assert not result.is_null
    assert result.value is False
    
    # Map containment (key check)
    map_val = Value(CtyMap(element_type=CtyNumber()), {"a": 1, "b": 2, "c": 3})
    
    result = contains(map_val, Value(CtyString(), "a"))
    assert result.is_known
    assert not result.is_null
    assert result.value is True
    
    result = contains(map_val, Value(CtyString(), "d"))
    assert result.is_known
    assert not result.is_null
    assert result.value is False
    
    # Set containment
    set_val = Value(CtySet(element_type=CtyString()), {"a", "b", "c"})
    
    result = contains(set_val, Value(CtyString(), "a"))
    assert result.is_known
    assert not result.is_null
    assert result.value is True
    
    result = contains(set_val, Value(CtyString(), "d"))
    assert result.is_known
    assert not result.is_null
    assert result.value is False
    
    # Type compatibility
    result = contains(list_val, Value(CtyNumber(), 1))
    assert result.is_known
    assert not result.is_null
    assert result.value is False
    
    # Null and unknown collections
    str_null = Value.null(CtyString())
    str_unknown = Value.unknown(CtyString())
    item = Value(CtyString(), "a")
    
    result = contains(str_null, item)
    assert result.is_null
    assert isinstance(result.type, CtyBool)
    
    result = contains(str_unknown, item)
    assert not result.is_known
    assert isinstance(result.type, CtyBool)
    
    # Null and unknown items
    item_null = Value.null(CtyString())
    item_unknown = Value.unknown(CtyString())
    
    result = contains(str_val, item_null)
    assert result.is_null
    assert isinstance(result.type, CtyBool)
    
    result = contains(str_val, item_unknown)
    assert not result.is_known
    assert isinstance(result.type, CtyBool)
    
    # Type error
    num_val = Value(CtyNumber(), 42)
    
    with pytest.raises(TypeError):
        contains(num_val, item)


@pytest.mark.asyncio
async def test_concat_lists():
    """Test concat_lists operation."""
    # Basic list concatenation
    list1 = Value(CtyList(element_type=CtyString()), ["a", "b"])
    list2 = Value(CtyList(element_type=CtyString()), ["c", "d"])
    list3 = Value(CtyList(element_type=CtyString()), ["e", "f"])
    
    result = concat_lists(list1, list2, list3)
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyList)
    assert isinstance(result.type.element_type, CtyString)
    assert result.value == ["a", "b", "c", "d", "e", "f"]
    
    # Empty lists
    empty_list = Value(CtyList(element_type=CtyString()), [])
    
    result = concat_lists(empty_list, empty_list)
    assert result.is_known
    assert not result.is_null
    assert result.value == []
    
    result = concat_lists(list1, empty_list, list3)
    assert result.is_known
    assert not result.is_null
    assert result.value == ["a", "b", "e", "f"]
    
    # No lists
    result = concat_lists()
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyList)
    assert isinstance(result.type.element_type, CtyDynamic)
    assert result.value == []
    
    # Incompatible element types
    list4 = Value(CtyList(element_type=CtyNumber()), [1, 2])
    
    with pytest.raises(ValueError):
        concat_lists(list1, list4)
    
    # Null and unknown lists
    list_null = Value.null(CtyList(element_type=CtyString()))
    list_unknown = Value.unknown(CtyList(element_type=CtyString()))
    
    result = concat_lists(list1, list_null, list3)
    assert result.is_known
    assert not result.is_null
    assert result.value == ["a", "b", "e", "f"]
    
    result = concat_lists(list1, list_unknown)
    assert not result.is_known
    assert isinstance(result.type, CtyList)
    assert isinstance(result.type.element_type, CtyString)
    
    result = concat_lists(list_null, list_null)
    assert result.is_null
    assert isinstance(result.type, CtyList)
    assert isinstance(result.type.element_type, CtyString)
    
    # Type error
    str_val = Value(CtyString(), "hello")
    
    with pytest.raises(TypeError):
        concat_lists(list1, str_val)


@pytest.mark.asyncio
async def test_merge_maps():
    """Test merge_maps operation."""
    # Basic map merging
    map1 = Value(CtyMap(element_type=CtyString()), {"a": "A", "b": "B"})
    map2 = Value(CtyMap(element_type=CtyString()), {"c": "C", "d": "D"})
    map3 = Value(CtyMap(element_type=CtyString()), {"e": "E", "f": "F"})
    
    result = merge_maps(map1, map2, map3)
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyMap)
    assert isinstance(result.type.element_type, CtyString)
    assert result.value == {"a": "A", "b": "B", "c": "C", "d": "D", "e": "E", "f": "F"}
    
    # Overlapping keys (later maps override earlier ones)
    map4 = Value(CtyMap(element_type=CtyString()), {"a": "X", "c": "Y"})
    
    result = merge_maps(map1, map2, map4)
    assert result.is_known
    assert not result.is_null
    assert result.value == {"a": "X", "b": "B", "c": "Y", "d": "D"}
    
    # Empty maps
    empty_map = Value(CtyMap(element_type=CtyString()), {})
    
    result = merge_maps(empty_map, empty_map)
    assert result.is_known
    assert not result.is_null
    assert result.value == {}
    
    result = merge_maps(map1, empty_map, map3)
    assert result.is_known
    assert not result.is_null
    assert result.value == {"a": "A", "b": "B", "e": "E", "f": "F"}
    
    # No maps
    result = merge_maps()
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyMap)
    assert isinstance(result.type.element_type, CtyDynamic)
    assert result.value == {}
    
    # Incompatible element types
    map5 = Value(CtyMap(element_type=CtyNumber()), {"a": 1, "b": 2})
    
    with pytest.raises(ValueError):
        merge_maps(map1, map5)
    
    # Null and unknown maps
    map_null = Value.null(CtyMap(element_type=CtyString()))
    map_unknown = Value.unknown(CtyMap(element_type=CtyString()))
    
    result = merge_maps(map1, map_null, map3)
    assert result.is_known
    assert not result.is_null
    assert result.value == {"a": "A", "b": "B", "e": "E", "f": "F"}
    
    result = merge_maps(map1, map_unknown)
    assert not result.is_known
    assert isinstance(result.type, CtyMap)
    assert isinstance(result.type.element_type, CtyString)
    
    result = merge_maps(map_null, map_null)
    assert result.is_null
    assert isinstance(result.type, CtyMap)
    assert isinstance(result.type.element_type, CtyString)
    
    # Type error
    str_val = Value(CtyString(), "hello")
    
    with pytest.raises(TypeError):
        merge_maps(map1, str_val)


@pytest.mark.asyncio
async def test_slice_string():
    """Test slice_string operation."""
    # Basic string slicing
    str_val = Value(CtyString(), "hello world")
    
    result = slice_string(str_val, Value(CtyNumber(), 0), Value(CtyNumber(), 5))
    assert result.is_known
    assert not result.is_null
    assert isinstance(result.type, CtyString)
    assert result.value == "hello"
    
    result = slice_string(str_val, Value(CtyNumber(), 6), Value(CtyNumber(), 11))
    assert result.is_known
    assert not result.is_null
    assert result.value == "world"
    
    # Implicit end index
    result = slice_string(str_val, Value(CtyNumber(), 6))
    assert result.is_known
    assert not result.is_null
    assert result.value == "world"
    
    # Empty slice
    result = slice_string(str_val, Value(CtyNumber(), 5), Value(CtyNumber(), 5))
    assert result.is_known
    assert not result.is_null
    assert result.value == ""
    