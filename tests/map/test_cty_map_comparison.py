#
# tests/map/test_cty_map_comparison.py
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

class TestCtyMapComparison:
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
    async def test_cty_map_equality_and_type_comparison_1(self):
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

        # Fix: use is_known instead of _is_known for any CtyValue property access
        assert map_val1 == map_val2
        assert map_val1 != map_val3
        assert map_val1 != CtyString(value="not a map")

    @pytest.mark.asyncio
    async def test_cty_map_inequality(self):
        """Test inequality of maps with different element types."""
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyString())
        assert map1.equal(map2) is False

    @pytest.mark.asyncio
    async def test_cty_map_string_representation(self):
        """Test string representation of map types."""
        # Create map types
        string_map = CtyMap(key_type=CtyString(), value_type=CtyString())
        number_map = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        bool_map = CtyMap(key_type=CtyString(), value_type=CtyBool())

        # Test __str__ method
        assert "map" in str(string_map)
        assert "CtyString" in str(string_map)

        assert "map" in str(number_map)
        assert "CtyString" in str(number_map)
        assert "CtyNumber" in str(number_map)

        assert "map" in str(bool_map)
        assert "CtyBool" in str(bool_map)

        # Test __repr__ method
        assert "CtyMap" in repr(string_map)
        assert "key_type" in repr(string_map)
        assert "value_type" in repr(string_map)

    @pytest.mark.asyncio
    async def test_cty_map_equality(self):
        """Test equality of map types."""
        # Create similar map types
        map1 = CtyMap(key_type=CtyString(), value_type=CtyNumber())
        map2 = CtyMap(key_type=CtyString(), value_type=CtyNumber())  # Same types as map1
        map3 = CtyMap(key_type=CtyString(), value_type=CtyString())  # Different value type

        # Test equality
        assert map1.equal(map2)
        assert map2.equal(map1)
        assert not map1.equal(map3)
        assert not map3.equal(map1)

        # Test equality operator
        assert map1 == map2
        assert map2 == map1
        assert map1 != map3
        assert map3 != map1

        # Test with non-map type
        assert not map1.equal(CtyString())
        assert map1 != CtyString()

# 🐍🏗️🧪
