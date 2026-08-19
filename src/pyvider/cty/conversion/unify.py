#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/convert/unify.go`, `compare_types.go` and `sort_types.go`.

Type unification decides the element type of every set operation, of `concat`,
of `chunklist` over a tuple, and of `setproduct`'s tuple arguments -- so an
implementation that unifies differently disagrees with go-cty across a family of
functions at once rather than in one place.

What was here before answered `dynamic` for all but the trivial cases, and
`dynamic` is also what it answered for "these types have nothing in common".
Those are different facts: `setunion(set(number), set(bool))` is an error in
go-cty and was a `set(dynamic)` here. A differential run against the oracle
agreed on 6 of 38 cases. Hence `None` for no-common-type, matching go-cty's
`cty.NilType`, and hence this being a port rather than a patch.

Verified against `soup-go cty unify`, which exists because unification takes no
values and so cannot be reached through `cty call`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from functools import lru_cache
from typing import Any

from pyvider.cty.types import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)

# Every collection kind that unifies elementwise with itself, and the callable
# that rebuilds it from a unified element type.
_COLLECTIONS: tuple[tuple[type[CtyType[Any]], Any], ...] = (
    (CtyMap, lambda element: CtyMap(element_type=element)),
    (CtyList, lambda element: CtyList(element_type=element)),
    (CtySet, lambda element: CtySet(element_type=element)),
)


def compare_types(a: CtyType[Any], b: CtyType[Any]) -> int:  # noqa: C901
    """go-cty's `compareTypes`: negative when `a` is the more general of the two.

    "More general" means the one the other can convert *to*, so the result
    orders candidates for a unified type, best first.
    """
    a_dynamic, b_dynamic = isinstance(a, CtyDynamic), isinstance(b, CtyDynamic)
    if a_dynamic or b_dynamic:
        # Dynamic has the lowest preference of all: anything converts to it, so
        # choosing it throws away every other type's information. go-cty
        # optimistically assumes a dynamic will turn out to match its
        # neighbours instead.
        if not a_dynamic:
            return -1
        if not b_dynamic:
            return 1
        return 0

    if a.is_primitive_type() and b.is_primitive_type():
        # String is the supertype of the primitives, because every primitive
        # value has a string form. Number and bool have no supertype between
        # them at all.
        a_string, b_string = isinstance(a, CtyString), isinstance(b, CtyString)
        if a_string or b_string:
            if not a_string:
                return 1
            if not b_string:
                return -1
            return 0

    for kind, _ in _COLLECTIONS:
        if isinstance(a, kind) and isinstance(b, kind):
            return compare_types(a.element_type, b.element_type)  # type: ignore[attr-defined]

    # From here the pair may be swapped to halve the number of cases, so every
    # non-zero result below is multiplied back through `swap`.
    swap = 1
    if (
        (isinstance(a, CtyTuple) and isinstance(b, CtyList))
        or (isinstance(a, CtyObject) and isinstance(b, CtyMap))
        or (isinstance(a, CtySet) and isinstance(b, CtyTuple | CtyList))
    ):
        a, b = b, a
        swap = -1

    # Each of these optimistically assumes the element or attribute types can
    # themselves be unified; `unify` re-checks that and rejects the candidate if
    # they cannot.
    if isinstance(b, CtySet) and isinstance(a, CtyTuple | CtyList):
        return -1 * swap
    if isinstance(a, CtyList) and isinstance(b, CtyTuple):
        return -1 * swap
    if isinstance(a, CtyMap) and isinstance(b, CtyObject):
        return -1 * swap

    # Two objects or two tuples may have a supertype that is neither of them,
    # built by unifying their members one at a time. `unify` handles that; here
    # only the case where one of the two given types already *is* the supertype
    # is decided, and anything else is left as "no preference".
    if isinstance(a, CtyObject) and isinstance(b, CtyObject):
        if a.attribute_types.keys() != b.attribute_types.keys():
            return 0
        return _compare_members(
            [(a.attribute_types[name], b.attribute_types[name]) for name in a.attribute_types], swap
        )
    if isinstance(a, CtyTuple) and isinstance(b, CtyTuple):
        if len(a.element_types) != len(b.element_types):
            return 0
        return _compare_members(list(zip(a.element_types, b.element_types, strict=True)), swap)

    return 0


def _compare_members(pairs: list[tuple[CtyType[Any], CtyType[Any]]], swap: int) -> int:
    """Whether one side is the more general at every member, or neither is."""
    a_super = b_super = False
    for left, right in pairs:
        member = compare_types(left, right)
        if member < 0:
            a_super = True
        elif member > 0:
            b_super = True
    if a_super and b_super:
        return 0
    if a_super:
        return -1 * swap
    if b_super:
        return 1 * swap
    return 0


def sort_types(types: Sequence[CtyType[Any]]) -> list[int]:
    """Indices of `types`, most general first.

    go-cty's `sortTypes`: a topological sort of the "more general than" graph,
    which is a partial order -- some pairs are simply incomparable -- so a total
    sort would have to invent a preference the type system does not have. Ties
    keep their input order.
    """
    count = len(types)
    edges: list[list[int]] = [[] for _ in range(count)]
    for i in range(count - 1):
        for j in range(i + 1, count):
            comparison = compare_types(types[i], types[j])
            if comparison < 0:
                edges[i].append(j)
            elif comparison > 0:
                edges[j].append(i)

    in_degree = [0] * count
    for outs in edges:
        for j in outs:
            in_degree[j] += 1

    result = [i for i, degree in enumerate(in_degree) if degree == 0]
    cursor = 0
    while cursor < len(result):
        i = result[cursor]
        cursor += 1
        for j in edges[i]:
            in_degree[j] -= 1
            if in_degree[j] == 0:
                result.append(j)
    return result


def unify(types: Iterable[CtyType[Any]]) -> CtyType[Any] | None:
    """The single type all of `types` can convert to, or None if there is none.

    None rather than dynamic. Dynamic is a real answer -- it is what a group of
    collections containing a dynamic unifies to -- so using it for failure as
    well made an error indistinguishable from a result, and callers that should
    have raised silently produced a `dynamic`-typed value instead.
    """
    return _unify_cached(tuple(types))


@lru_cache(maxsize=1024)
def _unify_cached(types: tuple[CtyType[Any], ...]) -> CtyType[Any] | None:  # noqa: C901
    if not types:
        return None
    if len(types) == 1:
        return types[0]

    first = types[0]
    if all(other.equal(first) for other in types[1:]):
        return first

    # Same-kind groups first. In unsafe mode the general path below can convert
    # an object type to a *subset* of itself, which is a legal conversion and a
    # useless unification, so the structural cases have to win before it runs.
    counts = {kind: sum(isinstance(t, kind) for t in types) for kind, _ in _COLLECTIONS}
    objects = sum(isinstance(t, CtyObject) for t in types)
    tuples = sum(isinstance(t, CtyTuple) for t in types)
    dynamics = sum(isinstance(t, CtyDynamic) for t in types)
    total = len(types)

    for kind, rebuild in _COLLECTIONS:
        if counts[kind] > 0 and counts[kind] + dynamics == total:
            return _unify_collections(rebuild, types, has_dynamic=dynamics > 0)

    if counts[CtyMap] > 0 and counts[CtyMap] + objects + dynamics == total:
        # Objects often hold map-shaped data without being typed as maps.
        unified = _unify_objects_as_maps(types)
        if isinstance(unified, CtyMap):
            return unified
    if counts[CtyList] > 0 and counts[CtyList] + tuples + dynamics == total:
        # Tuples are often lists in disguise.
        unified = _unify_tuples_as_list(types)
        if isinstance(unified, CtyList):
            return unified
    if objects > 0 and objects + dynamics == total:
        return _unify_objects(types, has_dynamic=dynamics > 0)
    if tuples > 0 and tuples + dynamics == total:
        return _unify_tuples(types, has_dynamic=dynamics > 0)
    if objects > 0 and tuples > 0:
        # Incompatible kinds; no amount of member unification bridges them.
        return None

    return _unify_by_preference(types)


def _unify_by_preference(types: tuple[CtyType[Any], ...]) -> CtyType[Any] | None:
    """Take the most general candidate every other type can convert to."""
    from pyvider.cty.conversion.explicit import can_convert_unsafe

    for index in sort_types(types):
        want = types[index]
        if all(
            other.equal(want) or can_convert_unsafe(other, want) for i, other in enumerate(types) if i != index
        ):
            return want
    return None


def _unify_collections(
    rebuild: Any, types: tuple[CtyType[Any], ...], *, has_dynamic: bool
) -> CtyType[Any] | None:
    if has_dynamic:
        # Which path this takes once the dynamic resolves cannot be predicted,
        # so the honest answer is that the type is not yet decided.
        return CtyDynamic()
    element = _unify_cached(tuple(t.element_type for t in types))  # type: ignore[attr-defined]
    if element is None:
        return None
    return rebuild(element)  # type: ignore[no-any-return]


def _unify_objects(types: tuple[CtyType[Any], ...], *, has_dynamic: bool) -> CtyType[Any] | None:
    """Attribute by attribute if the names match exactly, otherwise as a map.

    Deliberately stricter than conversion is: `{"foo": true}` may convert to the
    empty object type, but unifying an object with the empty object type down to
    the empty object type would discard the attribute and surprise everyone.
    """
    if has_dynamic:
        return CtyDynamic()

    objects = [t for t in types if isinstance(t, CtyObject)]
    names = objects[0].attribute_types.keys()
    if any(other.attribute_types.keys() != names for other in objects[1:]):
        return _unify_objects_as_maps(types)

    attributes: dict[str, CtyType[Any]] = {}
    for name in names:
        unified = _unify_cached(tuple(obj.attribute_types[name] for obj in objects))
        if unified is None:
            # If one attribute has no common type then neither does the map
            # fallback, which unifies that same attribute against the others.
            return None
        attributes[name] = unified
    return CtyObject(attribute_types=attributes)


def _unify_objects_as_maps(types: tuple[CtyType[Any], ...]) -> CtyType[Any] | None:
    """Every attribute of every object, unified into one map element type."""
    from pyvider.cty.conversion.explicit import can_convert_unsafe

    attribute_types: list[CtyType[Any]] = []
    for candidate in types:
        if isinstance(candidate, CtyObject):
            attribute_types.extend(candidate.attribute_types.values())
        elif isinstance(candidate, CtyMap):
            attribute_types.append(candidate.element_type)

    element = _unify_cached(tuple(attribute_types))
    if element is None:
        return None
    result = CtyMap(element_type=element)
    if any(not t.equal(result) and not can_convert_unsafe(t, result) for t in types):
        return None
    return result


def _unify_tuples(types: tuple[CtyType[Any], ...], *, has_dynamic: bool) -> CtyType[Any] | None:
    """Position by position if the lengths match, otherwise as a list."""
    if has_dynamic:
        return CtyDynamic()

    tuples = [t for t in types if isinstance(t, CtyTuple)]
    length = len(tuples[0].element_types)
    if any(len(other.element_types) != length for other in tuples[1:]):
        return _unify_tuples_as_list(types)

    elements: list[CtyType[Any]] = []
    for position in range(length):
        unified = _unify_cached(tuple(candidate.element_types[position] for candidate in tuples))
        if unified is None:
            return None
        elements.append(unified)
    return CtyTuple(element_types=tuple(elements))


def _unify_tuple_types_to_list(tuples: tuple[CtyType[Any], ...]) -> CtyType[Any] | None:
    """go-cty's `unifyTupleTypesToList` (`convert/unify.go:457`).

    Every element of every *tuple*, unified into one list element type. Nothing
    else contributes: a list already in the caller's set is not folded in here,
    it is unified against the result afterwards.
    """
    from pyvider.cty.conversion.explicit import can_convert_unsafe

    element_types: list[CtyType[Any]] = []
    for candidate in tuples:
        element_types.extend(candidate.element_types)  # type: ignore[attr-defined]

    if not element_types:
        # `unify([])` is go-cty's degenerate case and answers nothing, so an
        # empty tuple cannot be made into a list here and the caller falls
        # through to the general path -- which is where go-cty answers it.
        return None

    element = _unify_cached(tuple(element_types))
    if element is None:
        return None
    result = CtyList(element_type=element)
    if any(not t.equal(result) and not can_convert_unsafe(t, result) for t in tuples):
        return None
    return result


def _unify_tuples_as_list(types: tuple[CtyType[Any], ...]) -> CtyType[Any] | None:
    """go-cty's `unifyTuplesAsList` (`convert/unify.go:135`).

    Two steps, and running them as one was the bug. This pooled every tuple's
    elements *and* every list's element type into a single unification, so
    `unify(tuple(list(string), number), list(dynamic))` folded the `dynamic`
    into the pool and answered `list(dynamic)` where go-cty finds no common type
    at all -- a container returned where real Terraform raises, so `concat` and
    `flatten` succeeded here on arguments Terraform rejects.

    go-cty unifies **only the tuples** into a list first. If that fails there is
    no list to reach, and the caller falls through to the general path. If it
    succeeds, each tuple is *replaced* by that list type and the whole set is
    unified again -- so a list already present is compared against the tuples'
    result rather than pooled with it.
    """
    tuples = tuple(t for t in types if isinstance(t, CtyTuple))
    as_list = _unify_tuple_types_to_list(tuples)
    if not isinstance(as_list, CtyList):
        return None

    listed = tuple(as_list if isinstance(t, CtyTuple) else t for t in types)
    unified = _unify_cached(listed)
    return unified if isinstance(unified, CtyList) else None


# 🌊🪢🔚
