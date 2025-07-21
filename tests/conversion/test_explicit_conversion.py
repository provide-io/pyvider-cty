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
            # --- To String ---
            (CtyValue(CtyNumber(), 123), CtyString(), "123"),
            (CtyValue(CtyNumber(), 123.45), CtyString(), "123.45"),
            (CtyValue(CtyBool(), True), CtyString(), "true"),
            (CtyValue(CtyBool(), False), CtyString(), "false"),
            # --- To Number ---
            (CtyValue(CtyString(), "123"), CtyNumber(), 123),
            (CtyValue(CtyString(), "123.45"), CtyNumber(), 123.45),
            (CtyValue(CtyString(), "-1.5e2"), CtyNumber(), -150),
            # --- To Bool ---
            (CtyValue(CtyString(), "true"), CtyBool(), True),
            (CtyValue(CtyString(), "false"), CtyBool(), False),
            (CtyValue(CtyString(), "TRUE"), CtyBool(), True),
            # --- Collection to Collection ---
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
                [CtyValue(CtyString(), "a"), CtyValue(CtyNumber(), 1)],
            ),
            # --- To Dynamic ---
            (CtyValue(CtyNumber(), 42), CtyDynamic(), CtyValue(CtyNumber(), 42)),
            # --- Special Values ---
            (CtyValue.null(CtyString()), CtyNumber(), None),
            (CtyValue.unknown(CtyString()), CtyNumber(), None),
        ],
        ids=[
            "num_to_str",
            "float_to_str",
            "true_to_str",
            "false_to_str",
            "str_to_num",
            "str_to_float",
            "str_exp_to_num",
            "str_true_to_bool",
            "str_false_to_bool",
            "str_TRUE_to_bool",
            "list_to_set",
            "set_to_list",
            "tuple_to_list_dynamic",
            "num_to_dynamic",
            "null_str_to_num",
            "unknown_str_to_num",
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
        ids=[
            "str_to_num_fail",
            "str_to_bool_fail",
            "num_to_bool_fail",
            "obj_to_list_fail",
            "list_str_to_list_num_fail",
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
            # --- Existing Passing Tests ---
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
            # --- NEW TDD TESTS FOR ADVANCED OBJECT UNIFICATION ---
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
                    CtyObject({"a": CtyString()}), # a is required
                    CtyObject({"a": CtyString(), "b": CtyNumber()}, optional_attributes={"b"}),
                ],
                CtyObject({"a": CtyString()}), # a remains required
            ),
            (
                [
                    CtyObject({"a": CtyString()}), # a is required
                    CtyObject({"a": CtyString()}, optional_attributes={"a"}), # a is optional
                ],
                CtyObject({"a": CtyString()}, optional_attributes={"a"}), # unified 'a' is optional
            ),
            (
                [
                    CtyObject({"a": CtyString()}, optional_attributes={"a"}),
                    CtyObject({"a": CtyString()}, optional_attributes={"a"}),
                ],
                CtyObject({"a": CtyString()}, optional_attributes={"a"}), # optional + optional -> optional
            ),
            (
                [
                    CtyObject({}),
                    CtyObject({"a": CtyString()}),
                ],
                CtyObject({}), # Intersection with empty object is empty object
            ),
        ],
        ids=[
            "empty_list",
            "single_type",
            "identical_types",
            "different_primitives",
            "identical_lists",
            "lists_of_different_elements",
            "list_and_set",
            "identical_objects",
            "objects_with_different_attrs",
            "tuples_of_different_length",
            # --- NEW TDD TEST IDS ---
            "TDD: objects_with_common_attribute",
            "TDD: objects_with_recursive_unification",
            "TDD: three_objects_with_common_subset",
            "TDD: objects_with_optional_attributes_disjoint",
            "TDD: objects_with_required_and_optional",
            "TDD: objects_with_both_optional",
            "TDD: object_unify_with_empty_object",
        ],
    )
    def test_unification_scenarios(
        self, type_list: Iterable[CtyType], expected_unified_type: CtyType
    ) -> None:
        unified_type = unify(type_list)
        assert unified_type.equal(expected_unified_type)
