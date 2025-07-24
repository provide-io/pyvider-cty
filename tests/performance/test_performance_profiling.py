import random
import time
from typing import Any

import pytest

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack

# --- Configuration ---
NUM_OBJECTS = 1000  # Number of CtyValues to process per benchmark round
NESTING_DEPTH = 3  # Depth of nested objects within the test data

# --- Test Data Generation ---


def generate_complex_object_data(depth: int) -> dict[str, Any]:
    """Generates a nested Python dictionary to simulate complex config data."""
    if depth <= 0:
        return {
            "id": f"leaf-{random.randint(1000, 9999)}",
            "value": random.random() * 100,
            "enabled": random.choice([True, False]),
        }
    return {
        "id": f"node-{depth}-{random.randint(100, 999)}",
        "timestamp": time.time(),
        "metadata": {
            "source": "profiler",
            "version": "1.0",
        },
        "children": [generate_complex_object_data(depth - 1) for _ in range(2)],
    }


def generate_cty_schema_from_data(d: dict) -> CtyObject:
    """Recursively generates a CtyObject type from a sample dictionary."""
    attrs = {}
    for key, value in d.items():
        if isinstance(value, str):
            attrs[key] = CtyString()
        elif isinstance(value, int | float):
            attrs[key] = CtyNumber()
        elif isinstance(value, bool):
            attrs[key] = CtyBool()
        elif isinstance(value, dict):
            attrs[key] = generate_cty_schema_from_data(value)
        elif isinstance(value, list) and value:
            attrs[key] = CtyList(element_type=generate_cty_schema_from_data(value[0]))
        else:
            # Fallback for empty lists or other types
            attrs[key] = CtyList(element_type=CtyObject({}))
    return CtyObject(attribute_types=attrs)


# --- Pytest Fixture for Test Data ---


@pytest.fixture(scope="module")
def complex_data_and_schema() -> tuple[list[dict[str, Any]], CtyObject]:
    """
    Generates a large set of complex data and its corresponding schema.
    This fixture is module-scoped to avoid re-generating data for each test.
    """
    sample_data = generate_complex_object_data(NESTING_DEPTH)
    cty_schema = generate_cty_schema_from_data(sample_data)
    test_data = [
        generate_complex_object_data(NESTING_DEPTH) for _ in range(NUM_OBJECTS)
    ]
    return test_data, cty_schema


# --- Benchmark Test ---


def core_roundtrip_operation(data_list: list[dict], schema: CtyObject) -> None:
    """
    The core operation to be benchmarked: validating, marshalling to msgpack,
    and unmarshalling back for a list of objects.
    """
    for raw_data in data_list:
        # 1. Validate raw Python data into a CtyValue
        cty_val = schema.validate(raw_data)
        # 2. Marshal to msgpack bytes
        packed_bytes = cty_to_msgpack(cty_val, schema)
        # 3. Unmarshal back to a CtyValue
        _ = cty_from_msgpack(packed_bytes, schema)


@pytest.mark.benchmark
def test_benchmark_full_conversion_roundtrip(
    benchmark: Any, complex_data_and_schema: tuple[list[dict[str, Any]], CtyObject]
) -> None:
    """
    Uses pytest-benchmark to measure the performance of the full
    validate -> marshal -> unmarshal data conversion pipeline.
    This test is skipped by default unless --run-benchmarks is specified.
    """
    test_data, cty_schema = complex_data_and_schema

    # The benchmark fixture runs the provided function multiple times
    # to get statistically stable results.
    benchmark(core_roundtrip_operation, test_data, cty_schema)
