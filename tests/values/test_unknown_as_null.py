#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`unknown_as_null` — go-cty's `UnknownAsNull` (`cty/unknown_as_null.go`).

Terraform reaches for this when it needs a value it can *store*: an unknown is a
promise about a future apply and has no representation in state, while a null is
an ordinary value. So the failure mode is not a wrong answer, it is an unknown
surviving into somewhere that cannot hold one.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
    unknown_as_null,
)
from pyvider.cty.marks import CtyMark

S, N = CtyString(), CtyNumber()
SENSITIVE = CtyMark("sensitive")


class TestScalars:
    def test_an_unknown_becomes_a_null_of_the_same_type(self) -> None:
        result = unknown_as_null(CtyValue.unknown(S))

        assert result.is_null
        assert result.type.equal(S)

    def test_a_null_is_left_alone(self) -> None:
        """Only unknowns are rewritten; a null is already a value."""
        null = CtyValue.null(S)

        assert unknown_as_null(null) is null

    def test_a_known_value_is_left_alone(self) -> None:
        known = S.validate("a")

        assert unknown_as_null(known) is known


class TestContainers:
    def test_an_unknown_container_becomes_a_null_container(self) -> None:
        """Not a container of nulls -- there are no elements to descend into.

        The collection itself is what is unknown, so its contents are not merely
        unknown, they are unrepresented. Rewriting this to an empty or
        all-null collection would invent a length.
        """
        result = unknown_as_null(CtyValue.unknown(CtyList(element_type=S)))

        assert result.is_null
        assert result.value is None

    def test_an_unknown_element_becomes_null_and_the_type_survives(self) -> None:
        list_type = CtyList(element_type=S)
        value = CtyValue(vtype=list_type, value=(S.validate("a"), CtyValue.unknown(S)))

        result = unknown_as_null(value)

        assert [element.is_null for element in result.value] == [False, True]
        assert result.type.equal(list_type)

    def test_an_unknown_object_attribute_becomes_null(self) -> None:
        object_type = CtyObject({"a": S, "b": N})
        value = object_type.validate({"a": CtyValue.unknown(S), "b": 1})

        result = unknown_as_null(value)

        assert result.value["a"].is_null
        assert result.value["b"].value == 1

    def test_an_unknown_map_element_becomes_null(self) -> None:
        map_type = CtyMap(element_type=S)
        value = CtyValue(vtype=map_type, value={"k": CtyValue.unknown(S)})

        assert unknown_as_null(value).value["k"].is_null

    def test_a_tuple_keeps_its_positional_types(self) -> None:
        tuple_type = CtyTuple(element_types=(S, N))
        value = CtyValue(vtype=tuple_type, value=(CtyValue.unknown(S), N.validate(1)))

        result = unknown_as_null(value)

        assert result.type.equal(tuple_type)
        assert result.value[0].is_null

    def test_a_set_re_deduplicates(self) -> None:
        """Two elements can become equal once both are null, and a set holds one.

        go-cty rebuilds through `SetVal`, which de-duplicates. Constructing the
        payload directly would leave a set containing the same value twice --
        representable in Python, and not a set.
        """
        set_type = CtySet(element_type=S)
        value = CtyValue(vtype=set_type, value=frozenset({CtyValue.null(S), CtyValue.unknown(S)}))

        assert len(unknown_as_null(value).value) == 1

    @pytest.mark.parametrize(
        "empty",
        [
            CtyList(element_type=S).validate([]),
            CtyMap(element_type=S).validate({}),
            CtySet(element_type=S).validate([]),
        ],
        ids=str,
    )
    def test_an_empty_container_is_returned_untouched(self, empty: CtyValue[Any]) -> None:
        """With no elements nothing can be unknown, so there is nothing to do."""
        assert unknown_as_null(empty) is empty

    def test_nesting_is_rewritten_at_every_depth(self) -> None:
        inner = CtyObject({"x": S})
        outer = CtyList(element_type=inner)
        value = CtyValue(vtype=outer, value=(inner.validate({"x": CtyValue.unknown(S)}),))

        assert unknown_as_null(value).value[0].value["x"].is_null


class TestMarks:
    """go-cty 1.16.4 made this mark-preserving, and the reason is not cosmetic."""

    def test_a_mark_survives_the_rewrite(self) -> None:
        """Being unknown is not what made a value sensitive.

        A sensitive unknown becoming a plain null is silent declassification --
        the same fault class as every other mark bug on this branch.
        """
        result = unknown_as_null(CtyValue.unknown(S).mark(SENSITIVE))

        assert result.is_null
        assert SENSITIVE in result.marks

    def test_a_mark_on_a_nested_element_survives(self) -> None:
        list_type = CtyList(element_type=S)
        value = CtyValue(vtype=list_type, value=(CtyValue.unknown(S).mark(SENSITIVE),))

        assert SENSITIVE in unknown_as_null(value).value[0].marks

    def test_marks_at_two_levels_both_survive(self) -> None:
        other = CtyMark("other")
        list_type = CtyList(element_type=S)
        value = CtyValue(vtype=list_type, value=(CtyValue.unknown(S).mark(SENSITIVE),)).mark(other)

        result = unknown_as_null(value)

        assert other in result.marks
        assert SENSITIVE in result.value[0].marks

    def test_unmarking_uses_unmark_and_not_an_empty_union(self) -> None:
        """A regression guard for a real bug, not a hypothetical one.

        `with_marks` *unions*, so `with_marks(frozenset())` returns the value
        unchanged -- and the first draft of this function used it to strip
        marks, which recursed until the stack ran out. The failure was total
        rather than subtle, but only for a marked input: every unmarked test
        passed.
        """
        deeply_marked = CtyValue.unknown(S).mark(SENSITIVE).mark(CtyMark("b"))

        assert unknown_as_null(deeply_marked).is_null


# 🌊🪢🔚
