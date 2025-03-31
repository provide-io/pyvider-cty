#
# tests/map/test_cty_map.py
#

"""
Comprehensive test suite for CtyMap implementation.

Tests focus exclusively on CtyMap functionality without exposing or testing
CtyValue internals directly. All tests validate CtyMap operations and behavior
rather than the wrapping/unwrapping details.
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
    CtySet,
    CtyString,
    CtyTuple,
)


class TestCtyMapCreation:
    """Test CtyMap type creation and basic functionality."""

    @pytest.mark.asyncio
    async def test_map_type_initialization(self):
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
    async def test_map_type_with_complex_values(self):
        """Test map creation with complex value types."""
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
    async def test_map_type_with_invalid_types(self):
        """Test initialization with invalid key or value types."""
        # Invalid key_type (not a CtyType)
        with pytest.raises(CtyMapValidationError) as exc_info:
            CtyMap(key_type="string", value_type=CtyString())
        assert "Expected CtyType" in str(exc_info.value)

        # Invalid value_type (not a CtyType)
        with pytest.raises(CtyMapValidationError) as exc_info:
            CtyMap(key_type=CtyString(), value_type="string")
        assert "Expected CtyType" in str(exc_info.value)

        # Both invalid
        with pytest.raises(CtyMapValidationError):
            CtyMap(key_type=None, value_type=123)

    @pytest.mark.asyncio
    async def test_map_string_representation(self):
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
        """Set up common map types for tests."""
        self.string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        self.number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        self.bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())
        
        # Create more complex map types
        self.nested_map = CtyMap(
            key_type=CtyString(),
            value_type=CtyMap(key_type=CtyString(), value_type=CtyString())
        )
        
        self.list_map = CtyMap(
            key_type=CtyString(),
            value_type=CtyList(element_type=CtyString())
        )

    @pytest.mark.asyncio
    async def test_empty_map_validation(self):
        """Test validation of empty maps."""
        # Validate None (should create empty map)
        result = self.string_map.validate(None)
        assert len(result.value) == 0
        
        # Validate empty dict
        result = self.string_map.validate({})
        assert len(result.value) == 0

    @pytest.mark.asyncio
    async def test_simple_map_validation(self):
        """Test validation of maps with simple key-value pairs."""
        # String map
        string_data = {"key1": "value1", "key2": "value2"}
        result = self.string_map.validate(string_data)
        assert len(result.value) == 2
        
        # Number map
        number_data = {"count": 10, "total": 123.45, "decimal": Decimal("67.89")}
        result = self.number_map.validate(number_data)
        assert len(result.value) == 3
        
        # Boolean map
        bool_data = {"flag1": True, "flag2": False}
        result = self.bool_map.validate(bool_data)
        assert len(result.value) == 2

    @pytest.mark.asyncio
    async def test_map_with_invalid_inputs(self):
        """Test validation with invalid inputs."""
        # Non-dict input
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate([1, 2, 3])  # List, not dict
            
        # Invalid key type
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({123: "value"})  # Number key
            
        # Invalid value type
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({"key": 123})  # Number value

    @pytest.mark.asyncio
    async def test_nested_map_validation(self):
        """Test validation of maps with nested maps as values."""
        # Valid nested data
        nested_data = {
            "user1": {"name": "Alice", "email": "alice@example.com"},
            "user2": {"name": "Bob", "email": "bob@example.com"}
        }
        result = self.nested_map.validate(nested_data)
        assert len(result.value) == 2
        
        # Invalid nested data (wrong value type in nested map)
        invalid_data = {
            "user1": {"name": "Alice", "email": 123}  # Number where string expected
        }
        with pytest.raises(CtyMapValidationError):
            self.nested_map.validate(invalid_data)

    @pytest.mark.asyncio
    async def test_list_map_validation(self):
        """Test validation of maps with lists as values."""
        # Valid list data
        list_data = {
            "fruits": ["apple", "banana", "cherry"],
            "vegetables": ["carrot", "broccoli"],
            "empty": []
        }
        result = self.list_map.validate(list_data)
        assert len(result.value) == 3
        
        # Invalid list data (wrong element type)
        invalid_data = {"mixed": ["string", 123, True]}
        with pytest.raises(CtyMapValidationError):
            self.list_map.validate(invalid_data)


class TestCtyMapOperations:
    """Test map operations like get, set, and delete."""
    
    def setup_method(self):
        """Set up common map types for tests."""
        self.string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        self.number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        
        # Create and validate maps
        self.empty_map = self.string_map.validate({})
        self.sample_map = self.string_map.validate({
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        })

    @pytest.mark.asyncio
    async def test_map_get_operation(self):
        """Test getting values from a map."""
        # Get existing key
        result = self.string_map.get(self.sample_map, "key1")
        assert result is not None
        assert result.value == "value1"
        
        # Get non-existent key with default
        default_val = self.string_map.validate({"default": "default"}).value["default"]
        result = self.string_map.get(self.sample_map, "missing", default_val)
        assert result is default_val
        
        # Get non-existent key without default
        result = self.string_map.get(self.sample_map, "missing")
        assert result is None

    @pytest.mark.asyncio
    async def test_map_set_operation(self):
        """Test setting values in a map."""
        # Set new key
        updated_map = self.string_map.set(self.empty_map, "new_key", "new_value")
        assert len(updated_map.value) == 1
        
        result = self.string_map.get(updated_map, "new_key")
        assert result is not None
        assert result.value == "new_value"
        
        # Set existing key (should update)
        final_map = self.string_map.set(updated_map, "new_key", "updated_value")
        result = self.string_map.get(final_map, "new_key")
        assert result is not None
        assert result.value == "updated_value"
        
        # Original map should be unchanged (immutability)
        result = self.string_map.get(updated_map, "new_key")
        assert result.value == "new_value"

    @pytest.mark.asyncio
    async def test_map_delete_operation(self):
        """Test deleting keys from a map."""
        # Delete existing key
        updated_map = self.string_map.delete(self.sample_map, "key2")
        assert len(updated_map.value) == 2
        
        # Verify key2 is gone
        result = self.string_map.get(updated_map, "key2")
        assert result is None
        
        # key1 and key3 should still be there
        assert self.string_map.get(updated_map, "key1") is not None
        assert self.string_map.get(updated_map, "key3") is not None
        
        # Delete non-existent key (should be no-op)
        final_map = self.string_map.delete(updated_map, "missing")
        assert len(final_map.value) == 2
        assert final_map == updated_map
        
        # Original map should be unchanged (immutability)
        assert len(self.sample_map.value) == 3


class TestCtyMapComparison:
    """Test map comparison operations."""
    
    @pytest.mark.asyncio
    async def test_map_equality(self):
        """Test equality of map types."""
        # Create similar map types
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())  # Same types as map1
        map3 = CtyMap(key_type=CtyString(), value_type=CtyString())  # Different value type
        
        # Test equality using equal()
        assert map1.equal(map2)
        assert map2.equal(map1)
        assert not map1.equal(map3)
        assert not map3.equal(map1)
        
        # Test with non-map type
        assert not map1.equal(CtyString())
        
        # Test usable_as
        assert map1.usable_as(map2)
        assert map2.usable_as(map1)
        assert not map1.usable_as(map3)
        assert not map3.usable_as(map1)
        assert not map1.usable_as(CtyString())

    @pytest.mark.asyncio
    async def test_map_instance_equality(self):
        """Test equality of map instances with values."""
        # Create map with same type
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        
        # Create maps with same content
        map1 = map_type.validate({"a": 1, "b": 2})
        map2 = map_type.validate({"a": 1, "b": 2})
        
        # Create map with different content
        map3 = map_type.validate({"a": 1, "c": 3})
        
        # Test equality
        assert map1 == map2
        assert map1 != map3


@pytest.mark.asyncio
async def test_map_with_complex_nested_value_types():
    """Test map with complex nested value types."""
    # Create an object type for the map value
    person_type = CtyObject(
        attribute_types={
            "name": CtyString(),
            "age": CtyNumber()
        }
    )
    
    # Create a map type with the object as its value type
    map_type = CtyMap(key_type=CtyString(), value_type=person_type)
    
    # Create data
    data = {
        "person1": {
            "name": "Alice",
            "age": 30
        },
        "person2": {
            "name": "Bob",
            "age": 25
        }
    }
    
    # Validate the map
    result = map_type.validate(data)
    
    # Check basic structure
    assert len(result.value) == 2
    
    # Check we can access nested data
    p1 = map_type.get(result, "person1")
    assert p1 is not None
    
    # Verify attributes can be accessed
    from pyvider.cty.types.structural import CtyObject
    assert isinstance(p1.type, CtyObject)
    
    # Access and verify nested attributes
    from pyvider.cty.path import CtyPath
    p1_name_path = CtyPath.empty().child("person1").child("name")
    name_result = p1_name_path.apply_path(result)
    assert name_result.value == "Alice"
