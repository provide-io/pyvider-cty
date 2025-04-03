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
    async def test_cty_map_equality_and_type_comparison(self):
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


# 🐍🏗️🧪
