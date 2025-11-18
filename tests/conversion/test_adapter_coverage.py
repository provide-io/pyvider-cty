#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TODO: Add module docstring."""

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
    CtyValue,
)
from pyvider.cty.conversion.adapter import cty_to_native


class TestAdapterCoverage:
    def test_cty_to_native_unknown_returns_none(self) -> None:
        """
        Verifies that converting an unknown CtyValue to a native type
        gracefully returns None instead of raising an error.
        """
        unknown_val = CtyValue.unknown(CtyString())
        assert cty_to_native(unknown_val) is None

    def test_cty_to_native_already_native(self) -> None:
        assert cty_to_native(123) == 123
        assert cty_to_native("hello") == "hello"
        assert cty_to_native(True) is True
        assert cty_to_native(None) is None

    def test_cty_to_native_nested_collections(self) -> None:
        # GIVEN a complex nested structure
        obj_type = CtyObject(
            {
                "a": CtyList(element_type=CtyMap(element_type=CtyNumber())),
                "b": CtySet(element_type=CtyTuple(element_types=(CtyString(), CtyBool()))),
            }
        )
        cty_val = obj_type.validate(
            {
                "a": [{"x": 1, "y": 2}, {"z": 3}],
                "b": [("foo", True), ("bar", False)],
            }
        )

        # WHEN converting to native
        native = cty_to_native(cty_val)

        # THEN the structure is correct and contains only native types
        assert native == {
            "a": [{"x": 1, "y": 2}, {"z": 3}],
            "b": sorted([("bar", False), ("foo", True)]),
        }

    def test_cty_to_native_with_set_and_tuple(self) -> None:
        # Test with Set
        set_type = CtySet(element_type=CtyNumber())
        cty_set = set_type.validate({1, 2, 3})
        native_set = cty_to_native(cty_set)
        assert isinstance(native_set, list)  # Sets become sorted lists
        assert native_set == [1, 2, 3]

        # Test with Tuple
        tuple_type = CtyTuple(element_types=(CtyString(), CtyNumber()))
        cty_tuple = tuple_type.validate(["a", 1])
        native_tuple = cty_to_native(cty_tuple)
        assert isinstance(native_tuple, tuple)
        assert native_tuple == ("a", 1)

    def test_cty_to_native_with_repeated_values(self) -> None:
        # GIVEN a structure with repeated CtyValue instances
        inner_val = CtyString().validate("repeated")
        obj_type = CtyObject({"a": CtyString(), "b": CtyString()})
        cty_val = CtyValue(obj_type, {"a": inner_val, "b": inner_val})

        # WHEN converting to native
        native = cty_to_native(cty_val)

        # THEN the conversion handles the repeated value correctly
        assert native == {"a": "repeated", "b": "repeated"}

    def test_cty_to_native_malformed_list(self) -> None:
        list_type = CtyList(element_type=CtyString())
        # Create a CtyValue with a non-iterable internal value
        malformed_value = CtyValue(list_type, 123)
        # Expect it to be converted to an empty list
        assert cty_to_native(malformed_value) == []

    def test_cty_to_native_malformed_set(self) -> None:
        set_type = CtySet(element_type=CtyString())
        # Create a CtyValue with a non-iterable internal value
        malformed_value = CtyValue(set_type, 123)
        # Expect it to be converted to an empty list
        assert cty_to_native(malformed_value) == []

    def test_cty_to_native_malformed_tuple(self) -> None:
        tuple_type = CtyTuple(element_types=(CtyString(),))
        # Create a CtyValue with a non-iterable internal value
        malformed_value = CtyValue(tuple_type, 123)
        # Expect it to be converted to an empty tuple
        assert cty_to_native(malformed_value) == ()

    def test_cty_to_native_malformed_object(self) -> None:
        obj_type = CtyObject({"a": CtyString()})
        # Create a CtyValue with a non-iterable internal value
        malformed_value = CtyValue(obj_type, 123)
        # Expect it to be converted to an empty dict
        assert cty_to_native(malformed_value) == {}

    def test_cty_to_native_with_set(self) -> None:
        set_type = CtySet(element_type=CtyString())
        cty_val = set_type.validate({"a", "b", "c"})
        native = cty_to_native(cty_val)
        assert isinstance(native, list)
        assert sorted(native) == ["a", "b", "c"]

    def test_cty_to_native_with_dynamic_value(self) -> None:
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

    def test_cty_to_native_primitive(self) -> None:
        val = CtyNumber().validate(123)
        native = cty_to_native(val)
        assert native == 123


# 🌊🪢🔚
