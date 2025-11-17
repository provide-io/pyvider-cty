#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

from decimal import Decimal

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
from pyvider.cty.conversion.adapter import cty_to_native


def test_cty_to_native_with_set() -> None:
    set_type = CtySet(element_type=CtyString())
    cty_val = set_type.validate({"a", "b", "c"})
    native = cty_to_native(cty_val)
    assert isinstance(native, list)
    assert sorted(native) == ["a", "b", "c"]


def test_cty_to_native_with_tuple() -> None:
    tuple_type = CtyTuple(element_types=(CtyString(), CtyString()))
    cty_val = tuple_type.validate(("a", "b"))
    native = cty_to_native(cty_val)
    assert isinstance(native, tuple)
    assert native == ("a", "b")


def test_cty_to_native_with_non_cty_value() -> None:
    assert cty_to_native("hello") == "hello"
    assert cty_to_native(123) == 123
    assert cty_to_native(None) is None


def test_cty_to_native_with_dynamic_value() -> None:
    # Test with a CtyValue wrapping a primitive
    dynamic_type = CtyDynamic()
    cty_val = dynamic_type.validate("hello")
    native = cty_to_native(cty_val)
    assert native == "hello"

    # Test with a CtyValue wrapping a collection
    list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
    cty_val_dynamic_list = dynamic_type.validate(list_val)
    native_list = cty_to_native(cty_val_dynamic_list)
    assert native_list == ["a", "b"]


def test_cty_to_native_with_decimal() -> None:
    # Test integer conversion
    cty_val_int = CtyNumber().validate(Decimal("123"))
    native_int = cty_to_native(cty_val_int)
    assert isinstance(native_int, int)
    assert native_int == 123

    # Test float conversion
    cty_val_float = CtyNumber().validate(Decimal("123.45"))
    native_float = cty_to_native(cty_val_float)
    assert isinstance(native_float, float)
    assert native_float == 123.45


class TestCtyToNativeCorrectness:
    """
    This test suite verifies the contract that `cty_to_native` ALWAYS returns
    a structure containing exclusively native Python types, with no residual
    CtyValue objects, especially in complex cases with CtyDynamic.
    """

    def test_cty_to_native_with_dynamic_values_in_list(self) -> None:
        # GIVEN a CtyList containing CtyDynamic values that wrap other CtyValues.
        list_type = CtyList(element_type=CtyDynamic())

        # Create a list with a mix of types wrapped in CtyDynamic.
        validated_list = list_type.validate(
            [
                CtyString().validate("a"),
                CtyNumber().validate(123),
                CtyBool().validate(True),
                # A nested object, which will also be wrapped dynamically
                CtyObject(attribute_types={"key": CtyString()}).validate({"key": "value"}),
            ]
        )

        # WHEN we convert this list to its native representation.
        native_result = cty_to_native(validated_list)

        # THEN the result must be a pure Python list of pure Python types.
        assert isinstance(native_result, list)
        assert native_result[0] == "a"
        assert native_result[1] == 123
        assert native_result[2] is True
        assert isinstance(native_result[3], dict)
        assert native_result[3]["key"] == "value"

    def test_cty_to_native_with_nested_dynamic_value(self) -> None:
        # GIVEN a complex structure with a CtyDynamic value nested inside.
        obj_type = CtyObject(
            attribute_types={
                "id": CtyNumber(),
                "data": CtyDynamic(),  # The dynamic part
            }
        )

        # The value for 'data' is another CtyValue.
        inner_value = CtyList(element_type=CtyString()).validate(["x", "y", "z"])

        validated_obj = obj_type.validate({"id": 1, "data": inner_value})

        # WHEN we convert to native.
        native_result = cty_to_native(validated_obj)

        # THEN the entire structure must be native.
        assert isinstance(native_result, dict)
        assert native_result["id"] == 1
        assert isinstance(native_result["data"], list)
        assert native_result["data"] == ["x", "y", "z"]


# 🌊🪢🔚
