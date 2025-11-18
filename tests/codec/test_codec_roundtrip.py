#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from decimal import Decimal

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyValue,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.values.markers import RefinedUnknownValue


def test_primitive_roundtrip() -> None:
    schema = CtyString()
    value = schema.validate("hello world")
    msgpack_data = cty_to_msgpack(value, schema)
    new_value = cty_from_msgpack(msgpack_data, schema)
    assert value == new_value, f"Roundtrip failed: original {value} != deserialized {new_value}"


def test_list_roundtrip() -> None:
    schema = CtyList(element_type=CtyNumber())
    value = schema.validate([1, 2, 3])
    msgpack_data = cty_to_msgpack(value, schema)
    new_value = cty_from_msgpack(msgpack_data, schema)
    assert value == new_value, f"Roundtrip failed: original {value} != deserialized {new_value}"


def test_map_roundtrip() -> None:
    schema = CtyMap(element_type=CtyBool())
    value = schema.validate({"a": True, "b": False})
    msgpack_data = cty_to_msgpack(value, schema)
    new_value = cty_from_msgpack(msgpack_data, schema)
    assert value == new_value, f"Roundtrip failed: original {value} != deserialized {new_value}"


def test_object_roundtrip() -> None:
    schema = CtyObject({"name": CtyString(), "age": CtyNumber()})
    value = schema.validate({"name": "Alice", "age": 30})
    msgpack_data = cty_to_msgpack(value, schema)
    new_value = cty_from_msgpack(msgpack_data, schema)
    assert value == new_value, f"Roundtrip failed: original {value} != deserialized {new_value}"


def test_null_roundtrip() -> None:
    schema = CtyString()
    value = CtyValue.null(schema)
    msgpack_data = cty_to_msgpack(value, schema)
    new_value = cty_from_msgpack(msgpack_data, schema)
    assert value == new_value, f"Roundtrip failed: original {value} != deserialized {new_value}"


def test_unknown_roundtrip() -> None:
    schema = CtyString()
    value = CtyValue.unknown(schema)
    msgpack_data = cty_to_msgpack(value, schema)
    new_value = cty_from_msgpack(msgpack_data, schema)
    assert value.is_unknown and new_value.is_unknown, "Both original and deserialized values should be unknown"


def test_refined_unknown_roundtrip() -> None:
    schema = CtyString()
    refinements = {
        "is_known_null": False,
        "string_prefix": "hello",
        "number_lower_bound": (Decimal("10"), True),
        "number_upper_bound": (Decimal("20"), False),
        "collection_length_lower_bound": 5,
        "collection_length_upper_bound": 10,
    }
    value = CtyValue.unknown(schema, value=RefinedUnknownValue(**refinements))
    msgpack_data = cty_to_msgpack(value, schema)
    new_value = cty_from_msgpack(msgpack_data, schema)
    assert new_value.is_unknown, "Deserialized value should be unknown"
    assert isinstance(new_value.value, RefinedUnknownValue), (
        f"Expected RefinedUnknownValue, but got {type(new_value.value)}"
    )
    for key, val in refinements.items():
        assert getattr(new_value.value, key) == val, (
            f"Refinement {key}: expected {val}, but got {getattr(new_value.value, key)}"
        )


# 🌊🪢🔚
