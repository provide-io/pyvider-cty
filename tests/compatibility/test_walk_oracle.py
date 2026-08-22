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
from pyvider.cty.walk import deep_values, transform, walk
from tests.compatibility._oracle import canonical, rich, type_spec
from tests.compatibility._traversal import REWRITES, traversal_answer, visit_form

pytestmark = pytest.mark.compat

S = CtyString()
N = CtyNumber()
STRINGS = CtyList(element_type=S)
STRING_SET = CtySet(element_type=S)
NUMBER_SET = CtySet(element_type=N)
STRING_MAP = CtyMap(element_type=S)
PAIR = CtyObject(attribute_types={"a": S, "b": N})
NESTED = CtyObject(attribute_types={"inner": STRINGS})
TUPLE = CtyTuple(element_types=(S, N))

SENSITIVE = frozenset({"sensitive"})


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
    # A set of numbers, and the pair of them go-cty keeps apart while Python's
    # `==` does not: `Decimal("-0") == Decimal("0")`, but `makeSetHashBytes`
    # writes `-0` and `0`, so the oracle visits *two* elements and gives each
    # its own path. Only string sets were covered here, and in a string set the
    # two relations agree, so nothing in the suite ever told them apart.
    ("a set of numbers", NUMBER_SET, NUMBER_SET.validate([1, 2])),
    ("a set holding both zeros", NUMBER_SET, NUMBER_SET.validate([Decimal("-0"), Decimal("0")])),
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
    theirs = traversal_answer("walk", cty_type, value)

    here = [visit_form(path, visited) for path, visited in deep_values(value)]
    assert here == [canonical(visit) for visit in theirs["visits"]], label


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_every_path_the_oracle_emits_leads_back_to_what_it_visited(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    """A path is only worth what re-applying it gets you.

    The tests above check paths going *out* -- the ones this walk emits against
    the ones go-cty emits. Nothing checked them coming back *in*, so
    `KeyStep._apply_to_set` was unverified against the oracle entirely, and a
    set element's path is the one case where applying a path is more than
    bookkeeping: the step holds the element itself and has to find it again.

    That is how a real defect survived a green suite. The lookup used Python
    `==`, under which `Decimal("-0") == Decimal("0")`, so the two paths the
    oracle emits for `set{-0, 0}` both led to the positive zero -- one of them
    to an element that is not the one it names. Only string sets were covered,
    and there the two relations agree.

    The round trip is *up to the marks an ancestor contributes*, because in
    go-cty these two operations are deliberately not inverses. `Walk` descends
    through the unmarked container, so it visits a bare child; `Index` and
    `GetAttr` (`cty/value_ops.go:866` and `:819`) unmark, take the step and put
    the marks back, so applying the same path hands back a marked one. Asked of
    the oracle rather than assumed::

        soup-go cty walk --type '["list","string"]' '{"$marks":["sensitive"],"$value":["a"]}'
        "visits":[{"path":[],...}, {"path":[{"index":0}], "value":"a"}]

    The child is visited as a bare `"a"`. A marked *leaf* keeps its own mark
    there, which is what the second assertion holds on to.
    """
    theirs = traversal_answer("walk", cty_type, value)

    for path, visited in deep_values(value):
        applied = path.apply_path(value)
        assert applied.unmark()[0] == visited.unmark()[0], f"{label}: {path.string()}"
        # The visited value's own marks are never lost on the way back in; the
        # applied value may carry more, contributed by the containers traversed.
        assert visited.marks <= applied.marks, f"{label}: {path.string()}"

    # And the count the *oracle* reported, not only what this walk produced, so
    # the trip is anchored to go-cty's spelling of a set element's path.
    assert len(list(deep_values(value))) == len(theirs["visits"]), label


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_declining_to_descend_stops_at_the_same_place(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    """The callback's other answer, which a generator cannot express.

    Pruning at depth 1 keeps the root and its immediate children and stops
    there. A walk that ignores the answer visits values the caller asked not to
    see -- and for a sensitive subtree, "asked not to see" can be the point.
    """
    theirs = traversal_answer("walk", cty_type, value, "--prune-depth", "1")

    here: list[dict[str, Any]] = []

    def visit(path: Any, visited: CtyValue[Any]) -> bool:
        here.append(visit_form(path, visited))
        return len(path.steps) < 1

    walk(value, visit)

    assert here == [canonical(visit_record) for visit_record in theirs["visits"]], label


@pytest.mark.parametrize("op", ["upper", "unknown-to-null"])
@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_transform_rebuilds_the_same_value(
    op: str, label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    theirs = traversal_answer("transform", cty_type, value, "--op", op)

    here = transform(value, REWRITES[op])

    assert canonical(rich(here)) == canonical(theirs["value"]), f"{label} / {op}"
    assert json.loads(type_spec(here.type)) == theirs["type"], f"{label} / {op}: result type"


def test_transform_reaches_the_same_answer_as_unknown_as_null() -> None:
    """Two routes to one answer, which is why both are worth having.

    `unknown_as_null` is a purpose-built walk; this is the general one carrying
    the same rewrite. They agree with each other and with go-cty, so a fault in
    either traversal would have to be a fault in both to go unnoticed.
    """
    from pyvider.cty.unknown import unknown_as_null

    value = NESTED.validate({"inner": ["a", CtyValue.unknown(S)]})

    assert transform(value, REWRITES["unknown-to-null"]) == unknown_as_null(value)


# 🌊🪢🔚
