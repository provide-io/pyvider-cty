"""
Performance benchmark suite for the parallel API of pyvider.cty.

This suite measures the throughput of bulk operations when distributed
across all available CPU cores.
"""
import functools
import multiprocessing
import os
import random
import time
from typing import Any

import pytest

from pyvider.cty import CtyObject, CtyString, CtyNumber, CtyBool, CtyList, CtyType
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack

# --- Configuration ---
NUM_OBJECTS = 2000
NESTING_DEPTH = 3

# --- Worker-Global State and Initializer ---
_worker_schema: CtyType | None = None

def _initializer(schema: CtyType) -> None:
    """Initializes each worker process with the schema just once."""
    global _worker_schema
    _worker_schema = schema

def _roundtrip_worker(raw_data: dict) -> bytes:
    """
    The unit of work for a single item in the parallel benchmark.
    It performs a full validate -> serialize -> deserialize roundtrip.
    """
    if _worker_schema is None:
        raise RuntimeError("Worker schema not initialized.")
    
    validated_val = _worker_schema.validate(raw_data)
    packed_bytes = cty_to_msgpack(validated_val, _worker_schema)
    _ = cty_from_msgpack(packed_bytes, _worker_schema)
    return packed_bytes # Return data to ensure work is not optimized away

# --- Test Data Generation ---

def generate_complex_object_data(depth: int) -> dict[str, Any]:
    """Generates a unique, nested Python dictionary."""
    if depth <= 0:
        return {
            "id": f"leaf-{random.randint(1000, 9999)}",
            "value": random.random() * 100,
            "enabled": random.choice([True, False]),
        }
    return {
        "id": f"node-{depth}-{random.randint(100, 999)}",
        "timestamp": time.time(),
        "metadata": {"source": "profiler", "version": "1.0"},
        "children": [generate_complex_object_data(depth - 1) for _ in range(2)],
    }

def generate_cty_schema_from_data(d: dict) -> CtyObject:
    """Recursively generates a CtyObject type from a sample dictionary."""
    attrs = {}
    for key, value in d.items():
        if isinstance(value, str): attrs[key] = CtyString()
        elif isinstance(value, int | float): attrs[key] = CtyNumber()
        elif isinstance(value, bool): attrs[key] = CtyBool()
        elif isinstance(value, dict): attrs[key] = generate_cty_schema_from_data(value)
        elif isinstance(value, list) and value:
            attrs[key] = CtyList(element_type=generate_cty_schema_from_data(value[0]))
        else:
            attrs[key] = CtyList(element_type=CtyObject({}))
    return CtyObject(attribute_types=attrs)

@pytest.fixture(scope="module")
def complex_data_and_schema() -> tuple[list[dict[str, Any]], CtyObject]:
    """Generates a large set of unique data objects and a representative schema."""
    sample_data = generate_complex_object_data(NESTING_DEPTH)
    cty_schema = generate_cty_schema_from_data(sample_data)
    test_data = [generate_complex_object_data(NESTING_DEPTH) for _ in range(NUM_OBJECTS)]
    return test_data, cty_schema

# --- Core Operation for Benchmarking ---

def parallel_roundtrip_operation(data_list: list[dict], schema: CtyObject) -> None:
    """
    The core operation to be benchmarked. It uses a single process pool
    to run the full roundtrip worker over all data.
    """
    cpu_count = os.cpu_count() or 1
    with multiprocessing.Pool(processes=cpu_count, initializer=_initializer, initargs=(schema,)) as pool:
        pool.map(_roundtrip_worker, data_list)


@pytest.mark.benchmark
def test_benchmark_parallel_full_roundtrip(
    benchmark: Any, complex_data_and_schema: tuple[list[dict[str, Any]], CtyObject]
) -> None:
    """
    Measures the throughput of the full validate -> serialize -> deserialize
    pipeline using an efficient, single-pool parallel execution strategy.
    """
    test_data, cty_schema = complex_data_and_schema
    benchmark(parallel_roundtrip_operation, test_data, cty_schema)
