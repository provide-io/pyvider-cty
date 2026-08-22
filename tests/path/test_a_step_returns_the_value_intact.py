#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A path step hands back the value it selected, whole.

Two defects met here. A step out of a marked container dropped the container's
marks, the same way a subscript did -- see
`tests/values/test_marks_survive_selection.py` for the go-cty citation.

And a step *through* a `dynamic` wrapper rebuilt its answer as
`CtyValue(result.type, result.value)`, which keeps two of the five fields a
`CtyValue` has. A null came back as `is_null=False, value=None`; an unknown as
`is_unknown=False, value=UNREFINED_UNKNOWN`; a refined unknown as a known value
whose payload was a `RefinedUnknownValue`. None of those three is a value this
library can represent, so the check is internal consistency rather than
go-cty parity: go-cty has no known-dynamic value to compare against, because
`Index` and `GetAttr` on a `DynamicPseudoType` receiver return `DynamicVal`.
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
from pyvider.cty.refinement import refine
from pyvider.cty.values.markers import RefinedUnknownValue

S, N = CtyString(), CtyNumber()
SENSITIVE = CtyMark("sensitive")
OTHER = CtyMark("other")

LIST = CtyList(element_type=S)
MAP = CtyMap(element_type=S)
OBJECT = CtyObject({"a": S})
TUPLE = CtyTuple((S, N))
SET = CtySet(element_type=S)


def _marked_traversals() -> list[tuple[str, CtyValue[object], CtyPath]]:
    return [
        ("list", LIST.validate(["x"]).mark(SENSITIVE), CtyPath.index(0)),
        ("tuple", TUPLE.validate(("x", 1)).mark(SENSITIVE), CtyPath.index(0)),
        ("map", MAP.validate({"k": "x"}).mark(SENSITIVE), CtyPath.key("k")),
        ("object", OBJECT.validate({"a": "x"}).mark(SENSITIVE), CtyPath.get_attr("a")),
        ("set", SET.validate(["x"]).mark(SENSITIVE), CtyPath.key(S.validate("x"))),
    ]


@pytest.mark.parametrize(
    ("kind", "container", "path"), _marked_traversals(), ids=lambda p: p if isinstance(p, str) else ""
)
class TestAStepCarriesTheContainersMarks:
    def test_the_selected_value_is_marked(self, kind: str, container: CtyValue[object], path: CtyPath) -> None:
        assert path.apply_path(container).marks == frozenset({SENSITIVE})

    def test_the_selected_value_is_otherwise_unchanged(
        self, kind: str, container: CtyValue[object], path: CtyPath
    ) -> None:
        assert path.apply_path(container).value == "x"


class TestMarksAccumulate:
    def test_an_elements_own_mark_survives_alongside_the_containers(self) -> None:
        marked = LIST.validate([S.validate("x").mark(OTHER)]).mark(SENSITIVE)
        assert CtyPath.index(0).apply_path(marked).marks == frozenset({SENSITIVE, OTHER})

    def test_a_two_step_path_unions_both_levels(self) -> None:
        inner = OBJECT.validate({"a": "x"}).mark(OTHER)
        outer = CtyList(element_type=OBJECT).validate([inner]).mark(SENSITIVE)
        selected = CtyPath.index(0).child("a").apply_path(outer)
        assert selected.marks == frozenset({SENSITIVE, OTHER})


class TestAnUnknownContainerHandsBackAMarkedUnknown:
    def test_index_into_an_unknown_list(self) -> None:
        selected = CtyPath.index(0).apply_path(CtyValue.unknown(LIST).mark(SENSITIVE))
        assert selected.is_unknown and selected.marks == frozenset({SENSITIVE})

    def test_key_into_an_unknown_map(self) -> None:
        selected = CtyPath.key("k").apply_path(CtyValue.unknown(MAP).mark(SENSITIVE))
        assert selected.is_unknown and selected.marks == frozenset({SENSITIVE})


class TestThroughADynamicWrapper:
    """The receiver is `dynamic` and the payload is a concrete value."""

    def test_a_null_element_stays_null(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate([CtyValue.null(S)]))
        selected = CtyPath.index(0).apply_path(wrapped)
        assert selected.is_null
        assert selected.value is None

    def test_an_unknown_element_stays_unknown(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate([CtyValue.unknown(S)]))
        selected = CtyPath.index(0).apply_path(wrapped)
        assert selected.is_unknown

    def test_a_refined_unknown_keeps_its_refinement(self) -> None:
        refined = refine(CtyValue.unknown(S)).string_prefix("sec").new_value()
        wrapped = CtyDynamic().validate(LIST.validate([refined]))
        selected = CtyPath.index(0).apply_path(wrapped)
        assert selected.is_unknown
        assert isinstance(selected.value, RefinedUnknownValue)
        # Compared against the refinement that went in rather than the literal
        # "sec": `string_prefix` trims a trailing grapheme that could still be
        # extended, so what survives is what was stored, not what was asked for.
        assert selected.value == refined.value

    def test_a_marked_element_keeps_its_mark(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate([S.validate("x").mark(OTHER)]))
        assert CtyPath.index(0).apply_path(wrapped).marks == frozenset({OTHER})

    def test_a_marked_wrapper_marks_what_it_hands_back(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate(["x"])).mark(SENSITIVE)
        assert CtyPath.index(0).apply_path(wrapped).marks == frozenset({SENSITIVE})

    def test_a_null_map_element_stays_null(self) -> None:
        wrapped = CtyDynamic().validate(MAP.validate({"k": CtyValue.null(S)}))
        selected = CtyPath.key("k").apply_path(wrapped)
        assert selected.is_null
        assert selected.value is None

    def test_an_unknown_map_element_stays_unknown(self) -> None:
        wrapped = CtyDynamic().validate(MAP.validate({"k": CtyValue.unknown(S)}))
        assert CtyPath.key("k").apply_path(wrapped).is_unknown

    def test_a_known_element_comes_through_unharmed(self) -> None:
        wrapped = CtyDynamic().validate(LIST.validate(["x"]))
        selected = CtyPath.index(0).apply_path(wrapped)
        assert selected.type.equal(S)
        assert selected.value == "x"
        assert not selected.is_null and not selected.is_unknown


class TestGetAttrTraversesADynamicWrapperToo:
    """`IndexStep` and `KeyStep` both step through a wrapper; `GetAttrStep` did not."""

    def test_an_attribute_is_reachable_through_a_wrapper(self) -> None:
        wrapped = CtyDynamic().validate(OBJECT.validate({"a": "x"}))
        assert CtyPath.get_attr("a").apply_path(wrapped).value == "x"

    def test_a_null_attribute_stays_null(self) -> None:
        wrapped = CtyDynamic().validate(CtyObject({"a": S}).validate({"a": CtyValue.null(S)}))
        selected = CtyPath.get_attr("a").apply_path(wrapped)
        assert selected.is_null
        assert selected.value is None

    def test_a_marked_wrapper_marks_the_attribute(self) -> None:
        wrapped = CtyDynamic().validate(OBJECT.validate({"a": "x"})).mark(SENSITIVE)
        assert CtyPath.get_attr("a").apply_path(wrapped).marks == frozenset({SENSITIVE})


# 🌊🪢🔚
