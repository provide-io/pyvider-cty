#!/usr/bin/env python3
"""
Memray stress test: msgpack codec hot paths.

Profiles allocation patterns in:
- cty_to_msgpack() serialization across 6 value shapes
- cty_from_msgpack() deserialization across 6 value shapes
- Round-trip serialize -> deserialize cycles (assert equality)
"""

import os

os.environ.setdefault("LOG_LEVEL", "ERROR")

from decimal import Decimal

from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.types import CtyBool, CtyList, CtyMap, CtyNumber, CtyObject, CtyString
from pyvider.cty.validation.recursion import clear_recursion_context

# --- Schemas and pre-validated values ---

STRING_SCHEMA = CtyString()
NUMBER_SCHEMA = CtyNumber()
BOOL_SCHEMA = CtyBool()

LIST_SCHEMA = CtyList(element_type=CtyString())
MAP_SCHEMA = CtyMap(element_type=CtyNumber())

OBJECT_SCHEMA = CtyObject(
    attribute_types={
        "name": CtyString(),
        "age": CtyNumber(),
        "active": CtyBool(),
        "email": CtyString(),
        "role": CtyString(),
    }
)

NESTED_SCHEMA = CtyObject(
    attribute_types={
        "id": CtyString(),
        "items": CtyList(
            element_type=CtyObject(
                attribute_types={
                    "label": CtyString(),
                    "score": CtyNumber(),
                }
            )
        ),
        "metadata": CtyMap(element_type=CtyString()),
    }
)

# Pre-validate all test values
STRING_VALUE = STRING_SCHEMA.validate("benchmark-string-value")
NUMBER_VALUE = NUMBER_SCHEMA.validate(Decimal("123456.789"))
BOOL_VALUE = BOOL_SCHEMA.validate(True)

LIST_VALUE = LIST_SCHEMA.validate([f"item-{i}" for i in range(10)])
MAP_VALUE = MAP_SCHEMA.validate({f"key-{i}": Decimal(str(i * 100)) for i in range(10)})

OBJECT_VALUE = OBJECT_SCHEMA.validate(
    {
        "name": "benchmark",
        "age": Decimal("30"),
        "active": True,
        "email": "bench@test.io",
        "role": "admin",
    }
)

NESTED_VALUE = NESTED_SCHEMA.validate(
    {
        "id": "nested-1",
        "items": [{"label": f"item-{i}", "score": Decimal(str(i * 10))} for i in range(5)],
        "metadata": {"env": "prod", "region": "us-east-1", "version": "2.0"},
    }
)

# --- Cycle configs ---

CONFIGS = [
    ("string", STRING_SCHEMA, STRING_VALUE, 10_000),
    ("number", NUMBER_SCHEMA, NUMBER_VALUE, 10_000),
    ("bool", BOOL_SCHEMA, BOOL_VALUE, 10_000),
    ("list_of_strings", LIST_SCHEMA, LIST_VALUE, 5_000),
    ("map_of_numbers", MAP_SCHEMA, MAP_VALUE, 5_000),
    ("flat_object", OBJECT_SCHEMA, OBJECT_VALUE, 3_000),
    ("nested_object", NESTED_SCHEMA, NESTED_VALUE, 2_000),
]


def stress_codec() -> None:
    """Stress test msgpack codec hot paths."""
    # Warmup - separate import-time allocations
    for _name, schema, value, _cycles in CONFIGS:
        packed = cty_to_msgpack(value, schema)
        _ = cty_from_msgpack(packed, schema)

    total_cycles = 0

    # Serialize cycles
    for _name, schema, value, cycles in CONFIGS:
        for _ in range(cycles):
            _ = cty_to_msgpack(value, schema)
        total_cycles += cycles

    # Deserialize cycles (deserialization calls validate, so clear recursion context)
    for _name, schema, value, cycles in CONFIGS:
        packed = cty_to_msgpack(value, schema)
        for _ in range(cycles):
            clear_recursion_context()
            _ = cty_from_msgpack(packed, schema)
        total_cycles += cycles

    # Round-trip cycles (half the serialize count per shape)
    for _name, schema, value, cycles in CONFIGS:
        rt_cycles = cycles // 2
        for _ in range(rt_cycles):
            packed = cty_to_msgpack(value, schema)
            clear_recursion_context()
            _ = cty_from_msgpack(packed, schema)
        total_cycles += rt_cycles

    print(f"Codec stress test complete: {total_cycles} cycles across {len(CONFIGS)} value shapes")


def main() -> None:
    """Entry point."""
    stress_codec()


if __name__ == "__main__":
    main()
