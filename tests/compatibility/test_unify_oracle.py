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

Sweeping every pair and triple of a representative type set found **4 divergent
combinations out of 455**, in one shape, recorded below.

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
    ("tuple(string,number)", CtyTuple(element_types=(S, N))),
    ("tuple(string,string)", CtyTuple(element_types=(S, S))),
    ("object{a:string}", CtyObject(attribute_types={"a": S})),
    ("object{a:number}", CtyObject(attribute_types={"a": N})),
    ("object{a:string,b:number}", CtyObject(attribute_types={"a": S, "b": N})),
]

# The one shape where the two disagree, by label. Both members need a `dynamic`,
# a list and a tuple together: with any two of the three the answers match.
# go-cty lets the *list's* element type survive, where this package unifies the
# tuple's elements first and carries that result into the list.
#
# Worth noting what go-cty does here, because it is what makes the case odd:
# adding a `dynamic` -- a wildcard that conforms to anything -- *changes* its
# answer, from `list(string)` without it to `list(number)` with it. Matching
# that means reproducing `convert`'s unification order, which is a piece of work
# rather than a patch, so it is recorded here and not yet decided.
KNOWN_DIVERGENCES = {
    "dynamic + list(number) + tuple(string,number)",
    "dynamic + list(dynamic) + tuple(string,number)",
    "dynamic + list(number) + tuple(string,string)",
    "dynamic + list(dynamic) + tuple(string,string)",
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
                reason="dynamic + list + tuple: go-cty keeps the list's element type",
                strict=True,
            )
        )

    assert _ours(types) == _theirs(types), label


def test_the_divergence_list_is_not_stale() -> None:
    """Every recorded entry has to name a combination this sweep drives."""
    labels = {label for label, _types in CASES}

    assert labels >= KNOWN_DIVERGENCES, KNOWN_DIVERGENCES - labels


# 🌊🪢🔚
