"""
TDD Test Suite for the explicit conversion and unification functions.

These tests define the required behavior for the `convert` and `unify`
functions, which are intended to mirror the functionality of the `go-cty/convert`
package. These tests will fail until the functions are implemented in the
`pyvider.cty.conversion.explicit` module.
"""

from collections.abc import Iterable

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
                frozenset([CtyValue(CtyString(), "a"), CtyValue(CtyString(), "b")]),
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
            assert converted_val.value == expected_val
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
    def test_failed_conversions(
        self, source_val: CtyValue, target_type: CtyType
    ) -> None:
        with pytest.raises(CtyConversionError):
            convert(source_val, target_type)

    def test_conversion_preserves_marks(self) -> None:
        marked_val = CtyValue(CtyNumber(), 123).mark(CtyMark("sensitive"))
        converted_val = convert(marked_val, CtyString())
        assert converted_val.has_mark(CtyMark("sensitive"))
        assert converted_val.value == "123"


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
                CtyObject({"a": CtyString()}),
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
                CtyObject({"a": CtyString(), "b": CtyNumber()}),
            ),
            (
                [
                    CtyObject({"a": CtyString()}),
                    CtyObject({"a": CtyString(), "b": CtyNumber()}, optional_attributes={"b"}),
                ],
                CtyObject({"a": CtyString()}),
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
                CtyObject({}),
            ),
        ],
    )
    def test_unification_scenarios(
        self, type_list: Iterable[CtyType], expected_unified_type: CtyType
    ) -> None:
        unified_type = unify(type_list)
        assert unified_type.equal(expected_unified_type)
