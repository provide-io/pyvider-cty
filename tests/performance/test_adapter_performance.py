#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Dedicated performance benchmark for the `cty_to_native` function.

This suite tests the adapter's performance against both deeply nested and
wide (many-element) data structures to ensure it is efficient under
different kinds of load."""

import random
from typing import Any

import pytest

from pyvider.cty import CtyDynamic
from pyvider.cty.conversion import cty_to_native

# --- Test Data Generation ---


def generate_deep_object(depth: int) -> dict[str, Any]:
    """Generates a deeply nested dictionary."""
    if depth <= 0:
        return {"leaf": random.randint(0, 1000)}
    return {
        "id": f"node-{depth}",
        "child": generate_deep_object(depth - 1),
    }


def generate_wide_list(count: int) -> list[dict[str, Any]]:
    """Generates a wide list of moderately complex objects."""
    return [
        {
            "name": f"item-{i}",
            "enabled": i % 2 == 0,
            "config": {"retries": 3, "ports": [80, 443]},
        }
        for i in range(count)
    ]


# --- Pytest Fixtures ---


@pytest.fixture(scope="module")
def deep_cty_value() -> CtyDynamic:
    """Provides a validated CtyValue for a deeply nested object."""
    raw_data = generate_deep_object(depth=200)
    return CtyDynamic().validate(raw_data)


@pytest.fixture(scope="module")
def wide_cty_value() -> CtyDynamic:
    """Provides a validated CtyValue for a wide list of objects."""
    raw_data = generate_wide_list(count=1000)
    return CtyDynamic().validate(raw_data)


# --- Benchmark Tests ---


@pytest.mark.benchmark
def test_benchmark_cty_to_native_deep_structure(benchmark: Any, deep_cty_value: CtyDynamic) -> None:
    """
    Measures the performance of `cty_to_native` on a deeply nested object
    to test the efficiency of the iterative, stack-based approach.
    """
    benchmark(cty_to_native, deep_cty_value)


@pytest.mark.benchmark
def test_benchmark_cty_to_native_wide_structure(benchmark: Any, wide_cty_value: CtyDynamic) -> None:
    """
    Measures the performance of `cty_to_native` on a wide list of objects
    to test its efficiency with large collections.
    """
    benchmark(cty_to_native, wide_cty_value)


# 🌊🪢🔚
