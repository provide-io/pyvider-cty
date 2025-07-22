from types import MappingProxyType
from typing import Any

import attrs
import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.marks import CtyMark


def normalize_repr(value: Any) -> str:
    """Creates a compact, whitespace-normalized repr for easier diffing."""
    return " ".join(repr(value).split())


def deep_unmark(value: CtyValue) -> CtyValue:
    if not isinstance(value, CtyValue):
        return value
    new_inner_value = value.value
    if isinstance(new_inner_value, CtyValue):
        new_inner_value = deep_unmark(new_inner_value)
    elif isinstance(new_inner_value, list | tuple):
        new_inner_value = type(new_inner_value)(deep_unmark(v) for v in new_inner_value)
    elif isinstance(new_inner_value, dict | MappingProxyType):
        new_inner_value = type(new_inner_value)(
            {k: deep_unmark(v) for k, v in new_inner_value.items()}
        )
    return attrs.evolve(value, value=new_inner_value, marks=frozenset())


def assert_value_roundtrip(value: CtyValue) -> None:
    try:
        packed = cty_to_msgpack(value, CtyDynamic())
        unpacked = cty_from_msgpack(packed, CtyDynamic())

        original_unmarked = deep_unmark(value)

        value_to_compare = unpacked
        if not isinstance(original_unmarked.type, CtyDynamic):
            value_to_compare = unpacked.value

        assert value_to_compare == original_unmarked, (
            f"Roundtrip failed!\n"
            f"Original (norm): {normalize_repr(original_unmarked)}\n"
            f"Got (norm):      {normalize_repr(value_to_compare)}"
        )
    except Exception as e:
        pytest.fail(f"Roundtrip assertion failed with an exception: {e}", pytrace=False)


class TestTddDefinitiveCorrectness:
    def test_dynamic_wrapping_list_of_marked_strings(self) -> None:
        list_type = CtyList(element_type=CtyString())
        marked_list_val = list_type.validate(["a", "b"]).mark(CtyMark("sensitive"))
        dynamic_val = CtyDynamic().validate(marked_list_val)
        assert_value_roundtrip(dynamic_val)

    def test_map_of_tuples_containing_marked_values(self) -> None:
        tuple_type = CtyTuple(element_types=(CtyNumber(), CtyString()))
        map_type = CtyMap(element_type=tuple_type)
        tuple_val_1 = tuple_type.validate([1, "one"])
        tuple_val_2_unmarked = tuple_type.validate([2, "two"])
        marked_inner_string = CtyString().validate("two").mark(CtyMark("secret"))
        tuple_val_2 = CtyValue(
            vtype=tuple_type, value=(tuple_val_2_unmarked.value[0], marked_inner_string)
        )
        map_val = map_type.validate({"first": tuple_val_1, "second": tuple_val_2})
        assert_value_roundtrip(map_val)

    def test_object_with_marked_dynamic_list(self) -> None:
        list_type = CtyList(element_type=CtyString())
        marked_list = list_type.validate(["x", "y"]).mark(CtyMark("tainted"))
        obj_type = CtyObject(attribute_types={"data": CtyDynamic()})
        obj_val = obj_type.validate({"data": marked_list})
        assert_value_roundtrip(obj_val)

    def test_list_of_dynamic_values_wrapping_marked_primitives(self) -> None:
        list_type = CtyList(element_type=CtyDynamic())
        marked_num = CtyNumber().validate(100).mark(CtyMark("computed"))
        marked_bool = CtyBool().validate(True).mark(CtyMark("sensitive"))
        list_val = list_type.validate([marked_num, marked_bool, "unmarked"])
        assert_value_roundtrip(list_val)
