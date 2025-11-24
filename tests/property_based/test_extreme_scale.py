#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Extreme scale property-based tests for massive data structures.

Tests the system's ability to handle:
- Very large collections (10k+ items)
- Many object attributes (500+)
- Deep nesting (200+ levels)
- Huge strings (10MB+)
- Large maps (10k+ keys)"""

from hypothesis import HealthCheck, given, settings, strategies as st
import pytest

from pyvider.cty import CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack

# Extreme scale settings
EXTREME_SETTINGS = settings(
    deadline=30000,  # 30 seconds for large data
    max_examples=100,  # Fewer examples since each is expensive
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.filter_too_much],
)


@pytest.mark.slow
@EXTREME_SETTINGS
@given(size=st.integers(min_value=1_000, max_value=10_000))
def test_extreme_list_size(size: int) -> None:
    """
    Extreme scale: Lists with 1k-10k items.

    Tests that large lists can be validated and serialized.
    Note: Reduced from 100k to avoid validation timeout (30s limit).
    Under parallel execution, even 25k can timeout, so reduced to 10k max.
    """
    # Create large list
    items = list(range(size))
    list_type = CtyList(element_type=CtyNumber())

    # Validate
    cty_value = list_type.validate(items)
    assert len(cty_value.value) == size

    # Serialize
    msgpack_bytes = cty_to_msgpack(cty_value, list_type)
    assert len(msgpack_bytes) > 0

    # Deserialize
    decoded = cty_from_msgpack(msgpack_bytes, list_type)
    assert len(decoded.value) == size


@pytest.mark.slow
@EXTREME_SETTINGS
@given(size=st.integers(min_value=1_000, max_value=8_000))
def test_extreme_map_size(size: int) -> None:
    """
    Extreme scale: Maps with 1k-8k key-value pairs.

    Tests that large maps can be validated and serialized.
    Note: Reduced from 50k to avoid validation timeout during parallel execution.
    """
    # Create large map
    items = {f"key_{i}": f"value_{i}" for i in range(size)}
    map_type = CtyMap(element_type=CtyString())

    # Validate
    cty_value = map_type.validate(items)
    assert len(cty_value.value) == size

    # Serialize
    msgpack_bytes = cty_to_msgpack(cty_value, map_type)
    assert len(msgpack_bytes) > 0


@pytest.mark.slow
@EXTREME_SETTINGS
@given(num_attrs=st.integers(min_value=500, max_value=2000))
def test_extreme_object_attributes(num_attrs: int) -> None:
    """
    Extreme scale: Objects with 500-2000 attributes.

    Tests that objects with hundreds of attributes are handled.
    """
    # Create object type with many attributes
    attr_types = {f"attr_{i}": CtyString() for i in range(num_attrs)}
    obj_type = CtyObject(attribute_types=attr_types)

    # Create object value
    obj_value = {f"attr_{i}": f"val_{i}" for i in range(num_attrs)}

    # Validate
    cty_obj = obj_type.validate(obj_value)
    assert len(cty_obj.value) == num_attrs


@pytest.mark.slow
@EXTREME_SETTINGS
@given(depth=st.integers(min_value=200, max_value=400))
def test_extreme_nesting_depth(depth: int) -> None:
    """
    Extreme scale: Deeply nested structures (200-400 levels).

    Tests that very deep nesting either works or fails gracefully.
    """
    # Build deeply nested list
    data = None
    for _ in range(depth):
        data = [data]

    schema = CtyDynamic()

    try:
        # Might hit recursion limits
        cty_value = schema.validate(data)
        assert cty_value is not None
    except (RecursionError, ValueError):
        # Acceptable failure mode
        pass


@pytest.mark.slow
@EXTREME_SETTINGS
@given(length=st.integers(min_value=1_000_000, max_value=10_000_000))
def test_extreme_string_length(length: int) -> None:
    """
    Extreme scale: Strings of 1MB-10MB.

    Tests that megabyte-sized strings are handled.
    """
    # Create very long string
    text = "a" * length
    string_type = CtyString()

    # Validate
    cty_value = string_type.validate(text)
    assert len(cty_value.value) == length


@pytest.mark.slow
@EXTREME_SETTINGS
@given(
    num_lists=st.integers(min_value=20, max_value=100),
    items_per_list=st.integers(min_value=20, max_value=100),
)
def test_extreme_nested_collection_count(num_lists: int, items_per_list: int) -> None:
    """
    Extreme scale: Many nested collections.

    Tests list containing many sublists, each with many items.
    Note: Reduced from 500x1000 to avoid validation timeout during parallel execution.
    Max 100x100=10k total items to ensure reliable performance.
    """
    # Create nested structure
    data = [[i + j for j in range(items_per_list)] for i in range(num_lists)]

    inner_list = CtyList(element_type=CtyNumber())
    outer_list = CtyList(element_type=inner_list)

    # Validate
    cty_value = outer_list.validate(data)
    assert len(cty_value.value) == num_lists


@pytest.mark.slow
@EXTREME_SETTINGS
@given(width=st.integers(min_value=2, max_value=4), depth=st.integers(min_value=5, max_value=8))
def test_extreme_wide_and_deep(width: int, depth: int) -> None:
    """
    Extreme scale: Both wide (many siblings) and deep (many levels).

    Tests structures that are both wide and deep.
    CRITICAL: This creates width^depth total nodes!
    - 4^8 = 65,536 nodes (max)
    - 2^5 = 32 nodes (min)
    Previous limits caused exponential memory explosion (50^50 = astronomical!).
    """

    # Build structure with both width and depth
    def build_level(current_depth):
        if current_depth >= depth:
            return 0
        return [build_level(current_depth + 1) for _ in range(width)]

    data = build_level(0)
    schema = CtyDynamic()

    try:
        cty_value = schema.validate(data)
        assert cty_value is not None
    except (RecursionError, ValueError):
        # Acceptable for very large structures
        pass


# 🌊🪢🔚
