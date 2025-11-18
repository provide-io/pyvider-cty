#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD Test Suite for the explicit conversion and unification functions.

These tests define the required behavior for the `convert` and `unify`
functions, which are intended to mirror the functionality of the `go-cty/convert`
package. These tests will fail until the functions are implemented in the
`pyvider.cty.conversion.explicit` module."""

from collections.abc import Iterable

import pytest

from pyvider.cty import (
    CtyBool,
    CtyCapsuleWithOps,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.conversion import convert, unify
from pyvider.cty.exceptions import CtyConversionError
from pyvider.cty.marks import CtyMark


class TestConvertFunction:
    """Tests the `convert(value, target_type)` function."""

    @pytest.mark.parametrize(
        "source_val, target_type, expected_val",
        [
            (CtyValue(CtyNumber(), 123), CtyString(), "123"),
            (CtyValue(CtyNumber(), 123.45), CtyString(), "123.45"),
            (CtyValue(CtyBool(), True), CtyString(), "true"),
            (CtyValue(CtyBool(), False), CtyString(), "false"),
            (CtyValue(CtyString(), "123"), CtyNumber(), 123),
            (CtyValue(CtyString(), "123.45"), CtyNumber(), 123.45),
            (CtyValue(CtyString(), "-1.5e2"), CtyNumber(), -150),
            (CtyValue(CtyString(), "true"), CtyBool(), True),
            (CtyValue(CtyString(), "false"), CtyBool(), False),
            (CtyValue(CtyString(), "TRUE"), CtyBool(), True),
            (
                CtyValue(CtyList(element_type=CtyString()), ["a", "b"]),
                CtySet(element_type=CtyString()),
                CtySet(element_type=CtyString()).validate(["a", "b"]),
            ),
            (
                CtyValue(CtySet(element_type=CtyString()), {"a", "b"}),
                CtyList(element_type=CtyString()),
                ["a", "b"],
            ),
            (
                CtyValue(CtyTuple(element_types=(CtyString(), CtyNumber())), ("a", 1)),
                CtyList(element_type=CtyDynamic()),
                [CtyDynamic().validate("a"), CtyDynamic().validate(1)],
            ),
            (CtyValue(CtyNumber(), 42), CtyDynamic(), CtyValue(CtyNumber(), 42)),
            (CtyValue.null(CtyString()), CtyNumber(), None),
            (CtyValue.unknown(CtyString()), CtyNumber(), None),
        ],
    )
    def test_successful_conversions(
        self, source_val: CtyValue, target_type: CtyType, expected_val: object
    ) -> None:
        converted_val = convert(source_val, target_type)
        if isinstance(target_type, CtyDynamic):
            assert converted_val == source_val
            return
        assert converted_val.type.equal(target_type)
        if source_val.is_null:
            assert converted_val.is_null
        elif source_val.is_unknown:
            assert converted_val.is_unknown
        elif isinstance(target_type, CtySet):
            assert converted_val == expected_val
        elif isinstance(target_type, CtyList) and isinstance(source_val.type, CtySet):
            assert isinstance(converted_val.value, tuple)
            assert len(converted_val.value) == len(expected_val)
            assert {v.value for v in converted_val.value} == set(expected_val)
        elif isinstance(target_type, CtyList) and isinstance(source_val.type, CtyTuple):
            assert list(converted_val.value) == expected_val
        else:
            assert converted_val.raw_value == expected_val

    @pytest.mark.parametrize(
        "source_val, target_type",
        [
            (CtyValue(CtyString(), "not-a-number"), CtyNumber()),
            (CtyValue(CtyString(), "yes"), CtyBool()),
            (CtyValue(CtyNumber(), 1), CtyBool()),
            (CtyValue(CtyObject({}), {}), CtyList(element_type=CtyDynamic())),
            (
                CtyValue(CtyList(element_type=CtyString()), ["a"]),
                CtyList(element_type=CtyNumber()),
            ),
        ],
    )
    def test_failed_conversions(self, source_val: CtyValue, target_type: CtyType) -> None:
        with pytest.raises(CtyConversionError):
            convert(source_val, target_type)

    def test_conversion_preserves_marks(self) -> None:
        marked_val = CtyValue(CtyNumber(), 123).mark(CtyMark("sensitive"))
        converted_val = convert(marked_val, CtyString())
        assert converted_val.has_mark(CtyMark("sensitive"))
        assert converted_val.value == "123"

    def test_convert_list_to_list_same_type(self) -> None:
        list_val = CtyValue(CtyList(element_type=CtyString()), ["a", "b"])
        converted_val = convert(list_val, CtyList(element_type=CtyString()))
        assert converted_val is list_val

    def test_convert_list_to_list_of_dynamic(self) -> None:
        list_val = CtyValue(CtyList(element_type=CtyString()), ["a", "b"])
        converted_val = convert(list_val, CtyList(element_type=CtyDynamic()))
        assert converted_val.type.equal(CtyList(element_type=CtyDynamic()))
        assert len(converted_val.value) == 2
        assert converted_val.value[0].type.equal(CtyDynamic())
        assert converted_val.value[0].value.type.equal(CtyString())

    def test_capsule_conversion(self) -> None:
        class MyType:
            def __init__(self, value) -> None:
                self.value = value

        def convert_my_type(raw, target_type):
            if target_type.equal(CtyString()):
                return CtyString().validate(str(raw.value))
            return None

        capsule_type = CtyCapsuleWithOps(
            "MyType",
            MyType,
            convert_fn=convert_my_type,
        )

        val = CtyValue(capsule_type, MyType(123))
        converted = convert(val, CtyString())
        assert converted.type.equal(CtyString())
        assert converted.raw_value == "123"

        with pytest.raises(CtyConversionError):
            convert(val, CtyNumber())

        def bad_converter_non_cty(raw, target_type) -> str:
            return "not a cty value"

        capsule_type_bad_converter = CtyCapsuleWithOps(
            "MyType",
            MyType,
            convert_fn=bad_converter_non_cty,
        )
        val_bad = CtyValue(capsule_type_bad_converter, MyType(123))
        with pytest.raises(CtyConversionError, match="non-CtyValue"):
            convert(val_bad, CtyString())

        def bad_converter_wrong_type(raw, target_type):
            return CtyNumber().validate(123)

        capsule_type_wrong_type = CtyCapsuleWithOps(
            "MyType",
            MyType,
            convert_fn=bad_converter_wrong_type,
        )
        val_wrong = CtyValue(capsule_type_wrong_type, MyType(123))
        with pytest.raises(CtyConversionError, match="wrong type"):
            convert(val_wrong, CtyString())


class TestUnifyFunction:
    """Tests the `unify(types)` function."""

    @pytest.mark.parametrize(
        "type_list, expected_unified_type",
        [
            ([], CtyDynamic()),
            ([CtyString()], CtyString()),
            ([CtyString(), CtyString()], CtyString()),
            ([CtyString(), CtyNumber()], CtyDynamic()),
            (
                [CtyList(element_type=CtyString()), CtyList(element_type=CtyString())],
                CtyList(element_type=CtyString()),
            ),
            (
                [CtyList(element_type=CtyString()), CtyList(element_type=CtyNumber())],
                CtyList(element_type=CtyDynamic()),
            ),
            (
                [CtyList(element_type=CtyString()), CtySet(element_type=CtyString())],
                CtyDynamic(),
            ),
            (
                [CtyObject({"a": CtyString()}), CtyObject({"a": CtyString()})],
                CtyObject({"a": CtyString()}),
            ),
            (
                [CtyObject({"a": CtyString()}), CtyObject({"b": CtyString()})],
                CtyDynamic(),
            ),
            (
                [CtyTuple((CtyString(),)), CtyTuple((CtyString(), CtyNumber()))],
                CtyDynamic(),
            ),
            (
                [
                    CtyObject({"a": CtyString(), "b": CtyNumber()}),
                    CtyObject({"a": CtyString(), "c": CtyBool()}),
                ],
                CtyDynamic(),
            ),
            (
                [
                    CtyObject({"common": CtyString()}),
                    CtyObject({"common": CtyNumber()}),
                ],
                CtyObject({"common": CtyDynamic()}),
            ),
            (
                [
                    CtyObject({"a": CtyString(), "b": CtyNumber()}),
                    CtyObject({"a": CtyString(), "b": CtyNumber(), "c": CtyBool()}),
                    CtyObject({"a": CtyString(), "b": CtyNumber(), "d": CtyString()}),
                ],
                CtyDynamic(),
            ),
            (
                [
                    CtyObject({"a": CtyString()}),
                    CtyObject({"a": CtyString(), "b": CtyNumber()}, optional_attributes={"b"}),
                ],
                CtyDynamic(),
            ),
            (
                [
                    CtyObject({"a": CtyString()}),
                    CtyObject({"a": CtyString()}, optional_attributes={"a"}),
                ],
                CtyObject({"a": CtyString()}, optional_attributes={"a"}),
            ),
            (
                [
                    CtyObject({"a": CtyString()}, optional_attributes={"a"}),
                    CtyObject({"a": CtyString()}, optional_attributes={"a"}),
                ],
                CtyObject({"a": CtyString()}, optional_attributes={"a"}),
            ),
            (
                [
                    CtyObject({}),
                    CtyObject({"a": CtyString()}),
                ],
                CtyDynamic(),
            ),
        ],
    )
    def test_unification_scenarios(self, type_list: Iterable[CtyType], expected_unified_type: CtyType) -> None:
        unified_type = unify(type_list)
        assert unified_type.equal(expected_unified_type)


# 🌊🪢🔚
