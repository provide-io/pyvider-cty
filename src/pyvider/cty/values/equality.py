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

Refinements are consulted, as of 2026-08-17: go-cty disqualifies some
comparisons early from the bounds on an unknown (`Value.Range().Includes`), and
so does this -- an unknown number refined to [1, 10] is definitely not 50. Only
a hard *exclusion* is usable. Passing every bound is not equality, so anything
short of a definite false stays undecided, which keeps the previous safe
direction wherever the range cannot decide.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pyvider.cty.values.base import CtyValue


_CACHED: dict[bool, CtyValue[Any]] = {}


def _bool(result: bool) -> CtyValue[Any]:
    """A true/false answer, built once.

    `CtyBool().validate(...)` constructs a type and runs the full validation
    path, recursion guard included, to produce one of two possible values. A
    comparison returns one of them every time, so they are built once and
    shared -- CtyValue is immutable, and marks are applied with `with_marks`,
    which evolves a new instance rather than touching this one.
    """
    cached = _CACHED.get(result)
    if cached is None:
        from pyvider.cty.types import CtyBool

        cached = CtyBool().validate(result)
        _CACHED[result] = cached
    return cached


def _undecided() -> CtyValue[Any]:
    """ "Not yet decided", and *not null* -- which go-cty says explicitly.

    `Equals` returns `UnknownVal(Bool).Refine().NotNull().NewValue()`. The
    refinement costs nothing and is observable: a caller asking whether the
    answer could be null gets "no" from go-cty, and used to get "possibly" here.
    """
    from pyvider.cty.types import CtyBool
    from pyvider.cty.values.base import CtyValue
    from pyvider.cty.values.markers import RefinedUnknownValue

    return CtyValue(
        vtype=CtyBool(),
        value=RefinedUnknownValue(is_known_null=False),
        is_unknown=True,
    )


# Payloads that can hold a nested CtyValue, and so a nested mark or unknown.
_NESTING_PAYLOADS = (dict, list, tuple, set, frozenset)


def _has_dynamic(vtype: Any) -> bool:
    """Whether `vtype` is, or contains, a dynamic pseudo-type.

    Iterative. Types nest as deeply as values do, and this runs on every
    comparison against an unknown -- a recursive version raised RecursionError
    out of `equals` for a sufficiently nested type.
    """
    from pyvider.cty.types import CtyDynamic, CtyList, CtyMap, CtyObject, CtySet, CtyTuple

    stack = [vtype]
    seen: set[int] = set()
    while stack:
        current = stack.pop()
        if isinstance(current, CtyDynamic):
            return True
        current_id = id(current)
        if current_id in seen:
            continue
        seen.add(current_id)
        if isinstance(current, CtyList | CtySet | CtyMap):
            stack.append(current.element_type)
        elif isinstance(current, CtyTuple):
            stack.extend(current.element_types)
        elif isinstance(current, CtyObject):
            stack.extend(current.attribute_types.values())
    return False


def _is_leaf(value: CtyValue[Any]) -> bool:
    """Whether `value` has nothing nested inside it."""
    from pyvider.cty.values.base import CtyValue

    inner = value.value
    return not isinstance(inner, CtyValue) and not isinstance(inner, _NESTING_PAYLOADS)


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

    # Two leaves cannot hide a mark below the top level, so their own `marks`
    # settles it. Comparing scalars is the overwhelmingly common case and must
    # not pay to set up a walk that can only ever look at one value.
    if _is_leaf(a) and _is_leaf(b) and not a.marks and not b.marks:
        return _equals_leaves(a, b)

    # `collect_marks_deep` is memoized, but only after it has walked once, and
    # for a freshly built value that first walk dominates the comparison.
    a_marks = collect_marks_deep(a)
    b_marks = collect_marks_deep(b)
    if not a_marks and not b_marks:
        return _equals_unmarked(a, b)
    marks = a_marks | b_marks

    # go-cty keeps only top-level marks when exactly one side is null, on the
    # grounds that nested marks cannot have informed a decision that never
    # looked at nested values. Same reasoning, same behaviour.
    if a.is_null != b.is_null:
        marks = a.marks | b.marks

    result = _equals_unmarked(unmark_deep(a)[0], unmark_deep(b)[0])
    return result.with_marks(marks)


def _equals_leaves(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Both operands hold no nested value, so skip the container dispatch.

    Same decisions as `_equals_unmarked`, in the same order, minus the dynamic
    unwrapping a leaf cannot need and the isinstance chain over container types
    it can never match. Comparing two scalars is the common case by a wide
    margin and it is worth not walking past five container tests to reach it.
    """
    from pyvider.cty.types import CtyCapsule

    if a.is_unknown or b.is_unknown:
        return _equals_with_unknown(a, b)
    if a.is_null and b.is_null:
        return _bool(True)
    if a.is_null or b.is_null:
        return _bool(False)
    if not a.vtype.equal(b.vtype):
        return _bool(False)
    if isinstance(a.vtype, CtyCapsule):
        return _bool(a == b)
    return _bool(bool(a.value == b.value))


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

    from pyvider.cty.value_range import value_range

    known, unknown = (a, b) if not a.is_unknown else (b, a)
    if known.is_null:
        # The unknown may yet resolve to null, which would make them equal --
        # unless it has been refined as *not* null, in which case the answer is
        # settled without knowing anything else about it. go-cty decides this
        # first of all (`val.IsNull() && definitelyNotNull(other)`), and without
        # it a comparison against null stayed undecided forever no matter how
        # much the unknown had been narrowed.
        if value_range(unknown).definitely_not_null():
            return _bool(False)
        return _undecided()
    if _has_dynamic(known.vtype) or _has_dynamic(unknown.vtype):
        # go-cty checks `other.ty.HasDynamicTypes()` here. An unknown of dynamic
        # type has no settled type to compare against -- it is what
        # `cty_from_msgpack` produces for every not-yet-known dynamic attribute
        # Terraform sends -- so the type test below would rule it unequal on a
        # difference that has not been decided yet.
        return _undecided()
    if not known.vtype.equal(unknown.vtype):
        # No null comparison is in play, so mismatched types can never be equal
        # however the unknown resolves.
        return _bool(False)

    # The unknown's refinements may rule the known value out entirely: an
    # unknown number refined to [1, 10] is definitely not 50, whatever it turns
    # out to be. go-cty asks `Value.Range().Includes` here. Only a definite
    # *exclusion* is usable -- "within the bounds" is not "equal" -- so anything
    # other than a hard false stays undecided.
    excluded = value_range(unknown).includes(known)
    if not excluded.is_unknown and excluded.value is False:
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
    # An unknown's payload is a marker object, so comparing it raw would answer
    # definitely about a value that is not known.
    for side in (x, y):
        if isinstance(side, CtyValue) and (side.is_unknown or not side.is_wholly_known()):
            return _undecided()
    x_raw = x.value if isinstance(x, CtyValue) else x
    y_raw = y.value if isinstance(y, CtyValue) else y
    return _bool(bool(x_raw == y_raw))


def _equals_sequence(a_items: tuple[Any, ...], b_items: tuple[Any, ...]) -> CtyValue[Any]:
    """Index order, and the first undecided element settles it.

    Not `_combine`. go-cty walks a list or tuple by index and *returns* at the
    first element it cannot decide, so an undecided element at a low index wins
    over a definite difference at a higher one: `[unknown, "z"]` against
    `["a", "b"]` is undecided, while `["z", unknown]` against the same is a
    definite false. Measured against go-cty on 2026-08-17, deterministic across
    runs -- unlike objects and maps, where Go's randomised map iteration makes
    the same question a coin flip and this library deliberately answers false.

    Arguably go-cty is leaving information on the floor here, since the later
    difference is just as conclusive whichever order you find it in. But it is
    *deterministic* about it, so matching it is well-defined and cheap, and a
    provider that agrees with Terraform about a plan matters more than one that
    is cleverer than it.
    """
    if len(a_items) != len(b_items):
        return _bool(False)
    for x, y in zip(a_items, b_items, strict=True):
        result = _equals_item(x, y)
        if result.is_unknown:
            return _undecided()
        if result.value is False:
            return _bool(False)
    return _bool(True)


def _equals_mapping(a_map: dict[str, Any], b_map: dict[str, Any]) -> CtyValue[Any]:
    if a_map.keys() != b_map.keys():
        return _bool(False)
    return _combine([_equals_item(a_map[k], b_map[k]) for k in a_map])


def _equals_set(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Sets compare by membership, in both directions, as go-cty does.

    go-cty (`cty/value_ops.go:332-357`) walks each set once and declines to
    answer only when an element is unknown *at its own top level* -- because
    that element's identity is undecided, so how many distinct members the set
    has is undecided with it. Anything shallower than that it decides: it asks
    `s2.Has(rv)`, whose `Equivalent` is `Equals(...) == true`
    (`cty/set_internals.go:52-68`), so an element that merely *contains* an
    unknown is not equivalent to anything and the sets are definitely unequal.

    Two things were wrong here before 2026-08-17, both measured against the
    harness. The guard was `is_wholly_known()`, a deep walk, so a set of objects
    with one unknown attribute came back undecided where go-cty says a definite
    `false` -- and `set(object({...}))` is Terraform's nested-block-set type,
    so that is the common shape. And membership was tested one way round after a
    length comparison, over a `frozenset` of the elements, which raised
    `TypeError: unhashable type` for exactly those container elements.

    Both directions, and no length comparison, because that is what go-cty does:
    two payloads of different length can still each contain the other, and go-cty
    would call them equal.

    "Two unknown values are not equivalent for the sake of set membership" is
    preserved by the same guard that go-cty uses: the moment either set holds an
    unknown element, nothing is claimed about either set's cardinality.
    """
    from pyvider.cty.values.base import CtyValue

    a_items, b_items = _items(a), _items(b)
    for element in (*a_items, *b_items):
        if isinstance(element, CtyValue) and element.is_unknown:
            return _undecided()

    if _contains_every(a_items, b_items) and _contains_every(b_items, a_items):
        return _bool(True)
    return _bool(False)


def _bucket(member: Any) -> int:
    """A hash to group set members by, or 0 for a member that will not hash.

    Only ever a *hint*, so a coarse answer costs a scan and never a wrong one.
    The remaining refusals are the Python-protocol ones -- a mark object that is
    itself an unhashable container -- which is why the fallback exists rather
    than the raise being allowed through: the caller asked whether two sets are
    equal, not whether their members are hashable.
    """
    from pyvider.cty.values.base import CtyValue

    if not isinstance(member, CtyValue):
        return 0
    try:
        return hash(member)
    except TypeError:
        return 0


def _contains_every(needles: tuple[Any, ...], haystack: tuple[Any, ...]) -> bool:
    """Whether every needle has an *equivalent* in haystack. go-cty's `Set.Has`.

    Bucketed by hash, which is what go-cty's set package does and what
    `CtyValue.__hash__` became able to support on 2026-08-17. A pure pairwise
    scan is O(n*m), and `Value.Equals` on a nested block set is something a
    provider does on every plan: two equal 1000-element sets cost 1.3 s that way.

    The bucket is a hint and the fallback is the answer. `Equals` can call two
    values equal that hash apart -- nulls of two different types are equal in
    cty, and a hand-built `set(dynamic)` can hold both -- so a bucket miss
    re-checks the whole haystack instead of concluding from the hash. That keeps
    the result identical to the pairwise scan while paying for it at most once,
    because the first genuine miss ends the walk.
    """
    buckets: dict[int, list[Any]] = {}
    for candidate in haystack:
        buckets.setdefault(_bucket(candidate), []).append(candidate)

    def equivalent_in(candidates: Any) -> bool:
        return any(_equals_item(needle, candidate).value is True for candidate in candidates)

    for needle in needles:
        if equivalent_in(buckets.get(_bucket(needle), ())):
            continue
        if not equivalent_in(haystack):
            return False
    return True


# 🌊🪢🔚
