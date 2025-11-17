#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Comprehensive performance benchmark suite for pyvider.cty.

This suite includes 7 tests to measure the performance of key functions
before and after caching optimizations, including a full round-trip test."""

import pytest

from pyvider.cty import CtyDynamic, CtyList, CtyNumber, CtyObject, CtyString
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.conversion import cty_to_native, infer_cty_type_from_raw, unify

# --- Fixtures for Benchmark Data ---


@pytest.fixture(scope="module")
def complex_type_list():
    """Generates a list of complex, nested types for the unify benchmark."""
    types = [
        CtyObject({"a": CtyString(), "b": CtyList(element_type=CtyNumber())}),
        CtyObject({"a": CtyString(), "b": CtyList(element_type=CtyNumber()), "c": CtyString()}),
        CtyObject({"a": CtyString(), "b": CtyList(element_type=CtyNumber())}),
        CtyObject({"a": CtyString()}),
    ]
    # Make it longer and more repetitive to better test caching
    return types * 200


@pytest.fixture(scope="module")
def complex_raw_data():
    """Generates a SINGLE, deeply nested, unhashable dictionary for inference benchmarks."""
    return {
        "id": "item-_COMPLEX_",
        "enabled": True,
        "config": {
            "params": [10, 20.5, 30, 40, 50],
            "metadata": {
                "source": "benchmark",
                "nested": {"value": True, "tags": ["a", "b"]},
            },
            "ports": (80, 443),
        },
        "data_points": [{"x": i, "y": i * 2} for i in range(50)],
    }


@pytest.fixture(scope="module")
def validated_complex_cty_value(complex_raw_data):
    """Provides a validated CtyValue corresponding to the raw data."""
    schema = infer_cty_type_from_raw(complex_raw_data)
    return schema.validate(complex_raw_data)


# --- Benchmark Tests ---


@pytest.mark.benchmark
def test_benchmark_unify_performance(benchmark, complex_type_list) -> None:
    """[1/7] Measures the performance of the `unify` function."""
    benchmark(unify, complex_type_list)


@pytest.mark.benchmark
def test_benchmark_infer_type_performance(benchmark, complex_raw_data) -> None:
    """[2/7] Measures `infer_cty_type_from_raw` on the SAME complex object."""
    # This correctly tests the cache by calling the function repeatedly
    # on the same input object within the benchmark loop.
    benchmark(infer_cty_type_from_raw, complex_raw_data)


@pytest.mark.benchmark
def test_benchmark_validation_performance(benchmark, complex_raw_data) -> None:
    """[3/7] Measures schema validation, which implicitly uses inference."""
    # Since validation of raw data calls infer_cty_type_from_raw,
    # this benchmark should also see a significant speedup from caching.
    schema = infer_cty_type_from_raw(complex_raw_data)
    benchmark(schema.validate, complex_raw_data)


@pytest.mark.benchmark
def test_benchmark_serialization_performance(benchmark, validated_complex_cty_value) -> None:
    """[4/7] Measures serialization (`cty_to_msgpack`) performance."""
    schema = validated_complex_cty_value.type
    benchmark(cty_to_msgpack, validated_complex_cty_value, schema)


@pytest.mark.benchmark
def test_benchmark_deserialization_performance(benchmark, validated_complex_cty_value) -> None:
    """[5/7] Measures deserialization (`cty_from_msgpack`) performance."""
    schema = validated_complex_cty_value.type
    packed_bytes = cty_to_msgpack(validated_complex_cty_value, schema)
    benchmark(cty_from_msgpack, packed_bytes, schema)


@pytest.mark.benchmark
def test_benchmark_to_native_performance(benchmark, validated_complex_cty_value) -> None:
    """[6/7] Measures `cty_to_native` conversion performance."""
    benchmark(cty_to_native, validated_complex_cty_value)


@pytest.mark.benchmark
def test_benchmark_full_round_trip(benchmark, complex_raw_data) -> None:
    """
    [7/7] Measures the full, real-world round-trip performance:
    validate -> serialize -> deserialize -> convert_to_native
    """
    schema = CtyDynamic()  # Use dynamic for the most general case

    def round_trip_operation() -> None:
        # 1. Validate (includes type inference)
        cty_val = schema.validate(complex_raw_data)
        # 2. Serialize
        packed = cty_to_msgpack(cty_val, schema)
        # 3. Deserialize
        unpacked_val = cty_from_msgpack(packed, schema)
        # 4. Convert back to native
        _ = cty_to_native(unpacked_val)

    benchmark(round_trip_operation)


# 🌊🪢🔚
