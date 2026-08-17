#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`unmark_deep_with_paths` / `mark_with_paths` — go-cty's path-aware mark pair.

The load-bearing test is the wire round trip at the bottom. These exist because
`cty_to_msgpack` refuses a marked value, so a caller must strip marks to
serialize -- and `collect_marks_deep` returns the union, which is enough to
decide "is this sensitive" and not enough to put the marks back where they were.
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
    CtyValue,
    mark_with_paths,
    unmark_deep_with_paths,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.marks import CtyMark

S, N = CtyString(), CtyNumber()
SENSITIVE = CtyMark("sensitive")
OTHER = CtyMark("other")


def _paths(value: CtyValue[object]) -> dict[str, frozenset[object]]:
    return {str(path): marks for path, marks in unmark_deep_with_paths(value)[1].items()}


class TestLocations:
    def test_a_top_level_mark_is_recorded_at_the_root(self) -> None:
        assert _paths(S.validate("a").mark(SENSITIVE)) == {"(root)": frozenset({SENSITIVE})}

    def test_an_object_attribute_is_recorded_by_name(self) -> None:
        object_type = CtyObject({"a": S, "b": N})
        value = object_type.validate({"a": S.validate("secret").mark(SENSITIVE), "b": 1})

        assert _paths(value) == {"a": frozenset({SENSITIVE})}

    def test_a_list_element_is_recorded_by_index(self) -> None:
        list_type = CtyList(element_type=S)
        value = CtyValue(
            vtype=list_type,
            value=(S.validate("a").mark(SENSITIVE), S.validate("b").mark(OTHER)),
        )

        assert _paths(value) == {"[0]": frozenset({SENSITIVE}), "[1]": frozenset({OTHER})}

    def test_a_map_element_is_recorded_by_key(self) -> None:
        map_type = CtyMap(element_type=S)
        value = CtyValue(vtype=map_type, value={"k": S.validate("v").mark(SENSITIVE)})

        assert _paths(value) == {"['k']": frozenset({SENSITIVE})}

    def test_nesting_composes_the_path(self) -> None:
        inner = CtyObject({"i": S})
        outer = CtyObject({"o": inner})
        value = outer.validate({"o": {"i": S.validate("x").mark(SENSITIVE)}})

        assert _paths(value) == {"o.i": frozenset({SENSITIVE})}

    def test_marks_at_several_depths_are_all_recorded(self) -> None:
        list_type = CtyList(element_type=S)
        value = CtyValue(vtype=list_type, value=(S.validate("a").mark(SENSITIVE),)).mark(OTHER)

        assert _paths(value) == {"(root)": frozenset({OTHER}), "[0]": frozenset({SENSITIVE})}


class TestRoundTrip:
    def test_stripping_then_restoring_is_the_identity(self) -> None:
        object_type = CtyObject({"a": S, "b": S})
        value = object_type.validate({"a": S.validate("x").mark(SENSITIVE), "b": "y"})

        bare, paths = unmark_deep_with_paths(value)
        restored = mark_with_paths(bare, paths)

        assert restored.value["a"].marks == frozenset({SENSITIVE})
        assert restored.value["a"].value == "x"
        assert not restored.value["b"].marks

    def test_the_stripped_value_carries_no_marks_anywhere(self) -> None:
        """It has to be clean, or serializing it still raises."""
        object_type = CtyObject({"a": S})
        value = object_type.validate({"a": S.validate("x").mark(SENSITIVE)})

        bare, _ = unmark_deep_with_paths(value)

        assert not bare.marks
        assert not bare.value["a"].marks

    def test_marks_survive_a_trip_through_the_wire(self) -> None:
        """The reason these functions exist.

        `cty_to_msgpack` refuses a marked value, so the only way a sensitive
        value reaches the wire is stripped -- and the only way its sensitivity
        comes back is from the paths recorded here.
        """
        object_type = CtyObject({"a": S, "b": N})
        value = object_type.validate({"a": S.validate("hunter2").mark(SENSITIVE), "b": 1})

        bare, paths = unmark_deep_with_paths(value)
        decoded = cty_from_msgpack(cty_to_msgpack(bare, object_type), object_type)
        restored = mark_with_paths(decoded, paths)

        assert restored.value["a"].value == "hunter2"
        assert SENSITIVE in restored.value["a"].marks


class TestFastPathsAndEdges:
    def test_applying_no_marks_returns_the_same_object(self) -> None:
        """go-cty's own fast path: nothing to apply, so do not rebuild."""
        value = S.validate("a")

        assert mark_with_paths(value, {}) is value

    def test_an_unmarked_value_records_nothing(self) -> None:
        assert unmark_deep_with_paths(CtyObject({"a": S}).validate({"a": "x"}))[1] == {}

    def test_a_path_that_no_longer_resolves_is_skipped(self) -> None:
        """A shape change must not cost every other mark in the set.

        Round trips do change shape -- an unknown becomes something else on the
        far side -- and failing the whole restore because one location moved
        would lose the marks that *did* still apply.
        """
        _, paths = unmark_deep_with_paths(
            CtyObject({"o": CtyObject({"i": S})}).validate({"o": {"i": S.validate("x").mark(SENSITIVE)}})
        )

        assert mark_with_paths(S.validate("z"), paths).value == "z"

    @pytest.mark.parametrize("absent", ["null", "unknown"])
    def test_a_null_or_unknown_is_handled_without_descending(self, absent: str) -> None:
        list_type = CtyList(element_type=S)
        value = CtyValue.null(list_type) if absent == "null" else CtyValue.unknown(list_type)
        marked = value.mark(SENSITIVE)

        bare, paths = unmark_deep_with_paths(marked)

        assert not bare.marks
        assert SENSITIVE in mark_with_paths(bare, paths).marks


class TestSets:
    def test_a_marked_set_element_is_hoisted_rather_than_dropped(self) -> None:
        """Set elements have no stable path, so their marks move up.

        A set keys its elements by value, and marking one changes it -- so a
        path recorded on the way out would not resolve on the way back. cty's
        own `CtySet.validate` already hoists element marks onto the set for the
        same reason. Less precise than go-cty and in the safe direction: the
        mark is recorded higher up, never lost.
        """
        set_type = CtySet(element_type=S)
        value = CtyValue(vtype=set_type, value=frozenset({S.validate("a").mark(SENSITIVE)}))

        bare, paths = unmark_deep_with_paths(value)

        assert {str(path): marks for path, marks in paths.items()} == {"(root)": frozenset({SENSITIVE})}
        assert all(not element.marks for element in bare.value)


# 🌊🪢🔚
