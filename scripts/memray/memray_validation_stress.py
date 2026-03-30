#!/usr/bin/env python3
"""
Memray stress test: type validation hot paths.

Profiles allocation patterns in:
- CtyObject.validate() across 5 schema complexities
- CtyList.validate() with element validation
- CtyMap.validate() with key/value validation
- CtyValue attrs frozen dataclass instantiation
"""

import os

os.environ.setdefault("LOG_LEVEL", "ERROR")

from decimal import Decimal

from pyvider.cty.types import CtyBool, CtyList, CtyMap, CtyNumber, CtyObject, CtyString
from pyvider.cty.validation.recursion import clear_recursion_context

# --- Schema definitions ---

FLAT_SCHEMA = CtyObject(
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
        "user": CtyObject(
            attribute_types={
                "profile": CtyObject(
                    attribute_types={
                        "name": CtyString(),
                        "score": CtyNumber(),
                    }
                ),
                "active": CtyBool(),
            }
        ),
        "version": CtyNumber(),
    }
)

LIST_OF_OBJECTS_SCHEMA = CtyObject(
    attribute_types={
        "items": CtyList(
            element_type=CtyObject(
                attribute_types={
                    "id": CtyNumber(),
                    "label": CtyString(),
                }
            )
        ),
        "count": CtyNumber(),
    }
)

MAP_SCHEMA = CtyObject(
    attribute_types={
        "tags": CtyMap(element_type=CtyString()),
        "scores": CtyMap(element_type=CtyNumber()),
    }
)

COMBINED_SCHEMA = CtyObject(
    attribute_types={
        "id": CtyString(),
        "enabled": CtyBool(),
        "config": CtyObject(
            attribute_types={
                "params": CtyList(element_type=CtyNumber()),
                "metadata": CtyMap(element_type=CtyString()),
            }
        ),
        "nested": CtyObject(
            attribute_types={
                "inner": CtyObject(
                    attribute_types={
                        "value": CtyNumber(),
                    }
                ),
            }
        ),
    }
)

# --- Test data ---

FLAT_DATA = {
    "name": "benchmark",
    "age": Decimal("30"),
    "active": True,
    "email": "bench@test.io",
    "role": "admin",
}

NESTED_DATA = {
    "user": {
        "profile": {"name": "test", "score": Decimal("95")},
        "active": True,
    },
    "version": Decimal("2"),
}

LIST_OF_OBJECTS_DATA = {
    "items": [{"id": Decimal(str(i)), "label": f"item-{i}"} for i in range(10)],
    "count": Decimal("10"),
}

MAP_DATA = {
    "tags": {f"key-{i}": f"value-{i}" for i in range(10)},
    "scores": {f"metric-{i}": Decimal(str(i * 10)) for i in range(10)},
}

COMBINED_DATA = {
    "id": "combo-1",
    "enabled": True,
    "config": {
        "params": [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4"), Decimal("5")],
        "metadata": {"env": "prod", "region": "us-east-1"},
    },
    "nested": {"inner": {"value": Decimal("42")}},
}

# --- Cycle configs ---

CONFIGS = [
    ("flat_object", FLAT_SCHEMA, FLAT_DATA, 5_000),
    ("nested_object", NESTED_SCHEMA, NESTED_DATA, 3_000),
    ("list_of_objects", LIST_OF_OBJECTS_SCHEMA, LIST_OF_OBJECTS_DATA, 2_000),
    ("map_attributes", MAP_SCHEMA, MAP_DATA, 3_000),
    ("combined", COMBINED_SCHEMA, COMBINED_DATA, 2_000),
]


def stress_validation() -> None:
    """Stress test type validation hot paths."""
    # Warmup - separate import-time allocations
    for _name, schema, data, _cycles in CONFIGS:
        _ = schema.validate(data)

    total_cycles = 0

    for name, schema, data, cycles in CONFIGS:
        for _ in range(cycles):
            clear_recursion_context()
            _ = schema.validate(data)
        total_cycles += cycles

    print(f"Validation stress test complete: {total_cycles} cycles across {len(CONFIGS)} schemas")


def main() -> None:
    """Entry point."""
    stress_validation()


if __name__ == "__main__":
    main()
