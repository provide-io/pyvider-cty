#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`Type.TestConformance`, against real go-cty -- messages included.

Most parity work compares answers. This compares *prose*, because that is what
this operation produces: go-cty's own comment says the compound cases exist "so
that we can report specifically what is non-conforming", and a message a
practitioner reads is the whole output. Two differences showed up here and both
were only visible once real go-cty could be asked:

  - a collection named itself as "set", where go-cty says "set of string"
  - an attribute name was quoted Python-style, `'b'`, where go-cty writes `"b"`

Neither changes a decision. Both are the difference between an error a
practitioner can compare against go-cty's documentation and one they cannot.

Paths are compared by rendering go-cty's structured steps into this library's
display spelling. go-cty marks a collection element with an index step holding
an *unknown* key -- "some element, we cannot say which" -- which is exactly what
`[*]` says here.
"""

from __future__ import annotations

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
from pyvider.cty.conformance import conformance_errors
from tests.compatibility._oracle import canonical, run, type_spec

pytestmark = pytest.mark.compat

S = CtyString()
N = CtyNumber()
B = CtyBool()


def _rendered(steps: list[Any]) -> str:
    """go-cty's structured path in this library's display spelling."""
    out = ""
    for step in steps:
        if "attr" in step:
            out = f"{out}.{step['attr']}" if out else str(step["attr"])
            continue
        key = canonical(step["index"])
        # An unknown key is go-cty saying "an element, we cannot say which".
        out += "[*]" if isinstance(key, dict) and key.get("$unknown") else f"[{int(key)}]"
    return out


def _theirs(given: CtyType[Any], want: CtyType[Any]) -> dict[str, Any]:
    result = run("cty", "conformance", "--given", type_spec(given), "--want", type_spec(want))
    assert result["ok"], result
    return result


CASES: list[tuple[str, CtyType[Any], CtyType[Any]]] = [
    ("identical", S, S),
    ("string for number", S, N),
    ("bool for string", B, S),
    ("anything for dynamic", CtyList(element_type=S), CtyDynamic()),
    ("dynamic for a concrete type", CtyDynamic(), S),
    ("list element type", CtyList(element_type=S), CtyList(element_type=N)),
    ("set element type", CtySet(element_type=S), CtySet(element_type=N)),
    ("map element type", CtyMap(element_type=S), CtyMap(element_type=N)),
    ("list for set", CtyList(element_type=S), CtySet(element_type=S)),
    ("list of dynamic accepts anything", CtyList(element_type=S), CtyList(element_type=CtyDynamic())),
    (
        "nested collections",
        CtyList(element_type=CtyList(element_type=S)),
        CtyList(element_type=CtyList(element_type=N)),
    ),
    ("attribute type", CtyObject(attribute_types={"a": S}), CtyObject(attribute_types={"a": N})),
    ("extra attribute", CtyObject(attribute_types={"a": S, "b": S}), CtyObject(attribute_types={"a": S})),
    ("missing attribute", CtyObject(attribute_types={"a": S}), CtyObject(attribute_types={"a": S, "b": S})),
    (
        "both extra and missing",
        CtyObject(attribute_types={"a": S, "b": S}),
        CtyObject(attribute_types={"a": S, "c": S}),
    ),
    (
        "an attribute holding a collection",
        CtyObject(attribute_types={"a": CtyList(element_type=S)}),
        CtyObject(attribute_types={"a": CtyList(element_type=N)}),
    ),
    (
        "a collection of objects",
        CtyList(element_type=CtyObject(attribute_types={"a": S})),
        CtyList(element_type=CtyObject(attribute_types={"a": N})),
    ),
    ("tuple length", CtyTuple(element_types=(S,)), CtyTuple(element_types=(S, N))),
    ("tuple element type", CtyTuple(element_types=(S, N)), CtyTuple(element_types=(S, S))),
    (
        "several wrong tuple elements",
        CtyTuple(element_types=(S, N, B)),
        CtyTuple(element_types=(N, S, B)),
    ),
    ("object for map", CtyObject(attribute_types={"a": S}), CtyMap(element_type=S)),
    ("collection for primitive", CtyList(element_type=S), N),
    (
        "dynamic inside a tuple accepts anything",
        CtyTuple(element_types=(S,)),
        CtyTuple(element_types=(CtyDynamic(),)),
    ),
]

IDS = [case[0] for case in CASES]


@pytest.mark.parametrize(("label", "given", "want"), CASES, ids=IDS)
def test_the_two_agree_on_conformance(label: str, given: CtyType[Any], want: CtyType[Any]) -> None:
    theirs = _theirs(given, want)

    assert (not conformance_errors(given, want)) == theirs["conforms"], label


@pytest.mark.parametrize(("label", "given", "want"), CASES, ids=IDS)
def test_the_two_report_the_same_errors(label: str, given: CtyType[Any], want: CtyType[Any]) -> None:
    theirs = _theirs(given, want)

    # Sorted, not sequenced: go-cty walks an object's attributes in Go map
    # order, which is randomised per run.
    expected = sorted((_rendered(entry.get("path", [])), entry["message"]) for entry in theirs["errors"])
    here = sorted((error.path, error.message) for error in conformance_errors(given, want))

    assert here == expected, label


def test_an_optional_attribute_is_still_a_required_conformance() -> None:
    """Optionality is a conversion concept, and conformance is not conversion.

    go-cty's `TestConformance` compares attribute *types* and never consults the
    optional set, so an object whose attribute is optional still fails to
    conform to one where it is not present -- and vice versa. Worth pinning,
    because "optional" reads like it should make a difference here.
    """
    optional = CtyObject(attribute_types={"a": S, "b": N}, optional_attributes=frozenset({"b"}))
    required = CtyObject(attribute_types={"a": S, "b": N})

    theirs = _theirs(optional, required)

    assert theirs["conforms"] is True
    assert conformance_errors(optional, required) == []


# 🌊🪢🔚
