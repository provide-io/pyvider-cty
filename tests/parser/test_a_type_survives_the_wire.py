#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Every type round-trips through its wire JSON unchanged.

`_to_wire_json` and `parse_tf_type_to_ctytype` are the two halves of how a type
crosses a process boundary, and **every differential test in this repository
rests on them**: `tests/compatibility/_oracle.type_spec` spells our type for the
harness with the first, and the harness builds its own type from that spelling.
A type that loses something on the way out would not make the comparisons fail
-- it would make them compare the wrong thing, quietly, and agree.

That is the same shape as the blind spot in
`tests/values/test_nothing_is_lost_before_the_comparison.py`, one level up: a
loss that happens *before* the comparison cannot be seen by the comparison.

Both directions are asserted, because they fail differently. Parsing back to an
equal type catches a loss of meaning; re-spelling to identical JSON catches a
loss of *form* -- two spellings of one type would still compare equal here while
producing different bytes at the harness.
"""

from __future__ import annotations

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
from pyvider.cty.parser import parse_tf_type_to_ctytype

S, N, B, D = CtyString(), CtyNumber(), CtyBool(), CtyDynamic()

TYPES: list[tuple[str, CtyType[Any]]] = [
    ("string", S),
    ("number", N),
    ("bool", B),
    ("dynamic", D),
    ("list(string)", CtyList(element_type=S)),
    ("set(number)", CtySet(element_type=N)),
    ("map(bool)", CtyMap(element_type=B)),
    ("list(dynamic)", CtyList(element_type=D)),
    ("list(list(string))", CtyList(element_type=CtyList(element_type=S))),
    # The empty containers, which are the ones a spelling is most likely to
    # normalise into something else.
    ("tuple()", CtyTuple(element_types=())),
    ("object{}", CtyObject(attribute_types={})),
    ("tuple(string,number)", CtyTuple(element_types=(S, N))),
    (
        "tuple(list(string),object)",
        CtyTuple(element_types=(CtyList(element_type=S), CtyObject(attribute_types={"a": N}))),
    ),
    ("object{a,b}", CtyObject(attribute_types={"a": S, "b": N})),
    # Optional attributes travel in a third element of the object spec, which is
    # the part a round-trip is most likely to drop.
    ("object with an optional", CtyObject(attribute_types={"a": S}, optional_attributes=frozenset({"a"}))),
    (
        "object with one of two optional",
        CtyObject(attribute_types={"a": S, "b": N}, optional_attributes=frozenset({"b"})),
    ),
    ("deeply nested", CtyObject(attribute_types={"a": CtyMap(element_type=CtySet(element_type=D))})),
    # Attribute order: the spelling sorts, and a round-trip must not depend on
    # the order they were declared in.
    ("attributes out of order", CtyObject(attribute_types={"z": S, "a": N})),
]


@pytest.mark.parametrize(("label", "cty_type"), TYPES, ids=[case[0] for case in TYPES])
def test_a_type_parses_back_to_itself(label: str, cty_type: CtyType[Any]) -> None:
    """Meaning survives. `json.dumps`/`loads` is included so nothing rests on
    the in-memory object being handed straight back."""
    spelled = json.loads(json.dumps(cty_type._to_wire_json()))

    assert parse_tf_type_to_ctytype(spelled).equal(cty_type), label


@pytest.mark.parametrize(("label", "cty_type"), TYPES, ids=[case[0] for case in TYPES])
def test_the_spelling_is_stable(label: str, cty_type: CtyType[Any]) -> None:
    """Form survives too: re-spelling the parsed type gives identical JSON.

    Equality alone would accept two spellings of one type, and the harness reads
    the spelling rather than the type.
    """
    spelled = cty_type._to_wire_json()
    reparsed = parse_tf_type_to_ctytype(json.loads(json.dumps(spelled)))

    assert reparsed._to_wire_json() == spelled, label


def test_an_optional_attribute_is_not_lost() -> None:
    """Named separately: optionality is the one bit of an object's spelling that
    is carried outside the attribute map, so it is the one a round-trip drops
    without changing anything else."""
    original = CtyObject(attribute_types={"a": S, "b": N}, optional_attributes=frozenset({"b"}))

    reparsed = parse_tf_type_to_ctytype(json.loads(json.dumps(original._to_wire_json())))

    assert isinstance(reparsed, CtyObject)
    assert reparsed.optional_attributes == frozenset({"b"})


# 🌊🪢🔚
