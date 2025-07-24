from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
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
    assert isinstance(inferred_type, expected_type_cls)


def test_infer_list_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw([1, 2, 3])
    assert isinstance(inferred_type, CtyList)
    assert isinstance(inferred_type.element_type, CtyNumber)


def test_infer_set_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw({True, False})
    assert isinstance(inferred_type, CtySet)
    assert isinstance(inferred_type.element_type, CtyBool)


def test_infer_tuple_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw(("a", 1))
    assert isinstance(inferred_type, CtyTuple)
    assert isinstance(inferred_type.element_types[0], CtyString)
    assert isinstance(inferred_type.element_types[1], CtyNumber)


def test_infer_map_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw({"a-b": 1, "c": 2})
    assert isinstance(inferred_type, CtyMap)
    assert isinstance(inferred_type.element_type, CtyNumber)


def test_infer_object_of_primitives() -> None:
    inferred_type = infer_cty_type_from_raw({"a": 1, "b": "c"})
    assert isinstance(inferred_type, CtyObject)
    assert isinstance(inferred_type.attribute_types["a"], CtyNumber)
    assert isinstance(inferred_type.attribute_types["b"], CtyString)


def test_infer_nested_object() -> None:
    inferred_type = infer_cty_type_from_raw({"user": {"name": "Alice", "age": 30}})
    assert isinstance(inferred_type, CtyObject)
    assert isinstance(inferred_type.attribute_types["user"], CtyObject)
    assert isinstance(
        inferred_type.attribute_types["user"].attribute_types["name"], CtyString
    )
    assert isinstance(
        inferred_type.attribute_types["user"].attribute_types["age"], CtyNumber
    )


def test_infer_list_of_objects() -> None:
    inferred_type = infer_cty_type_from_raw([{"name": "Alice"}, {"name": "Bob"}])
    assert isinstance(inferred_type, CtyList)
    assert isinstance(inferred_type.element_type, CtyObject)
    assert isinstance(inferred_type.element_type.attribute_types["name"], CtyString)


def test_infer_mixed_list() -> None:
    inferred_type = infer_cty_type_from_raw([1, "a"])
    assert isinstance(inferred_type, CtyList)
    assert isinstance(inferred_type.element_type, CtyDynamic)


def test_infer_empty_list() -> None:
    inferred_type = infer_cty_type_from_raw([])
    assert isinstance(inferred_type, CtyList)
    assert isinstance(inferred_type.element_type, CtyDynamic)


def test_infer_map_with_mixed_types() -> None:
    inferred_type = infer_cty_type_from_raw({"a": 1, "b": "c"})
    assert isinstance(inferred_type, CtyObject)


def test_infer_from_attrs_object() -> None:
    import attrs

    @attrs.define
    class MyClass:
        a: int
        b: str

    instance = MyClass(a=1, b="c")
    inferred_type = infer_cty_type_from_raw(instance)
    assert isinstance(inferred_type, CtyObject)
    assert isinstance(inferred_type.attribute_types["a"], CtyNumber)
    assert isinstance(inferred_type.attribute_types["b"], CtyString)
