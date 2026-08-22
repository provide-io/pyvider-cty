#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Selecting out of a marked container, and rebuilding one, keeps the marks.

go-cty's `Value.Index` and `Value.GetAttr` (`cty/value_ops.go:866` and `:819`)
both open with the same three lines -- unmark the receiver, do the access, put
the marks back on the result -- so a mark on a container is a mark on every
value read out of it. A mark is how sensitivity travels, and `cty_to_msgpack`
refuses to serialize a marked value; a subscript that dropped the mark handed
back a value the codec would happily write to the wire.
"""

from __future__ import annotations

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
)
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.exceptions import CtyMarksSerializationError
from pyvider.cty.marks import CtyMark

S, N = CtyString(), CtyNumber()
SENSITIVE = CtyMark("sensitive")
OTHER = CtyMark("other")

LIST = CtyList(element_type=S)
MAP = CtyMap(element_type=S)
OBJECT = CtyObject({"a": S, "b": N})
TUPLE = CtyTuple((S, N))


def _marked_containers() -> list[tuple[str, CtyValue[object], object]]:
    """One container of each subscriptable kind, marked, with a key into it."""
    return [
        ("list", LIST.validate(["x", "y"]).mark(SENSITIVE), 0),
        ("map", MAP.validate({"k": "x"}).mark(SENSITIVE), "k"),
        ("object", OBJECT.validate({"a": "x", "b": 1}).mark(SENSITIVE), "a"),
        ("tuple", TUPLE.validate(("x", 1)).mark(SENSITIVE), 0),
    ]


@pytest.mark.parametrize(
    ("kind", "container", "key"), _marked_containers(), ids=lambda p: p if isinstance(p, str) else ""
)
class TestASubscriptCarriesTheContainersMarks:
    def test_the_selected_element_is_marked(self, kind: str, container: CtyValue[object], key: object) -> None:
        assert container[key].marks == frozenset({SENSITIVE})

    def test_the_element_is_otherwise_unchanged(
        self, kind: str, container: CtyValue[object], key: object
    ) -> None:
        assert container[key].value == "x"

    def test_the_container_itself_is_not_disturbed(
        self, kind: str, container: CtyValue[object], key: object
    ) -> None:
        container[key]
        assert container.marks == frozenset({SENSITIVE})

    def test_the_selected_element_cannot_be_serialized(
        self, kind: str, container: CtyValue[object], key: object
    ) -> None:
        selected = container[key]
        with pytest.raises(CtyMarksSerializationError):
            cty_to_msgpack(selected, selected.type)


class TestMarksAccumulateRatherThanReplace:
    def test_an_elements_own_mark_survives_alongside_the_containers(self) -> None:
        inner = S.validate("x").mark(OTHER)
        marked = LIST.validate([inner]).mark(SENSITIVE)
        assert marked[0].marks == frozenset({SENSITIVE, OTHER})

    def test_an_unmarked_container_hands_back_the_elements_own_mark(self) -> None:
        inner = S.validate("x").mark(OTHER)
        assert LIST.validate([inner])[0].marks == frozenset({OTHER})

    def test_an_unmarked_container_hands_back_an_unmarked_element(self) -> None:
        assert LIST.validate(["x"])[0].marks == frozenset()

    def test_nesting_unions_every_level(self) -> None:
        outer = CtyList(element_type=LIST).validate([LIST.validate(["x"]).mark(OTHER)]).mark(SENSITIVE)
        assert outer[0][0].marks == frozenset({SENSITIVE, OTHER})


class TestASliceCarriesThemToo:
    def test_a_list_slice_is_marked(self) -> None:
        assert LIST.validate(["x", "y"]).mark(SENSITIVE)[0:1].marks == frozenset({SENSITIVE})

    def test_a_tuple_slice_is_marked(self) -> None:
        assert TUPLE.validate(("x", 1)).mark(SENSITIVE)[0:1].marks == frozenset({SENSITIVE})

    def test_a_list_slice_still_holds_the_right_elements(self) -> None:
        sliced = LIST.validate(["x", "y"]).mark(SENSITIVE)[0:1]
        assert [element.value for element in sliced.value] == ["x"]  # type: ignore[union-attr]


class TestIteratingIsAccessToo:
    """`for element in marked_container` was the widest hole of the family.

    go-cty refuses instead (`ElementIterator`, `cty/value_ops.go:1260`), but its
    refusals are the value-to-Go-native escapes; everything answering with
    another `Value` unmarks, acts and remarks. This yields `CtyValue`s.
    """

    def test_a_marked_list_yields_marked_elements(self) -> None:
        assert [e.marks for e in LIST.validate(["x", "y"]).mark(SENSITIVE)] == [frozenset({SENSITIVE})] * 2

    def test_a_marked_map_yields_marked_values(self) -> None:
        assert [e.marks for e in MAP.validate({"k": "x"}).mark(SENSITIVE)] == [frozenset({SENSITIVE})]

    def test_a_marked_set_yields_marked_elements(self) -> None:
        marked = CtySet(element_type=S).validate(["x"]).mark(SENSITIVE)
        assert [e.marks for e in marked] == [frozenset({SENSITIVE})]

    def test_a_marked_tuple_yields_marked_elements(self) -> None:
        assert [e.marks for e in TUPLE.validate(("x", 1)).mark(SENSITIVE)] == [frozenset({SENSITIVE})] * 2

    def test_an_elements_own_mark_survives(self) -> None:
        marked = LIST.validate([S.validate("x").mark(OTHER)]).mark(SENSITIVE)
        assert [e.marks for e in marked] == [frozenset({SENSITIVE, OTHER})]

    def test_the_elements_are_otherwise_unchanged(self) -> None:
        assert [e.value for e in LIST.validate(["x", "y"]).mark(SENSITIVE)] == ["x", "y"]

    def test_an_iterated_element_cannot_be_serialized(self) -> None:
        element = next(iter(LIST.validate(["x"]).mark(SENSITIVE)))
        with pytest.raises(CtyMarksSerializationError):
            cty_to_msgpack(element, S)

    def test_an_unmarked_container_is_untouched(self) -> None:
        assert [e.marks for e in LIST.validate(["x"])] == [frozenset()]


class TestAnAbsentElementIsMarkedToo:
    """The remark in go-cty wraps the whole access, the not-there branch included.

    A subscript of a null or unknown *container* raises here rather than
    answering, so those two rows of the matrix belong to the path steps, which
    do answer; `tests/path/test_a_step_returns_the_value_intact.py` has them.
    """

    def test_a_missing_object_attribute_yields_a_marked_null(self) -> None:
        marked = CtyObject({"a": S}, optional_attributes=frozenset({"a"})).validate({}).mark(SENSITIVE)
        selected = marked["a"]
        assert selected.is_null and selected.marks == frozenset({SENSITIVE})

    def test_a_missing_map_key_yields_a_marked_null(self) -> None:
        selected = MAP.validate({"k": "x"}).mark(SENSITIVE)["absent"]
        assert selected.is_null and selected.marks == frozenset({SENSITIVE})


class TestRebuildingAContainerKeepsItsMarks:
    """`validate` builds a fresh value, and marks live on the value, not the payload."""

    def test_with_key(self) -> None:
        marked = MAP.validate({"k": "x"}).mark(SENSITIVE)
        assert marked.with_key("n", "y").marks == frozenset({SENSITIVE})

    def test_without_key(self) -> None:
        marked = MAP.validate({"k": "x"}).mark(SENSITIVE)
        assert marked.without_key("k").marks == frozenset({SENSITIVE})

    def test_without_a_key_that_is_not_there(self) -> None:
        marked = MAP.validate({"k": "x"}).mark(SENSITIVE)
        assert marked.without_key("absent").marks == frozenset({SENSITIVE})

    def test_append(self) -> None:
        marked = LIST.validate(["x"]).mark(SENSITIVE)
        assert marked.append("y").marks == frozenset({SENSITIVE})

    def test_with_element_at(self) -> None:
        marked = LIST.validate(["x"]).mark(SENSITIVE)
        assert marked.with_element_at(0, "y").marks == frozenset({SENSITIVE})

    def test_the_rebuilt_value_is_otherwise_right(self) -> None:
        marked = LIST.validate(["x"]).mark(SENSITIVE)
        assert [element.value for element in marked.append("y").value] == ["x", "y"]  # type: ignore[union-attr]

    def test_a_rebuilt_container_cannot_be_serialized(self) -> None:
        rebuilt = LIST.validate(["x"]).mark(SENSITIVE).append("y")
        with pytest.raises(CtyMarksSerializationError):
            cty_to_msgpack(rebuilt, rebuilt.type)


# 🌊🪢🔚
