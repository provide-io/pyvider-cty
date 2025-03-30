#
# tests/map/test_cty_map_iteration.py
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


@pytest.mark.asyncio
async def test_cty_map_iteration():
    """Test iteration over map keys."""
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())

    # Create a map with data
    data = {"one": 1, "two": 2, "three": 3}
    map_val = map_type.validate(data)

    # Test __iter__
    keys = set()
    for key in map_val:
        assert isinstance(key, CtyString)
        keys.add(key.value)

    assert keys == {"one", "two", "three"}
