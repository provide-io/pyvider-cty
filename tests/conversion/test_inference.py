#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
)
from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw


@pytest.mark.parametrize(
    "raw_value, expected_type_cls",
    [
        ("hello", CtyString),
        (123, CtyNumber),
        (3.14, CtyNumber),
        (Decimal("99.9"), CtyNumber),
        (True, CtyBool),
        (None, CtyDynamic),
    ],
)
def test_infer_primitive_types(raw_value: Any, expected_type_cls: type) -> None:
    """Tests that the type inference correctly identifies primitive types."""
    inferred_type = infer_cty_type_from_raw(raw_value)
    assert isinstance(inferred_type, expected_type_cls), (
        f"Expected {expected_type_cls.__name__}, but got {type(inferred_type).__name__}"
    )


def test_infer_list_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw([1, 2, 3])
    assert isinstance(inferred_type, CtyList), f"Expected CtyList, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.element_type, CtyNumber), (
        f"Expected element type CtyNumber, but got {type(inferred_type.element_type).__name__}"
    )


def test_infer_set_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw({True, False})
    assert isinstance(inferred_type, CtySet), f"Expected CtySet, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.element_type, CtyBool), (
        f"Expected element type CtyBool, but got {type(inferred_type.element_type).__name__}"
    )


def test_infer_tuple_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw(("a", 1))
    assert isinstance(inferred_type, CtyTuple), f"Expected CtyTuple, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.element_types[0], CtyString), (
        f"Expected first element type CtyString, but got {type(inferred_type.element_types[0]).__name__}"
    )
    assert isinstance(inferred_type.element_types[1], CtyNumber), (
        f"Expected second element type CtyNumber, but got {type(inferred_type.element_types[1]).__name__}"
    )


def test_infer_object_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw({"a": 1, "c": 2})
    assert isinstance(inferred_type, CtyObject), f"Expected CtyObject, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.attribute_types["a"], CtyNumber), (
        f"Expected attribute 'a' type CtyNumber, but got {type(inferred_type.attribute_types['a']).__name__}"
    )
    assert isinstance(inferred_type.attribute_types["c"], CtyNumber), (
        f"Expected attribute 'c' type CtyNumber, but got {type(inferred_type.attribute_types['c']).__name__}"
    )


def test_infer_object_of_primitives_mixed() -> None:
    inferred_type = infer_cty_type_from_raw({"a": 1, "b": "c"})
    assert isinstance(inferred_type, CtyObject), f"Expected CtyObject, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.attribute_types["a"], CtyNumber), (
        f"Expected attribute 'a' type CtyNumber, but got {type(inferred_type.attribute_types['a']).__name__}"
    )
    assert isinstance(inferred_type.attribute_types["b"], CtyString), (
        f"Expected attribute 'b' type CtyString, but got {type(inferred_type.attribute_types['b']).__name__}"
    )


def test_infer_nested_object() -> None:
    inferred_type = infer_cty_type_from_raw({"user": {"name": "Alice", "age": 30}})
    assert isinstance(inferred_type, CtyObject), f"Expected CtyObject, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.attribute_types["user"], CtyObject)
    assert isinstance(inferred_type.attribute_types["user"].attribute_types["name"], CtyString), (
        f"Expected nested attribute 'name' type CtyString, but got {type(inferred_type.attribute_types['user'].attribute_types['name']).__name__}"
    )
    assert isinstance(inferred_type.attribute_types["user"].attribute_types["age"], CtyNumber), (
        f"Expected nested attribute 'age' type CtyNumber, but got {type(inferred_type.attribute_types['user'].attribute_types['age']).__name__}"
    )


def test_infer_list_of_objects() -> None:
    inferred_type = infer_cty_type_from_raw([{"name": "Alice"}, {"name": "Bob"}])
    assert isinstance(inferred_type, CtyList), f"Expected CtyList, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.element_type, CtyObject)
    assert isinstance(inferred_type.element_type.attribute_types["name"], CtyString), (
        f"Expected list element attribute 'name' type CtyString, but got {type(inferred_type.element_type.attribute_types['name']).__name__}"
    )


def test_infer_mixed_list() -> None:
    inferred_type = infer_cty_type_from_raw([1, "a"])
    assert isinstance(inferred_type, CtyList), f"Expected CtyList, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.element_type, CtyDynamic), (
        f"Expected element type CtyDynamic for mixed list, but got {type(inferred_type.element_type).__name__}"
    )


def test_infer_empty_list() -> None:
    inferred_type = infer_cty_type_from_raw([])
    assert isinstance(inferred_type, CtyList), f"Expected CtyList, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.element_type, CtyDynamic), (
        f"Expected element type CtyDynamic for mixed list, but got {type(inferred_type.element_type).__name__}"
    )


def test_infer_map_with_mixed_types() -> None:
    inferred_type = infer_cty_type_from_raw({"a": 1, "b": "c"})
    assert isinstance(inferred_type, CtyObject), f"Expected CtyObject, but got {type(inferred_type).__name__}"


def test_infer_from_attrs_object() -> None:
    import attrs

    @attrs.define
    class MyClass:
        a: int
        b: str

    instance = MyClass(a=1, b="c")
    inferred_type = infer_cty_type_from_raw(instance)
    assert isinstance(inferred_type, CtyObject), f"Expected CtyObject, but got {type(inferred_type).__name__}"
    assert isinstance(inferred_type.attribute_types["a"], CtyNumber), (
        f"Expected attribute 'a' type CtyNumber, but got {type(inferred_type.attribute_types['a']).__name__}"
    )
    assert isinstance(inferred_type.attribute_types["b"], CtyString), (
        f"Expected attribute 'b' type CtyString, but got {type(inferred_type.attribute_types['b']).__name__}"
    )


# 🌊🪢🔚
