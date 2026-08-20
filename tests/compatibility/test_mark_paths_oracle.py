#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`UnmarkDeepWithPaths` and `MarkWithPaths`, against real go-cty.

Marks are how sensitivity travels, and this pair is the only lossless way to put
a value through something that cannot carry them -- serialize, compute, restore.
So the thing worth comparing is not that the marks come off, but that the paths
point back at the same places: a path that resolves somewhere else on the way in
silently moves a sensitivity flag onto the wrong value, and a path that resolves
nowhere drops it.

Paths are compared structurally rather than as display strings. go-cty spells a
map key as an index step holding a string and this library has a distinct
`KeyStep`; comparing the two renderings would compare spelling conventions
instead of locations.

Sets are absent on purpose. go-cty's `SetVal` panics on a marked element, so a
set whose element carries a mark is not a value go-cty can be asked about --
which is why this library hoists such marks onto the set instead, covered by
`tests/values/test_mark_paths.py`.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.mark_paths import mark_with_paths, unmark_deep_with_paths
from pyvider.cty.path import CtyPath
from tests.compatibility._oracle import canonical, rich, run, type_spec
from tests.compatibility._traversal import step_form

pytestmark = pytest.mark.compat

STRINGS = CtyList(element_type=CtyString())
STRING_MAP = CtyMap(element_type=CtyString())
PAIR = CtyObject(attribute_types={"a": CtyString(), "b": CtyNumber()})
NESTED = CtyObject(attribute_types={"inner": STRINGS})
TUPLE = CtyTuple(element_types=(CtyString(), CtyNumber()))

SENSITIVE = frozenset({"sensitive"})


def _ordered(entries: Any) -> list[str]:
    """Entries as sorted, key-order-independent strings.

    Sorting the dicts by `repr` compares their key insertion order, which is a
    property of how each side happened to build them and not of where the marks
    were found.
    """
    return sorted(json.dumps(entry, sort_keys=True, default=str) for entry in entries)


def _paths_here(value: CtyValue[Any]) -> list[str]:
    _, found = unmark_deep_with_paths(value)
    return _ordered(
        {
            "path": [step_form(step) for step in path.steps],
            "marks": sorted(str(mark) for mark in marks),
        }
        for path, marks in found.items()
    )


def _theirs(cty_type: CtyType[Any], value: CtyValue[Any]) -> dict[str, Any]:
    result = run("cty", "marks", "--type", type_spec(cty_type), json.dumps(rich(value)))
    assert result["ok"], result
    return result


CASES: list[tuple[str, CtyType[Any], CtyValue[Any]]] = [
    ("a marked string", CtyString(), CtyString().validate("x").with_marks(SENSITIVE)),
    ("two marks on one value", CtyString(), CtyString().validate("x").with_marks({"a", "b"})),
    ("a marked null", CtyString(), CtyValue.null(CtyString()).with_marks(SENSITIVE)),
    ("a marked unknown", CtyString(), CtyValue.unknown(CtyString()).with_marks(SENSITIVE)),
    ("nothing marked", STRINGS, STRINGS.validate(["a", "b"])),
    (
        "a marked list element",
        STRINGS,
        STRINGS.validate([CtyString().validate("a").with_marks(SENSITIVE), "b"]),
    ),
    (
        "two marked list elements",
        STRINGS,
        STRINGS.validate(
            [
                CtyString().validate("a").with_marks(SENSITIVE),
                CtyString().validate("b").with_marks({"other"}),
            ]
        ),
    ),
    ("a marked list", STRINGS, STRINGS.validate(["a"]).with_marks(SENSITIVE)),
    (
        "a mark on both the list and its element",
        STRINGS,
        STRINGS.validate([CtyString().validate("a").with_marks(SENSITIVE)]).with_marks({"outer"}),
    ),
    (
        "a marked attribute",
        PAIR,
        PAIR.validate({"a": CtyString().validate("x").with_marks(SENSITIVE), "b": 1}),
    ),
    (
        "a marked map value",
        STRING_MAP,
        STRING_MAP.validate({"k": CtyString().validate("x").with_marks(SENSITIVE), "j": "y"}),
    ),
    (
        "a mark two levels down",
        NESTED,
        NESTED.validate({"inner": [CtyString().validate("a").with_marks(SENSITIVE)]}),
    ),
    (
        "a marked tuple element",
        TUPLE,
        TUPLE.validate([CtyString().validate("x").with_marks(SENSITIVE), 1]),
    ),
]

IDS = [case[0] for case in CASES]


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_the_stripped_value_is_the_same(label: str, cty_type: CtyType[Any], value: CtyValue[Any]) -> None:
    theirs = _theirs(cty_type, value)

    stripped, _ = unmark_deep_with_paths(value)
    assert canonical(rich(stripped)) == canonical(theirs["unmarked"]), label


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_the_marks_were_found_in_the_same_places(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    theirs = _theirs(cty_type, value)

    # Sorted, not sequenced: go-cty walks an object's attributes in Go map
    # order, which is deliberately randomised per run, so the order of the
    # reported paths is not part of the answer.
    assert _paths_here(value) == _ordered(canonical(entry) for entry in theirs["paths"]), label


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_the_round_trip_restores_the_original(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    """Both implementations must put every mark back where it came from."""
    theirs = _theirs(cty_type, value)
    assert theirs["round_trip_equal"] is True, label

    stripped, found = unmark_deep_with_paths(value)
    assert mark_with_paths(stripped, found) == value, label


def test_a_path_that_no_longer_resolves_is_skipped() -> None:
    """Not compared against go-cty, because go-cty panics instead.

    `MarkWithPaths` calls `ApplyPath` and lets its error surface as a panic. A
    restore is routinely attempted against a value that changed shape in
    between -- that is what a round trip through the wire does to an unknown --
    and taking the whole process down loses every other mark along with the one
    that moved.
    """
    value = STRINGS.validate(["a"])
    stale = {CtyPath.empty().index_step(5): SENSITIVE}

    assert mark_with_paths(value, stale) == value


# 🌊🪢🔚
