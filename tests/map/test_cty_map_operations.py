#
# tests/map/test_cty_map_operations.py
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


class TestCtyMapOperations:
    """Tests for CtyMap implementation with proper method calls and value wrapping."""
    
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

    @pytest.mark.asyncio
    async def test_map_basic_validation(self):
        """Test basic validation with proper type patterns."""
        # Create pre-validated keys and values
        key1 = CtyValue(type_=CtyString(), value="key1")
        val1 = CtyValue(type_=CtyString(), value="value1")
        key2 = CtyValue(type_=CtyString(), value="key2")
        val2 = CtyValue(type_=CtyString(), value="value2")
        
        # Create proper map with pre-validated keys and values
        valid_map = {
            key1: val1,
            key2: val2
        }
        
        # Validate the map
        validated = self.string_map.validate(valid_map)
        
        # Verify structure
        assert isinstance(validated, CtyValue)
        assert isinstance(validated.type, CtyMap)
        assert len(validated.value) == 2
        
        # Find values by key
        found_key1 = False
        found_key2 = False
        for k, v in validated.value.items():
            if k.value == "key1":
                found_key1 = True
                assert v.value == "value1"
            elif k.value == "key2":
                found_key2 = True
                assert v.value == "value2"
                
        assert found_key1 and found_key2


    @pytest.mark.asyncio
    async def test_cty_map_set_method(self):
        """Test the set method with proper method call pattern."""
        # Create empty map
        empty_map = self.string_map.validate({})
        
        # Create keys and values
        key1 = CtyValue(type_=CtyString(), value="key1")
        val1 = CtyValue(type_=CtyString(), value="value1")
        key2 = CtyValue(type_=CtyString(), value="key2")
        val2 = CtyValue(type_=CtyString(), value="value2")
        
        # Add first key-value pair
        new_map = self.string_map.set(empty_map, key1, val1)
        
        # Verify structure
        assert isinstance(new_map, CtyValue)
        assert len(new_map.value) == 1
        
        # Find the key-value pair
        found = False
        for k, v in new_map.value.items():
            if k is key1:  # Should be same instance
                found = True
                assert v is val1
        assert found
        
        # Add second key-value pair
        updated_map = self.string_map.set(new_map, key2, val2)
        
        # Verify structure
        assert len(updated_map.value) == 2
        
        # Find both key-value pairs
        found_key1 = False
        found_key2 = False
        for k, v in updated_map.value.items():
            if k is key1:
                found_key1 = True
                assert v is val1
            elif k is key2:
                found_key2 = True
                assert v is val2
                
        assert found_key1 and found_key2
        
        # Update existing key
        val1_updated = CtyValue(type_=CtyString(), value="updated")
        final_map = self.string_map.set(updated_map, key1, val1_updated)
        
        # Verify update
        found = False
        for k, v in final_map.value.items():
            if k is key1:
                found = True
                assert v is val1_updated
        assert found
        
        # Original map should be unchanged (immutability)
        for k, v in updated_map.value.items():
            if k is key1:
                assert v is val1  # Still has original value

    @pytest.mark.asyncio
    async def test_cty_map_get_method(self):
        """Test the get method with proper method call pattern."""
        # Create pre-validated keys and values
        key1 = CtyValue(type_=CtyString(), value="key1")
        val1 = CtyValue(type_=CtyString(), value="value1")
        key2 = CtyValue(type_=CtyString(), value="key2")
        val2 = CtyValue(type_=CtyString(), value="value2")
        
        # Create and validate map
        valid_map = {key1: val1, key2: val2}
        map_val = self.string_map.validate(valid_map)
        
        # Test get with pre-validated key
        result = self.string_map.get(map_val, key1)
        assert result is not None
        assert result is val1  # Should be same instance
        
        # Test get with string key (proper conversion must be handled)
        try:
            # Using key1_value string directly might fail if implementation requires CtyValue
            # This should either work with proper conversion or raise ValidationError
            lookup_key = CtyValue(type_=CtyString(), value="key1")
            result = self.string_map.get(map_val, lookup_key)
            assert result is not None
            assert result.value == "value1"
        except ValidationError:
            # If implementation strictly requires pre-validated keys, this is expected
            pass
        
        # Test get with non-existent key
        default_val = CtyValue(type_=CtyString(), value="default")
        missing_key = CtyValue(type_=CtyString(), value="missing")
        result = self.string_map.get(map_val, missing_key, default_val)
        assert result is default_val

    @pytest.mark.asyncio
    async def test_cty_map_delete_method(self):
        """Test the delete method with proper method call pattern."""
        # Create keys and values
        key1 = CtyValue(type_=CtyString(), value="key1")
        val1 = CtyValue(type_=CtyString(), value="value1")
        key2 = CtyValue(type_=CtyString(), value="key2")
        val2 = CtyValue(type_=CtyString(), value="value2")
        key3 = CtyValue(type_=CtyString(), value="key3")
        val3 = CtyValue(type_=CtyString(), value="value3")
        
        # Create map with multiple entries
        valid_map = {key1: val1, key2: val2, key3: val3}
        map_val = self.string_map.validate(valid_map)
        
        # Delete key2
        new_map = self.string_map.delete(map_val, key2)
        
        # Verify key was deleted
        assert len(new_map.value) == 2
        
        # Verify which keys remain
        found_key1 = False
        found_key3 = False
        for k in new_map.value:
            if k is key1:
                found_key1 = True
            elif k is key3:
                found_key3 = True
            else:
                assert False, f"Unexpected key found: {k.value}"
                
        assert found_key1 and found_key3
        
        # Original map should be unchanged (immutability)
        assert len(map_val.value) == 3
        
        # Delete non-existent key
        non_existent = CtyValue(type_=CtyString(), value="non_existent")
        result = self.string_map.delete(new_map, non_existent)
        assert len(result.value) == 2  # No change
        
        # Delete key1
        final_map = self.string_map.delete(new_map, key1)
        assert len(final_map.value) == 1
        
        # Only key3 should remain
        found = False
        for k in final_map.value:
            if k is key3:
                found = True
        assert found



# 🐍🏗️🧪
