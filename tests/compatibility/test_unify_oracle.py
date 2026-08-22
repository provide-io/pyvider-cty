#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Type unification, compared against real go-cty.

**Nothing compared this surface until 2026-08-19.** `unify` was in the harness's
`REQUIRED_COMMANDS` -- so a build without it was refused -- and no test ever
called it. `tests/conversion/test_unify_*.py` checks the answers against
expectations written here, which cannot see a divergence: an agreed-upon wrong
answer passes.

The surface is load-bearing. Unification decides the element type of `concat`,
`flatten` and every set operation, and `setproduct` uses it to decide whether a
tuple argument is usable at all. An element type that differs from go-cty's is a
different type on the wire, not a different opinion.

Sweeping every pair and triple of a representative type set found **17 divergent
combinations out of 969**, in two shapes. All seventeen are fixed as of
2026-08-19 and this sweep is clean; a deeper run over sizes 2-4 with the same
types is clean too, at 2500 combinations.

The first version of this sweep used a *flat* type set and found four of the
seventeen. Without a nested element type or an empty tuple in the mix most of
the surface is unreachable, which is the reason `TYPES` below carries both.

`convert.Unify` (safe) is deliberately not compared: this package implements
`UnifyUnsafe` only -- `unify.py` reaches for `can_convert_unsafe` throughout --
so asking the harness for `--safe` compares two different functions. That was
the first version of this sweep and it reported 38 divergences, nearly all of
them that mistake.
"""

from __future__ import annotations

import itertools
import json
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
from pyvider.cty.conversion import unify
from tests.compatibility._oracle import run, type_spec

pytestmark = pytest.mark.compat

S, N, B, D = CtyString(), CtyNumber(), CtyBool(), CtyDynamic()

TYPES: list[tuple[str, CtyType[Any]]] = [
    ("string", S),
    ("number", N),
    ("bool", B),
    ("dynamic", D),
    ("list(string)", CtyList(element_type=S)),
    ("list(number)", CtyList(element_type=N)),
    ("list(dynamic)", CtyList(element_type=D)),
    ("set(string)", CtySet(element_type=S)),
    ("map(string)", CtyMap(element_type=S)),
    # An empty tuple, and a tuple whose elements have no common type of their
    # own. Both were missing from the first version of this sweep, and both turn
    # out to matter -- the divergences below are concentrated in them.
    ("tuple()", CtyTuple(element_types=())),
    ("tuple(string,number)", CtyTuple(element_types=(S, N))),
    ("tuple(string,string)", CtyTuple(element_types=(S, S))),
    ("tuple(list(string),number)", CtyTuple(element_types=(CtyList(element_type=S), N))),
    ("object{a:string}", CtyObject(attribute_types={"a": S})),
    ("object{a:number}", CtyObject(attribute_types={"a": N})),
    # A map whose element type is dynamic, and an object whose attributes have
    # no common type. Neither was here, and between them they are the case where
    # preferring the *more general* candidate is the wrong preference: go-cty
    # keeps the object, because the object cannot be re-cast as a map at all.
    # With only `map(string)` and single-attribute objects present, every pair
    # map-ified successfully and the question never arose.
    ("map(dynamic)", CtyMap(element_type=D)),
    (
        "object{a:list(string),b:number}",
        CtyObject(attribute_types={"a": CtyList(element_type=S), "b": N}),
    ),
    # Nested element types. A flat set of types cannot reach the case where the
    # *element* unification is what differs.
    ("list(list(string))", CtyList(element_type=CtyList(element_type=S))),
    ("list(object{a:string})", CtyList(element_type=CtyObject(attribute_types={"a": S}))),
    ("set(list(string))", CtySet(element_type=CtyList(element_type=S))),
]

# Empty, and kept. The seventeen entries that were here on 2026-08-19 are all
# fixed; the list stays so the next divergence has somewhere to go and so a
# regression names itself rather than appearing as a bare assertion failure.
#
# What they were, because the shape is worth remembering: every one needed a
# `dynamic` (bare, or as a list's element type), a list or set, and a tuple
# together, and with any two of the three the answers already agreed. Two
# faults produced them. `_unify_tuples_as_list` pooled every tuple's elements
# *and* every list's element type into one unification, where go-cty unifies
# only the tuples and then re-unifies with the tuples replaced. And
# `can_convert_unsafe` answered yes for every tuple against a
# `dynamic`-element collection, because `can_convert_unsafe(anything, dynamic)`
# is yes -- go-cty asks a different question there, unifying the tuple's own
# elements and refusing when they have no common type.
#
# The four below were uncovered on 2026-08-22 by adding `map(dynamic)` and
# `object{a:list(string),b:number}` to the set above. They are not regressions:
# each answers identically with and without the preference-order fix that landed
# alongside them, and they were simply unreachable while every object in the set
# had a single attribute that map-ified cleanly.
#
# Three of the four are this library being *more* permissive than go-cty, which
# is the worse direction: go-cty finds no common type and refuses, and this
# answers `map(dynamic)`. The fourth wants the object where this gives
# `map(dynamic)` -- the same fault the preference order fixes for the pair, but
# with a bare `dynamic` also present, which is exactly the case that fix holds
# back from because `_unify_objects_as_maps` gives up there and its refusal
# stops meaning "these cannot be a map".
#
# The real repair is in `_unify_objects_as_maps`: it should map-ify the objects
# and dynamics separately rather than abandoning the attempt whenever a bare
# `dynamic` is in the group. That is a larger change to the structural unifier
# than the preference order, and it is not attempted here.
KNOWN_DIVERGENCES: set[str] = {
    "dynamic + map(dynamic) + object{a:list(string),b:number}",
    "map(string) + map(dynamic) + object{a:list(string),b:number}",
    "object{a:string} + map(dynamic) + object{a:list(string),b:number}",
    "object{a:number} + map(dynamic) + object{a:list(string),b:number}",
}


def _combinations() -> list[tuple[str, list[CtyType[Any]]]]:
    rows = []
    for size in (2, 3):
        for combo in itertools.combinations(TYPES, size):
            rows.append((" + ".join(c[0] for c in combo), [c[1] for c in combo]))
    return rows


CASES = _combinations()


def _theirs(types: list[CtyType[Any]]) -> Any:
    """go-cty's `convert.UnifyUnsafe`, or None where it finds no common type."""
    reported = run("cty", "unify", *[type_spec(t) for t in types])
    return reported.get("unified") if reported.get("ok") else None


def _ours(types: list[CtyType[Any]]) -> Any:
    result = unify(list(types))
    return None if result is None else json.loads(type_spec(result))


@pytest.mark.parametrize(("label", "types"), CASES, ids=[case[0] for case in CASES])
def test_the_two_unify_the_same_way(label: str, types: list[CtyType[Any]], request: Any) -> None:
    """Every pair and triple of the representative set, including the refusals.

    `None` on both sides counts as agreement: finding no common type is an
    answer, and one side refusing where the other unifies is the failure that
    matters -- it means a caller gets a container whose element type the other
    implementation would not have chosen.
    """
    if label in KNOWN_DIVERGENCES:
        # A marker rather than `pytest.xfail()`, so the body runs and a fix
        # turns the entry red instead of leaving it to rot.
        request.node.add_marker(
            pytest.mark.xfail(
                reason="map(dynamic) + an object whose attributes do not unify: "
                "go-cty refuses, or keeps the object; this answers map(dynamic)",
                strict=True,
            )
        )

    assert _ours(types) == _theirs(types), label


def test_the_divergence_list_is_not_stale() -> None:
    """Every recorded entry has to name a combination this sweep drives."""
    labels = {label for label, _types in CASES}

    assert labels >= KNOWN_DIVERGENCES, KNOWN_DIVERGENCES - labels


# 🌊🪢🔚
