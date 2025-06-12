#
# tests/map/test_cty_map_fixed.py
#

import pytest
from decimal import Decimal

from pyvider.cty.exceptions import CtyMapValidationError
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

        # Add the missing list_map attribute
        self.list_map = CtyMap(
            key_type=CtyString(),
            value_type=CtyList(element_type=CtyString())
        )


    @pytest.mark.asyncio
    async def test_cty_map_with_invalid_inputs(self):
        """Test validation with invalid inputs."""
        # Test with non-dict input
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate([1, 2, 3])  # List, not dict

        # Test with invalid key type
        invalid_key = CtyValue(vtype=CtyNumber(), value=123)  # Should be string
        valid_val = CtyValue(vtype=CtyString(), value="value")
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({invalid_key: valid_val})

        # Test with invalid value type
        valid_key = CtyValue(vtype=CtyString(), value="key")
        invalid_val = CtyValue(vtype=CtyNumber(), value=123)  # Should be string
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({valid_key: invalid_val})

        # Test with null/unknown values
        null_key = CtyValue(vtype=CtyString(), is_null=True)
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({null_key: valid_val})

        unknown_key = CtyValue(vtype=CtyString(), is_unknown=True)
        with pytest.raises(CtyMapValidationError):
            self.string_map.validate({unknown_key: valid_val})


    @pytest.mark.asyncio
    async def test_nested_map(self):
        """Test nested map with proper value wrapping."""
        # Create inner map keys and values
        inner_key1 = CtyValue(vtype=CtyString(), value="name")
        inner_val1 = CtyValue(vtype=CtyString(), value="Alice")
        inner_key2 = CtyValue(vtype=CtyString(), value="email")
        inner_val2 = CtyValue(vtype=CtyString(), value="alice@example.com")

        # Create inner map
        inner_map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
        inner_map_raw = {inner_key1: inner_val1, inner_key2: inner_val2}
        inner_map = inner_map_type.validate(inner_map_raw)

        # Create outer map key and value
        outer_key = CtyValue(vtype=CtyString(), value="user1")

        # Create outer map
        outer_map_raw = {outer_key: inner_map}
        outer_map = self.nested_map.validate(outer_map_raw)

        # Verify structure
        assert len(outer_map.value) == 1

        # Find the nested value - adjusted for string keys
        found = False
        # Get internal key_mapping to access original CtyValue keys
        outer_keys = outer_map._key_mapping.values() if hasattr(outer_map, '_key_mapping') else []

        # Check if we have our outer_key in the mapping
        for k in outer_keys:
            if k.value == "user1":
                found = True

        # Alternative check directly with string keys
        if "user1" in outer_map.value:
            found = True
            v = outer_map.value["user1"]
            assert isinstance(v, CtyValue)
            assert isinstance(v.type, CtyMap)

            # Check inner map values - adjusted for string keys
            inner_found_name = False
            inner_found_email = False

            # Use get method to retrieve inner values
            inner_name = inner_map_type.get(v, "name")
            inner_email = inner_map_type.get(v, "email")

            assert inner_name is not None
            assert inner_email is not None
            assert inner_name.value == "Alice"
            assert inner_email.value == "alice@example.com"
            inner_found_name = inner_found_email = True

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

        # Find user1 data - adjusted for string keys
        user1_data = None

        # Direct string key lookup
        if "user1" in validated.value:
            user1_data = validated.value["user1"]

        assert user1_data is not None
        assert isinstance(user1_data, CtyValue)
        assert isinstance(user1_data.type, CtyMap)

        # Check nested map content - adjusted for string keys
        name_value = None
        email_value = None

        # Use string keys for nested map lookup
        if "name" in user1_data.value:
            name_value = user1_data.value["name"]
        if "email" in user1_data.value:
            email_value = user1_data.value["email"]

        assert name_value is not None
        assert isinstance(name_value, CtyValue)
        assert name_value.value == "Alice"

        assert email_value is not None
        assert isinstance(email_value, CtyValue)
        assert email_value.value == "alice@example.com"

        # Test with invalid nested value
        invalid_data = {
            "user1": {
                "name": "Alice",
                "email": 123  # Should be string
            }
        }

        with pytest.raises(CtyMapValidationError):
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

        # Find fruits list - adjusted for string keys
        fruits_list = None

        # Direct string key lookup
        if "fruits" in validated.value:
            fruits_list = validated.value["fruits"]

        assert fruits_list is not None
        assert isinstance(fruits_list, CtyValue)
        assert isinstance(fruits_list.type, CtyList)

        # Check list content
        assert len(fruits_list.value) == 3
        assert all(isinstance(item, CtyValue) for item in fruits_list.value)
        assert all(isinstance(item.type, CtyString) for item in fruits_list.value)
        assert [item.value for item in fruits_list.value] == ["apple", "banana", "cherry"]

        # Check empty list
        empty_list = None

        # Direct string key lookup
        if "empty" in validated.value:
            empty_list = validated.value["empty"]

        assert empty_list is not None
        assert isinstance(empty_list, CtyValue)
        assert isinstance(empty_list.type, CtyList)
        assert len(empty_list.value) == 0

        # Test with invalid list elements
        invalid_data = {
            "mixed": ["string", 123, True]  # Should be all strings
        }

        with pytest.raises(CtyMapValidationError):
            self.list_map.validate(invalid_data)

    @pytest.mark.asyncio
    async def test_cty_map_validate_nested_map(self):
        """Test validation with a nested map."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        valid = {"config": {"filename": "test.txt"}}
        validated = nested_map.validate(valid)

        # Find the value for "config" key
        config_value = None
        # Iterate through the keys (strings) of the internal dictionary
        for k in validated.value:
            # --- FIX: Check the string key directly ---
            if k == "config":
                # Access the value using the string key k
                config_value = validated.value[k]
                break # Found it, exit loop

        # Now, config_value should be the CtyValue representing the nested map
        assert isinstance(validated, CtyValue)
        # --- Check the TYPE of the retrieved CtyValue ---
        assert isinstance(config_value, CtyValue), "Config value should be a CtyValue"
        assert isinstance(config_value.type, CtyMap), "Config value's type should be CtyMap" # Check the type *within* the CtyValue

        # You can add further checks on the nested map's content if needed:
        assert config_value is not None, "Key 'config' not found in map"

        # Find "filename" in the nested map's internal dictionary
        nested_map_data = config_value.value # Get the inner dict {'filename': CtyValue(...)}
        assert isinstance(nested_map_data, dict)
        filename_value = None
        for nested_k in nested_map_data:
            # nested_k is the string 'filename'
            if nested_k == "filename":
                filename_value = nested_map_data[nested_k] # This is the CtyValue for the filename
                break

        assert filename_value is not None, "Key 'filename' not found in nested map"
        assert isinstance(filename_value, CtyValue)
        assert isinstance(filename_value.type, CtyString) # Check the type
        assert filename_value.value == "test.txt" # Check the actual string value

    @pytest.mark.asyncio
    async def test_cty_map_validate_nested_map_invalid(self):
        """Test validation with an invalid nested map."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        invalid = {"config": {"filename": 123}}
        with pytest.raises(CtyMapValidationError):
            nested_map.validate(invalid)


    @pytest.mark.asyncio
    async def test_cty_map_with_complex_nested_value_types(self):
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
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyMap)
        assert len(result.value) == 2

        # Check values - adapted for string key access pattern
        found_person1 = False
        found_person2 = False

        # Direct string key lookup to access map elements
        assert "person1" in result.value
        assert "person2" in result.value

        # Get the person objects directly by string keys
        person1_val = result.value["person1"]
        person2_val = result.value["person2"]

        # Verify the person objects have the right type
        assert isinstance(person1_val, CtyValue)
        assert isinstance(person1_val.type, CtyObject)
        assert isinstance(person2_val, CtyValue)
        assert isinstance(person2_val.type, CtyObject)

        # Access person1 attributes by key
        assert "name" in person1_val.value
        assert "age" in person1_val.value

        # Verify attribute values directly
        assert person1_val.value["name"].value == "Alice"
        assert person1_val.value["age"].value == 30

        # Access person2 attributes by key
        assert "name" in person2_val.value
        assert "age" in person2_val.value

        # Verify attribute values directly
        assert person2_val.value["name"].value == "Bob"
        assert person2_val.value["age"].value == 25

        # Alternative approach using CtyPath
        from pyvider.cty.path import CtyPath

        # Test path to person1's name
        person1_name_path = CtyPath.key("person1").child("name")
        name_result = person1_name_path.apply_path(result)
        assert isinstance(name_result, CtyValue)
        assert isinstance(name_result.type, CtyString)
        assert name_result.value == "Alice"

# 🐍🏗️🧪
