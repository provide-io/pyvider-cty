"""
TDD Performance Test for Inference Optimization.

This test specifically targets the performance bottleneck identified when
inferring types for a large number of structurally identical but distinct
Python objects. This simulates a common workload, such as processing a list
of resources from a configuration file.
"""
import pytest
from pyvider.cty.conversion import infer_cty_type_from_raw

# Number of unique but structurally identical objects to create.
NUM_REPEATED_OBJECTS = 2000

@pytest.fixture(scope="module")
def structurally_repeated_data() -> list[dict]:
    """
    Creates a list of many dictionary objects that have the same keys
    but are distinct instances. This is designed to defeat instance-based
    caching (like functools.lru_cache) and test structural caching.
    """
    return [
        {
            "id": f"id-{i}",
            "name": "benchmark-object",
            "config": {"retries": 3, "enabled": True},
            "ports": [80, 443],
        }
        for i in range(NUM_REPEATED_OBJECTS)
    ]


def inference_operation(data_list: list[dict]) -> None:
    """The core operation to benchmark: inferring the type for each object."""
    for item in data_list:
        _ = infer_cty_type_from_raw(item)


@pytest.mark.benchmark
def test_inference_performance_on_repeated_structures(
    benchmark, structurally_repeated_data: list[dict]
) -> None:
    """
    Benchmarks the performance of `infer_cty_type_from_raw` on a list of
    structurally identical objects.

    This test will be slow with the original implementation but should become
    significantly faster after structural caching is introduced.
    """
    benchmark(inference_operation, structurally_repeated_data)
