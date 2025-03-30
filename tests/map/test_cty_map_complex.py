#
# tests/map/test_cty_map_fixed.py
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

class TestCtyMapComplex:
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
    async def test_cty_map_with_invalid_inputs(self):
        """Test validation with invalid inputs."""
        # Test with non-dict input
        with pytest.raises(ValidationError):
            self.string_map.validate([1, 2, 3])  # List, not dict
            
        # Test with invalid key type
        invalid_key = CtyValue(type_=CtyNumber(), value=123)  # Should be string
        valid_val = CtyValue(type_=CtyString(), value="value")
        with pytest.raises(ValidationError):
            self.string_map.validate({invalid_key: valid_val})
            
        # Test with invalid value type
        valid_key = CtyValue(type_=CtyString(), value="key")
        invalid_val = CtyValue(type_=CtyNumber(), value=123)  # Should be string
        with pytest.raises(ValidationError):
            self.string_map.validate({valid_key: invalid_val})
            
        # Test with null/unknown values
        null_key = CtyValue(type_=CtyString(), is_null=True)
        with pytest.raises(ValidationError):
            self.string_map.validate({null_key: valid_val})
            
        unknown_key = CtyValue(type_=CtyString(), is_unknown=True)
        with pytest.raises(ValidationError):
            self.string_map.validate({unknown_key: valid_val})

    @pytest.mark.asyncio
    async def test_nested_map_2(self):
        """Test nested map with proper value wrapping."""
        # Create inner map keys and values
        inner_key1 = CtyValue(type_=CtyString(), value="name")
        inner_val1 = CtyValue(type_=CtyString(), value="Alice")
        inner_key2 = CtyValue(type_=CtyString(), value="email")
        inner_val2 = CtyValue(type_=CtyString(), value="alice@example.com")
        
        # Create inner map
        inner_map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        inner_map_raw = {inner_key1: inner_val1, inner_key2: inner_val2}
        inner_map = inner_map_type.validate(inner_map_raw)
        
        # Create outer map key and value
        outer_key = CtyValue(type_=CtyString(), value="user1")
        
        # Create outer map
        outer_map_raw = {outer_key: inner_map}
        outer_map = self.nested_map.validate(outer_map_raw)
        
        # Verify structure
        assert len(outer_map.value) == 1
        
        # Find the nested value
        found = False
        for k, v in outer_map.value.items():
            if k is outer_key:
                found = True
                assert isinstance(v, CtyValue)
                assert isinstance(v.type, CtyMap)
                
                # Check inner map values
                inner_found_name = False
                inner_found_email = False
                for ik, iv in v.value.items():
                    if ik is inner_key1:
                        inner_found_name = True
                        assert iv is inner_val1
                    elif ik is inner_key2:
                        inner_found_email = True
                        assert iv is inner_val2
                
                assert inner_found_name and inner_found_email
                
        assert found

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
    async def test_nested_map_1(self):
        """Test nested map with proper value wrapping."""
        # Create inner map keys and values
        inner_key1 = CtyValue(type_=CtyString(), value="name")
        inner_val1 = CtyValue(type_=CtyString(), value="Alice")
        inner_key2 = CtyValue(type_=CtyString(), value="email")
        inner_val2 = CtyValue(type_=CtyString(), value="alice@example.com")
        
        # Create inner map
        inner_map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        inner_map_raw = {inner_key1: inner_val1, inner_key2: inner_val2}
        inner_map = inner_map_type.validate(inner_map_raw)
        
        # Create outer map key and value
        outer_key = CtyValue(type_=CtyString(), value="user1")
        
        # Create outer map
        outer_map_raw = {outer_key: inner_map}
        outer_map = self.nested_map.validate(outer_map_raw)
        
        # Verify structure
        assert len(outer_map.value) == 1
        
        # Find the nested value
        found = False
        for k, v in outer_map.value.items():
            if k is outer_key:
                found = True
                assert isinstance(v, CtyValue)
                assert isinstance(v.type, CtyMap)
                
                # Check inner map values
                inner_found_name = False
                inner_found_email = False
                for ik, iv in v.value.items():
                    if ik is inner_key1:
                        inner_found_name = True
                        assert iv is inner_val1
                    elif ik is inner_key2:
                        inner_found_email = True
                        assert iv is inner_val2
                
                assert inner_found_name and inner_found_email
                
        assert found


    @pytest.mark.asyncio
    async def test_cty_map_validate_nested_map(self):
        """Test validation with a nested map."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        valid = {"config": {"filename": "test.txt"}}
        validated = nested_map.validate(valid)

        # Find the value for "config" key
        config_value = None
        for k in validated.value:
            if isinstance(k, CtyString) and k.value == "config":
                config_value = validated.value[k]
                break

        assert isinstance(validated, CtyValue)
        assert isinstance(config_value, CtyMap)

        assert config_value is not None, "Key 'config' not found in map"

        # Now find "filename" in the nested map
        filename_value = None
        for k in config_value.value:
            if isinstance(k, CtyString) and k.value == "filename":
                filename_value = config_value.value[k]
                break

        assert filename_value is not None, "Key 'filename' not found in nested map"
        assert isinstance(filename_value, CtyString)
        assert filename_value.value == "test.txt"

    @pytest.mark.asyncio
    async def test_cty_map_validate_nested_map_invalid(self):
        """Test validation with an invalid nested map."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        invalid = {"config": {"filename": 123}}
        with pytest.raises(ValidationError):
            nested_map.validate(invalid)


################################################################################

@pytest.mark.asyncio
async def test_cty_map_with_nested_value_types():
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

    # Validate
    result = map_type.validate(data)

    # Verify structure
    assert isinstance(result, CtyMap)
    assert len(result.value) == 2

    # Check values
    found_person1 = False
    found_person2 = False
    
    for k, v in result.value.items():
        assert hasattr(k, 'value'), "Key should be a CtyValue or have a value attribute"
        
        if k.value == "person1":
            found_person1 = True
            # v should be a CtyValue or have accessible attributes
            assert "name" in v
            assert "age" in v
            
            name_val = v["name"]
            age_val = v["age"]
            
            assert isinstance(name_val, CtyValue)
            assert isinstance(age_val, CtyValue)
            assert name_val.value == "Alice"
            assert age_val.value == 30
            
        elif k.value == "person2":
            found_person2 = True
            assert "name" in v
            assert "age" in v
            
            name_val = v["name"]
            age_val = v["age"]
            
            assert isinstance(name_val, CtyValue)
            assert isinstance(age_val, CtyValue)
            assert name_val.value == "Bob"
            assert age_val.value == 25
    
    # Ensure we found both test persons
    assert found_person1, "person1 not found in map"
    assert found_person2, "person2 not found in map"


# 🐍🏗️🧪
