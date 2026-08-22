#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A known `dynamic` value acts like the value it wraps, in every operation.

A `dynamic` position holds the concrete value it was given, so anything that
treats a value as a container has to look through the wrapper to find one.
`__len__` and `__bool__` each did that inline; `__getitem__` and `__iter__` did
not. The same wrapper therefore answered `len(wrapper)` and raised `TypeError`
for `wrapper[0]` and `list(wrapper)` -- not a policy about dynamic values, just
a missing branch in two of the four.

Path traversal already steps through a wrapper, which left the direct façade as
the odd one out and made the inconsistency easy to hit: the same value reached
one way worked and reached the other did not.
"""

from __future__ import annotations

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.marks import CtyMark
from pyvider.cty.path import CtyPath

S, N = CtyString(), CtyNumber()
SENSITIVE = CtyMark("sensitive")

LIST = CtyList(element_type=S)
MAP = CtyMap(element_type=S)
OBJECT = CtyObject({"a": S})
TUPLE = CtyTuple((S, N))
SET = CtySet(element_type=S)


def wrapped(value: CtyValue[object]) -> CtyValue[object]:
    return CtyDynamic().validate(value)


class TestASubscriptLooksThroughTheWrapper:
    def test_a_list(self) -> None:
        assert wrapped(LIST.validate(["a", "b"]))[0].value == "a"

    def test_a_tuple(self) -> None:
        assert wrapped(TUPLE.validate(("a", 1)))[0].value == "a"

    def test_a_map(self) -> None:
        assert wrapped(MAP.validate({"k": "v"}))["k"].value == "v"

    def test_an_object(self) -> None:
        assert wrapped(OBJECT.validate({"a": "x"}))["a"].value == "x"

    def test_a_slice(self) -> None:
        sliced = wrapped(LIST.validate(["a", "b"]))[0:1]

        assert [element.value for element in sliced.value] == ["a"]  # type: ignore[union-attr]


class TestIteratingLooksThroughItToo:
    def test_a_list(self) -> None:
        assert [element.value for element in wrapped(LIST.validate(["a", "b"]))] == ["a", "b"]

    def test_a_set(self) -> None:
        assert [element.value for element in wrapped(SET.validate(["a"]))] == ["a"]

    def test_a_map_yields_its_values(self) -> None:
        assert [element.value for element in wrapped(MAP.validate({"k": "v"}))] == ["v"]

    def test_a_tuple(self) -> None:
        assert [element.value for element in wrapped(TUPLE.validate(("a", 1)))] == ["a", 1]


class TestTheFourAgreeWithEachOther:
    """The point of the fix: no operation answers where another refuses."""

    def test_length_and_iteration_agree(self) -> None:
        held = wrapped(LIST.validate(["a", "b"]))

        assert len(held) == len(list(held))

    def test_every_index_length_promises_is_reachable(self) -> None:
        held = wrapped(LIST.validate(["a", "b", "c"]))

        assert [held[i].value for i in range(len(held))] == ["a", "b", "c"]

    def test_a_subscript_agrees_with_a_path(self) -> None:
        """`CtyPath` stepped through a wrapper while `[...]` did not."""
        held = wrapped(LIST.validate(["a", "b"]))

        assert held[0] == CtyPath.index(0).apply_path(held)


class TestTheWrappersMarksStillTravel:
    def test_a_subscript_carries_them(self) -> None:
        held = wrapped(LIST.validate(["a"])).mark(SENSITIVE)

        assert held[0].marks == frozenset({SENSITIVE})

    def test_iteration_carries_them(self) -> None:
        held = wrapped(LIST.validate(["a", "b"])).mark(SENSITIVE)

        assert [element.marks for element in held] == [frozenset({SENSITIVE})] * 2

    def test_an_inner_mark_survives(self) -> None:
        held = wrapped(LIST.validate([S.validate("a").mark(SENSITIVE)]))

        assert held[0].marks == frozenset({SENSITIVE})


class TestNullAndUnknownAreUnchanged:
    """Neither holds an inner value, so there is nothing to look through to."""

    def test_a_null_dynamic_has_no_length(self) -> None:
        assert len(CtyValue.null(CtyDynamic())) == 0

    def test_a_null_dynamic_iterates_empty(self) -> None:
        assert list(CtyValue.null(CtyDynamic())) == []

    def test_an_unknown_dynamic_refuses_length(self) -> None:
        with pytest.raises(TypeError):
            len(CtyValue.unknown(CtyDynamic()))

    def test_an_unknown_dynamic_refuses_iteration(self) -> None:
        with pytest.raises(TypeError):
            list(CtyValue.unknown(CtyDynamic()))

    def test_an_unknown_dynamic_refuses_a_subscript(self) -> None:
        with pytest.raises(TypeError):
            CtyValue.unknown(CtyDynamic())[0]


class TestAWrapperAroundSomethingUnsubscriptable:
    def test_a_wrapped_string_is_still_not_subscriptable(self) -> None:
        """Looking through the wrapper finds a string, which refuses on its own
        account -- the refusal comes from the value, not from the wrapper."""
        with pytest.raises(TypeError):
            wrapped(S.validate("x"))[0]

    def test_a_wrapped_string_is_still_not_iterable(self) -> None:
        with pytest.raises(TypeError):
            list(wrapped(S.validate("x")))


class TestContainsWasNotBroken:
    """`__contains__` already delegated: a wrapper's payload *is* a `CtyValue`.

    A raw operand finds nothing in a list either way, because the elements are
    `CtyValue`s -- but that is equally true of a plain list, so it is not the
    wrapper's doing and is not changed here.
    """

    def test_a_cty_value_operand_is_found_through_the_wrapper(self) -> None:
        assert S.validate("a") in wrapped(LIST.validate(["a", "b"]))

    def test_the_wrapper_answers_the_same_as_the_value_it_holds(self) -> None:
        held = LIST.validate(["a", "b"])

        assert (S.validate("a") in wrapped(held)) == (S.validate("a") in held)

    def test_a_raw_operand_behaves_the_same_either_way(self) -> None:
        held = LIST.validate(["a", "b"])

        assert ("a" in wrapped(held)) == ("a" in held)


# 🌊🪢🔚
