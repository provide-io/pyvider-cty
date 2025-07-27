"""
Targeted benchmark to verify the effectiveness of the type inference cache.
"""
import pytest
from pyvider.cty.conversion import infer_cty_type_from_raw

# A list of 1000 structurally identical objects.
# The cache should hit for 999 of these calls.
STRUCTURALLY_IDENTICAL_OBJECTS = [
    {"name": f"item_{i}", "config": {"enabled": True, "retries": i % 5}}
    for i in range(1000)
]

# A list of 1000 structurally unique objects.
# The cache should miss for every call.
STRUCTURALLY_UNIQUE_OBJECTS = [
    {"name": f"item_{i}", f"config_{i}": {"enabled": True, "retries": i % 5}}
    for i in range(1000)
]

def run_inference(data: list[dict]) -> None:
    """Helper function to run inference on a list of data."""
    for item in data:
        infer_cty_type_from_raw(item)

@pytest.mark.benchmark
def test_inference_cache_hit_performance(benchmark):
    """
    Benchmarks inference where the cache should be highly effective.
    This should be significantly faster than the cache miss test.
    """
    benchmark(run_inference, STRUCTURALLY_IDENTICAL_OBJECTS)

@pytest.mark.benchmark
def test_inference_cache_miss_performance(benchmark):
    """
    Benchmarks inference where the cache should be ineffective.
    This establishes a baseline performance.
    """
    benchmark(run_inference, STRUCTURALLY_UNIQUE_OBJECTS)
