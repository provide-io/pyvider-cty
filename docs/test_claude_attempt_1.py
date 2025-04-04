#
# tests/map/test_cty_map.py
#

"""
Comprehensive test suite for CtyMap implementation.

Tests focus on validating CtyMap behavior as implemented in map.py, covering:
1. Type creation and validation
2. Map operations (get, set, delete)
3. Type comparison and equality
4. Edge cases and error handling
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
    CtyPath,
)


class TestCtyMapCreation:
    """Test CtyMap type creation and initialization."""

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
        # Invalid key_type (not a CtyString)
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
    async def test_cty_map_string_representation(self):
        """Test string representation of map types."""
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        
        # Test __str__ representation
        str_repr = str(string_map)
        assert "map" in str_repr
        assert "CtyString" in str_repr
        
        # Test __repr__ representation
        repr_str = repr(string_map)
        assert "CtyMap" in repr_str
        assert "key_type" in repr_str
        assert "value_type" in repr_str


class TestCtyMapValidation:
    """Test validation of maps with various input types."""
    
    def setup_method(self):
        """Set up common map types and values for tests."""
        self.string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        self.number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        self.bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())
        
        # Create complex map types
        self.nested_map = CtyMap(
            key_type=CtyString(),
            value_type=CtyMap(key_type=CtyString(), value_type=CtyString())
        )
        
        self.list_map = CtyMap(
            key_type=CtyString(),
            value_type=CtyList(element_type=CtyString())
        )
        
        # Create sample CtyValue instances for tests
        self.key1 = CtyValue(vtype=CtyString(), value="key1")
        self.key2 = CtyValue(vtype=CtyString(), value="key2")
        self.val1 = CtyValue(vtype=CtyString(), value="value1")
        self.val2 = CtyValue(vtype=CtyString(), value="value2")

    @pytest.mark.asyncio
    async def test_cty_map_empty_map_validation(self):
        """Test validation of empty maps."""
        # Validate None (should create empty map)
        result = self.string_map.validate(None)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        assert len(result.value) == 0
        
        # Validate empty dict
        result = self.string_map.validate({})
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        assert len(result.value) == 0

    @pytest.mark.asyncio
    async def test_cty_map_validate_with_prevalidated_values(self):
        """Test validation with pre-validated CtyValue keys and values."""
        # Create map with pre-validated values
        data = {
            self.key1: self.val1,
            self.key2: self.val2
        }

        result = self.string_map.validate(data)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        
        # Verify map structure
        map_data = result.value
        assert len(map_data) == 2
        
        # Verify keys are stored as strings
        assert "key1" in map_data
        assert "key2" in map_data
        
        # Verify values are preserved
        assert map_data["key1"] is self.val1
        assert map_data["key2"] is self.val2

    @pytest.mark.asyncio
    async def test_cty_map_validate_with_raw_values(self):
        """Test validation with raw Python values."""
        # Create map with raw values
        data = {
            "key1": "value1",
            "key2": "value2"
        }

        result = self.string_map.validate(data)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        
        # Verify map structure
        map_data = result.value
        assert len(map_data) == 2
        
        # Verify keys are stored as strings
        assert "key1" in map_data
        assert "key2" in map_data
        
        # Verify values are converted to CtyValue
        assert isinstance(map_data["key1"], CtyValue)
        assert isinstance(map_data["key2"], CtyValue)
        assert map_data["key1"].value == "value1"
        assert map_data["key2"].value == "value2"

    @pytest.mark.asyncio
    async def test_cty_map_validate_non_dict(self):
        """Test validation of non-dictionary values."""
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
                self.string_map.validate(value)
            assert f"Expected dict, got {type(value).__name__}" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cty_map_validate_invalid_key(self):
        """Test validation with invalid key type."""
        # Invalid key type - a number instead of a string
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({123: "value"})
        
        # Invalid CtyValue key type
        invalid_key = CtyValue(vtype=CtyNumber(), value=123)
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({invalid_key: self.val1})
        
        # Null key
        null_key = CtyValue(vtype=CtyString(), is_null=True)
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({null_key: self.val1})
        
        # Unknown key
        unknown_key = CtyValue(vtype=CtyString(), is_unknown=True)
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({unknown_key: self.val1})

    @pytest.mark.asyncio
    async def test_cty_map_validate_invalid_value(self):
        """Test validation with invalid value type."""
        # Invalid value type for string map
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({"key": 123})
        
        # Invalid CtyValue value type
        invalid_value = CtyValue(vtype=CtyNumber(), value=123)
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({self.key1: invalid_value})

    @pytest.mark.asyncio
    async def test_cty_map_validate_mixed_types(self):
        """Test validation with mix of raw values and CtyValues."""
        # Create map with mixed inputs
        data = {
            self.key1: "value1",       # CtyValue key, raw value
            "key2": self.val2,         # Raw key, CtyValue value
            "key3": "value3"           # Raw key, raw value
        }

        result = self.string_map.validate(data)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        
        # Verify map structure
        map_data = result.value
        assert len(map_data) == 3
        
        # Verify keys are stored as strings
        assert "key1" in map_data
        assert "key2" in map_data
        assert "key3" in map_data
        
        # Verify values
        assert isinstance(map_data["key1"], CtyValue)
        assert map_data["key1"].value == "value1"
        assert map_data["key2"] is self.val2
        assert isinstance(map_data["key3"], CtyValue)
        assert map_data["key3"].value == "value3"

    @pytest.mark.asyncio
    async def test_cty_map_validate_nested_map(self):
        """Test validation of maps with nested maps as values."""
        # Create nested map data with pre-validated values
        inner_map1 = {
            CtyValue(vtype=CtyString(), value="name"): CtyValue(vtype=CtyString(), value="Alice"),
            CtyValue(vtype=CtyString(), value="email"): CtyValue(vtype=CtyString(), value="alice@example.com")
        }
        
        inner_map2 = {
            CtyValue(vtype=CtyString(), value="name"): CtyValue(vtype=CtyString(), value="Bob"),
            CtyValue(vtype=CtyString(), value="email"): CtyValue(vtype=CtyString(), value="bob@example.com")
        }
        
        data = {
            CtyValue(vtype=CtyString(), value="user1"): inner_map1,
            CtyValue(vtype=CtyString(), value="user2"): inner_map2
        }
        
        # Validate nested map
        result = self.nested_map.validate(data)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        
        # Verify map structure
        map_data = result.value
        assert len(map_data) == 2
        
        # Verify nested maps
        user1_data = map_data["user1"]
        assert isinstance(user1_data, CtyValue)
        assert isinstance(user1_data.type, CtyMap)
        assert len(user1_data.value) == 2
        assert user1_data.value["name"].value == "Alice"
        assert user1_data.value["email"].value == "alice@example.com"
        
        user2_data = map_data["user2"]
        assert isinstance(user2_data, CtyValue)
        assert isinstance(user2_data.type, CtyMap)
        assert len(user2_data.value) == 2
        assert user2_data.value["name"].value == "Bob"
        assert user2_data.value["email"].value == "bob@example.com"

    @pytest.mark.asyncio
    async def test_cty_map_validate_nested_map_with_raw_values(self):
        """Test validation of nested maps with raw values."""
        # Valid nested data with raw values
        data = {
            "user1": {"name": "Alice", "email": "alice@example.com"},
            "user2": {"name": "Bob", "email": "bob@example.com"}
        }
        
        result = self.nested_map.validate(data)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        
        # Verify map structure
        map_data = result.value
        assert len(map_data) == 2
        
        # Verify nested maps
        user1_data = map_data["user1"]
        assert isinstance(user1_data, CtyValue)
        assert isinstance(user1_data.type, CtyMap)
        assert len(user1_data.value) == 2
        assert user1_data.value["name"].value == "Alice"
        assert user1_data.value["email"].value == "alice@example.com"

    @pytest.mark.asyncio
    async def test_cty_map_validate_nested_map_invalid(self):
        """Test validation with invalid nested map data."""
        # Invalid nested data (wrong value type in nested map)
        invalid_data = {
            "user1": {"name": "Alice", "email": 123}  # Number where string expected
        }
        
        with pytest.raises(CtyMapValidationError):
            self.nested_map.validate(invalid_data)

    @pytest.mark.asyncio
    async def test_cty_map_validate_list_map(self):
        """Test validation of maps with lists as values."""
        # Valid list data
        data = {
            "fruits": ["apple", "banana", "cherry"],
            "vegetables": ["carrot", "broccoli"],
            "empty": []
        }
        
        result = self.list_map.validate(data)
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        
        # Verify map structure
        map_data = result.value
        assert len(map_data) == 3
        
        # Verify list values
        fruits = map_data["fruits"]
        assert isinstance(fruits, CtyValue)
        assert isinstance(fruits.type, CtyList)
        assert len(fruits.value) == 3
        assert [item.value for item in fruits.value] == ["apple", "banana", "cherry"]
        
        vegetables = map_data["vegetables"]
        assert isinstance(vegetables, CtyValue)
        assert isinstance(vegetables.type, CtyList)
        assert len(vegetables.value) == 2
        
        empty = map_data["empty"]
        assert isinstance(empty, CtyValue)
        assert isinstance(empty.type, CtyList)
        assert len(empty.value) == 0

    @pytest.mark.asyncio
    async def test_cty_map_validate_list_map_invalid(self):
        """Test validation with invalid list map data."""
        # Invalid list data (wrong element type)
        invalid_data = {
            "mixed": ["string", 123, True]  # Should be all strings
        }
        
        with pytest.raises(CtyMapValidationError):
            self.list_map.validate(invalid_data)


class TestCtyMapOperations:
    """Test map operations like get, set, and delete."""
    
    def setup_method(self):
        """Set up common map types and values for tests."""
        self.string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        self.number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        
        # Create pre-validated keys and values
        self.key1 = CtyValue(vtype=CtyString(), value="key1")
        self.key2 = CtyValue(vtype=CtyString(), value="key2")
        self.key3 = CtyValue(vtype=CtyString(), value="key3")
        self.val1 = CtyValue(vtype=CtyString(), value="value1")
        self.val2 = CtyValue(vtype=CtyString(), value="value2")
        self.val3 = CtyValue(vtype=CtyString(), value="value3")
        
        # Create and validate maps
        self.empty_map = self.string_map.validate({})
        self.sample_map = self.string_map.validate({
            self.key1: self.val1,
            self.key2: self.val2,
            self.key3: self.val3
        })

    @pytest.mark.asyncio
    async def test_cty_map_get_operation(self):
        """Test getting values from a map."""
        # Get existing key with pre-validated key
        result = self.string_map.get(self.sample_map, self.key1)
        assert result is not None
        assert result is self.val1
        
        # Get existing key with raw string
        result = self.string_map.get(self.sample_map, "key2")
        assert result is not None
        assert result is self.val2
        
        # Get non-existent key with default
        default_val = CtyValue(vtype=CtyString(), value="default")
        result = self.string_map.get(self.sample_map, "missing", default_val)
        assert result is default_val
        
        # Get non-existent key without default
        result = self.string_map.get(self.sample_map, "missing")
        assert result is None

    @pytest.mark.asyncio
    async def test_cty_map_get_operation_invalid_inputs(self):
        """Test get operation with invalid inputs."""
        # Get from null map
        null_map = CtyValue(vtype=self.string_map, is_null=True)
        with pytest.raises((TypeError, CtyMapValidationError)):
            self.string_map.get(null_map, "key")
        
        # Get from unknown map
        unknown_map = CtyValue(vtype=self.string_map, is_unknown=True)
        with pytest.raises((TypeError, CtyMapValidationError)):
            self.string_map.get(unknown_map, "key")
        
        # Get with invalid key type (should return default, not raise)
        result = self.string_map.get(self.sample_map, 123)
        assert result is None

    @pytest.mark.asyncio
    async def test_cty_map_set_operation(self):
        """Test setting values in a map."""
        # Set new key with pre-validated key and value
        new_key = CtyValue(vtype=CtyString(), value="new_key")
        new_val = CtyValue(vtype=CtyString(), value="new_value")
        
        updated_map = self.string_map.set(self.empty_map, new_key, new_val)
        assert isinstance(updated_map, CtyValue)
        assert isinstance(updated_map.type, CtyMap)
        assert len(updated_map.value) == 1
        assert "new_key" in updated_map.value
        assert updated_map.value["new_key"] is new_val
        
        # Set new key with raw values
        updated_map2 = self.string_map.set(updated_map, "raw_key", "raw_value")
        assert len(updated_map2.value) == 2
        assert "raw_key" in updated_map2.value
        assert updated_map2.value["raw_key"].value == "raw_value"
        
        # Update existing key
        updated_map3 = self.string_map.set(updated_map2, "new_key", "updated_value")
        assert len(updated_map3.value) == 2
        assert updated_map3.value["new_key"].value == "updated_value"
        
        # Original maps should be unchanged (immutability)
        assert len(self.empty_map.value) == 0
        assert len(updated_map.value) == 1
        assert updated_map.value["new_key"] is new_val

    @pytest.mark.asyncio
    async def test_cty_map_set_operation_invalid_inputs(self):
        """Test set operation with invalid inputs."""
        # Set with invalid key type
        with pytest.raises((TypeError, CtyMapValidationError)):
            self.string_map.set(self.empty_map, 123, "value")
        
        # Set with invalid value type
        with pytest.raises((TypeError, CtyMapValidationError)):
            self.string_map.set(self.empty_map, "key", 123)
        
        # Set on null map
        null_map = CtyValue(vtype=self.string_map, is_null=True)
        with pytest.raises((TypeError, CtyMapValidationError)):
            self.string_map.set(null_map, "key", "value")

    @pytest.mark.asyncio
    async def test_cty_map_delete_operation(self):
        """Test deleting keys from a map."""
        # Delete existing key with pre-validated key
        updated_map = self.string_map.delete(self.sample_map, self.key2)
        assert isinstance(updated_map, CtyValue)
        assert isinstance(updated_map.type, CtyMap)
        assert len(updated_map.value) == 2
        assert "key1" in updated_map.value
        assert "key3" in updated_map.value
        assert "key2" not in updated_map.value
        
        # Delete key with raw string
        updated_map2 = self.string_map.delete(updated_map, "key1")
        assert len(updated_map2.value) == 1
        assert "key3" in updated_map2.value
        assert "key1" not in updated_map2.value
        
        # Delete non-existent key (should be no-op)
        updated_map3 = self.string_map.delete(updated_map2, "missing")
        assert len(updated_map3.value) == 1
        assert updated_map3.value == updated_map2.value
        
        # Original maps should be unchanged (immutability)
        assert len(self.sample_map.value) == 3
        assert "key1" in self.sample_map.value
        assert "key2" in self.sample_map.value
        assert "key3" in self.sample_map.value

    @pytest.mark.asyncio
    async def test_cty_map_delete_operation_invalid_inputs(self):
        """Test delete operation with invalid inputs."""
        # Delete with invalid key type (should not raise, just return unchanged map)
        result = self.string_map.delete(self.sample_map, 123)
        assert result.value == self.sample_map.value
        
        # Delete from null map
        null_map = CtyValue(vtype=self.string_map, is_null=True)
        with pytest.raises((TypeError, CtyMapValidationError)):
            self.string_map.delete(null_map, "key")


class TestCtyMapComparison:
    """Test map comparison operations."""
    
    @pytest.mark.asyncio
    async def test_cty_map_type_equality(self):
        """Test equality of map types."""
        # Create similar map types
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())  # Same as map1
        map3 = CtyMap(key_type=CtyString(), value_type=CtyString())  # Different value type
        
        # Test equality using equal() method
        assert map1.equal(map2)
        assert map2.equal(map1)
        assert not map1.equal(map3)
        assert not map3.equal(map1)
        
        # Test equality using == operator
        assert map1 == map2
        assert map2 == map1
        assert map1 != map3
        assert map3 != map1
        
        # Test with non-map type
        assert not map1.equal(CtyString())
        assert map1 != CtyString()

    @pytest.mark.asyncio
    async def test_cty_map_type_usable_as(self):
        """Test usable_as compatibility of map types."""
        # Create similar map types
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())  # Same as map1
        map3 = CtyMap(key_type=CtyString(), value_type=CtyString())  # Different value type
        
        # Test usable_as
        assert map1.usable_as(map2)
        assert map2.usable_as(map1)
        assert not map1.usable_as(map3)
        assert not map3.usable_as(map1)
        assert not map1.usable_as(CtyString())

    @pytest.mark.asyncio
    async def test_cty_map_instance_equality(self):
        """Test equality of map instances with values."""
        # Create map type
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        
        # Create keys and values
        key1 = CtyValue(vtype=CtyString(), value="a")
        key2 = CtyValue(vtype=CtyString(), value="b")
        val1 = CtyValue(vtype=CtyNumber(), value=1)
        val2 = CtyValue(vtype=CtyNumber(), value=2)
        
        # Create maps with same content
        map1_data = {key1: val1, key2: val2}
        map2_data = {key1: val1, key2: val2}  # Same data as map1
        map3_data = {key1: val1, CtyValue(vtype=CtyString(), value="c"): val2}  # Different content
        
        map1 = map_type.validate(map1_data)
        map2 = map_type.validate(map2_data)
        map3 = map_type.validate(map3_data)
        
        # Test equality
        assert map1 == map2
        assert map1 != map3
        assert map2 != map3

