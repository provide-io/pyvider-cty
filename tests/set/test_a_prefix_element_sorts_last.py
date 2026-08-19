#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A set element that is a prefix of another sorts *after* it, as in go-cty.

Set element order reaches the wire. go-cty compares composite elements
element-wise and ranks *running out* last, so `{["a"], ["a","c"]}` serializes as
`[["a","c"], ["a"]]` and an empty element goes at the end. A plain Python tuple
comparison does the opposite -- a prefix is less than its extension -- so every
set whose elements were composite and of differing length re-encoded in a
different byte order.

Both spellings decode to the same value, so nothing but a byte comparison sees
it, and Terraform compares serialized state: it is a diff that reappears on
every plan. Exactly the failure mode as the null-rank inversion fixed on
2026-08-17, in the half nobody had measured -- the parity file recorded at the
time that "set ordering agrees everywhere else; only a null moves it", which was
true of primitives and untested for composites.

Found 2026-08-19 by generating sets of lists and comparing both encoders against
the harness: 232 of 300 generated sets diverged, and **every one of them
contained a pair where one element was a prefix of another.** Nothing else about
set ordering disagreed.

`_EXHAUSTED` in `CtyValue._canonical_sort_key` is what inverts it. The
differential cases live in `tests/compatibility/`; these run without a Go
toolchain and state the rule directly.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtySet, CtyString, CtyValue

S = CtyString()
LISTS = CtySet(element_type=CtyList(element_type=S))
MAPS = CtySet(element_type=CtyMap(element_type=S))
NUMBER_LISTS = CtySet(element_type=CtyList(element_type=CtyNumber()))


def elements(value: CtyValue[Any]) -> list[Any]:
    """A set's payload as plain Python, in the order it will serialize in."""
    return [[element.value for element in row.value] for row in value.value]


class TestExhaustionRanksLast:
    """The rule itself, on the shapes that carry it to the wire."""

    def test_a_prefix_sorts_after_its_extension(self) -> None:
        assert elements(LISTS.validate([["a"], ["a", "c"], ["b"]])) == [["a", "c"], ["a"], ["b"]]

    def test_an_empty_element_sorts_last(self) -> None:
        """The extreme case: the empty list is a prefix of every other."""
        assert elements(LISTS.validate([["b"], [], ["a", "c"]])) == [["a", "c"], ["b"], []]

    def test_a_chain_of_prefixes_reverses(self) -> None:
        built = LISTS.validate([["m"], ["m", "m"], ["m", "m", "m"]])

        assert elements(built) == [["m", "m", "m"], ["m", "m"], ["m"]]

    def test_a_shorter_element_that_is_not_a_prefix_still_sorts_first(self) -> None:
        """Not length-descending. Only exhaustion moves, and only against a prefix.

        `["a"]` stays ahead of `["b","c"]` because the comparison decides at the
        first element and never runs out. A length-first rule would answer the
        other way, and go-cty does not.
        """
        assert elements(LISTS.validate([["a"], ["b", "c"]])) == [["a"], ["b", "c"]]

    def test_the_rule_holds_for_number_elements(self) -> None:
        """`[1]` keeps its place -- it is not a prefix of `[2, 3]`; only `[]` moves."""
        built = NUMBER_LISTS.validate([[1], [], [2, 3]])

        assert elements(built) == [[Decimal(1)], [Decimal(2), Decimal(3)], []]

    def test_a_mapping_with_fewer_entries_sorts_last(self) -> None:
        """Mappings vary in size within one set type, so they need it too."""
        built = MAPS.validate([{"k": "b"}, {}, {"k": "a"}])
        rows = [{k: v.value for k, v in row.value.items()} for row in built.value]

        assert rows == [{"k": "a"}, {"k": "b"}, {}]


class TestTheRuleDidNotDisturbWhatWorked:
    """Primitives and equal-length composites never disagreed; they still don't."""

    @pytest.mark.parametrize(
        ("label", "cty_type", "raw", "expected"),
        [
            ("strings", CtySet(element_type=S), ["b", "", "a"], ["", "a", "b"]),
            ("numbers", CtySet(element_type=CtyNumber()), [3, 1, 10, -5], [-5, 1, 3, 10]),
        ],
    )
    def test_primitive_order_is_unchanged(
        self, label: str, cty_type: Any, raw: list[Any], expected: list[Any]
    ) -> None:
        assert [element.value for element in cty_type.validate(raw).value] == expected, label

    def test_equal_length_composites_are_ordered_element_wise(self) -> None:
        assert elements(LISTS.validate([["b"], ["a"], ["c"]])) == [["a"], ["b"], ["c"]]

    def test_identity_is_unchanged(self) -> None:
        """The terminator reorders; it must not make two equal sets unequal.

        `_canonical_sort_key` is this package's only notion of value identity --
        de-duplication and `__hash__` both read it -- so a change to its layout
        has to leave equality and hashing exactly where they were.
        """
        one, two = LISTS.validate([["a"], ["a", "c"]]), LISTS.validate([["a", "c"], ["a"]])

        assert one == two
        assert hash(one) == hash(two)
        assert len({one, two}) == 1

    def test_de_duplication_still_collapses_equal_elements(self) -> None:
        assert len(LISTS.validate([["a"], ["a"], ["a", "c"]]).value) == 2


# 🌊🪢🔚
