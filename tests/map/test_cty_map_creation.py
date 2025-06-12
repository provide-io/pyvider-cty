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
    CtyDynamic # Added for consistency if used
)


class TestCtyMapCreation:
    """Test CtyMap type creation and basic validation."""

    def setup_method(self):
        """Set up common map types and values for tests."""
        # Create map types with proper CtyString key type
        self.string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        self.number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        self.bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())

        # Pre-create CtyValue instances for keys and values
        self.key1 = CtyValue(vtype=CtyString(), value="key1")
        self.val1_str = CtyValue(vtype=CtyString(), value="value1")
        self.key2 = CtyValue(vtype=CtyString(), value="key2")
        self.val2_str = CtyValue(vtype=CtyString(), value="value2")
        self.val1_num = CtyValue(vtype=CtyNumber(), value=1)
        self.val2_num = CtyValue(vtype=CtyNumber(), value=2)
        self.val1_bool = CtyValue(vtype=CtyBool(), value=True)
        self.val2_bool = CtyValue(vtype=CtyBool(), value=False)

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
        with pytest.raises(CtyMapValidationError, match=r"key_type must be a CtyType instance, got str"):
            CtyMap(key_type="string", value_type=CtyString())

        # Invalid value_type (not a CtyType)
        with pytest.raises(CtyMapValidationError, match=r"value_type must be a CtyType instance, got str"):
            CtyMap(key_type=CtyString(), value_type="string")

        # Both invalid - key_type=None should be caught first
        with pytest.raises(CtyMapValidationError, match=r"key_type must be a CtyType instance, got NoneType"):
            CtyMap(key_type=None, value_type=123) # This will hit key_type check first

        # Invalid key_type (not primitive)
        with pytest.raises(CtyMapValidationError, match=r"Map key_type must be a primitive type, got CtyList"):
            CtyMap(key_type=CtyList(element_type=CtyString()), value_type=CtyString())


    @pytest.mark.asyncio
    async def test_empty_map_validation(self):
        """Test validation of empty maps."""
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())

        # Validate empty dict (None now raises error as per CtyMap.validate change in src)
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
            assert f"Expected dict or CtyValue map, got {type(value).__name__}" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cty_map_validate_simple_values(self):
        """Test validation of maps with simple values using direct internal value access."""
        # Create map with pre-validated keys and values
        data = {
            self.key1: self.val1_str,
            self.key2: self.val2_str
        }

        # Validate the map
        result = self.string_map.validate(data)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)

        # Access values directly from the internal map
        # The implementation stores keys as string values
        assert len(result.value) == 2
        assert "key1" in result.value
        assert "key2" in result.value
        assert result.value["key1"] is self.val1_str
        assert result.value["key2"] is self.val2_str

        # Test number map
        number_data = {
            self.key1: self.val1_num,
            self.key2: self.val2_num
        }

        number_result = self.number_map.validate(number_data)
        assert isinstance(number_result, CtyValue)
        assert len(number_result.value) == 2
        assert "key1" in number_result.value
        assert "key2" in number_result.value
        assert number_result.value["key1"] is self.val1_num
        assert number_result.value["key2"] is self.val2_num

        # Test boolean map
        bool_data = {
            self.key1: self.val1_bool,
            self.key2: self.val2_bool
        }

        bool_result = self.bool_map.validate(bool_data)
        assert isinstance(bool_result, CtyValue)
        assert len(bool_result.value) == 2
        assert "key1" in bool_result.value
        assert "key2" in bool_result.value
        assert bool_result.value["key1"] is self.val1_bool
        assert bool_result.value["key2"] is self.val2_bool

    @pytest.mark.asyncio
    async def test_cty_map_validate_with_prevalidated_values(self):
        """Test validation with pre-validated CtyValue inputs."""
        # Create map with pre-validated values
        data = {
            self.key1: self.val1_str,
            self.key2: self.val2_str
        }

        # Validate the map
        result = self.string_map.validate(data)
        assert isinstance(result, CtyValue)

        # Direct access to internal dictionary
        assert len(result.value) == 2
        assert "key1" in result.value
        assert "key2" in result.value
        assert result.value["key1"] is self.val1_str
        assert result.value["key2"] is self.val2_str

    @pytest.mark.asyncio
    async def test_cty_map_validate_with_mixed_inputs(self):
        """Test validation with a mix of raw values and CtyValues."""
        # Create map with mixed inputs
        data = {
            self.key1: "value1",       # CtyValue key, raw value
            "key2": self.val2_str,     # Raw key, CtyValue value
            "key3": "value3"           # Raw key, raw value
        }

        # Validate the map
        result = self.string_map.validate(data)
        assert isinstance(result, CtyValue)

        # Direct access to internal dictionary
        assert len(result.value) == 3
        assert "key1" in result.value
        assert "key2" in result.value
        assert "key3" in result.value

        # Raw values should be wrapped in CtyValue
        assert isinstance(result.value["key1"], CtyValue)
        assert result.value["key1"].value == "value1"

        # Pre-validated values should be preserved
        assert result.value["key2"] is self.val2_str

        # Raw values should be wrapped in CtyValue
        assert isinstance(result.value["key3"], CtyValue)
        assert result.value["key3"].value == "value3"

    @pytest.mark.asyncio
    async def test_cty_map_validate_invalid_key_type(self):
        """Test validation with invalid key type."""
        # Invalid key type - use a numeric key
        invalid_data = {
            123: "value1"  # Number key, should fail
        }

        try:
            self.string_map.validate(invalid_data)
            pytest.fail("Expected CtyMapValidationError but no exception was raised")
        except CtyMapValidationError:
            # Test passes - exception was raised as expected
            pass

        # Invalid key using wrong CtyValue type
        invalid_key = CtyValue(vtype=CtyNumber(), value=456)
        invalid_data = {
            invalid_key: self.val1_str
        }

        try:
            self.string_map.validate(invalid_data)
            pytest.fail("Expected CtyMapValidationError but no exception was raised")
        except CtyMapValidationError:
            # Test passes - exception was raised as expected
            pass


class TestCtyMapIteration:
    """Test map iteration operations."""

    @pytest.mark.asyncio
    async def test_cty_map_iteration(self):
        """Test iteration over map keys using ElementIterator."""
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

        # Create CtyValue keys and values
        key1 = CtyValue(vtype=CtyString(), value="one")
        key2 = CtyValue(vtype=CtyString(), value="two")
        key3 = CtyValue(vtype=CtyString(), value="three")
        val1 = CtyValue(vtype=CtyNumber(), value=1)
        val2 = CtyValue(vtype=CtyNumber(), value=2)
        val3 = CtyValue(vtype=CtyNumber(), value=3)

        # Create map data dictionary
        data = {key1: val1, key2: val2, key3: val3}

        # Validate the map
        map_val = map_type.validate(data)

        # Direct verification using internal dictionary
        assert len(map_val.value) == 3
        assert "one" in map_val.value
        assert "two" in map_val.value
        assert "three" in map_val.value
        assert map_val.value["one"] is val1
        assert map_val.value["two"] is val2
        assert map_val.value["three"] is val3

        # Manual iteration test - collect keys from internal dictionary
        keys = set()
        for key_str in map_val.value:
            keys.add(key_str)

        # Verify key strings from internal map
        assert keys == {"one", "two", "three"}

# fuck
# 🐍🏗️🧪
