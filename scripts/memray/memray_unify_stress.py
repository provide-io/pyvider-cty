#!/usr/bin/env python3
"""
Memray stress test: type unification hot paths.

Profiles allocation patterns in:
- unify() across 7 type list configurations
- frozenset creation from input iterables
- lru_cache interaction with _unify_frozen
- Pairwise type comparison allocations
"""

import os

os.environ.setdefault("LOG_LEVEL", "ERROR")

from pyvider.cty.conversion import unify
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
)

# --- Type lists to unify ---

HOMOGENEOUS_STRINGS = [CtyString(), CtyString(), CtyString(), CtyString()]
HOMOGENEOUS_NUMBERS = [CtyNumber(), CtyNumber(), CtyNumber()]

MIXED_PRIMITIVES = [CtyString(), CtyNumber(), CtyBool()]

COMPATIBLE_LISTS = [
    CtyList(element_type=CtyString()),
    CtyList(element_type=CtyString()),
]

COMPATIBLE_MAPS = [
    CtyMap(element_type=CtyNumber()),
    CtyMap(element_type=CtyNumber()),
]

SAME_SCHEMA_OBJECTS = [
    CtyObject(attribute_types={"name": CtyString(), "count": CtyNumber()}),
    CtyObject(attribute_types={"name": CtyString(), "count": CtyNumber()}),
    CtyObject(attribute_types={"name": CtyString(), "count": CtyNumber()}),
]

DYNAMIC_WITH_CONCRETE = [CtyDynamic(), CtyString()]

LARGE_TYPE_LIST = [
    CtyString(), CtyNumber(), CtyBool(),
    CtyList(element_type=CtyString()),
    CtyMap(element_type=CtyNumber()),
    CtyObject(attribute_types={"a": CtyString()}),
    CtyDynamic(),
    CtyString(), CtyNumber(), CtyBool(),
]

# --- Cycle configs ---

CONFIGS = [
    ("homogeneous_strings", HOMOGENEOUS_STRINGS, 10_000),
    ("homogeneous_numbers", HOMOGENEOUS_NUMBERS, 10_000),
    ("mixed_primitives", MIXED_PRIMITIVES, 10_000),
    ("compatible_lists", COMPATIBLE_LISTS, 5_000),
    ("compatible_maps", COMPATIBLE_MAPS, 5_000),
    ("same_schema_objects", SAME_SCHEMA_OBJECTS, 5_000),
    ("dynamic_with_concrete", DYNAMIC_WITH_CONCRETE, 5_000),
    ("large_type_list", LARGE_TYPE_LIST, 2_000),
]


def stress_unify() -> None:
    """Stress test type unification hot paths."""
    # Warmup - separate import-time allocations
    for _name, type_list, _cycles in CONFIGS:
        _ = unify(type_list)

    total_cycles = 0

    for name, type_list, cycles in CONFIGS:
        for _ in range(cycles):
            _ = unify(type_list)
        total_cycles += cycles

    print(f"Unify stress test complete: {total_cycles} cycles across {len(CONFIGS)} type lists")


def main() -> None:
    """Entry point."""
    stress_unify()


if __name__ == "__main__":
    main()
