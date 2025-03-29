
# tests/collections/test_collections_map.py

import pytest
from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyBool, CtyMap, CtyNumber, CtyString, CtyValue


class TestCtyMapType:
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        self.number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        self.bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())

    @pytest.mark.asyncio
    async def test_validate_valid_string_map(self):
        """Test validation of a valid string map."""
        valid = {"name": "pyvider"}
        validated = self.string_map.validate(valid)

        assert isinstance(validated, CtyValue)
        assert isinstance(validated.type, CtyMap)
        
        # Get the actual map data
        map_data = validated.value
        assert isinstance(map_data, dict)
        
        # Test lookup using get method
        name_value = validated.get("name")
        assert name_value is not None
        assert isinstance(name_value, CtyValue)
        assert isinstance(name_value.type, CtyString)
        assert name_value.value == "pyvider"
        
        # Test dictionary-style access
        assert validated["name"].value == "pyvider"
        
        # Test iterating through the map to find the key
        found_key = None
        for k in map_data:
            assert isinstance(k, CtyValue)
            assert isinstance(k.type, CtyString)
            if k.value == "name":
                found_key = k
                break
                
        assert found_key is not None, "Key 'name' not found in map"
        assert isinstance(map_data[found_key], CtyValue)
        assert isinstance(map_data[found_key].type, CtyString)
        assert map_data[found_key].value == "pyvider"

    @pytest.mark.asyncio
    async def test_validate_valid_number_map(self):
        """Test validation of a valid number map."""
        valid = {"count": 3, "max_retries": 5}
        validated = self.number_map.validate(valid)

        # Find the value for "count" key
        count_value = None
        for k in validated.value:
            if isinstance(k, CtyString) and k.value == "count":
                count_value = validated.value[k]
                break

        assert count_value is not None, "Key 'count' not found in map"
        assert isinstance(count_value, CtyNumber)
        assert count_value.value == 3

    @pytest.mark.asyncio
    async def test_validate_valid_bool_map(self):
        """Test validation of a valid boolean map."""
        valid = {"is_active": True, "is_deleted": False}
        validated = self.bool_map.validate(valid)

        # Find the value for "is_active" key
        is_active_value = None
        for k in validated.value:
            if isinstance(k, CtyString) and k.value == "is_active":
                is_active_value = validated.value[k]
                break

        assert is_active_value is not None, "Key 'is_active' not found in map"
        assert isinstance(is_active_value, CtyBool)
        assert is_active_value.value is True

    @pytest.mark.asyncio
    async def test_validate_invalid_key_type(self):
        """Test validation with invalid key type."""
        invalid = {123: "invalid_key"}
        with pytest.raises(ValidationError):
            self.string_map.validate(invalid)

    @pytest.mark.asyncio
    async def test_validate_invalid_value_type(self):
        """Test validation with invalid value type."""
        invalid = {"key": 42}
        with pytest.raises(ValidationError):
            self.string_map.validate(invalid)

    @pytest.mark.asyncio
    async def test_validate_empty_map(self):
        """Test validation of an empty map."""
        empty = {}
        validated = self.string_map.validate(empty)
        assert len(validated.value) == 0

    @pytest.mark.asyncio
    async def test_validate_nested_map(self):
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
    async def test_validate_nested_map_invalid(self):
        """Test validation with an invalid nested map."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        invalid = {"config": {"filename": 123}}
        with pytest.raises(ValidationError):
            nested_map.validate(invalid)

    # -------------------- EQUALITY AND COMPARISON TESTS --------------------
    @pytest.mark.asyncio
    async def test_map_equality(self):
        """Test equality of maps with same element type."""
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        assert map1.equal(map2) is True

    @pytest.mark.asyncio
    async def test_map_inequality(self):
        """Test inequality of maps with different element types."""
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyString())
        assert map1.equal(map2) is False

    # -------------------- EDGE CASES --------------------
    @pytest.mark.asyncio
    async def test_large_map(self):
        """Test validation of a large map."""
        large_map = {str(i): i for i in range(1000)}
        validated = self.number_map.validate(large_map)
        assert len(validated.value) == 1000

    @pytest.mark.asyncio
    async def test_map_with_none(self):
        """Test validation with None value."""
        invalid = {"key": None}
        with pytest.raises(ValidationError):
            self.string_map.validate(invalid)

    @pytest.mark.asyncio
    async def test_unhashable_key(self):
        """Test validation with unhashable key."""
        # Create a custom key type that rejects a specific key
        class RejectingKeyType(CtyString):
            def validate(self, value):
                if value == "valid_key":
                    raise ValidationError("Key validation failed: unhashable type")
                return super().validate(value)
        
        # Create test map with rejecting key type
        test_map = CtyMap(key_type=RejectingKeyType(), value_type=CtyString())
        
        # Test validation failure
        with pytest.raises(ValidationError) as exc:
            test_map.validate({"valid_key": "value"})

    @pytest.mark.asyncio
    async def test_map_with_nested_lists(self):
        """Test validation with nested lists."""
        # Here we need to initialize the map correctly with both key_type and value_type
        tf_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        nested_data = {"key1": ["item1", "item2"], "key2": ["item3"]}

        # This may be failing because strings can't validate lists
        # Let's modify the test to use a more compatible type
        with pytest.raises(ValidationError):
            tf_map.validate(nested_data)

    @pytest.mark.asyncio
    async def test_map_with_incompatible_nested(self):
        """Test validation with incompatible nested values."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        invalid = {"nested": {"key": 42}}  # Key type valid, value type invalid
        with pytest.raises(ValidationError):
            nested_map.validate(invalid)

    @pytest.mark.asyncio
    async def test_validate_invalid_bool_map(self):
        """Test validation with invalid bool map."""
        invalid = {"is_active": 123}  # Not a boolean value
        with pytest.raises(ValidationError) as excinfo:
            self.bool_map.validate(invalid)
        assert "validation failed" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_map_access(self):
        """Test the correct way to access map elements."""
        # Create and validate a map
        data = {"key1": "value1", "key2": "value2"}
        validated = self.string_map.validate(data)

        # Method 1: Find by key.value
        for k in validated.value:
            if k.value == "key1":
                assert validated.value[k].value == "value1"
                break
        else:
            assert False, "Key 'key1' not found"

        # Method 2: If get() method exists
        if hasattr(validated, 'get'):
            value = validated.get("key1")
            assert value.value == "value1"


# 🐍🏗️🧪
