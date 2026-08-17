#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`compare_types` and `sort_types`, the ordering `unify` searches in.

`test_explicit_conversion.py` covers what unification *answers*; this covers how
it decides, because the answer for a mixed group is whichever candidate the
ordering reaches first and every other type can convert to. The swap cases below
in particular exist only inside `compare_types` and are invisible from the
result: a tuple compared against a list gives the same answer either way round,
and getting the sign wrong would silently reverse the preference.
"""

from __future__ import annotations

from typing import Any

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
)
from pyvider.cty.conversion.unify import compare_types, sort_types

S, N, B, D = CtyString(), CtyNumber(), CtyBool(), CtyDynamic()


def lst(element: CtyType[Any]) -> CtyType[Any]:
    return CtyList(element_type=element)


def se(element: CtyType[Any]) -> CtyType[Any]:
    return CtySet(element_type=element)


def mp(element: CtyType[Any]) -> CtyType[Any]:
    return CtyMap(element_type=element)


def tp(*elements: CtyType[Any]) -> CtyType[Any]:
    return CtyTuple(element_types=elements)


class TestCompareTypes:
    """Negative means the left is the more general -- the better unified type."""

    @pytest.mark.parametrize(
        ("left", "right", "expected"),
        [
            # Dynamic is least preferred of all, so a concrete neighbour wins.
            (S, D, -1),
            (D, S, 1),
            (D, D, 0),
            # String is the supertype of the primitives; number and bool are
            # incomparable, which is a partial order rather than a tie.
            (S, N, -1),
            (N, S, 1),
            (S, S, 0),
            (N, B, 0),
            # Collections of a kind compare by their elements.
            (lst(S), lst(N), -1),
            (se(N), se(S), 1),
            (mp(S), mp(N), -1),
        ],
        ids=str,
    )
    def test_the_preference_order(self, left: CtyType[Any], right: CtyType[Any], expected: int) -> None:
        assert compare_types(left, right) == expected

    @pytest.mark.parametrize(
        ("left", "right"),
        [
            (lst(S), tp(S, S)),
            (lst(S), se(S)),
            (tp(S, S), se(S)),
            (mp(S), CtyObject({"a": S})),
        ],
        ids=str,
    )
    def test_comparison_is_antisymmetric_across_the_swapped_cases(
        self, left: CtyType[Any], right: CtyType[Any]
    ) -> None:
        """Comparing the pair the other way round must invert the sign.

        These four are the pairs `compare_types` normalises by swapping its
        arguments, and the swap is undone by multiplying the result back
        through. A missed multiplication reverses the preference without
        changing which types are comparable, so nothing else would notice.
        """
        assert compare_types(left, right) == -compare_types(right, left)
        assert compare_types(left, right) < 0

    def test_objects_compare_attribute_by_attribute(self) -> None:
        assert compare_types(CtyObject({"a": S}), CtyObject({"a": N})) < 0
        assert compare_types(CtyObject({"a": N}), CtyObject({"a": S})) > 0
        assert compare_types(CtyObject({"a": S}), CtyObject({"a": S})) == 0

    def test_objects_that_disagree_in_both_directions_have_no_preference(self) -> None:
        """Neither is the supertype, though a third type may still unify them."""
        assert compare_types(CtyObject({"a": S, "b": N}), CtyObject({"a": N, "b": S})) == 0

    def test_objects_with_different_attribute_names_have_no_preference(self) -> None:
        assert compare_types(CtyObject({"a": S}), CtyObject({"b": S})) == 0
        assert compare_types(CtyObject({"a": S}), CtyObject({"a": S, "b": S})) == 0

    def test_tuples_compare_positionally(self) -> None:
        assert compare_types(tp(S, S), tp(N, N)) < 0
        assert compare_types(tp(N, N), tp(S, S)) > 0
        assert compare_types(tp(S, N), tp(N, S)) == 0
        assert compare_types(tp(S), tp(S)) == 0

    def test_tuples_of_different_lengths_have_no_preference(self) -> None:
        assert compare_types(tp(S), tp(S, S)) == 0

    def test_unrelated_kinds_have_no_preference(self) -> None:
        assert compare_types(S, mp(S)) == 0
        assert compare_types(CtyObject({"a": S}), tp(S)) == 0


class TestSortTypes:
    def test_the_most_general_comes_first(self) -> None:
        assert sort_types([N, S])[0] == 1
        assert sort_types([S, N])[0] == 0

    def test_dynamic_sorts_last(self) -> None:
        order = sort_types([D, S])

        assert order[-1] == 0

    def test_incomparable_types_keep_their_input_order(self) -> None:
        """The relation is a partial order, so ties must not be invented."""
        assert sort_types([N, B]) == [0, 1]
        assert sort_types([B, N]) == [0, 1]

    def test_every_index_appears_exactly_once(self) -> None:
        order = sort_types([S, N, B, D, lst(S)])

        assert sorted(order) == [0, 1, 2, 3, 4]


# 🌊🪢🔚
