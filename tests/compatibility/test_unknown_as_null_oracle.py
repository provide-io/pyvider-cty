#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`cty.UnknownAsNull`, against real go-cty.

The interesting cases are all about depth, which is why no stdlib function could
stand in for this one: the operation exists to rewrite unknowns *inside*
containers, and a comparison that only ever passes a top-level unknown proves
nothing about the part that does the work.

Two of these cases are load-bearing and neither is obvious from the signature. A
set of two unknowns collapses to a set of one null, because rewriting the
elements makes them equal and the set re-deduplicates. And an empty container is
returned untouched -- go-cty short-circuits on length zero -- which matters
because rebuilding it would be an opportunity to lose its element type.
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
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.unknown import unknown_as_null
from tests.compatibility._oracle import canonical, rich, run, type_spec

pytestmark = pytest.mark.compat

STRINGS = CtyList(element_type=CtyString())
STRING_SET = CtySet(element_type=CtyString())
STRING_MAP = CtyMap(element_type=CtyString())
PAIR = CtyObject(attribute_types={"a": CtyString(), "b": CtyNumber()})
NESTED = CtyObject(attribute_types={"inner": STRINGS})
TUPLE = CtyTuple(element_types=(CtyString(), CtyNumber()))

UNKNOWN_STRING = CtyValue.unknown(CtyString())


def _theirs(cty_type: CtyType[Any], value: CtyValue[Any]) -> dict[str, Any]:
    result = run("cty", "unknown-as-null", "--type", type_spec(cty_type), json.dumps(rich(value)))
    assert result["ok"], result
    return result


CASES: list[tuple[str, CtyType[Any], CtyValue[Any]]] = [
    ("a bare unknown", CtyString(), UNKNOWN_STRING),
    ("a known value", CtyString(), CtyString().validate("x")),
    ("a null", CtyString(), CtyValue.null(CtyString())),
    ("an unknown list", STRINGS, CtyValue.unknown(STRINGS)),
    ("an unknown inside a list", STRINGS, STRINGS.validate(["a", UNKNOWN_STRING])),
    ("only unknowns inside a list", STRINGS, STRINGS.validate([UNKNOWN_STRING, UNKNOWN_STRING])),
    ("an empty list", STRINGS, STRINGS.validate([])),
    # The de-duplicating case: two unknowns become two nulls become one null.
    ("two unknowns inside a set", STRING_SET, STRING_SET.validate([UNKNOWN_STRING, "a"])),
    ("an empty set", STRING_SET, STRING_SET.validate([])),
    ("an unknown inside a map", STRING_MAP, STRING_MAP.validate({"k": UNKNOWN_STRING, "j": "a"})),
    ("an empty map", STRING_MAP, STRING_MAP.validate({})),
    ("an unknown attribute", PAIR, PAIR.validate({"a": UNKNOWN_STRING, "b": 1})),
    ("an unknown inside a nested list", NESTED, NESTED.validate({"inner": ["a", UNKNOWN_STRING]})),
    ("an unknown tuple element", TUPLE, TUPLE.validate([UNKNOWN_STRING, 1])),
    ("a marked unknown", CtyString(), UNKNOWN_STRING.with_marks({"sensitive"})),
    (
        "a marked element inside a list",
        STRINGS,
        STRINGS.validate([UNKNOWN_STRING.with_marks({"sensitive"}), "a"]),
    ),
]


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=[case[0] for case in CASES])
def test_the_two_rewrite_the_same_way(label: str, cty_type: CtyType[Any], value: CtyValue[Any]) -> None:
    theirs = _theirs(cty_type, value)

    assert canonical(rich(unknown_as_null(value))) == canonical(theirs["value"]), label


def test_the_result_type_is_preserved_where_go_cty_loses_optionality() -> None:
    """The one deliberate difference, and it is go-cty disagreeing with itself.

    `UnknownAsNull`'s own docstring promises "a value of the same type as the
    given value". For an object with optional attributes it does not deliver
    that: it rebuilds through `ObjectVal`, which re-infers the type from the
    attribute values and has no way to know which attributes were optional.

    This library keeps the original type. The values are identical either way --
    optionality only affects conversion, and there is nothing left to convert --
    so no answer a caller can compare changes. Recorded here rather than in a
    comment so that a future reader finds the evidence with the claim.
    """
    optional = CtyObject(
        attribute_types={"a": CtyString(), "b": CtyNumber()}, optional_attributes=frozenset({"b"})
    )
    value = optional.validate({"a": UNKNOWN_STRING, "b": 1})

    theirs = _theirs(optional, value)
    here = unknown_as_null(value)

    assert canonical(rich(here)) == canonical(theirs["value"])
    assert theirs["type"] == ["object", {"a": "string", "b": "number"}]
    assert here.type.optional_attributes == frozenset({"b"})


# 🌊🪢🔚
