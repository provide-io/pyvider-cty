#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The traversal surfaces, against real go-cty, on values neither side chose.

`walk`, `transform`, `unknown_as_null` and `mark_paths` were the last four
surfaces still held by tables alone. Each had a careful oracle module and each
could only find a divergence somebody had already suspected -- which is exactly
what the stdlib was in before 2026-08-19, when generated arguments turned up
sixteen divergences across functions that all had hand-written rows.

Traversal is where a generator earns the most, because everything that decides
the answer is *shape*: which container was entered first, whether a null was
descended into, what a set element's path says, whether an empty container was
rebuilt or returned. Those are the properties a chosen example fixes by
accident and a drawn one does not.

The values come from `_strategies.cases()`, the same population the codec
properties use, so a shape that has broken a codec is a shape this sees too.
The vocabulary -- path steps, visit records, the two named rewrites -- comes
from `_traversal`, so this compares through exactly the translation the
table-driven modules compare through, and a fault in that translation cannot
show up as agreement here and a divergence there.

Two narrowings, both recorded rather than worked around:

  * **Sets are excluded from the mark property.** go-cty's `SetVal` panics on a
    marked element, so a set holding a marked element is not a value go-cty can
    be asked about at all. `tests/values/test_mark_paths.py` covers what this
    library does there instead (it hoists the mark onto the set).
  * **Marks are placed by walking the value**, not drawn independently. A path
    drawn at random mostly does not resolve, and a property that spends its
    examples on unresolvable paths is a property that tests nothing.
"""

from __future__ import annotations

from typing import Any
import warnings

from hypothesis import assume, given, settings, strategies as st
from hypothesis.errors import NonInteractiveExampleWarning
import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.mark_paths import mark_with_paths, unmark_deep_with_paths
from pyvider.cty.unknown import unknown_as_null
from pyvider.cty.walk import deep_values, transform, walk
from tests.compatibility._oracle import canonical, examples, rich, type_spec
from tests.compatibility._strategies import cases
from tests.compatibility._traversal import (
    REWRITES,
    implied_type,
    mark_paths_here,
    ordered,
    subject,
    traversal_answer,
    visit_form,
)

pytestmark = pytest.mark.compat

# One subprocess per property per example, as everywhere else in this directory.
# `PYVIDER_COMPAT_EXAMPLES=400 make compat` widens all of them at once.
EXAMPLES = examples(40)

SENSITIVE = frozenset({"sensitive"})

Case = tuple[CtyType[Any], CtyValue[Any]]


def _contains_a_set(cty_type: CtyType[Any]) -> bool:
    """Walked, not recursed -- the lesson `CtyTuple.equal` taught on 2026-08-20."""
    pending: list[CtyType[Any]] = [cty_type]
    while pending:
        current = pending.pop()
        match current:
            case CtySet():
                return True
            case CtyList() | CtyMap():
                pending.append(current.element_type)
            case CtyTuple():
                pending.extend(current.element_types)
            case CtyObject():
                pending.extend(current.attribute_types.values())
    return False


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_the_walk_visits_the_same_places_in_the_same_order(case: Case) -> None:
    """Order and paths together, which is the whole of what a walk decides.

    An object's attributes and a map's keys are visited in sorted order by
    go-cty, explicitly "so that results will always be stable given the same
    input"; both of this library's natural orders -- declaration and insertion --
    are properties of how the value was built rather than of the value.
    """
    cty_type, value = case

    theirs = traversal_answer("walk", cty_type, value)
    here = [visit_form(path, visited) for path, visited in deep_values(subject(cty_type, value))]

    assert here == [canonical(visit) for visit in theirs["visits"]], type_spec(cty_type)


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_declining_to_descend_stops_at_the_same_places(case: Case) -> None:
    """The callback's other answer, which a generator cannot express.

    Pruning at depth 1 keeps the root and its immediate children and stops. A
    walk that ignores the answer visits values the caller asked not to see, and
    for a sensitive subtree "asked not to see" can be the point.
    """
    cty_type, value = case

    theirs = traversal_answer("walk", cty_type, value, "--prune-depth", "1")

    here: list[dict[str, Any]] = []

    def visit(path: Any, visited: CtyValue[Any]) -> bool:
        here.append(visit_form(path, visited))
        return len(path.steps) < 1

    walk(subject(cty_type, value), visit)

    assert here == [canonical(visit_record) for visit_record in theirs["visits"]], type_spec(cty_type)


@pytest.mark.parametrize("op", sorted(REWRITES))
@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_transform_rebuilds_the_same_value(op: str, case: Case) -> None:
    """Rebuilding is where a traversal loses things: an element type off an
    emptied container, a mark off a leaf it rewrote, a refinement off an unknown
    it left alone."""
    cty_type, value = case

    theirs = traversal_answer("transform", cty_type, value, "--op", op)
    here = transform(subject(cty_type, value), REWRITES[op])

    assert canonical(rich(here)) == canonical(theirs["value"]), f"{type_spec(cty_type)} / {op}"
    assert implied_type(here.type) == theirs["type"], f"{type_spec(cty_type)} / {op}: type"


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_unknown_as_null_rewrites_to_the_same_value(case: Case) -> None:
    """A purpose-built walk with two answers that are not obvious from the name:
    a set of two unknowns collapses to a set of one null, because rewriting the
    elements makes them equal and the set re-deduplicates; and an empty container
    is returned untouched, so rebuilding it is never a chance to lose its element
    type."""
    cty_type, value = case

    theirs = traversal_answer("unknown-as-null", cty_type, value)
    here = unknown_as_null(subject(cty_type, value))

    assert canonical(rich(here)) == canonical(theirs["value"]), type_spec(cty_type)
    assert implied_type(here.type) == theirs["type"], f"{type_spec(cty_type)}: type"


def _paths_of(value: CtyValue[Any]) -> list[Any]:
    return [path for path, _ in deep_values(value)]


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases(), st.integers(min_value=0, max_value=32))
def test_a_mark_is_found_at_the_place_it_was_put(case: Case, offset: int) -> None:
    """`UnmarkDeepWithPaths` is the only lossless way to put a value through
    something that cannot carry marks -- serialize, compute, restore -- so what
    matters is not that the marks come off but that the paths point back at the
    same places. A path that resolves somewhere else silently moves a
    sensitivity flag onto the wrong value; one that resolves nowhere drops it.

    The mark is placed at a path taken from the value's *own* walk, so it always
    resolves. A path drawn independently mostly does not, and a property that
    spends its examples on unresolvable paths tests nothing.
    """
    cty_type, value = case
    assume(not _contains_a_set(cty_type))
    assume(not isinstance(cty_type, CtyDynamic))

    places = _paths_of(value)
    marked = mark_with_paths(value, {places[offset % len(places)]: SENSITIVE})

    theirs = traversal_answer("marks", cty_type, marked)

    assert mark_paths_here(marked) == ordered(canonical(entry) for entry in theirs["paths"]), type_spec(
        cty_type
    )


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases(), st.integers(min_value=0, max_value=32))
def test_stripping_the_marks_leaves_the_same_value(case: Case, offset: int) -> None:
    """The other half of the round trip, and the half that reaches the wire:
    what is left after the marks come off is what gets serialized."""
    cty_type, value = case
    assume(not _contains_a_set(cty_type))
    assume(not isinstance(cty_type, CtyDynamic))

    places = _paths_of(value)
    marked = mark_with_paths(value, {places[offset % len(places)]: SENSITIVE})

    theirs = traversal_answer("marks", cty_type, marked)
    stripped, _ = unmark_deep_with_paths(marked)

    assert canonical(rich(stripped)) == canonical(theirs["unmarked"]), type_spec(cty_type)
    assert theirs["round_trip_equal"] is True, type_spec(cty_type)


@settings(max_examples=EXAMPLES, deadline=None)
@given(cases())
def test_the_two_routes_to_unknown_as_null_agree(case: Case) -> None:
    """`unknown_as_null` is a purpose-built walk and `transform` is the general
    one carrying the same rewrite. Both are checked against go-cty above, so a
    fault in either traversal would have to be a fault in both to survive -- but
    this asks them of each other directly, which costs no subprocess and catches
    the case where both agree with go-cty for different reasons."""
    _, value = case

    assert transform(value, REWRITES["unknown-to-null"]) == unknown_as_null(value)


def test_the_generated_population_reaches_every_container_kind() -> None:
    """A guard on the generator, not on the library.

    Narrowing a strategy until it stops finding anything is the easy way to make
    a differential suite pass, so the population is asserted to still contain
    what it is here to exercise.
    """
    kinds: set[str] = set()
    # `.example()` warns that `@given` is the better tool, and it is -- for a
    # property. This is a census of the population itself, which `@given` cannot
    # express: it reports one falsifying case, not what the whole draw covered.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", NonInteractiveExampleWarning)
        strategy = cases()
        for _ in range(200):
            cty_type, _ = strategy.example()
            kinds.add(type(cty_type).__name__)

    assert {"CtyList", "CtySet", "CtyMap", "CtyObject", "CtyTuple"} <= kinds, sorted(kinds)


# 🌊🪢🔚
