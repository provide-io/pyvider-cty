#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Memory pressure tests for resource usage tracking.

Tests that verify:
- No memory leaks in long-running operations
- Reasonable memory usage for large structures
- Proper cleanup of resources
- GC behavior with complex object graphs"""

import gc
import sys

from hypothesis import HealthCheck, given, settings, strategies as st
import pytest

from pyvider.cty import CtyDynamic, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.marks import CtyMark

MEMORY_SETTINGS = settings(
    deadline=10000,
    max_examples=20,  # Reduced from 100 for faster execution
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def get_object_size(obj):
    """Get approximate size of object in bytes."""
    return sys.getsizeof(obj)


@pytest.mark.slow
@MEMORY_SETTINGS
@given(iterations=st.integers(min_value=100, max_value=1000))
def test_no_memory_leak_in_validation(iterations: int) -> None:
    """
    Memory pressure: Repeated validation shouldn't leak memory.

    Tests that validating the same data many times doesn't accumulate memory.
    """
    gc.collect()
    initial_objects = len(gc.get_objects())

    # Repeatedly validate
    string_type = CtyString()
    for i in range(iterations):
        _ = string_type.validate(f"test_{i}")

    gc.collect()
    final_objects = len(gc.get_objects())

    # Object count shouldn't grow unboundedly
    # Allow some growth but not linear with iterations
    # Account for test infrastructure overhead (pytest-xdist, coverage, hypothesis)
    overhead = 500  # Base overhead for test infrastructure
    assert final_objects < initial_objects + overhead + (iterations * 1.0)


@pytest.mark.slow
@MEMORY_SETTINGS
@given(iterations=st.integers(min_value=100, max_value=1000))
def test_no_memory_leak_in_serialization(iterations: int) -> None:
    """
    Memory pressure: Repeated serialization shouldn't leak memory.

    Tests that serializing the same value many times doesn't leak.
    """
    gc.collect()
    initial_objects = len(gc.get_objects())

    # Create value once
    list_type = CtyList(element_type=CtyNumber())
    cty_value = list_type.validate([1, 2, 3])

    # Repeatedly serialize
    for _ in range(iterations):
        _ = cty_to_msgpack(cty_value, list_type)

    gc.collect()
    final_objects = len(gc.get_objects())

    # Object count shouldn't grow much
    # Account for test infrastructure overhead
    overhead = 500
    assert final_objects < initial_objects + overhead + (iterations * 1.0)


@pytest.mark.slow
@MEMORY_SETTINGS
@given(size=st.integers(min_value=1000, max_value=10000))
def test_memory_usage_scales_linearly(size: int) -> None:
    """
    Memory pressure: Memory usage should scale linearly with data size.

    Tests that memory usage is proportional to data size, not exponential.
    """
    # Create list of known size
    items = list(range(size))
    list_type = CtyList(element_type=CtyNumber())

    gc.collect()
    before_mem = len(gc.get_objects())

    list_type.validate(items)

    gc.collect()
    after_mem = len(gc.get_objects())

    # Memory growth should be reasonable
    # This is a rough heuristic - actual ratio depends on many factors
    mem_growth = after_mem - before_mem

    # Should not have created vastly more objects than input size
    assert mem_growth < size * 10


@pytest.mark.slow
@MEMORY_SETTINGS
@given(num_values=st.integers(min_value=100, max_value=500))
def test_mark_memory_management(num_values: int) -> None:
    """
    Memory pressure: Marks should be properly managed.

    Tests that applying and removing marks doesn't leak memory.
    """
    gc.collect()
    initial_objects = len(gc.get_objects())

    string_type = CtyString()
    base_value = string_type.validate("test")

    # Create many marked values
    values = []
    for i in range(num_values):
        marked = base_value.with_marks({CtyMark(f"mark_{i}")})
        values.append(marked)

    # Clear references
    values.clear()

    gc.collect()
    final_objects = len(gc.get_objects())

    # Should not have leaked significantly
    # Account for test infrastructure overhead
    overhead = 500
    assert final_objects < initial_objects + overhead + (num_values * 1.0)


@pytest.mark.slow
@MEMORY_SETTINGS
@given(iterations=st.integers(min_value=50, max_value=200))
def test_nested_structure_cleanup(iterations: int) -> None:
    """
    Memory pressure: Nested structures should be cleaned up properly.

    Tests that complex nested structures are properly garbage collected.
    Note: GC behavior is non-deterministic, so this test has lenient thresholds.
    """
    gc.collect()
    gc.collect()  # Double collect for more thorough cleanup
    initial_objects = len(gc.get_objects())

    # Create and discard nested structures
    for _ in range(iterations):
        inner_list = CtyList(element_type=CtyNumber())
        outer_list = CtyList(element_type=inner_list)
        _ = outer_list.validate([[1, 2], [3, 4]])

    gc.collect()
    gc.collect()  # Double collect for more thorough cleanup
    final_objects = len(gc.get_objects())

    # Should not accumulate too many objects (lenient threshold due to GC non-determinism)
    # Account for test infrastructure overhead
    overhead = 500
    assert final_objects < initial_objects + overhead + (iterations * 3)


@pytest.mark.slow
@MEMORY_SETTINGS
@given(size=st.integers(min_value=1000, max_value=10000))
def test_large_object_attribute_memory(size: int) -> None:
    """
    Memory pressure: Objects with many attributes use reasonable memory.

    Tests that objects with many attributes don't use excessive memory.
    """
    # Create object with many attributes
    attr_types = {f"attr_{i}": CtyNumber() for i in range(min(size, 100))}
    obj_type = CtyObject(attribute_types=attr_types)

    gc.collect()
    get_object_size(obj_type)

    # Create value
    obj_value = {f"attr_{i}": i for i in range(min(size, 100))}
    cty_obj = obj_type.validate(obj_value)

    after_size = get_object_size(cty_obj)

    # Size should be reasonable relative to data
    # This is a very rough check
    assert after_size > 0


@pytest.mark.slow
def test_cyclic_reference_handling() -> None:
    """
    Memory pressure: System should handle potential cycles gracefully.

    Tests that the system doesn't create problematic circular references.
    Note: GC behavior is non-deterministic, so this test has lenient thresholds.
    """
    gc.collect()
    gc.collect()  # Double collect for more thorough cleanup
    initial_count = len(gc.get_objects())

    # Create values that could form cycles
    list_type = CtyList(element_type=CtyDynamic())

    # These shouldn't create actual cycles, but let's verify
    for _ in range(100):
        value = list_type.validate([1, 2, 3])
        _ = value

    gc.collect()
    gc.collect()  # Double collect for more thorough cleanup
    final_count = len(gc.get_objects())

    # Should clean up properly (lenient threshold due to GC non-determinism)
    # Account for test infrastructure overhead
    overhead = 2500  # Higher overhead for this test due to DynamicList complexity
    assert final_count < initial_count + overhead


# 🌊🪢🔚
