#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`cty.Walk`, `cty.DeepValues` and `cty.Transform`, against real go-cty.

Traversal is all order and paths, and neither is checkable by reading: a
container is visited before its children, an object's attributes arrive in
whatever order its iterator produces, a set element's path holds the element
*itself*, and a null or unknown has nothing inside it to visit whatever its type
says. Every one of those is a decision a second implementation makes silently.

`transform` cannot take a function over a command line, so both sides implement
the same two rewrites by name. That is a real constraint on what this can check
and it is stated rather than worked around: the comparison is of *how the
traversal rebuilds*, with the rewrite held fixed.
"""

from __future__ import annotations

from decimal import Decimal
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
from pyvider.cty.path import GetAttrStep, IndexStep, KeyStep
from pyvider.cty.walk import deep_values, transform, walk
from tests.compatibility._oracle import canonical, rich, run, type_spec

pytestmark = pytest.mark.compat

S = CtyString()
N = CtyNumber()
STRINGS = CtyList(element_type=S)
STRING_SET = CtySet(element_type=S)
STRING_MAP = CtyMap(element_type=S)
PAIR = CtyObject(attribute_types={"a": S, "b": N})
NESTED = CtyObject(attribute_types={"inner": STRINGS})
TUPLE = CtyTuple(element_types=(S, N))

SENSITIVE = frozenset({"sensitive"})


def _step_form(step: Any) -> Any:
    match step:
        case GetAttrStep(name=name):
            return {"attr": name}
        case IndexStep(index=index):
            return {"index": Decimal(index)}
        case KeyStep(key=key):
            return {"index": canonical(rich(key)) if isinstance(key, CtyValue) else key}
    raise AssertionError(f"no structural form for {step!r}")


def _visit(path: Any, value: CtyValue[Any]) -> dict[str, Any]:
    return {
        "path": [_step_form(step) for step in path.steps],
        "value": canonical(rich(value)),
        "type": json.loads(type_spec(value.type)),
    }


def _theirs(command: str, cty_type: CtyType[Any], value: CtyValue[Any], *extra: str) -> dict[str, Any]:
    result = run("cty", command, "--type", type_spec(cty_type), json.dumps(rich(value)), *extra)
    assert result["ok"], result
    return result


CASES: list[tuple[str, CtyType[Any], CtyValue[Any]]] = [
    ("a bare string", S, S.validate("x")),
    ("a null", S, CtyValue.null(S)),
    ("an unknown", S, CtyValue.unknown(S)),
    ("a list", STRINGS, STRINGS.validate(["a", "b"])),
    ("an empty list", STRINGS, STRINGS.validate([])),
    ("a null list", STRINGS, CtyValue.null(STRINGS)),
    ("an unknown list", STRINGS, CtyValue.unknown(STRINGS)),
    ("a list holding a null", STRINGS, STRINGS.validate(["a", CtyValue.null(S)])),
    ("a set", STRING_SET, STRING_SET.validate(["b", "a"])),
    ("a map", STRING_MAP, STRING_MAP.validate({"b": "2", "a": "1"})),
    ("an object", PAIR, PAIR.validate({"a": "x", "b": 1})),
    # Declared out of order, and built out of order, because both orders are
    # properties of how the value was made rather than of the value. go-cty
    # sorts, explicitly so that "results will always be stable given the same
    # input", and this walked in declaration and insertion order instead.
    (
        "an object whose attributes are declared out of order",
        CtyObject(attribute_types={"z": S, "a": S, "m": S}),
        CtyObject(attribute_types={"z": S, "a": S, "m": S}).validate({"m": "3", "z": "1", "a": "2"}),
    ),
    ("a map built out of order", STRING_MAP, STRING_MAP.validate({"z": "1", "a": "2", "m": "3"})),
    ("a nested object", NESTED, NESTED.validate({"inner": ["a", "b"]})),
    ("a tuple", TUPLE, TUPLE.validate(["x", 1])),
    ("a marked leaf", STRINGS, STRINGS.validate([CtyString().validate("a").with_marks(SENSITIVE)])),
    ("a marked container", STRINGS, STRINGS.validate(["a"]).with_marks(SENSITIVE)),
    (
        "three levels",
        CtyObject(attribute_types={"outer": CtyList(element_type=PAIR)}),
        CtyObject(attribute_types={"outer": CtyList(element_type=PAIR)}).validate(
            {"outer": [{"a": "x", "b": 1}]}
        ),
    ),
]

IDS = [case[0] for case in CASES]


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_the_visit_order_and_paths_agree(label: str, cty_type: CtyType[Any], value: CtyValue[Any]) -> None:
    theirs = _theirs("walk", cty_type, value)

    here = [_visit(path, visited) for path, visited in deep_values(value)]
    assert here == [canonical(visit) for visit in theirs["visits"]], label


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_declining_to_descend_stops_at_the_same_place(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    """The callback's other answer, which a generator cannot express.

    Pruning at depth 1 keeps the root and its immediate children and stops
    there. A walk that ignores the answer visits values the caller asked not to
    see -- and for a sensitive subtree, "asked not to see" can be the point.
    """
    theirs = _theirs("walk", cty_type, value, "--prune-depth", "1")

    here: list[dict[str, Any]] = []

    def visit(path: Any, visited: CtyValue[Any]) -> bool:
        here.append(_visit(path, visited))
        return len(path.steps) < 1

    walk(value, visit)

    assert here == [canonical(visit_record) for visit_record in theirs["visits"]], label


@pytest.mark.parametrize("op", ["upper", "unknown-to-null"])
@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_transform_rebuilds_the_same_value(
    op: str, label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    theirs = _theirs("transform", cty_type, value, "--op", op)

    here = transform(value, _REWRITES[op])

    assert canonical(rich(here)) == canonical(theirs["value"]), f"{label} / {op}"
    assert json.loads(type_spec(here.type)) == theirs["type"], f"{label} / {op}: result type"


def _upper(_path: Any, value: CtyValue[Any]) -> CtyValue[Any]:
    """Uppercase a known, non-null string, keeping its marks."""
    if not isinstance(value.type, CtyString) or value.is_null or value.is_unknown:
        return value
    return CtyString().validate(str(value.value).upper()).with_marks(value.marks)


def _unknown_to_null(_path: Any, value: CtyValue[Any]) -> CtyValue[Any]:
    if not value.is_unknown:
        return value
    return CtyValue.null(value.type).with_marks(value.marks)


_REWRITES = {"upper": _upper, "unknown-to-null": _unknown_to_null}


def test_transform_reaches_the_same_answer_as_unknown_as_null() -> None:
    """Two routes to one answer, which is why both are worth having.

    `unknown_as_null` is a purpose-built walk; this is the general one carrying
    the same rewrite. They agree with each other and with go-cty, so a fault in
    either traversal would have to be a fault in both to go unnoticed.
    """
    from pyvider.cty.unknown import unknown_as_null

    value = NESTED.validate({"inner": ["a", CtyValue.unknown(S)]})

    assert transform(value, _unknown_to_null) == unknown_as_null(value)


# 🌊🪢🔚
