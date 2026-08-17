#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`Value.Equals` and `Value.RawEquals`, against real go-cty.

`cty call equal` reaches `stdlib.EqualFunc`, which unifies its arguments first,
so the sweep's two cases said nothing about `Value.Equals` itself -- the
comparison a provider makes when it asks whether planned state matches prior
state, and the one place in cty where "not yet decided" is a legitimate answer.

The rules being checked are the ones that read backwards until you see why:

  - **nulls of any two types are equal**, because a null carries no type
    information a comparison could disagree about
  - an unknown compared with a *null* is undecided even across types, because
    the unknown could still turn out to be null
  - an unknown compared with a known value of a *different* type is definitely
    false -- unless a dynamic type is involved anywhere, which puts it back to
    undecided
  - the undecided answer is refined not-null
  - a mark anywhere in either operand comes out on the answer, except that
    comparing against a null keeps only top-level marks

`RawEquals` is included because it answers a different question -- about
representations rather than values -- and it is what distinguishes an unknown
from a null of the same type.
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
from pyvider.cty.refinement import refine
from pyvider.cty.values.equality import equals
from tests.compatibility._oracle import rich, run, type_spec

pytestmark = pytest.mark.compat

S = CtyString()
N = CtyNumber()
B = CtyBool()
D = CtyDynamic()
STRINGS = CtyList(element_type=S)
NUMBERS = CtyList(element_type=N)
STRING_SET = CtySet(element_type=S)
STRING_MAP = CtyMap(element_type=S)
PAIR = CtyObject(attribute_types={"a": S, "b": N})
TUPLE = CtyTuple(element_types=(S, N))

US = CtyValue.unknown(S)
UN = CtyValue.unknown(N)
SENSITIVE = frozenset({"sensitive"})

# (label, left type, left, right type, right)
CASES: list[tuple[str, CtyType[Any], CtyValue[Any], CtyType[Any], CtyValue[Any]]] = [
    ("equal strings", S, S.validate("a"), S, S.validate("a")),
    ("different strings", S, S.validate("a"), S, S.validate("b")),
    ("equal numbers", N, N.validate(1), N, N.validate(1)),
    ("a number and its text", N, N.validate(1), S, S.validate("1")),
    ("different types", S, S.validate("a"), N, N.validate(1)),
    # Nulls.
    ("two nulls of one type", S, CtyValue.null(S), S, CtyValue.null(S)),
    ("two nulls of different types", S, CtyValue.null(S), N, CtyValue.null(N)),
    ("a null and a value", S, CtyValue.null(S), S, S.validate("a")),
    ("a null and a value of another type", S, CtyValue.null(S), N, N.validate(1)),
    ("a null collection and an empty one", STRINGS, CtyValue.null(STRINGS), STRINGS, STRINGS.validate([])),
    # Unknowns.
    ("two unknowns", S, US, S, US),
    ("an unknown and a known", S, US, S, S.validate("a")),
    ("an unknown and a null", S, US, S, CtyValue.null(S)),
    ("an unknown and a null of another type", S, US, N, CtyValue.null(N)),
    ("an unknown and a known of another type", S, US, N, N.validate(1)),
    ("an unknown and an unknown of another type", S, US, N, UN),
    # Refinements are what let a comparison decide despite an unknown.
    (
        "an unknown excluded by its prefix",
        S,
        refine(US).string_prefix("ht").new_value(),
        S,
        S.validate("ftp"),
    ),
    (
        "an unknown admitted by its prefix",
        S,
        refine(US).string_prefix("ht").new_value(),
        S,
        S.validate("http"),
    ),
    (
        "an unknown excluded by its bounds",
        N,
        refine(UN).number_range_inclusive(1, 10).new_value(),
        N,
        N.validate(50),
    ),
    (
        "an unknown excluded by its length",
        STRINGS,
        refine(CtyValue.unknown(STRINGS)).collection_length_lower_bound(3).new_value(),
        STRINGS,
        STRINGS.validate(["a"]),
    ),
    ("a not-null unknown and a null", S, refine(US).not_null().new_value(), S, CtyValue.null(S)),
    # Dynamic anywhere puts a decision back out of reach.
    ("an unknown of dynamic type and a string", D, CtyValue.unknown(D), S, S.validate("a")),
    ("a dynamic and a string", D, D.validate("a"), S, S.validate("a")),
    # Containers, where the interesting part is an unknown at depth.
    ("equal lists", STRINGS, STRINGS.validate(["a"]), STRINGS, STRINGS.validate(["a"])),
    ("lists of different lengths", STRINGS, STRINGS.validate(["a"]), STRINGS, STRINGS.validate(["a", "b"])),
    (
        "a list with an unknown element",
        STRINGS,
        STRINGS.validate(["a", US]),
        STRINGS,
        STRINGS.validate(["a", "b"]),
    ),
    (
        "a list whose known element already differs",
        STRINGS,
        STRINGS.validate(["z", US]),
        STRINGS,
        STRINGS.validate(["a", "b"]),
    ),
    # Order decides the answer for a sequence, and go-cty is deterministic about
    # it: it walks by index and returns at the first element it cannot decide,
    # so an undecided element at a low index beats a definite difference at a
    # higher one. Both directions are pinned because a rule that only looked at
    # "is anything definitely different" would pass one and fail the other.
    (
        "an undecided element before a difference",
        STRINGS,
        STRINGS.validate([US, "z"]),
        STRINGS,
        STRINGS.validate(["a", "b"]),
    ),
    (
        "a difference before an undecided element",
        STRINGS,
        STRINGS.validate(["z", US]),
        STRINGS,
        STRINGS.validate(["a", "b"]),
    ),
    (
        "an undecided tuple element before a difference",
        TUPLE,
        TUPLE.validate([US, 1]),
        TUPLE,
        TUPLE.validate(["a", 2]),
    ),
    # A refinement that *excludes* the candidate counts as a definite
    # difference, so a later index is still reached; one that merely admits it
    # leaves the element undecided and short-circuits.
    (
        "an element excluded by its prefix",
        STRINGS,
        STRINGS.validate([refine(US).string_prefix("ht").new_value(), "z"]),
        STRINGS,
        STRINGS.validate(["ftp", "b"]),
    ),
    (
        "an element admitted by its prefix",
        STRINGS,
        STRINGS.validate([refine(US).string_prefix("ht").new_value(), "z"]),
        STRINGS,
        STRINGS.validate(["http", "b"]),
    ),
    # A set holding an unknown can never answer definitely: go-cty requires both
    # sides wholly known, because an unknown element changes how many distinct
    # members the set has.
    (
        "a set holding an unknown element",
        STRING_SET,
        STRING_SET.validate(["a", US]),
        STRING_SET,
        STRING_SET.validate(["b", "c"]),
    ),
    (
        "a set holding two unknown elements",
        STRING_SET,
        STRING_SET.validate([US, US]),
        STRING_SET,
        STRING_SET.validate(["a", "b"]),
    ),
    ("lists of different element types", STRINGS, STRINGS.validate([]), NUMBERS, NUMBERS.validate([])),
    ("equal sets", STRING_SET, STRING_SET.validate(["a", "b"]), STRING_SET, STRING_SET.validate(["b", "a"])),
    ("equal maps", STRING_MAP, STRING_MAP.validate({"a": "1"}), STRING_MAP, STRING_MAP.validate({"a": "1"})),
    (
        "maps with different keys",
        STRING_MAP,
        STRING_MAP.validate({"a": "1"}),
        STRING_MAP,
        STRING_MAP.validate({"b": "1"}),
    ),
    ("equal objects", PAIR, PAIR.validate({"a": "x", "b": 1}), PAIR, PAIR.validate({"a": "x", "b": 1})),
    (
        "an object with an unknown attribute",
        PAIR,
        PAIR.validate({"a": US, "b": 1}),
        PAIR,
        PAIR.validate({"a": "x", "b": 1}),
    ),
    # "an object whose known attribute differs" is deliberately absent -- it is
    # the one case where go-cty has no single answer. See the test below.
    ("equal tuples", TUPLE, TUPLE.validate(["x", 1]), TUPLE, TUPLE.validate(["x", 1])),
    # Marks come out on the answer.
    ("a marked operand", S, S.validate("a").with_marks(SENSITIVE), S, S.validate("a")),
    ("both operands marked", S, S.validate("a").with_marks({"one"}), S, S.validate("a").with_marks({"two"})),
    (
        "a mark inside a container",
        STRINGS,
        STRINGS.validate([CtyString().validate("a").with_marks(SENSITIVE)]),
        STRINGS,
        STRINGS.validate(["a"]),
    ),
    (
        "a marked value against a null",
        S,
        S.validate("a").with_marks(SENSITIVE),
        S,
        CtyValue.null(S),
    ),
    ("a marked bool", B, B.validate(True).with_marks(SENSITIVE), B, B.validate(True)),
]

IDS = [case[0] for case in CASES]


def _theirs(
    left_type: CtyType[Any], left: CtyValue[Any], right_type: CtyType[Any], right: CtyValue[Any]
) -> dict[str, Any]:
    result = run(
        "cty",
        "equals",
        "--left-type",
        type_spec(left_type),
        "--right-type",
        type_spec(right_type),
        json.dumps(rich(left)),
        json.dumps(rich(right)),
    )
    assert result["ok"], result
    return result


def _here(left: CtyValue[Any], right: CtyValue[Any]) -> dict[str, Any]:
    answer = equals(left, right)
    described: dict[str, Any] = {"known": not answer.is_unknown}
    if not answer.is_unknown:
        described["value"] = bool(answer.value)
    if answer.marks:
        described["marks"] = sorted(str(mark) for mark in answer.marks)
    return described


@pytest.mark.parametrize(("label", "left_type", "left", "right_type", "right"), CASES, ids=IDS)
def test_the_two_answer_the_same(
    label: str,
    left_type: CtyType[Any],
    left: CtyValue[Any],
    right_type: CtyType[Any],
    right: CtyValue[Any],
) -> None:
    theirs = _theirs(left_type, left, right_type, right)

    assert _here(left, right) == theirs["equals"], label


@pytest.mark.parametrize(("label", "left_type", "left", "right_type", "right"), CASES, ids=IDS)
def test_equality_is_symmetric_in_both_implementations(
    label: str,
    left_type: CtyType[Any],
    left: CtyValue[Any],
    right_type: CtyType[Any],
    right: CtyValue[Any],
) -> None:
    """Swapping the operands cannot change the answer.

    Worth asserting separately because `Equals` is written as a cascade of
    one-sided cases -- "known on the left and unknown on the right", then the
    mirror -- and a rule added to one arm and not the other is the natural way
    for this to break in either implementation.
    """
    theirs = _theirs(right_type, right, left_type, left)

    assert _here(right, left) == theirs["equals"], label
    assert _here(right, left) == _here(left, right), f"{label}: asymmetric here"


def test_an_object_with_both_an_unknown_and_a_difference() -> None:
    """The one case where go-cty has no single answer, and this does.

    `Equals` walks an object's attributes with `for attr := range oty.AttrTypes`
    -- Go map iteration, deliberately randomised -- and returns undecided on the
    *first* unknown attribute it meets while a definite difference breaks out as
    false. So for an object with one unknown attribute and one that definitely
    differs, the answer depends on which it happens to visit first. Measured: 4
    of 12 runs said definitely-false, 8 said undecided, for identical inputs.

    In Terraform that is a comparison which can report a difference on one plan
    and not the next.

    This library visits every attribute and reports false if any definitely
    differs, undecided otherwise. That is deterministic, and it is the better of
    go-cty's two answers rather than a third one -- a definite difference cannot
    be undone by whatever the unknown resolves to.

    Asserted here without pinning go-cty's coin flip: what is checked is that
    go-cty never answers *true*, that this library is deterministic, and that its
    answer is one go-cty also gives.
    """
    left = PAIR.validate({"a": US, "b": N.validate(2)})
    right = PAIR.validate({"a": S.validate("x"), "b": N.validate(1)})

    observed = set()
    for _ in range(12):
        answer = _theirs(PAIR, left, PAIR, right)["equals"]
        observed.add((answer["known"], answer.get("value")))

    assert observed <= {(False, None), (True, False)}, observed

    here = [_here(left, right) for _ in range(5)]
    assert here == [{"known": True, "value": False}] * 5


def test_an_undecided_answer_is_refined_not_null() -> None:
    """A detail a caller can observe, and go-cty spells it out.

    `Equals` returns `UnknownVal(Bool).Refine().NotNull().NewValue()`, so a
    caller asking whether the answer could be null gets "no" from both.
    """
    from pyvider.cty.value_range import value_range

    theirs = _theirs(S, US, S, S.validate("a"))
    assert theirs["equals"]["known"] is False

    answer = equals(US, S.validate("a"))

    assert answer.is_unknown
    assert value_range(answer).definitely_not_null()


# 🌊🪢🔚
