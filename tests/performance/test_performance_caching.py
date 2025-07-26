"""
Dedicated benchmark suite for testing performance improvements via caching
for the `unify` and `infer_cty_type_from_raw` functions.
"""

import pytest

from pyvider.cty import (
    CtyList, CtyNumber, CtyObject, CtyString
)
from pyvider.cty.conversion import infer_cty_type_from_raw, unify

# --- Benchmark for `unify` ---

@pytest.fixture(scope="module")
def complex_type_list():
    """Generates a list of complex, nested types for the unify benchmark."""
    types = [
        CtyObject({"a": CtyString(), "b": CtyList(element_type=CtyNumber())}),
        CtyObject({"a": CtyString(), "b": CtyList(element_type=CtyNumber()), "c": CtyString()}),
        CtyObject({"a": CtyString(), "b": CtyList(element_type=CtyNumber())}),
        CtyObject({"a": CtyString()}), # Different structure
    ]
    # Repeat the pattern to simulate many calls with similar structures
    return types * 50

@pytest.mark.benchmark
def test_benchmark_unify_performance(benchmark, complex_type_list):
    """Measures the performance of the `unify` function."""
    benchmark(unify, complex_type_list)

# --- Benchmark for `infer_cty_type_from_raw` ---

@pytest.fixture(scope="module")
def complex_raw_data_list():
    """Generates a list of complex, nested, unhashable dictionaries."""
    data = []
    for i in range(200): # Simulate a larger number of inference calls
        data.append({
            "id": f"item-{i}",
            "config": {
                "params": [1, 2, 3, 4, 5],
                "metadata": {"source": "benchmark", "nested": {"value": True}}
            },
            "data": ["a", "b", "c"]
        })
    return data

@pytest.mark.benchmark
def test_benchmark_infer_type_performance(benchmark, complex_raw_data_list):
    """Measures the performance of `infer_cty_type_from_raw` on many identical objects."""
    def infer_all():
        for item in complex_raw_data_list:
            infer_cty_type_from_raw(item)

    benchmark(infer_all)

