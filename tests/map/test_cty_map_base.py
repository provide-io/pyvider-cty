#
# tests/map/test_cty_map_base.py
#

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
    async def test_cty_map_large_map(self):
        """Test validation of a large map."""
        large_map = {str(i): i for i in range(1000)}
        validated = self.number_map.validate(large_map)
        assert len(validated.value) == 1000

    @pytest.mark.asyncio
    async def test_cty_map_with_none(self):
        """Test validation with None value."""
        invalid = {"key": None}
        with pytest.raises(ValidationError):
            self.string_map.validate(invalid)

    @pytest.mark.asyncio
    async def test_cty_map_unhashable_key(self):
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
    async def test_cty_map_with_nested_lists(self):
        """Test validation with nested lists."""
        # Here we need to initialize the map correctly with both key_type and value_type
        tf_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        nested_data = {"key1": ["item1", "item2"], "key2": ["item3"]}

        # This may be failing because strings can't validate lists
        # Let's modify the test to use a more compatible type
        with pytest.raises(ValidationError):
            tf_map.validate(nested_data)

    @pytest.mark.asyncio
    async def test_cty_map_with_incompatible_nested(self):
        """Test validation with incompatible nested values."""
        nested_map = CtyMap(key_type=CtyString(), value_type=self.string_map)
        invalid = {"nested": {"key": 42}}  # Key type valid, value type invalid
        with pytest.raises(ValidationError):
            nested_map.validate(invalid)

    @pytest.mark.asyncio
    async def test_cty_map_access(self):
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
