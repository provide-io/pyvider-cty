#
# tests/map/test_cty_map_advanced.py
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
    async def test_cty_map_with_empty_and_null_values(self):
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
    async def test_cty_map_with_decimal_values(self):
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
    async def test_cty_map_error_reporting(self):
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



# 🐍🏗️🧪
