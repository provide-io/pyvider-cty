#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`convert.Convert`, against real go-cty.

Conversion had only ever been checked *through* the three stdlib functions that
use it -- `tostring`, `tonumber`, `tobool` -- and that is how two earlier bugs
came to be filed against the functions when they were in `convert` underneath.
The harness's `cty convert` converts between serialization formats, not types,
so the conversion table itself had no oracle at all.

Four divergences came out of the first run, and the shape of them is worth
naming: **two were this library converting things go-cty refuses, and two were
its result carrying a type constraint where go-cty produces a concrete type.**

  - list-to-tuple and set-to-tuple were performed here and do not exist in
    go-cty's table. `can_convert_unsafe` already said they were impossible, so
    `convert` was also contradicting its own predicate -- unification asks that
    predicate, so it could refuse a type `convert` would have reached.
  - map-to-object was *missing*, so a provider decoding `map(string)` config
    into a schema object was simply refused.
  - converting to an object type with optional attributes produced a value
    whose type still said "optional", which is a constraint describing a value
    that already exists.
  - converting to `list(any)` produced `list(dynamic)` rather than resolving the
    element type from the source, so a provider returning one told Terraform
    nothing about its elements.

A fifth was in the harness. `GetConversionUnsafe(string, string)` returns nil --
identical types need no conversion function -- and reading that as "not
convertible" made the most ordinary case in the table look like a divergence.
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
    CtyValue,
)
from pyvider.cty.conversion import can_convert_unsafe, convert
from pyvider.cty.exceptions import CtyConversionError
from tests.compatibility._oracle import canonical, rich, run, type_spec

pytestmark = pytest.mark.compat

S = CtyString()
N = CtyNumber()
B = CtyBool()
D = CtyDynamic()
LS = CtyList(element_type=S)
LN = CtyList(element_type=N)
SS = CtySet(element_type=S)
MS = CtyMap(element_type=S)
MN = CtyMap(element_type=N)
TSS = CtyTuple(element_types=(S, S))
TSN = CtyTuple(element_types=(S, N))
OBJ = CtyObject(attribute_types={"a": S})
OBJ_N = CtyObject(attribute_types={"a": N})
OBJ_TWO = CtyObject(attribute_types={"a": S, "b": N})
OBJ_OPT = CtyObject(attribute_types={"a": S, "b": N}, optional_attributes=frozenset({"b"}))

# (label, source type, value, target type)
CASES: list[tuple[str, CtyType[Any], CtyValue[Any], CtyType[Any]]] = [
    ("a number to a string", N, N.validate(5), S),
    ("a fraction to a string", N, N.validate("1.50"), S),
    ("an exponent to a string", N, N.validate("1e2"), S),
    ("a string to a number", S, S.validate("5"), N),
    ("a string that is not a number", S, S.validate("abc"), N),
    ("a bool to a string", B, B.validate(True), S),
    ("a string to a bool", S, S.validate("true"), B),
    ("a string to a bool, wrong case", S, S.validate("TRUE"), B),
    ("a one to a bool", S, S.validate("1"), B),
    ("a number to a bool", N, N.validate(1), B),
    ("a bool to a number", B, B.validate(True), N),
    ("a string to itself", S, S.validate("x"), S),
    ("a null through a conversion", N, CtyValue.null(N), S),
    ("an unknown through a conversion", N, CtyValue.unknown(N), S),
    ("a null with no conversion available", LS, CtyValue.null(LS), N),
    ("a list to a set", LS, LS.validate(["a", "a", "b"]), SS),
    ("a set to a list", SS, SS.validate(["b", "a"]), LS),
    ("a tuple to a list", TSS, TSS.validate(["a", "b"]), LS),
    ("a mixed tuple to a list", TSN, TSN.validate(["a", 1]), LS),
    ("a tuple to a set", TSS, TSS.validate(["a", "a"]), SS),
    ("a list of numbers to a list of strings", LN, LN.validate([1, 2]), LS),
    ("an empty list to a set", LS, LS.validate([]), SS),
    ("a list holding a null to a set", LS, LS.validate(["a", CtyValue.null(S)]), SS),
    ("a null list to a set", LS, CtyValue.null(LS), SS),
    # The two go-cty does not have. A collection's length is a property of the
    # value and a tuple's is part of its type.
    ("a list to a tuple", LS, LS.validate(["a", "b"]), TSS),
    ("a set to a tuple", SS, SS.validate(["a", "b"]), TSS),
    ("a map to an object", MS, MS.validate({"a": "x"}), OBJ),
    ("a map with a spare key to an object", MS, MS.validate({"a": "x", "z": "y"}), OBJ),
    ("a map missing a required attribute", MS, MS.validate({"z": "y"}), OBJ),
    ("a map missing an optional attribute", MS, MS.validate({"a": "x"}), OBJ_OPT),
    ("a map whose elements need converting", MN, MN.validate({"a": 5}), OBJ),
    ("an object to a map", OBJ, OBJ.validate({"a": "x"}), MS),
    ("an object attribute needing conversion", OBJ, OBJ.validate({"a": "5"}), OBJ_N),
    ("an object missing an optional attribute", OBJ, OBJ.validate({"a": "x"}), OBJ_OPT),
    ("an object missing a required attribute", OBJ, OBJ.validate({"a": "x"}), OBJ_TWO),
    (
        "an object with a spare attribute",
        CtyObject(attribute_types={"a": S, "z": S}),
        CtyObject(attribute_types={"a": S, "z": S}).validate({"a": "x", "z": "y"}),
        OBJ,
    ),
    ("anything to dynamic", LS, LS.validate(["a"]), D),
    ("a dynamic to a string", D, D.validate("x"), S),
    # `list(any)` is the absence of a constraint, not a request for dynamics.
    ("a list to a list of any", LS, LS.validate(["a"]), CtyList(element_type=D)),
    ("a set to a list of any", SS, SS.validate(["a"]), CtyList(element_type=D)),
    ("a uniform tuple to a list of any", TSS, TSS.validate(["a", "b"]), CtyList(element_type=D)),
    ("an empty list to a list of any", LS, LS.validate([]), CtyList(element_type=D)),
    ("a string to a list", S, S.validate("x"), LS),
    ("a list to a number", LS, LS.validate(["a"]), N),
    ("an object to an unrelated object", OBJ, OBJ.validate({"a": "x"}), CtyObject(attribute_types={"q": S})),
    (
        "a list of objects to a list of objects",
        CtyList(element_type=OBJ),
        CtyList(element_type=OBJ).validate([{"a": "5"}]),
        CtyList(element_type=OBJ_N),
    ),
    (
        "a nested optional attribute",
        CtyObject(attribute_types={"inner": OBJ}),
        CtyObject(attribute_types={"inner": OBJ}).validate({"inner": {"a": "x"}}),
        CtyObject(attribute_types={"inner": OBJ_OPT}),
    ),
]

IDS = [case[0] for case in CASES]


def _theirs(source: CtyType[Any], value: CtyValue[Any], target: CtyType[Any]) -> dict[str, Any]:
    return run(
        "cty",
        "convert-value",
        "--from",
        type_spec(source),
        "--to",
        type_spec(target),
        json.dumps(rich(value)),
    )


@pytest.mark.parametrize(("label", "source", "value", "target"), CASES, ids=IDS)
def test_the_two_convert_the_same_way(
    label: str, source: CtyType[Any], value: CtyValue[Any], target: CtyType[Any]
) -> None:
    theirs = _theirs(source, value, target)

    if not theirs["ok"]:
        with pytest.raises(CtyConversionError):
            convert(value, target)
        return

    here = convert(value, target)
    assert canonical(rich(here)) == canonical(theirs["value"]), label
    assert json.loads(type_spec(here.type)) == theirs["type"], f"{label}: result type"


@pytest.mark.parametrize(("label", "source", "value", "target"), CASES, ids=IDS)
def test_the_predicate_agrees_with_go_cty(
    label: str, source: CtyType[Any], value: CtyValue[Any], target: CtyType[Any]
) -> None:
    """`can_convert_unsafe` is `GetConversionUnsafe` as a question about types.

    Unification asks it, so a divergence here means unification proposes a type
    nothing can reach, or refuses one that is reachable.
    """
    theirs = _theirs(source, value, target)

    assert can_convert_unsafe(source, target) == theirs["unsafe"], label


@pytest.mark.parametrize(("label", "source", "value", "target"), CASES, ids=IDS)
def test_the_predicate_agrees_with_this_librarys_own_convert(
    label: str, source: CtyType[Any], value: CtyValue[Any], target: CtyType[Any]
) -> None:
    """The internal half, which is how the list-to-tuple divergence was visible.

    `convert` performed a conversion `can_convert_unsafe` denied. A predicate
    that disagrees with the function it describes is wrong however go-cty
    behaves, so this holds without consulting the harness at all.

    The converse does not hold and is not asserted: "unsafe" means the
    conversion depends on the value, so a permitted conversion may still fail on
    a particular one -- `"abc"` to a number is the standing example.
    """
    try:
        convert(value, target)
    except CtyConversionError:
        return

    assert can_convert_unsafe(source, target), label


def test_a_conversion_result_never_carries_optional_attributes() -> None:
    """Optionality describes a constraint, and a converted value is not one.

    go-cty strips it in both directions -- deciding a conversion is unnecessary,
    and building the result -- and the difference reaches the wire, where a
    schema and a value would otherwise be told apart by it.
    """
    converted = convert(OBJ.validate({"a": "x"}), OBJ_OPT)

    assert isinstance(converted.type, CtyObject)
    assert converted.type.optional_attributes == frozenset()
    assert converted.value["b"].is_null


# 🌊🪢🔚
