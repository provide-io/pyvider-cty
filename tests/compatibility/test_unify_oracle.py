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

Sweeping every pair and triple of a representative type set finds **17 divergent
combinations out of 969**, in two shapes, recorded below. The first version of
this sweep used a flat type set and found four: without a nested element type or
an empty tuple in the mix, most of the surface is unreachable.

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
    # Nested element types. A flat set of types cannot reach the case where the
    # *element* unification is what differs.
    ("list(list(string))", CtyList(element_type=CtyList(element_type=S))),
    ("list(object{a:string})", CtyList(element_type=CtyObject(attribute_types={"a": S}))),
    ("set(list(string))", CtySet(element_type=CtyList(element_type=S))),
]

# Every combination the two answer differently. All seventeen share three
# ingredients: a `dynamic` (bare, or as a list's element type), a list or set,
# and a tuple. With any two of the three the answers agree, which is why a flat
# type set found only five of them -- the first version of this sweep had no
# nested element types and no empty tuple, and reported four.
#
# Two shapes, and the first is the worse one:
#
#   * **This package unifies where go-cty refuses.**
#     `unify(tuple(list(string), number), list(dynamic))` is `list(dynamic)`
#     here and *no common type* in go-cty. A caller gets a container back where
#     real Terraform would have raised, so `concat` and `flatten` succeed here
#     and fail there.
#   * **This package loses a concrete element type to `dynamic`.**
#     `unify(list(list(string)), tuple(), list(dynamic))` is `list(list(string))`
#     in go-cty and `list(dynamic)` here.
#
# What makes the first shape odd is go-cty's own behaviour: adding a `dynamic`
# -- a wildcard that conforms to anything -- *changes* its answer, from
# `list(string)` without it to `list(number)` with it. Matching any of this
# means reproducing `convert`'s unification order rather than patching a rule,
# so it is recorded and not yet decided.
KNOWN_DIVERGENCES = {
    "dynamic + list(dynamic) + tuple(list(string),number)",
    "dynamic + list(dynamic) + tuple(string,number)",
    "dynamic + list(dynamic) + tuple(string,string)",
    "dynamic + list(number) + tuple(string,number)",
    "dynamic + list(number) + tuple(string,string)",
    "list(dynamic) + set(string) + tuple(list(string),number)",
    "list(dynamic) + tuple() + list(list(string))",
    "list(dynamic) + tuple() + list(object{a:string})",
    "list(dynamic) + tuple() + tuple(list(string),number)",
    "list(dynamic) + tuple(list(string),number)",
    "list(dynamic) + tuple(list(string),number) + list(list(string))",
    "list(dynamic) + tuple(list(string),number) + list(object{a:string})",
    "list(dynamic) + tuple(list(string),number) + set(list(string))",
    "list(dynamic) + tuple(string,number) + tuple(list(string),number)",
    "list(dynamic) + tuple(string,string) + tuple(list(string),number)",
    "list(number) + list(dynamic) + tuple(list(string),number)",
    "list(string) + list(dynamic) + tuple(list(string),number)",
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
                reason="dynamic + a list + a tuple: go-cty refuses, or keeps a concrete element type",
                strict=True,
            )
        )

    assert _ours(types) == _theirs(types), label


def test_the_divergence_list_is_not_stale() -> None:
    """Every recorded entry has to name a combination this sweep drives."""
    labels = {label for label, _types in CASES}

    assert labels >= KNOWN_DIVERGENCES, KNOWN_DIVERGENCES - labels


# 🌊🪢🔚
