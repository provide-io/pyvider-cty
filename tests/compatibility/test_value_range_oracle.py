#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`Value.Range`, `Value.Refine` and `ValueRange.Includes`, against real go-cty.

These three landed together from a reading of `cty/value_range.go`, and a
reading is exactly what this replaces. The harness had no command that reached
them -- they are in the cty package rather than the standard library, so no
function call exposes them -- which meant the only thing checking the port was
the port's own account of what go-cty does.

That account was wrong in five places, and each one is a case below. The
pattern is worth naming: every mistake came from believing a docstring over the
code beneath it, or from making the answer *better* than go-cty's. Both produce
a library that behaves differently from the one it claims to reimplement, and
"more precise than the reference" is still a divergence when a caller is porting
a plan-time comparison across the two.
"""

from __future__ import annotations

from decimal import Decimal
import json
from typing import Any

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtySet, CtyString, CtyType, CtyValue
from pyvider.cty.refinement import refine, safe_known_prefix
from pyvider.cty.value_range import value_range
from tests.compatibility._oracle import canonical, rich, run, type_spec

pytestmark = pytest.mark.compat

UNKNOWN_STRING = CtyValue.unknown(CtyString())
UNKNOWN_NUMBER = CtyValue.unknown(CtyNumber())
NUMBERS = CtyList(element_type=CtyNumber())
STRINGS = CtyList(element_type=CtyString())


def _range_from_harness(cty_type: CtyType[Any], value: CtyValue[Any], candidate: Any = None) -> dict[str, Any]:
    args = ["cty", "range", "--type", type_spec(cty_type), json.dumps(rich(value))]
    if candidate is not None:
        args += ["--includes", json.dumps(rich(candidate))]
    result = run(*args)
    assert result["ok"], result
    return result


def _includes_here(value: CtyValue[Any], candidate: CtyValue[Any]) -> dict[str, Any]:
    answer = value_range(value).includes(candidate)
    if not answer.is_unknown:
        return {"known": True, "value": bool(answer.value)}
    return {"known": False, "definitely_not_null": value_range(answer).definitely_not_null()}


class TestNullness:
    @pytest.mark.parametrize(
        ("label", "cty_type", "value"),
        [
            ("unrefined unknown", CtyString(), UNKNOWN_STRING),
            ("not-null unknown", CtyString(), refine(UNKNOWN_STRING).not_null().new_value()),
            ("known value", CtyString(), CtyString().validate("x")),
            ("known null", CtyString(), CtyValue.null(CtyString())),
        ],
    )
    def test_the_two_agree(self, label: str, cty_type: CtyType[Any], value: CtyValue[Any]) -> None:
        theirs = _range_from_harness(cty_type, value)
        here = value_range(value)

        assert here.could_be_null() == theirs["could_be_null"], label
        assert here.definitely_not_null() == theirs["definitely_not_null"], label


class TestStringPrefix:
    @pytest.mark.parametrize(
        ("label", "prefix"),
        [
            ("plain ascii", "ht"),
            ("a whole word", "hello"),
            ("empty", ""),
            # A prefix may end mid-cluster, and the builder is documented to trim
            # it back to a point where appending anything is safe.
            ("ends in a combining base", "é"),
            ("ends in a ZWJ", "a‍"),
        ],
    )
    def test_a_refined_prefix_reads_back_the_same(self, label: str, prefix: str) -> None:
        value = refine(UNKNOWN_STRING).string_prefix(prefix).new_value()
        theirs = _range_from_harness(CtyString(), value)

        assert value_range(value).string_prefix() == theirs["string_prefix"], label

    def test_a_known_string_is_its_own_prefix(self) -> None:
        """go-cty synthesises a range for a known value, prefix and all."""
        value = CtyString().validate("hello")
        theirs = _range_from_harness(CtyString(), value)

        assert value_range(value).string_prefix() == theirs["string_prefix"]

    @pytest.mark.parametrize("prefix", ["hello", "é", "a‍", "\U0001f468‍\U0001f469", ""])
    def test_safe_known_prefix_agrees(self, prefix: str) -> None:
        result = run("cty", "safe-known-prefix", prefix)
        assert result["ok"], result

        assert safe_known_prefix(prefix) == result["prefix"]


class TestNumberBounds:
    @pytest.mark.parametrize(
        ("label", "value"),
        [
            ("unbounded", UNKNOWN_NUMBER),
            ("lower only", refine(UNKNOWN_NUMBER).number_range_lower_bound(3).new_value()),
            (
                "lower exclusive",
                refine(UNKNOWN_NUMBER).number_range_lower_bound(3, inclusive=False).new_value(),
            ),
            ("both", refine(UNKNOWN_NUMBER).number_range_inclusive(1, 10).new_value()),
            ("known number", CtyNumber().validate(5)),
        ],
    )
    def test_bounds_read_back_the_same(self, label: str, value: CtyValue[Any]) -> None:
        theirs = _range_from_harness(CtyNumber(), value)
        here = value_range(value)

        lower, lower_inclusive = here.number_lower_bound()
        upper, upper_inclusive = here.number_upper_bound()

        assert canonical(rich(lower)) == canonical(theirs["number_lower_bound"][0]), f"{label} lower"
        assert lower_inclusive == theirs["number_lower_bound"][1], f"{label} lower inclusive"
        assert canonical(rich(upper)) == canonical(theirs["number_upper_bound"][0]), f"{label} upper"
        assert upper_inclusive == theirs["number_upper_bound"][1], f"{label} upper inclusive"


class TestLengthBounds:
    @pytest.mark.parametrize(
        ("label", "value"),
        [
            ("unbounded", CtyValue.unknown(NUMBERS)),
            ("lower only", refine(CtyValue.unknown(NUMBERS)).collection_length_lower_bound(2).new_value()),
            ("exact", refine(CtyValue.unknown(NUMBERS)).collection_length(3).new_value()),
            ("known list", NUMBERS.validate([1, 2])),
            # A set and a map, added 2026-08-17: the audit found every length
            # bound here rode on a list, so the other two collection kinds'
            # range plumbing was asserted only against a reading of range.go.
            (
                "bounded set",
                refine(CtyValue.unknown(CtySet(element_type=CtyString())))
                .collection_length_lower_bound(1)
                .collection_length_upper_bound(4)
                .new_value(),
            ),
            (
                "bounded map",
                refine(CtyValue.unknown(CtyMap(element_type=CtyNumber())))
                .collection_length_upper_bound(2)
                .new_value(),
            ),
        ],
    )
    def test_length_bounds_read_back_the_same(self, label: str, value: CtyValue[Any]) -> None:
        theirs = _range_from_harness(value.type, value)
        here = value_range(value)

        assert here.length_lower_bound() == theirs["length_lower_bound"], f"{label} lower"

        # go-cty reports an unbounded length as maxint. This library reports -1
        # and says so, which is a deliberate difference in spelling rather than
        # in meaning -- so the comparison is against what the sentinel means.
        if theirs["length_upper_bound_is_maxint"]:
            assert here.length_upper_bound() == -1, f"{label} upper"
        else:
            assert here.length_upper_bound() == theirs["length_upper_bound"], f"{label} upper"


class TestIncludes:
    @pytest.mark.parametrize(
        ("label", "cty_type", "value", "candidate"),
        [
            ("known equals itself", CtyString(), CtyString().validate("hello"), CtyString().validate("hello")),
            ("known differs", CtyString(), CtyString().validate("hello"), CtyString().validate("world")),
            (
                "known string extended",
                CtyString(),
                CtyString().validate("hello"),
                CtyString().validate("hellothere"),
            ),
            ("unrefined unknown", CtyString(), UNKNOWN_STRING, CtyString().validate("x")),
            (
                "prefix admits",
                CtyString(),
                refine(UNKNOWN_STRING).string_prefix("ht").new_value(),
                CtyString().validate("http"),
            ),
            (
                "prefix excludes",
                CtyString(),
                refine(UNKNOWN_STRING).string_prefix("ht").new_value(),
                CtyString().validate("ftp"),
            ),
            (
                "number below the lower bound",
                CtyNumber(),
                refine(UNKNOWN_NUMBER).number_range_lower_bound(3).new_value(),
                CtyNumber().validate(1),
            ),
            (
                "number on an exclusive bound",
                CtyNumber(),
                refine(UNKNOWN_NUMBER).number_range_lower_bound(3, inclusive=False).new_value(),
                CtyNumber().validate(3),
            ),
            (
                "number inside",
                CtyNumber(),
                refine(UNKNOWN_NUMBER).number_range_inclusive(1, 10).new_value(),
                CtyNumber().validate(5),
            ),
            (
                "length too short",
                NUMBERS,
                refine(CtyValue.unknown(NUMBERS)).collection_length_lower_bound(2).new_value(),
                NUMBERS.validate([1]),
            ),
            (
                "length fits",
                NUMBERS,
                refine(CtyValue.unknown(NUMBERS)).collection_length_lower_bound(2).new_value(),
                NUMBERS.validate([1, 2, 3]),
            ),
            ("null candidate, nullable range", CtyString(), UNKNOWN_STRING, CtyValue.null(CtyString())),
            (
                "null candidate, not-null range",
                CtyString(),
                refine(UNKNOWN_STRING).not_null().new_value(),
                CtyValue.null(CtyString()),
            ),
            (
                "null range, null candidate",
                CtyString(),
                CtyValue.null(CtyString()),
                CtyValue.null(CtyString()),
            ),
            (
                "null range, known candidate",
                CtyString(),
                CtyValue.null(CtyString()),
                CtyString().validate("x"),
            ),
            ("unknown candidate", CtyString(), UNKNOWN_STRING, UNKNOWN_STRING),
        ],
    )
    def test_the_two_answer_the_same(
        self, label: str, cty_type: CtyType[Any], value: CtyValue[Any], candidate: CtyValue[Any]
    ) -> None:
        theirs = _range_from_harness(cty_type, value, candidate)
        assert "includes_panic" not in theirs, theirs

        assert _includes_here(value, candidate) == theirs["includes"], label


def test_a_marked_value_is_refused_the_same_way() -> None:
    """go-cty panics rather than answer for a value it cannot see through.

    A mark can carry sensitivity, and a range computed through one would
    describe the value while dropping the reason it was flagged. Answering is
    the wrong behaviour, so this library raises where go-cty panics.
    """
    marked = CtyString().validate("x").with_marks({"sensitive"})
    result = run("cty", "range", "--type", type_spec(CtyString()), json.dumps(rich(marked)))

    assert result["ok"] is False
    assert "marked" in result["panic"]

    with pytest.raises(ValueError, match="marked"):
        value_range(marked)


def test_the_number_bound_type_is_a_number_either_way() -> None:
    """A guard on the shape of the comparison above, not on go-cty.

    `number_lower_bound` returns a value plus an inclusive flag, and an earlier
    version of this test compared only the flag -- which passed while the two
    implementations disagreed about the bound itself.
    """
    lower, _ = value_range(UNKNOWN_NUMBER).number_lower_bound()

    assert isinstance(lower.value, Decimal | type(None)) or lower.is_unknown


# 🌊🪢🔚
