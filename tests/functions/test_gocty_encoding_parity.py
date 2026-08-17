#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""jsondecode and csvdecode against go-cty's `json.go` and `csv.go`.

Both used to return a value wrapped in `dynamic`. That is not a cosmetic
difference: the type is what crosses the wire to Terraform, so a decoded
document arrived describing itself as dynamic rather than as the object or
tuple it is.
"""

from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import SIGNATURES, csvdecode, jsondecode, jsonencode
from pyvider.cty.refinement import refine
from pyvider.cty.values.markers import RefinedUnknownValue


def S(v: str) -> object:
    return CtyString().validate(v)


def unknown_string(prefix: str | None = None) -> CtyValue[Any]:
    """An unknown string, optionally already known to start with `prefix`."""
    value = CtyValue.unknown(CtyString())
    if prefix is None:
        return value
    return refine(value).string_prefix_full(prefix).new_value()


def _refinement(value: CtyValue[Any]) -> RefinedUnknownValue:
    assert value.is_unknown
    assert isinstance(value.value, RefinedUnknownValue)
    return value.value


class TestJSONDecodeImpliedType:
    """go-cty's json.ImpliedType: an object becomes an object, an array a tuple."""

    def test_an_object_becomes_an_object_not_a_map(self) -> None:
        decoded = jsondecode(S('{"a": 1, "b": "x"}'))

        assert decoded.type == CtyObject(attribute_types={"a": CtyNumber(), "b": CtyString()})

    def test_an_array_becomes_a_tuple_not_a_list(self) -> None:
        """JSON promises nothing about an array's members sharing a type."""
        decoded = jsondecode(S('[1, "a", true]'))

        assert decoded.type == CtyTuple(element_types=(CtyNumber(), CtyString(), CtyBool()))

    @pytest.mark.parametrize(
        ("document", "expected"),
        [
            ('"x"', CtyString()),
            ("1", CtyNumber()),
            ("1.5", CtyNumber()),
            ("true", CtyBool()),
            ("false", CtyBool()),
        ],
    )
    def test_a_scalar_document(self, document: str, expected: object) -> None:
        assert jsondecode(S(document)).type == expected

    def test_a_null_document_is_dynamic_and_null(self) -> None:
        """A JSON null carries no type information for ImpliedType to read."""
        decoded = jsondecode(S("null"))

        assert decoded.type == CtyDynamic()
        assert decoded.is_null

    def test_a_null_member_is_a_dynamic_attribute(self) -> None:
        decoded = jsondecode(S('{"a": null}'))

        assert decoded.type == CtyObject(attribute_types={"a": CtyDynamic()})

    def test_nesting(self) -> None:
        decoded = jsondecode(S('{"a": {"b": [1, {"c": true}]}}'))

        assert decoded.type == CtyObject(
            attribute_types={
                "a": CtyObject(
                    attribute_types={
                        "b": CtyTuple(
                            element_types=(
                                CtyNumber(),
                                CtyObject(attribute_types={"c": CtyBool()}),
                            )
                        )
                    }
                )
            }
        )

    def test_an_empty_object_and_an_empty_array(self) -> None:
        assert jsondecode(S("{}")).type == CtyObject(attribute_types={})
        assert jsondecode(S("[]")).type == CtyTuple(element_types=())

    def test_numbers_do_not_go_through_float64(self) -> None:
        """go-cty decodes into a big.Float; a float64 hop would round first."""
        decoded = jsondecode(S("[0.1234567890123456789012345678901234567890]"))

        assert decoded[0].value == Decimal("0.1234567890123456789012345678901234567890")

    def test_invalid_json_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError, match="failed to decode JSON"):
            jsondecode(S("{not json}"))


class TestCSVDecode:
    def test_the_result_is_a_list_of_objects_of_strings(self) -> None:
        """CSV carries no type information, so go-cty does not infer one."""
        decoded = csvdecode(S("a,b\n1,2"))

        assert decoded.type == CtyList(
            element_type=CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})
        )
        assert decoded.raw_value == [{"a": "1", "b": "2"}]

    def test_a_header_with_no_rows_is_an_empty_list_of_that_type(self) -> None:
        decoded = csvdecode(S("a,b"))

        assert decoded.type == CtyList(
            element_type=CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})
        )
        assert decoded.raw_value == []

    def test_quoted_fields(self) -> None:
        assert csvdecode(S('a,b\n"x,y",2')).raw_value == [{"a": "x,y", "b": "2"}]

    def test_blank_lines_are_skipped(self) -> None:
        """Go's csv.Reader drops them; Python's hands back an empty record."""
        assert csvdecode(S("a,b\n1,2\n\n3,4")).raw_value == [
            {"a": "1", "b": "2"},
            {"a": "3", "b": "4"},
        ]

    def test_no_header_line(self) -> None:
        with pytest.raises(CtyFunctionError, match="missing header line"):
            csvdecode(S(""))

    def test_a_duplicate_column_name(self) -> None:
        with pytest.raises(CtyFunctionError, match="duplicate column name"):
            csvdecode(S("a,a\n1,2"))

    @pytest.mark.parametrize("document", ["a,b\n1", "a,b\n1,2,3", "a,b\n1,2\n3"])
    def test_a_ragged_row(self, document: str) -> None:
        """Go fixes FieldsPerRecord from the header, so a short row is an error."""
        with pytest.raises(CtyFunctionError, match="wrong number of fields"):
            csvdecode(S(document))


class TestTheReturnTypeComesFromTheValue:
    """The two functions whose return type is decided by an argument's *value*.

    New on 2026-08-17. go-cty's `Type` callback takes values rather than types
    precisely so that these two can exist (`function.go:78` says so, naming a
    JSON decoder), and until the framework landed this package had no way to
    answer the question at all -- the type was only discoverable by making the
    call. `csv.go:21` and `json.go:78`.
    """

    def test_the_columns_of_the_csv_decide_the_type_before_any_row_is_read(self) -> None:
        predicted = SIGNATURES["csvdecode"].return_type_for_values([S("a,b\n1,2")])

        assert predicted == CtyList(
            element_type=CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})
        )

    def test_the_shape_of_the_json_decides_the_type(self) -> None:
        assert SIGNATURES["jsondecode"].return_type_for_values([S('{"a": 1}')]) == CtyObject(
            attribute_types={"a": CtyNumber()}
        )

    def test_an_unknown_document_has_no_decided_type(self) -> None:
        """Both answer dynamic rather than reading a value that is not there."""
        assert SIGNATURES["csvdecode"].return_type_for_values([unknown_string()]) == CtyDynamic()
        assert SIGNATURES["jsondecode"].return_type_for_values([unknown_string()]) == CtyDynamic()
        assert SIGNATURES["jsondecode"].return_type([CtyString()]) == CtyDynamic()

    @pytest.mark.parametrize(
        ("prefix", "expected"),
        [
            ('"', CtyString()),
            ("t", CtyBool()),
            ("f", CtyBool()),
            ("-1", CtyNumber()),
            ("0", CtyNumber()),
            (".5", CtyNumber()),
            ("  \n 12", CtyNumber()),
            ("{", CtyDynamic()),
            ("[", CtyDynamic()),
            ("n", CtyDynamic()),
            ("", CtyDynamic()),
        ],
    )
    def test_a_refined_prefix_can_decide_the_type_of_an_unknown_document(
        self, prefix: str, expected: CtyType[Any]
    ) -> None:
        """One known character is enough for three of the five JSON productions.

        go-cty reads the refinement rather than giving up (`json.go:79`): a
        leading quote means a string or a syntax error and nothing else, `t`/`f`
        a bool, a digit or sign a number. An object or an array says nothing --
        the attributes and the length are still undecided -- and `n` opens
        `null`, which has no type of its own.
        """
        result = jsondecode(unknown_string(prefix))

        assert result.is_unknown
        assert result.type == expected

    def test_a_prefix_that_cannot_open_a_json_document_is_refused_early(self) -> None:
        """No other character can begin a JSON value, so the call fails now.

        Reported before the string is ever known, which is the point: a plan
        that cannot possibly succeed should not wait for apply to say so.
        """
        with pytest.raises(CtyFunctionError, match="cannot begin with the character 'z'"):
            jsondecode(unknown_string("zz"))

    def test_jsondecode_promises_nothing_about_a_deferred_answer(self) -> None:
        """`jsondecode` is go-cty's one decoder without `refineNonNull`.

        `jsondecode("null")` is a null, so not-null is exactly what this
        function cannot promise -- and `json.go:71` accordingly declares no
        `RefineResult` where `csv.go:45` and `jsonencode` both do.
        """
        assert jsondecode(unknown_string()).value is not None
        assert not isinstance(jsondecode(unknown_string()).value, RefinedUnknownValue)


def test_a_deferred_csvdecode_carries_no_refinement() -> None:
    """go-cty does not refine an unknown that has no type yet.

    `csv.go:45` declares `RefineResult: refineNonNull`, so this migration
    declares it too -- but `csvdecode`'s only unknown result is an unknown of
    *dynamic* type, because the columns are unknowable until the document is,
    and go-cty's `Call` refines a result only `if val.IsKnown() ||
    val.Type() != cty.DynamicPseudoType` (`function.go:281`): there is no type
    for a refinement to be about. The oracle bears that out --
    `csvdecode(unknown)` reports no `refine` at all -- and the difference is
    visible on the wire, `d4 00 00` against a msgpack ext 12 payload.

    This began as a strict xfail on 2026-08-17: the framework gated its
    refinement on whether an *argument* was dynamically typed rather than on the
    result, so the guard never fired for a function whose return type is the
    dynamic one. `_function.py` was fixed the same day and this became an
    ordinary assertion.
    """
    assert not isinstance(csvdecode(unknown_string()).value, RefinedUnknownValue)


class TestJSONEncodeDeferral:
    """What `jsonencode` still promises when it cannot encode. `json.go:26`."""

    def test_a_value_holding_an_unknown_promises_its_opening_character(self) -> None:
        partial = CtyList(element_type=CtyString()).validate(["a", CtyValue.unknown(CtyString())])

        refined = _refinement(jsonencode(partial))

        assert refined.string_prefix == "["
        assert refined.is_known_null is False

    def test_an_unknown_that_could_be_null_promises_no_prefix(self) -> None:
        """Asserted the opposite until 2026-08-17, and unsoundly.

        This package refined the result of `jsonencode(unknown string)` with the
        prefix `"`, reasoning from the argument's type alone. But a null string
        encodes as the four characters `null`, so a value that may still turn
        out to be null promises nothing about the first character -- go-cty
        checks `valRng.CouldBeNull()` first and returns a bare unknown
        (`json.go:34`). The oracle agrees: `is_known_null: false` and no prefix.
        """
        refined = _refinement(jsonencode(unknown_string()))

        assert refined.string_prefix is None
        assert refined.is_known_null is False

    def test_an_unknown_already_known_to_be_non_null_does_promise_one(self) -> None:
        """Nullness settled is the condition go-cty puts on the prefix."""
        refined = _refinement(jsonencode(refine(CtyValue.unknown(CtyString())).not_null().new_value()))

        assert refined.string_prefix == '"'

    def test_a_dynamic_unknown_has_no_type_to_promise_a_prefix_from(self) -> None:
        assert _refinement(jsonencode(CtyValue.unknown(CtyDynamic()))).string_prefix is None


# 🌊🪢🔚
