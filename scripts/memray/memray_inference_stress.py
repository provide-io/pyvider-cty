#!/usr/bin/env python3
"""
Memray stress test: type inference hot paths.

Profiles allocation patterns in:
- infer_cty_type_from_raw() across 6 data shapes
- Cache key generation and container schema caching
- Structural key computation for complex dicts
"""

import os

os.environ.setdefault("LOG_LEVEL", "ERROR")

from pyvider.cty.conversion import infer_cty_type_from_raw

# --- Test data shapes ---

PRIMITIVES = ["hello", 42, 3.14, True, None]

FLAT_DICT = {"name": "test", "count": 42, "active": True, "score": 3.14}

NESTED_DICT = {
    "level1": {
        "level2": {
            "level3": {"value": "deep", "count": 99},
        },
        "sibling": "data",
    },
    "top": True,
}

MIXED_LIST = [1, "two", 3.0, True, {"nested": "dict"}]

LIST_OF_DICTS = [{"id": i, "name": f"item-{i}", "active": i % 2 == 0} for i in range(10)]

COMPLEX_NESTED = {
    "id": "complex-1",
    "enabled": True,
    "config": {
        "params": [10, 20.5, 30, 40, 50],
        "metadata": {
            "source": "benchmark",
            "nested": {"value": True, "tags": ["a", "b"]},
        },
    },
    "data_points": [{"x": i, "y": i * 2} for i in range(20)],
}

# --- Cycle configs ---

CONFIGS = [
    ("primitives", PRIMITIVES, 10_000),
    ("flat_dict", FLAT_DICT, 5_000),
    ("nested_dict", NESTED_DICT, 3_000),
    ("mixed_list", MIXED_LIST, 5_000),
    ("list_of_dicts", LIST_OF_DICTS, 3_000),
    ("complex_nested", COMPLEX_NESTED, 2_000),
]


def stress_inference() -> None:
    """Stress test type inference hot paths."""
    # Warmup - separate import-time allocations
    for _name, data, _cycles in CONFIGS:
        if isinstance(data, list) and not isinstance(data[0], dict):
            for item in data:
                _ = infer_cty_type_from_raw(item)
        else:
            _ = infer_cty_type_from_raw(data)

    total_cycles = 0

    for name, data, cycles in CONFIGS:
        if name == "primitives":
            # Infer each primitive individually
            for _ in range(cycles):
                for item in data:
                    _ = infer_cty_type_from_raw(item)
            total_cycles += cycles * len(data)
        else:
            for _ in range(cycles):
                _ = infer_cty_type_from_raw(data)
            total_cycles += cycles

    print(f"Inference stress test complete: {total_cycles} cycles across {len(CONFIGS)} data shapes")


def main() -> None:
    """Entry point."""
    stress_inference()


if __name__ == "__main__":
    main()
