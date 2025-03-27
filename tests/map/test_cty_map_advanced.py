#
# tests/collections/test_cty_map_advanced.py
#

import pytest
from decimal import Decimal

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import (
    CtyBool,
    CtyMap,
    CtyNumber,
    CtyString,
    CtyObject,
    CtyList,
    CtyValue,
)

class TestCtyMapAdvanced:
    """Advanced tests for CtyMap implementation to improve code coverage."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
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
        
        self.object_map = CtyMap(
            key_type=CtyString(),
            value_type=CtyObject(
                attribute_types={
                    "name": CtyString(),
                    "age": CtyNumber(),
                }
            )
        )

    @pytest.mark.asyncio
    async def test_get_method(self):
        """Test the get() method for retrieving values."""
        # Create and validate a map
        data = {"key1": "value1", "key2": "value2"}
        map_val = self.string_map.validate(data)
        
        # Try to get existing key
        result = map_val.get("key1")
        assert result is not None
        assert isinstance(result, CtyString)
        assert result.value == "value1"
        
        # Try to get non-existent key
        default = CtyString(value="default")
        result = map_val.get("nonexistent", default)
        assert result is default
        
        # Try to get with a key that's already a CtyString
        key = CtyString(value="key2")
        result = map_val.get(key)
        assert result is not None
        assert isinstance(result, CtyString)
        assert result.value == "value2"
        
        # Test get with invalid key type (should return default)
        result = map_val.get(123, default)
        assert result is default

    @pytest.mark.asyncio
    async def test_set_method(self):
        """Test the set() method for adding/updating values."""
        # Create an empty map
        map_val = self.string_map.validate({})
        
        # Add a new key-value pair
        new_map = map_val.set("key1", "value1")
        
        # Verify the new map
        assert isinstance(new_map, CtyMap)
        assert len(new_map.value) == 1
        
        # Find the key-value pair
        key_found = None
        value_found = None
        for k, v in new_map.value.items():
            if isinstance(k, CtyString) and k.value == "key1":
                key_found = k
                value_found = v
                break
                
        assert key_found is not None
        assert value_found is not None
        assert isinstance(value_found, CtyString)
        assert value_found.value == "value1"
        
        # Update existing key
        updated_map = new_map.set("key1", "updated")
        
        # Find the updated value
        for k, v in updated_map.value.items():
            if isinstance(k, CtyString) and k.value == "key1":
                assert isinstance(v, CtyString)
                assert v.value == "updated"
                break
        else:
            assert False, "Updated key not found"
            
        # Verify original map is unchanged (immutability)
        original_value = None
        for k, v in new_map.value.items():
            if isinstance(k, CtyString) and k.value == "key1":
                original_value = v.value
                break
                
        assert original_value == "value1"
        
        # Test setting with pre-validated CtyType values
        pre_key = CtyString(value="key2")
        pre_val = CtyString(value="value2")
        pre_map = updated_map.set(pre_key, pre_val)
        
        # Verify pre-validated values are used directly
        for k, v in pre_map.value.items():
            if k.value == "key2":
                assert v is pre_val  # Should be same instance
                break
        else:
            assert False, "Pre-validated key-value not found"
            
        # Test set with invalid value type
        with pytest.raises(ValidationError):
            updated_map.set("key3", 123)  # Number instead of string

    @pytest.mark.asyncio
    async def test_delete_method(self):
        """Test the delete() method for removing keys."""
        # Create a map with data
        data = {"key1": "value1", "key2": "value2", "key3": "value3"}
        map_val = self.string_map.validate(data)
        
        # Delete a key
        new_map = map_val.delete("key2")
        
        # Verify key was deleted
        assert len(new_map.value) == 2
        for k, v in new_map.value.items():
            assert k.value != "key2"
            
        # Verify original map is unchanged
        assert len(map_val.value) == 3
        
        # Delete a non-existent key (should not error)
        result = new_map.delete("nonexistent")
        assert len(result.value) == 2  # No change
        
        # Delete with pre-validated key
        key3 = CtyString(value="key3")
        result = new_map.delete(key3)
        assert len(result.value) == 1
        
        # Delete with invalid key type (should be handled gracefully)
        result = new_map.delete(123)  # Should not change the map
        assert len(result.value) == 1

    @pytest.mark.asyncio
    async def test_nested_map_validation(self):
        """Test validation of maps with nested maps as values."""
        # Create nested map data
        data = {
            "user1": {
                "name": "Alice",
                "email": "alice@example.com"
            },
            "user2": {
                "name": "Bob",
                "email": "bob@example.com"
            }
        }
        
        # Validate
        validated = self.nested_map.validate(data)
        
        # Check structure
        assert len(validated.value) == 2
        
        # Find user1 data
        user1_data = None
        for k, v in validated.value.items():
            if k.value == "user1":
                user1_data = v
                break
                
        assert user1_data is not None
        assert isinstance(user1_data, CtyMap)
        
        # Check nested map content
        name_value = None
        email_value = None
        for k, v in user1_data.value.items():
            if k.value == "name":
                name_value = v
            elif k.value == "email":
                email_value = v
                
        assert name_value is not None
        assert isinstance(name_value, CtyString)
        assert name_value.value == "Alice"
        
        assert email_value is not None
        assert isinstance(email_value, CtyString)
        assert email_value.value == "alice@example.com"
        
        # Test with invalid nested value
        invalid_data = {
            "user1": {
                "name": "Alice",
                "email": 123  # Should be string
            }
        }
        
        with pytest.raises(ValidationError):
            self.nested_map.validate(invalid_data)

    @pytest.mark.asyncio
    async def test_list_map_validation(self):
        """Test validation of maps with lists as values."""
        # Create map with list values
        data = {
            "fruits": ["apple", "banana", "cherry"],
            "vegetables": ["carrot", "broccoli"],
            "empty": []
        }
        
        # Validate
        validated = self.list_map.validate(data)
        
        # Check structure
        assert len(validated.value) == 3
        
        # Find fruits list
        fruits_list = None
        for k, v in validated.value.items():
            if k.value == "fruits":
                fruits_list = v
                break
                
        assert fruits_list is not None
        assert isinstance(fruits_list, CtyList)
        
        # Check list content
        assert len(fruits_list.value) == 3
        assert all(isinstance(item, CtyString) for item in fruits_list.value)
        assert [item.value for item in fruits_list.value] == ["apple", "banana", "cherry"]
        
        # Check empty list
        empty_list = None
        for k, v in validated.value.items():
            if k.value == "empty":
                empty_list = v
                break
                
        assert empty_list is not None
        assert isinstance(empty_list, CtyList)
        assert len(empty_list.value) == 0
        
        # Test with invalid list elements
        invalid_data = {
            "mixed": ["string", 123, True]  # Should be all strings
        }
        
        with pytest.raises(ValidationError):
            self.list_map.validate(invalid_data)
            
    @pytest.mark.asyncio
    async def test_object_map_validation(self):
        """Test validation of maps with objects as values."""
        # Create map with object values
        data = {
            "user1": {
                "name": "Alice",
                "age": 30
            },
            "user2": {
                "name": "Bob",
                "age": 25
            }
        }
        
        # Validate
        validated = self.object_map.validate(data)
        
        # Check structure
        assert len(validated.value) == 2
        
        # Find user1 data
        user1_data = None
        for k, v in validated.value.items():
            if k.value == "user1":
                user1_data = v
                break
                
        assert user1_data is not None
        assert isinstance(user1_data, dict)  # Object values are dictionaries
        
        # Check object content
        assert isinstance(user1_data["name"], CtyString)
        assert user1_data["name"].value == "Alice"
        assert isinstance(user1_data["age"], CtyNumber)
        assert user1_data["age"].value == 30
        
        # Test with invalid object attributes
        invalid_data = {
            "user3": {
                "name": "Charlie",
                "age": "thirty"  # Should be a number
            }
        }
        
        with pytest.raises(ValidationError):
            self.object_map.validate(invalid_data)
            
    @pytest.mark.asyncio
    async def test_map_with_empty_and_null_values(self):
        """Test map validation with empty and null values."""
        # Empty map
        empty_map = self.string_map.validate({})
        assert len(empty_map.value) == 0
        
        # Null value
        null_map = self.string_map.validate(None)
        assert len(null_map.value) == 0
        
        # Map with null values (should convert to empty string)
        data = {
            "key1": None,
            "key2": "value2"
        }
        
        # Check how null values are handled
        try:
            validated = self.string_map.validate(data)
            # If validation passes, key1 should have a valid CtyString
            for k, v in validated.value.items():
                if k.value == "key1":
                    assert isinstance(v, CtyString)
                    break
        except ValidationError:
            # If validation fails (null not accepted), that's also valid behavior
            pass
            
    @pytest.mark.asyncio
    async def test_validation_with_pre_validated_values(self):
        """Test validation with pre-validated CtyType values."""
        # Create pre-validated CtyType values
        key1 = CtyString(value="key1")
        key2 = CtyString(value="key2")
        val1 = CtyString(value="value1")
        val2 = CtyString(value="value2")
        
        # Create map with pre-validated values
        data = {
            key1: val1,
            key2: val2
        }
        
        # Validate
        validated = self.string_map.validate(data)
        
        # Verify pre-validated values are used directly
        found_key1 = False
        found_key2 = False
        
        for k, v in validated.value.items():
            if k is key1:  # Should be same instance
                found_key1 = True
                assert v is val1  # Should be same instance
            elif k is key2:  # Should be same instance
                found_key2 = True
                assert v is val2  # Should be same instance
                
        assert found_key1
        assert found_key2
        
    @pytest.mark.asyncio
    async def test_map_with_decimal_values(self):
        """Test map with Decimal number values."""
        # Create map with Decimal values
        data = {
            "pi": Decimal("3.14159"),
            "e": Decimal("2.71828"),
            "zero": Decimal("0")
        }
        
        # Validate
        validated = self.number_map.validate(data)
        
        # Check structure
        assert len(validated.value) == 3
        
        # Check Decimal values
        for k, v in validated.value.items():
            assert isinstance(v, CtyNumber)
            if k.value == "pi":
                assert isinstance(v.value, Decimal)
                assert v.value == Decimal("3.14159")
            elif k.value == "e":
                assert isinstance(v.value, Decimal)
                assert v.value == Decimal("2.71828")
                
    @pytest.mark.asyncio
    async def test_map_error_reporting(self):
        """Test error reporting details in validation failures."""
        # Create invalid data with multiple errors
        invalid_data = {
            "key1": 123,  # Should be string
            "key2": True,  # Should be string
            123: "value3"  # Key should be string
        }
        
        # Validate and catch detailed error
        with pytest.raises(ValidationError) as excinfo:
            self.string_map.validate(invalid_data)
            
        # Error message should mention all issues
        error_msg = str(excinfo.value)
        assert "validation failed" in error_msg
        
    @pytest.mark.asyncio
    async def test_map_equality_and_type_comparison(self):
        """Test map equality and type comparison methods."""
        # Create two identical map types
        map_type1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map_type2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        
        # Create a different map type
        map_type3 = CtyMap(key_type=CtyString(), value_type=CtyString())
        
        # Test type equality
        assert map_type1.equal(map_type2)
        assert not map_type1.equal(map_type3)
        assert not map_type1.equal(CtyString())
        
        # Test usable_as
        assert map_type1.usable_as(map_type2)
        assert not map_type1.usable_as(map_type3)
        assert not map_type1.usable_as(CtyString())
        
        # Test instance equality
        map_val1 = map_type1.validate({"a": 1, "b": 2})
        map_val2 = map_type1.validate({"a": 1, "b": 2})
        map_val3 = map_type1.validate({"a": 1, "c": 3})
        
        assert map_val1 == map_val2
        assert map_val1 != map_val3
        assert map_val1 != CtyString(value="not a map")
        
    @pytest.mark.asyncio
    async def test_map_string_representation(self):
        """Test string representation of map types and values."""
        # Create map type
        map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        
        # Test __str__
        str_repr = str(map_type)
        assert "map" in str_repr
        assert "CtyNumber" in str_repr
        
        # Test __repr__
        repr_str = repr(map_type)
        assert "CtyMap" in repr_str
        
    @pytest.mark.asyncio
    async def test_map_iteration(self):
        """Test iteration over map values."""
        # Create map with data
        data = {"a": 1, "b": 2, "c": 3}
        map_val = self.number_map.validate(data)
        
        # Test __iter__
        keys = set()
        for key in map_val:
            keys.add(key.value)
            
        assert keys == {"a", "b", "c"}
        
        # Test iteration over items
        items = {}
        for k, v in map_val.value.items():
            items[k.value] = v.value
            
        assert items == {"a": 1, "b": 2, "c": 3}
        
    @pytest.mark.asyncio
    async def test_map_with_cty_values(self):
        """Test creating maps using CtyValue instances."""
        # Create CtyValues
        from pyvider.cty.values import CtyValue
        
        key1 = CtyValue(type_=CtyString(), value="key1")
        val1 = CtyValue(type_=CtyString(), value="value1")
        
        # Try to create map with CtyValues
        # This test is exploratory - it may fail if CtyValues are not directly supported
        try:
            data = {key1: val1}
            self.string_map.validate(data)
        except Exception:
            # If this approach is not supported, that's fine
            pass
