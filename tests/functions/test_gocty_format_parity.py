#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `format` and `formatlist`.

Every expectation here was taken from a differential run against the oracle
rather than from reading `format.go`: a 455-case matrix of 35 templates against
13 argument values. The first run of it agreed on 420, and the 35 it did not are
the reason the number formatting below looks the way it does -- Python and Go
disagree about exponent width, about when `%g` switches to exponent form, and
about where the sign goes relative to zero padding.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import format_fn, formatlist


def s(text: str) -> CtyValue[Any]:
    return CtyString().validate(text)


def n(value: Any) -> CtyValue[Any]:
    return CtyNumber().validate(value)


def strings(values: list[str]) -> CtyValue[Any]:
    return CtyList(element_type=CtyString()).validate(values)


def rendered(template: str, *arguments: CtyValue[Any]) -> str:
    return str(format_fn(s(template), *arguments).value)


class TestVerbs:
    @pytest.mark.parametrize(
        ("template", "argument", "expected"),
        [
            ("%s", s("hi"), "hi"),
            ("%q", s('a"b'), '"a\\"b"'),
            ("%t", CtyBool().validate(True), "true"),
            ("%t", CtyBool().validate(False), "false"),
            ("%d", n(42), "42"),
            ("%b", n(5), "101"),
            ("%o", n(64), "100"),
            ("%x", n(255), "ff"),
            ("%X", n(255), "FF"),
            ("%f", n("3.14159"), "3.141590"),
        ],
        ids=str,
    )
    def test_a_verb_renders_as_go_does(self, template: str, argument: CtyValue[Any], expected: str) -> None:
        assert rendered(template, argument) == expected

    def test_v_uses_the_type_to_choose_a_format(self) -> None:
        """String as-is, number as `%g`, everything else as JSON."""
        assert rendered("%v", s("hi")) == "hi"
        assert rendered("%v", n(42)) == "42"
        assert rendered("%v", CtyBool().validate(True)) == "true"
        assert rendered("%v", strings(["a"])) == '["a"]'

    def test_sharp_v_is_always_json(self) -> None:
        assert rendered("%#v", s("hi")) == '"hi"'
        assert rendered("%#v", n("0.00001")) == "0.00001"

    def test_only_v_accepts_a_null(self) -> None:
        """A null renders as the JSON keyword; anything else is an error."""
        assert rendered("%v", CtyValue.null(CtyString())) == "null"

        with pytest.raises(CtyFunctionError):
            format_fn(s("%s"), CtyValue.null(CtyString()))

    def test_an_unsupported_verb_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError):
            format_fn(s("%z"), s("a"))


class TestNumberRendering:
    """The half of this port that a reading of the source would have got wrong."""

    def test_the_exponent_is_always_at_least_two_digits(self) -> None:
        """Go writes `e+01`; Python's `Decimal.__format__` writes `e+1`."""
        assert rendered("%e", n(42)) == "4.200000e+01"
        assert rendered("%E", n("0.00001")) == "1.000000E-05"
        assert rendered("%.3e", n(0)) == "0.000e+00"

    def test_g_switches_to_exponent_form_the_way_go_does(self) -> None:
        assert rendered("%g", n("0.00001")) == "1e-05"
        assert rendered("%.5g", n("0.00001")) == "1e-05"
        assert rendered("%G", n("1e21")) == "1E+21"

    def test_the_sign_sits_outside_the_zero_padding(self) -> None:
        """`%08.2f` of -42 is `-0042.00`; padding the signed text gives `00-42.00`."""
        assert rendered("%08.2f", n(-42)) == "-0042.00"
        assert rendered("%05d", n(42)) == "00042"
        assert rendered("%+d", n(42)) == "+42"

    def test_an_integer_verb_requires_a_whole_number(self) -> None:
        with pytest.raises(CtyFunctionError):
            format_fn(s("%d"), n("1.5"))

    def test_a_value_that_cannot_convert_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError):
            format_fn(s("%d"), s("nope"))


class TestWidthAndPrecision:
    def test_width_pads_and_minus_pads_the_other_way(self) -> None:
        assert rendered("%5s|", s("ab")) == "   ab|"
        assert rendered("%-5s|", s("ab")) == "ab   |"

    def test_precision_truncates_a_string(self) -> None:
        assert rendered("%.2s", s("hello")) == "he"

    def test_width_and_precision_count_graphemes_not_code_points(self) -> None:
        """Both are measured the way go-cty measures them, in grapheme clusters.

        This test previously asserted the opposite, under a name that said so,
        as a pinned divergence. NFC normalization at construction hides the
        difference wherever a precomposed form exists, which is why it needs a
        cluster that has none -- and precision is where it bites: truncating by
        code point returns a different picture, not a shorter string.
        """
        family = "\U0001f468‍\U0001f469‍\U0001f467"

        assert rendered("%.1s", s(family)) == family
        assert rendered("%5s|", s(family)) == f"    {family}|"

    def test_a_quoted_string_keeps_its_non_ascii_characters(self) -> None:
        """`%q` is Go's `strconv.Quote`, which escapes only what it must.

        `json.dumps` defaults to `ensure_ascii=True`, which turned every
        non-ASCII string into a wall of \\uXXXX -- still valid JSON, and not
        what go-cty emits.
        """
        assert rendered("%q", s("héllo")) == '"héllo"'
        assert rendered("%q", s('a"b')) == '"a\\"b"'


class TestArgumentIndexing:
    def test_arguments_are_consumed_in_order(self) -> None:
        assert rendered("%s%s", s("a"), s("b")) == "ab"

    def test_an_explicit_index_selects_and_then_continues_from_there(self) -> None:
        assert rendered("%[2]s%[1]s", s("a"), s("b")) == "ba"

    def test_a_doubled_percent_consumes_no_argument(self) -> None:
        assert rendered("100%%") == "100%"

    def test_too_few_arguments_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError):
            format_fn(s("%s%s"), s("a"))

    def test_an_unused_argument_is_refused(self) -> None:
        """The caller believes it is being printed, so silence would be worse."""
        with pytest.raises(CtyFunctionError):
            format_fn(s("%s"), s("a"), s("b"))
        with pytest.raises(CtyFunctionError):
            format_fn(s("hi"), s("a"))


class TestFormatList:
    def test_sequences_are_iterated_in_lockstep(self) -> None:
        assert [
            element.value for element in formatlist(s("%s%s"), strings(["a", "b"]), strings(["1", "2"])).value
        ] == [
            "a1",
            "b2",
        ]

    def test_a_scalar_is_reused_on_every_iteration(self) -> None:
        result = formatlist(s("%s-%s"), strings(["a", "b"]), s("x"))

        assert [element.value for element in result.value] == ["a-x", "b-x"]

    def test_all_scalars_produce_exactly_one_row(self) -> None:
        assert [element.value for element in formatlist(s("%s"), s("a")).value] == ["a"]
        assert [element.value for element in formatlist(s("hi")).value] == ["hi"]

    def test_an_empty_sequence_produces_an_empty_list(self) -> None:
        assert list(formatlist(s("%s"), strings([])).value) == []

    def test_sequences_must_agree_on_length(self) -> None:
        with pytest.raises(CtyFunctionError, match="inconsistent"):
            formatlist(s("%s%s"), strings(["a", "b"]), strings(["1"]))

    def test_a_set_is_iterated_in_canonical_order(self) -> None:
        """`list(frozenset)` yields whatever the hash table does.

        This returned `["b", "a"]` for a set of "a" and "b", which is not
        wrong so much as unrepeatable -- and go-cty iterates its sets in a
        defined order.
        """
        result = formatlist(s("%s"), CtySet(element_type=CtyString()).validate(["a", "b"]))

        assert [element.value for element in result.value] == ["a", "b"]

    def test_a_tuple_is_a_sequence_too(self) -> None:
        pair = CtyTuple(element_types=(CtyString(), CtyNumber())).validate(("a", 1))

        result = formatlist(s("%s%s"), pair, s("z"))

        assert [element.value for element in result.value] == ["az", "1z"]

    def test_an_unknown_argument_yields_an_unknown_list(self) -> None:
        result = formatlist(s("%s"), CtyValue.unknown(CtyList(element_type=CtyString())))

        assert result.is_unknown
        assert result.type.equal(CtyList(element_type=CtyString()))


class TestEdges:
    """Paths a well-behaved format string never reaches."""

    def test_a_malformed_verb_is_refused(self) -> None:
        """A period with no digits after it is not a precision."""
        with pytest.raises(CtyFunctionError):
            format_fn(s("%.f"), n(1))
        with pytest.raises(CtyFunctionError):
            format_fn(s("%"), n(1))

    def test_a_null_format_string_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError):
            format_fn(CtyValue.null(CtyString()), s("a"))
        with pytest.raises(CtyFunctionError):
            formatlist(CtyValue.null(CtyString()), s("a"))

    def test_rounding_that_carries_bumps_the_exponent(self) -> None:
        """9.99 to one decimal is 1.0e+01, not 10.0e+00."""
        assert rendered("%.1e", n("9.99")) == "1.0e+01"
        assert rendered("%.2e", n("0.0000999")) == "9.99e-05"

    def test_a_sign_flag_applies_to_floats_as_well_as_integers(self) -> None:
        assert rendered("%+.1f", n("1.5")) == "+1.5"
        assert rendered("% .1f", n("1.5")) == " 1.5"
        assert rendered("%+.1f", n("-1.5")) == "-1.5"

    def test_zero_precision_on_g_keeps_one_significant_digit(self) -> None:
        assert rendered("%.0g", n("123")) == "1e+02"

    def test_a_non_finite_number_renders_as_itself(self) -> None:
        assert rendered("%v", n(Decimal("Infinity"))) == "Infinity"
        assert rendered("%g", n(Decimal("NaN"))) == "NaN"

    def test_a_nested_number_renders_without_an_exponent(self) -> None:
        """`%v` falls back to JSON, whose encoder never uses exponent form.

        A bare number was special-cased from the start; one inside a collection
        went through Python's float repr and came out `[1e-05]`.
        """
        assert rendered("%v", CtyList(element_type=CtyNumber()).validate(["0.00001"])) == "[0.00001]"
        assert (
            rendered("%v", CtyObject(attribute_types={"a": CtyNumber()}).validate({"a": "0.00001"}))
            == '{"a":0.00001}'
        )

    def test_json_keys_are_sorted_and_sets_are_canonically_ordered(self) -> None:
        both = CtyObject(attribute_types={"b": CtyString(), "a": CtyString()}).validate({"a": "1", "b": "2"})

        assert rendered("%v", both) == '{"a":"1","b":"2"}'
        assert rendered("%v", CtySet(element_type=CtyString()).validate(["b", "a"])) == '["a","b"]'


class TestUnknowns:
    def test_an_unknown_argument_makes_the_result_unknown(self) -> None:
        assert format_fn(s("%s"), CtyValue.unknown(CtyString())).is_unknown

    def test_an_unknown_template_makes_the_result_unknown(self) -> None:
        assert format_fn(CtyValue.unknown(CtyString()), s("a")).is_unknown

    def test_a_sequence_holding_an_unknown_is_resolved_row_by_row(self) -> None:
        """go-cty resolves this row by row, and now so does this package.

        This asserted the opposite until 2026-08-17: `CtyList.validate` marked
        the whole list unknown if any element was, so a partially-known list
        never arrived here as one and the per-row branch was unreachable
        through the public API. With the container no longer taking its
        unknown-ness from its elements, the known rows are formatted and only
        the undecided row stays undecided -- go-cty's `FormatList` answer.
        """
        partial = CtyList(element_type=CtyString()).validate(["a", CtyValue.unknown(CtyString())])

        assert not partial.is_unknown
        result = formatlist(s("%s!"), partial)

        assert not result.is_unknown
        formatted, deferred = result.value
        assert formatted.value == "a!"
        assert deferred.is_unknown

    def test_an_unknown_nested_inside_a_collection_counts(self) -> None:
        """`%v` prints a collection as JSON, which needs it wholly known."""
        partial = CtyObject(attribute_types={"a": CtyString()}).validate({"a": CtyValue.unknown(CtyString())})

        assert format_fn(s("%v"), partial).is_unknown


# 🌊🪢🔚
