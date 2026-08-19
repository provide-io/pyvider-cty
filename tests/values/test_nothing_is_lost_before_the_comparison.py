#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Validating a value a second time must not lose anything the first kept.

This exists because of a structural blind spot in the differential suites, and
it is the only guard that can see into it.

`tests/compatibility/` spells our value for the harness with `rich()` and then
compares. When this package drops information *before* that spelling -- at
`validate`, or in `CtyValue`'s own construction -- the spelling never carries it,
go-cty is handed the already-lossy value, and the two agree. A differential
property can only see what survives into the value it compares.

That is not hypothetical. `CtyValue.__attrs_post_init__` cleared the payload of
every null, and at `dynamic` the payload *is* the concrete type, so
`CtyDynamic().validate(CtyValue.null(CtyString()))` became an untyped dynamic
null. It went on the wire as a bare `c0` where go-cty writes `[type, value]`,
and **every differential test agreed**, because both sides were handed the same
untyped null. It was found by hand-building go's side instead
(`tests/compatibility/test_dynamic_carries_its_type.py`).

Two invariants here, and they catch different things. Neither needs an oracle,
so both run in the ordinary suite.

**Idempotence** -- validating an already-validated value changes nothing -- is
the weaker one, and on its own it would *not* have caught the dynamic-null bug:
once the concrete type is dropped, validating again drops nothing further, so
the value is stably lossy and idempotence holds. That was checked by reverting
the fix; only the second invariant went red.

**Wrapping preserves what it wraps** is the one with teeth. `CtyDynamic` exists
to stand in front of a concrete value, so `D.validate(x)` has to leave `x`
recoverable whatever `x` is -- known, null, unknown, refined or marked. That is
the property the bug broke, and it is the property a differential suite cannot
ask, because it is about what the value holds rather than about what two
implementations answer.
"""

from __future__ import annotations

from decimal import Decimal
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

S, N, B, D = CtyString(), CtyNumber(), CtyBool(), CtyDynamic()
STRINGS = CtyList(element_type=S)
PAIR = CtyObject(attribute_types={"a": S, "b": N})


def _describe(value: CtyValue[Any]) -> Any:
    """Everything a value carries that the wire can carry, structurally.

    Deliberately not `rich()`: that is the spelling the differential suite uses,
    and a guard against "the spelling loses something" cannot be written in the
    spelling. This walks the value itself.
    """
    if value.marks:
        return {"marks": sorted(str(m) for m in value.marks), "inner": _describe(value.unmark()[0])}
    if value.is_unknown:
        return {"unknown": str(value.type), "refined": repr(value.value)}
    if value.is_null:
        # The type of a null is the whole of what it carries -- and at `dynamic`
        # that includes the concrete type standing behind it.
        inner = value.value
        return {
            "null": str(value.type),
            "inner": _describe(inner) if isinstance(inner, CtyValue) else None,
        }
    if isinstance(value.value, CtyValue):
        return {"wrapped": str(value.type), "inner": _describe(value.value)}
    if isinstance(value.value, dict):
        return {"map": str(value.type), "items": {k: _describe(v) for k, v in sorted(value.value.items())}}
    if isinstance(value.value, tuple | list | frozenset | set):
        return {"seq": str(value.type), "items": [_describe(v) for v in value.value]}
    return {"scalar": str(value.type), "value": repr(value.value)}


CASES: list[tuple[str, CtyType[Any], Any]] = [
    # The shape that was actually broken, and its neighbours. Each holds the
    # value as a caller would already have it -- wrapped -- because the question
    # is whether validating it *again* is the identity, not what wrapping does.
    ("dynamic wrapping a null string", D, D.validate(CtyValue.null(S))),
    ("dynamic wrapping a null list", D, D.validate(CtyValue.null(STRINGS))),
    ("dynamic wrapping an unknown string", D, D.validate(CtyValue.unknown(S))),
    (
        "dynamic wrapping a refined unknown",
        D,
        D.validate(refine(CtyValue.unknown(S)).string_prefix_full("a").new_value()),
    ),
    ("dynamic wrapping a marked string", D, D.validate(S.validate("x").mark("sensitive"))),
    ("dynamic wrapping a dynamic", D, D.validate(D.validate(S.validate("x")))),
    ("dynamic wrapping a known list", D, D.validate(STRINGS.validate(["a"]))),
    # Nulls and unknowns at every container kind: the payload-clearing rule the
    # dynamic case was an exception to applies to all of them.
    ("null string", S, CtyValue.null(S)),
    ("null list", STRINGS, CtyValue.null(STRINGS)),
    ("null object", PAIR, CtyValue.null(PAIR)),
    ("null map", CtyMap(element_type=S), CtyValue.null(CtyMap(element_type=S))),
    ("unknown list", STRINGS, CtyValue.unknown(STRINGS)),
    (
        "refined unknown list",
        STRINGS,
        refine(CtyValue.unknown(STRINGS)).collection_length_lower_bound(2).new_value(),
    ),
    ("refined unknown number", N, refine(CtyValue.unknown(N)).not_null().new_value()),
    # Marks, which are carried beside the value rather than in it.
    ("marked null", S, CtyValue.null(S).mark("sensitive")),
    ("marked unknown", S, CtyValue.unknown(S).mark("sensitive")),
    ("marked list", STRINGS, STRINGS.validate(["a"]).mark("sensitive")),
    # Members that are themselves null, unknown or marked.
    ("object with a null attribute", PAIR, PAIR.validate({"a": CtyValue.null(S), "b": 1})),
    ("object with an unknown attribute", PAIR, PAIR.validate({"a": CtyValue.unknown(S), "b": 1})),
    ("list holding a marked element", STRINGS, STRINGS.validate([S.validate("x").mark("sensitive")])),
    ("set holding an unknown", CtySet(element_type=S), CtySet(element_type=S).validate([CtyValue.unknown(S)])),
    (
        "tuple holding a null",
        CtyTuple(element_types=(S, N)),
        CtyTuple(element_types=(S, N)).validate([CtyValue.null(S), 1]),
    ),
    # Scalars whose spelling is easy to normalise away.
    ("a trailing zero", N, N.validate(Decimal("1.50"))),
    ("negative zero", N, N.validate(Decimal("-0.0"))),
    ("an empty string", S, S.validate("")),
    ("a false bool", B, B.validate(False)),
]


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=[case[0] for case in CASES])
def test_validating_an_already_validated_value_loses_nothing(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    """The invariant. A second `validate` is the identity on what the value holds."""
    again = cty_type.validate(value)

    assert _describe(again) == _describe(value), label


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=[case[0] for case in CASES])
def test_it_is_still_the_identity_on_a_third_pass(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    """Idempotence, not merely one stable step.

    A rule that loses something on the *second* application would pass the test
    above while still dropping information from any value that round-trips more
    than once -- which a value does every time it crosses a function boundary.
    """
    once = cty_type.validate(value)
    twice = cty_type.validate(once)

    assert _describe(twice) == _describe(once), label


# Inner values a `dynamic` has to be able to stand in front of, one of each kind
# a caller can build. The bug was in the null row; the rest are here so a fix
# aimed at one kind cannot quietly cost another.
WRAPPED: list[tuple[str, CtyValue[Any]]] = [
    ("a known string", S.validate("x")),
    ("a known list", STRINGS.validate(["a", "b"])),
    ("a known object", PAIR.validate({"a": "x", "b": 1})),
    ("a null string", CtyValue.null(S)),
    ("a null list", CtyValue.null(STRINGS)),
    ("a null object", CtyValue.null(PAIR)),
    ("an unknown string", CtyValue.unknown(S)),
    ("an unknown list", CtyValue.unknown(STRINGS)),
    ("a refined unknown", refine(CtyValue.unknown(S)).string_prefix_full("a").new_value()),
    ("a marked string", S.validate("x").mark("sensitive")),
    ("a marked null", CtyValue.null(S).mark("sensitive")),
]


@pytest.mark.parametrize(("label", "inner"), WRAPPED, ids=[case[0] for case in WRAPPED])
def test_a_dynamic_keeps_the_value_it_wraps(label: str, inner: CtyValue[Any]) -> None:
    """The invariant with teeth, and the one the differential suite cannot ask.

    A `dynamic` carries no type of its own, so the value behind it *is* the
    information. Dropping it leaves something that still round-trips, still
    validates, and still compares equal to go-cty's equally-dropped answer --
    which is precisely why nothing else saw the bug.
    """
    wrapped = D.validate(inner)

    assert isinstance(wrapped.value, CtyValue), f"{label}: the wrapped value was dropped"
    assert _describe(wrapped.value) == _describe(inner), label
    assert wrapped.is_null == inner.is_null, f"{label}: nullness disagrees with the wrapped value"
    assert wrapped.is_unknown == inner.is_unknown, f"{label}: knownness disagrees"


def test_the_case_that_was_actually_broken_is_covered() -> None:
    """A named guard, so the regression cannot be deleted by tidying the table.

    Before 2026-08-19 this returned a value whose payload was `None`: the
    concrete `string` was gone, and with it the only thing a `dynamic` position
    has to carry.
    """
    wrapped = D.validate(CtyValue.null(S))

    assert wrapped.is_null is True
    assert isinstance(wrapped.value, CtyValue), "the concrete type was dropped"
    assert isinstance(wrapped.value.type, CtyString)


# 🌊🪢🔚
