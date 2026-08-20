#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A set of composite elements is ordered by go-cty's hash bytes, not by value.

go-cty orders a set two different ways, and only one of them compares the
values. `setRules.Less` (`cty/set_internals.go:85`) compares a string, a number
or a bool directly -- and for **every other element type** it compares
`makeSetHashBytes`, the byte string cty builds to bucket an element by. That
order reaches the wire: msgpack writes a set in iteration order, and Terraform
compares serialized state, so a different order is a diff on every plan.

The hash bytes carry delimiters and quotes that take part in the comparison, so
the two orders disagree on ordinary values:

  * numbers are written *as text*, so `<12;>` sorts before `<1;>` -- `2` before
    `;` -- and go-cty puts the tuple `[12]` before `[1]`, which is not the
    numeric order;
  * strings are written Go-quoted, so `<"";" ";>` sorts before `<"";"";>` -- a
    space before a quote -- and the *longer* string comes first.

Both were found on 2026-08-19 by the stdlib fuzz, through `setproduct`, whose
result is exactly a set of tuples. The structural comparison this package used
before -- and the "a sequence that has run out of members sorts last" rule that
approximates it, in `tests/set/test_a_prefix_element_sorts_last.py` -- gets the
first wrong always and the second wrong for any character below `"`. That
approximation was measured against generated sets drawn from the alphabet
`abc`, where every character outranks a quote and the two rules agree.

Ordering only. Identity stays with `_canonical_sort_key`, because the hash
renders a number with `big.Float.String()` -- ten significant digits -- and
de-duplicating on that would merge two elements go-cty keeps apart.

Every expected order below was read from `soup-go cty msgpack encode` against
go-cty v1.19.0; `tests/compatibility/` holds the differential cases, and these
run without a Go toolchain.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.values.set_order import go_number_text, go_quoted, hash_bytes

S, N, B = CtyString(), CtyNumber(), CtyBool()
NUMBER_TUPLES = CtySet(element_type=CtyTuple(element_types=(N,)))
STRING_PAIRS = CtySet(element_type=CtyTuple(element_types=(S, S)))
STRING_LISTS = CtySet(element_type=CtyList(element_type=S))


def rows(value: CtyValue[Any]) -> list[list[Any]]:
    """A set's elements as plain Python, in the order they will serialize in."""
    return [[member.value for member in row.value] for row in value.value]


class TestTheOrderIsTheHashBytes:
    def test_numbers_inside_a_tuple_sort_as_text(self) -> None:
        """`[12]` before `[1]` before `[2]`, which no numeric comparison gives."""
        assert rows(NUMBER_TUPLES.validate([[1], [12], [2]])) == [
            [Decimal(12)],
            [Decimal(1)],
            [Decimal(2)],
        ]

    def test_a_quote_decides_between_a_string_and_its_extension(self) -> None:
        """A space is 0x20 and a quote is 0x22, so `("", " ")` comes first."""
        assert rows(STRING_PAIRS.validate([["", ""], ["", " "]])) == [["", " "], ["", ""]]

    def test_a_character_above_the_quote_keeps_the_other_order(self) -> None:
        """`a` is 0x61 and the closing quote is 0x22, so the *empty* string wins
        here -- the opposite of the space above, and the reason a rule about
        running out of members cannot stand in for the byte comparison."""
        assert rows(STRING_PAIRS.validate([["", ""], ["", "a"]])) == [["", ""], ["", "a"]]

    def test_a_list_element_is_ordered_the_same_way(self) -> None:
        """Not only tuples: every non-primitive element type takes this path."""
        assert rows(STRING_LISTS.validate([["a"], ["a", "c"], ["b"]])) == [["a", "c"], ["a"], ["b"]]


class TestPrimitivesKeepTheirOwnOrder:
    """`setRules.Less` compares these directly, and must go on doing so."""

    @pytest.mark.parametrize(
        ("label", "cty_type", "raw", "expected"),
        [
            ("strings", CtySet(element_type=S), ["a", "a!", "ab"], ["a", "a!", "ab"]),
            ("numbers", CtySet(element_type=N), [3, 1, 12, -5], [-5, 1, 3, 12]),
            ("bools", CtySet(element_type=B), [True, False], [False, True]),
        ],
    )
    def test_a_primitive_set_is_ordered_by_value(
        self, label: str, cty_type: Any, raw: list[Any], expected: list[Any]
    ) -> None:
        """`a!` is where the two rules differ: quoted, `"a!"` sorts before `"a"`."""
        assert [element.value for element in cty_type.validate(raw).value] == expected, label


class TestTheHashItself:
    """The pieces, so a failure names which one moved."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [("", '""'), ("a", '"a"'), ('"', '"\\""'), ("\n", '"\\n"'), ("\x00", '"\\x00"'), ("é", '"é"')],
    )
    def test_a_string_is_written_the_way_gos_percent_q_writes_it(self, raw: str, expected: str) -> None:
        assert go_quoted(raw) == expected

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("0", "0"),
            ("1", "1"),
            ("12", "12"),
            ("1.5", "1.5"),
            ("-0", "-0"),
            ("100", "100"),
            ("1e10", "1e+10"),
            ("0.0001", "0.0001"),
            ("0.00001", "1e-05"),
            ("12345678901234567890", "1.23456789e+19"),
            ("3.14159265358979", "3.141592654"),
            ("1e300", "1e+300"),
            ("Infinity", "+Inf"),
            ("-Infinity", "-Inf"),
        ],
    )
    def test_a_number_is_written_the_way_big_float_string_writes_it(self, raw: str, expected: str) -> None:
        """`big.Float.String()` is `Text('g', 10)`. Every expectation here was
        read from a Go program, not derived from the documentation."""
        assert go_number_text(Decimal(raw)) == expected

    @pytest.mark.parametrize(
        ("label", "value", "expected"),
        [
            ("a null", CtyValue.null(S), "~"),
            ("an unknown", CtyValue.unknown(S), "?"),
            ("a bool", B.validate(True), "T"),
            ("a list", CtyList(element_type=S).validate(["a"]), '["a";]'),
            ("a tuple", CtyTuple(element_types=(S,)).validate(["a"]), '<"a";>'),
            ("a map", CtyMap(element_type=S).validate({"k": "v"}), '{"k":"v";}'),
            ("an object", CtyObject(attribute_types={"k": S}).validate({"k": "v"}), '<"v";>'),
            ("a set", CtySet(element_type=S).validate(["b", "a"]), '["a";"b";]'),
        ],
    )
    def test_each_bracketing_is_go_ctys(self, label: str, value: CtyValue[Any], expected: str) -> None:
        assert hash_bytes(value) == expected, label


def test_a_dynamic_wrapper_hashes_as_the_value_it_holds() -> None:
    """A `dynamic` position carries the concrete value, and that is what go-cty
    would have been handed. Missing this raised `NameError` from inside set
    validation for `set(dynamic)`, which is the shape a provider schema with an
    `any` attribute produces."""
    from pyvider.cty import CtyDynamic

    assert hash_bytes(CtyDynamic().validate(S.validate("a"))) == '"a"'
    assert len(CtySet(element_type=CtyDynamic()).validate([S.validate("a"), S.validate("b")]).value) == 2


def test_identity_is_untouched_by_the_ordering_rule() -> None:
    """The hash decides order and nothing else.

    `_canonical_sort_key` is this package's only notion of value identity --
    de-duplication and `__hash__` both read it -- and a number's hash text is
    ten significant digits, so identity had to stay where it was.
    """
    one = NUMBER_TUPLES.validate([[Decimal("1.00000000001")], [Decimal("1.00000000002")]])

    assert len(one.value) == 2, "two numbers agreeing to ten digits are still two elements"


# 🌊🪢🔚
