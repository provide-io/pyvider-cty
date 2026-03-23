#!/usr/bin/env python3
"""
Memray stress test: cty_to_native conversion hot paths.

Profiles allocation patterns in:
- cty_to_native() iterative stack-based conversion
- work_stack / results dict / processing set allocation per call
- POST_PROCESS sentinel and tuple/list/dict construction
"""

import os

os.environ.setdefault("LOG_LEVEL", "ERROR")

from decimal import Decimal

from pyvider.cty.conversion import cty_to_native
from pyvider.cty.types import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
)

# --- Pre-validated CtyValues ---

STRING_VALUE = CtyString().validate("hello-benchmark")
NUMBER_VALUE = CtyNumber().validate(Decimal("42.5"))
BOOL_VALUE = CtyBool().validate(True)

LIST_VALUE = CtyList(element_type=CtyString()).validate([f"item-{i}" for i in range(20)])

SET_VALUE = CtySet(element_type=CtyNumber()).validate({Decimal(str(i)) for i in range(10)})

MAP_VALUE = CtyMap(element_type=CtyString()).validate({f"key-{i}": f"value-{i}" for i in range(10)})

TUPLE_VALUE = CtyTuple(element_types=(CtyString(), CtyNumber(), CtyBool())).validate(
    ("mixed", Decimal("99"), True)
)

# Deep nesting: 4 levels of objects
DEEP_SCHEMA = CtyObject(
    attribute_types={
        "level1": CtyObject(
            attribute_types={
                "level2": CtyObject(
                    attribute_types={
                        "level3": CtyObject(
                            attribute_types={
                                "value": CtyNumber(),
                                "label": CtyString(),
                            }
                        ),
                        "sibling": CtyString(),
                    }
                ),
                "count": CtyNumber(),
            }
        ),
        "name": CtyString(),
    }
)

DEEP_VALUE = DEEP_SCHEMA.validate(
    {
        "level1": {
            "level2": {
                "level3": {"value": Decimal("42"), "label": "deep"},
                "sibling": "data",
            },
            "count": Decimal("7"),
        },
        "name": "root",
    }
)

# Complex: object with list of objects
COMPLEX_SCHEMA = CtyObject(
    attribute_types={
        "id": CtyString(),
        "items": CtyList(
            element_type=CtyObject(
                attribute_types={
                    "name": CtyString(),
                    "score": CtyNumber(),
                }
            )
        ),
        "tags": CtyMap(element_type=CtyString()),
    }
)

COMPLEX_VALUE = COMPLEX_SCHEMA.validate(
    {
        "id": "complex-1",
        "items": [{"name": f"item-{i}", "score": Decimal(str(i * 10))} for i in range(10)],
        "tags": {f"tag-{i}": f"val-{i}" for i in range(5)},
    }
)

# --- Cycle configs ---

CONFIGS = [
    ("string", STRING_VALUE, 10_000),
    ("number", NUMBER_VALUE, 10_000),
    ("bool", BOOL_VALUE, 10_000),
    ("list_20", LIST_VALUE, 5_000),
    ("set_10", SET_VALUE, 5_000),
    ("map_10", MAP_VALUE, 5_000),
    ("tuple_mixed", TUPLE_VALUE, 5_000),
    ("deep_nested", DEEP_VALUE, 2_000),
    ("complex_object", COMPLEX_VALUE, 2_000),
]


def stress_conversion() -> None:
    """Stress test cty_to_native conversion hot paths."""
    # Warmup - separate import-time allocations
    for _name, value, _cycles in CONFIGS:
        _ = cty_to_native(value)

    total_cycles = 0

    for name, value, cycles in CONFIGS:
        for _ in range(cycles):
            _ = cty_to_native(value)
        total_cycles += cycles

    print(f"Conversion stress test complete: {total_cycles} cycles across {len(CONFIGS)} value shapes")


def main() -> None:
    """Entry point."""
    stress_conversion()


if __name__ == "__main__":
    main()
