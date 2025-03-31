#
# tests/map/test_cty_map_creation.py
#

"""
Tests for CtyMap creation and basic validation functionality.

This module tests the creation of CtyMap types with different key and value types,
basic validation, and error handling during type creation.
"""

import pytest
from decimal import Decimal

from pyvider.cty.exceptions import CtyMapValidationError
from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)


class TestCtyMapCreation:
    """Test CtyMap type creation and basic validation."""

    @pytest.mark.asyncio
    async def test_cty_map_init_basic(self):
        """Test basic initialization of CtyMap types with different value types."""
        # String key, String value
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        assert isinstance(string_map, CtyMap)
        assert isinstance(string_map.key_type, CtyString)
        assert isinstance(string_map.value_type, CtyString)

        # String key, Number value
        number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        assert isinstance(number_map, CtyMap)
        assert isinstance(number_map.key_type, CtyString)
        assert isinstance(number_map.value_type, CtyNumber)

        # String key, Bool value
        bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())
        assert isinstance(bool_map, CtyMap)
        assert isinstance(bool_map.key_type, CtyString)
        assert isinstance(bool_map.value_type, CtyBool)

    @pytest.mark.asyncio
    async def test_cty_map_init_complex_value_types(self):
        """Test initialization with complex value types."""
        # Map with list value type
        list_type = CtyList(element_type=CtyString())
        list_map = CtyMap(key_type=CtyString(), value_type=list_type)
        assert isinstance(list_map, CtyMap)
        assert isinstance(list_map.value_type, CtyList)
        assert isinstance(list_map.value_type.element_type, CtyString)

        # Map with object value type
        object_type = CtyObject(attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        })
        object_map = CtyMap(key_type=CtyString(), value_type=object_type)
        assert isinstance(object_map, CtyMap)
        assert isinstance(object_map.value_type, CtyObject)
        assert "name" in object_map.value_type.attribute_types
        assert "age" in object_map.value_type.attribute_types

        # Map with tuple value type
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        tuple_map = CtyMap(key_type=CtyString(), value_type=tuple_type)
        assert isinstance(tuple_map, CtyMap)
        assert isinstance(tuple_map.value_type, CtyTuple)
        assert len(tuple_map.value_type.element_types) == 2

        # Nested map type (map of maps)
        inner_map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        nested_map = CtyMap(key_type=CtyString(), value_type=inner_map_type)
        assert isinstance(nested_map, CtyMap)
        assert isinstance(nested_map.value_type, CtyMap)
        assert isinstance(nested_map.value_type.key_type, CtyString)
        assert isinstance(nested_map.value_type.value_type, CtyString)

    @pytest.mark.asyncio
    async def test_cty_map_init_invalid_types(self):
        """Test initialization with invalid key or value types."""
        # Invalid key_type (not a CtyType)
        with pytest.raises(CtyMapValidationError) as exc_info:
            CtyMap(key_type="string", value_type=CtyString())
        assert "Map key type must be CtyString" in str(exc_info.value)

        # Invalid value_type (not a CtyType)
        with pytest.raises(CtyMapValidationError) as exc_info:
            CtyMap(key_type=CtyString(), value_type="string")
        assert "Expected CtyType for value_type" in str(exc_info.value)

        # Both invalid
        with pytest.raises(CtyMapValidationError):
            CtyMap(key_type=None, value_type=123)

    @pytest.mark.asyncio
    async def test_empty_map_validation(self):
        """Test validation of empty maps."""
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())

        # Validate None
        null_result = string_map.validate(None)
        assert isinstance(null_result, CtyValue)
        assert isinstance(null_result.type, CtyMap)
        assert null_result.type.equal(string_map)
        assert len(null_result.value) == 0

        # Validate empty dict
        empty_result = string_map.validate({})
        assert isinstance(empty_result, CtyValue)
        assert isinstance(empty_result.type, CtyMap)
        assert empty_result.type.equal(string_map)
        assert len(empty_result.value) == 0

    @pytest.mark.asyncio
    async def test_cty_map_validate_non_dict(self):
        """Test validation of non-dictionary values."""
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())

        # Test various non-dict types
        invalid_values = [
            "string",
            123,
            True,
            [1, 2, 3],
            (1, 2, 3),
            set([1, 2, 3])
        ]

        for value in invalid_values:
            with pytest.raises(CtyMapValidationError) as exc_info:
                string_map.validate(value)
            assert f"Expected dict, got {type(value).__name__}" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cty_map_validate_simple_values(self):
        """Test validation of maps with simple values."""
        # Create map types
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())

        # Validate string map
        string_data = {"key1": "value1", "key2": "value2"}
        string_result = string_map.validate(string_data)
        assert isinstance(string_result, CtyValue)
        assert isinstance(string_result.type, CtyMap)
        assert len(string_result.value) == 2

        # Check keys and values are properly wrapped
        for k, v in string_result.value.items():
            assert isinstance(k, CtyValue)
            assert isinstance(k.type, CtyString)
            assert isinstance(v, CtyValue)
            assert isinstance(v.type, CtyString)
            # Verify values match
            if k.value == "key1":
                assert v.value == "value1"
            elif k.value == "key2":
                assert v.value == "value2"

        # Validate number map
        number_data = {"count": 10, "total": 123.45, "decimal": Decimal("67.89")}
        number_result = number_map.validate(number_data)
        assert isinstance(number_result, CtyValue)
        assert len(number_result.value) == 3

        # Check keys and values
        for k, v in number_result.value.items():
            assert isinstance(k, CtyValue)
            assert isinstance(k.type, CtyString)
            assert isinstance(v, CtyValue)
            assert isinstance(v.type, CtyNumber)

        # Validate boolean map
        bool_data = {"flag1": True, "flag2": False}
        bool_result = bool_map.validate(bool_data)
        assert isinstance(bool_result, CtyValue)
        assert len(bool_result.value) == 2

        # Check keys and values
        for k, v in bool_result.value.items():
            assert isinstance(k, CtyValue)
            assert isinstance(k.type, CtyString)
            assert isinstance(v, CtyValue)
            assert isinstance(v.type, CtyBool)

    @pytest.mark.asyncio
    async def test_cty_map_validate_with_prevalidated_values(self):
        """Test validation with pre-validated CtyValue inputs."""
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())

        # Create CtyValues for keys and values
        key1 = CtyValue(type_=CtyString(), value="key1")
        key2 = CtyValue(type_=CtyString(), value="key2")
        val1 = CtyValue(type_=CtyString(), value="value1")
        val2 = CtyValue(type_=CtyString(), value="value2")

        # Create map with pre-validated values
        data = {
            key1: val1,
            key2: val2
        }

        result = string_map.validate(data)
        assert isinstance(result, CtyValue)
        assert len(result.value) == 2

        # Check that the original CtyValues are preserved
        for k, v in result.value.items():
            if k.value == "key1":
                assert k is key1  # Same instance
                assert v is val1  # Same instance
            elif k.value == "key2":
                assert k is key2  # Same instance
                assert v is val2  # Same instance

    @pytest.mark.asyncio
    async def test_cty_map_validate_with_mixed_inputs(self):
        """Test validation with a mix of raw values and CtyValues."""
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())

        # Create some CtyValues
        key1 = CtyValue(type_=CtyString(), value="key1")
        val2 = CtyValue(type_=CtyString(), value="value2")

        # Create map with mixed inputs
        data = {
            key1: "value1",       # CtyValue key, raw value
            "key2": val2,         # Raw key, CtyValue value
            "key3": "value3"      # Raw key, raw value
        }

        result = string_map.validate(data)
        assert isinstance(result, CtyValue)
        assert len(result.value) == 3

        # Check keys and values
        for k, v in result.value.items():
            assert isinstance(k, CtyValue)
            assert isinstance(k.type, CtyString)
            assert isinstance(v, CtyValue)
            assert isinstance(v.type, CtyString)

            if k.value == "key1":
                assert k is key1  # Same instance
                assert v.value == "value1"
            elif k.value == "key2":
                assert v is val2  # Same instance
            elif k.value == "key3":
                assert v.value == "value3"

    @pytest.mark.asyncio
    async def test_cty_map_validate_invalid_key_type(self):
        """Test validation with invalid key type."""
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())

        # Invalid key type - we need to use a key that Python allows but CtyMap will reject
        invalid_data = {
            123: "value2"  # Number key, should fail
        }

        with pytest.raises(CtyMapValidationError) as exc_info:
            string_map.validate(invalid_data)
        assert "validation failed" in str(exc_info.value)

@pytest.mark.asyncio
async def test_cty_map_iteration():
    """Test iteration over map keys."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Create a map with data
    data = {"one": 1, "two": 2, "three": 3}
    map_val = map_type.validate(data)

    # Test __iter__
    keys = set()
    for key in map_val.value:
        assert isinstance(key, CtyValue)
        assert isinstance(key.type, CtyString)
        keys.add(key.value)

    assert keys == {"one", "two", "three"}

# 🐍🏗️🧪
