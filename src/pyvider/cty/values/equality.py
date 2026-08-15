#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Three-valued equality, mirroring go-cty's `Value.Equals`.

`==` on a CtyValue answers with a plain `bool`, which forces a decision even
when the values do not support one. Comparing an object whose attribute is
unknown against one whose attribute is `"z"` is not `False` -- that attribute
could still resolve to `"z"`. It is *undecided*, and the only honest result
type is a value that can be unknown.

The rule this exists to enforce: **never claim a certainty the data does not
support.** Callers deciding "are these the same" from `is_unknown` alone get it
wrong, because `is_unknown` answers only for the top level and the containers
disagree with each other about propagating it -- a list built from an unknown
element reports itself unknown, an object with an unknown attribute does not.

Deliberately not implemented: go-cty disqualifies some comparisons early using
the refinement bounds on an unknown (`Value.Range().Includes`). pyvider.cty has
only partial refinement support, so those cases return unknown here instead of
`False`. That is the safe direction -- vaguer, never wrong.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pyvider.cty.values.base import CtyValue


def _bool(result: bool) -> CtyValue[Any]:
    from pyvider.cty.types import CtyBool

    return CtyBool().validate(result)


def _undecided() -> CtyValue[Any]:
    from pyvider.cty.types import CtyBool
    from pyvider.cty.values.base import CtyValue

    return CtyValue.unknown(CtyBool())


def _unwrap_dynamic(value: CtyValue[Any]) -> CtyValue[Any]:
    """CtyDynamic wraps rather than replaces, so compare what it wraps."""
    from pyvider.cty.types import CtyDynamic
    from pyvider.cty.values.base import CtyValue

    while isinstance(value.vtype, CtyDynamic) and isinstance(value.value, CtyValue):
        value = value.value
    return value


def equals(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Whether `a` and `b` are equal: true, false, or unknown.

    Mirrors go-cty's `Value.Equals`, including its handling of marks -- the
    comparison runs on unmarked copies and the union of both operands' marks is
    applied to the result, so asking whether a sensitive value equals something
    yields a sensitive answer.
    """
    from pyvider.cty.marks import collect_marks_deep, unmark_deep

    marks = collect_marks_deep(a) | collect_marks_deep(b)
    if not marks:
        return _equals_unmarked(a, b)

    # go-cty keeps only top-level marks when exactly one side is null, on the
    # grounds that nested marks cannot have informed a decision that never
    # looked at nested values. Same reasoning, same behaviour.
    if a.is_null != b.is_null:
        marks = a.marks | b.marks

    result = _equals_unmarked(unmark_deep(a)[0], unmark_deep(b)[0])
    return result.with_marks(marks)


def _equals_unmarked(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    a, b = _unwrap_dynamic(a), _unwrap_dynamic(b)

    # Unknowns first: an unknown that has not been refined as non-null could
    # still become null, and nulls of any type are equal to one another. Testing
    # nullness before knownness would answer that comparison wrongly.
    if a.is_unknown or b.is_unknown:
        return _equals_with_unknown(a, b)

    if a.is_null and b.is_null:
        return _bool(True)  # nulls are equal regardless of type
    if a.is_null or b.is_null:
        return _bool(False)

    if not a.vtype.equal(b.vtype):
        return _bool(False)

    return _equals_same_type(a, b)


def _equals_with_unknown(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """At least one side is unknown at the top level."""
    if a.is_unknown and b.is_unknown:
        return _undecided()

    known, unknown = (a, b) if not a.is_unknown else (b, a)
    if known.is_null:
        # The unknown may yet resolve to null, which would make them equal.
        return _undecided()
    if not known.vtype.equal(unknown.vtype):
        # No null comparison is in play, so mismatched types can never be equal
        # however the unknown resolves.
        return _bool(False)
    return _undecided()


def _items(value: CtyValue[Any]) -> tuple[Any, ...]:
    """The members of a sequence payload. `value` is typed as `object | None`."""
    return tuple(cast("tuple[Any, ...]", value.value or ()))


def _entries(value: CtyValue[Any]) -> dict[str, Any]:
    """The entries of a mapping payload."""
    return dict(cast("dict[str, Any]", value.value or {}))


def _equals_same_type(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    from pyvider.cty.types import (
        CtyCapsule,
        CtyList,
        CtyMap,
        CtyObject,
        CtySet,
        CtyTuple,
    )

    vtype = a.vtype
    if isinstance(vtype, CtyList | CtyTuple):
        return _equals_sequence(_items(a), _items(b))
    if isinstance(vtype, CtySet):
        return _equals_set(a, b)
    if isinstance(vtype, CtyMap | CtyObject):
        return _equals_mapping(_entries(a), _entries(b))
    if isinstance(vtype, CtyCapsule):
        # Capsules define their own equality, or fall back to identity as
        # go-cty's default capsule comparison does.
        return _bool(a == b)
    return _bool(a.value == b.value)


def _combine(results: list[CtyValue[Any]]) -> CtyValue[Any]:
    """True only if every part is true; unknown if any part is undecided.

    A definite `False` anywhere wins outright -- one unequal element makes the
    whole comparison false no matter what the undecided ones resolve to.
    """
    undecided = False
    for result in results:
        if result.is_unknown:
            undecided = True
        elif result.value is False:
            return _bool(False)
    return _undecided() if undecided else _bool(True)


def _equals_item(x: Any, y: Any) -> CtyValue[Any]:
    """Compare two container members, either of which may be a raw payload.

    Validation normalises members to CtyValues, but a hand-built CtyValue can
    hold raw Python objects, and those have no type to reason about -- so they
    get plain equality rather than a three-valued answer.
    """
    from pyvider.cty.values.base import CtyValue

    if isinstance(x, CtyValue) and isinstance(y, CtyValue):
        return _equals_unmarked(x, y)
    x_raw = x.value if isinstance(x, CtyValue) else x
    y_raw = y.value if isinstance(y, CtyValue) else y
    return _bool(bool(x_raw == y_raw))


def _equals_sequence(a_items: tuple[Any, ...], b_items: tuple[Any, ...]) -> CtyValue[Any]:
    if len(a_items) != len(b_items):
        return _bool(False)
    return _combine([_equals_item(x, y) for x, y in zip(a_items, b_items, strict=True)])


def _equals_mapping(a_map: dict[str, Any], b_map: dict[str, Any]) -> CtyValue[Any]:
    if a_map.keys() != b_map.keys():
        return _bool(False)
    return _combine([_equals_item(a_map[k], b_map[k]) for k in a_map])


def _equals_set(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Sets compare by membership, which needs every element decided.

    go-cty requires both sets to be wholly known before it will answer, because
    an unknown element changes how many distinct members the set has -- two sets
    of different apparent length can still turn out equal once it resolves.
    """
    if not a.is_wholly_known() or not b.is_wholly_known():
        return _undecided()
    a_items, b_items = frozenset(_items(a)), frozenset(_items(b))
    if len(a_items) != len(b_items):
        return _bool(False)
    return _bool(all(any(_equals_item(x, y).value is True for y in b_items) for x in a_items))


# 🌊🪢🔚
