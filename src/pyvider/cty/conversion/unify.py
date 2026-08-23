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
    from pyvider.cty.conversion.explicit import _without_optional

    if not types:
        return None
    # Both shortcuts hand back an *input* type, and an input can carry optional
    # attributes where a unified type must not: optionality describes a
    # constraint ("you need not supply this") and `unify` answers with a type
    # for values. go-cty strips it -- `unify(object({a=string}, optional=[a]))`
    # is `object({a=string})` there even for a single argument -- and the
    # difference reaches the wire, because the optional set is part of the type
    # a collection declares. Every other path here builds its result from
    # unified children and so is already stripped; these two were passing the
    # argument straight through. Found 2026-08-20 by the generated unify sweep.
    if len(types) == 1:
        return _without_optional(types[0])

    first = types[0]
    if all(other.equal(first) for other in types[1:]):
        return _without_optional(first)

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


def _preference_order(types: tuple[CtyType[Any], ...]) -> list[int]:
    """`sort_types`, with a structural candidate brought in front of a collection.

    `compare_types` ranks `map(dynamic)` as *more general* than an object type,
    which is true of conversion and wrong as a preference: unifying
    `map(dynamic)` with `object({a: list(string), b: number})` took the map and
    threw the structure away, where go-cty keeps the object.

    Asked of the oracle, and the pair of answers is what pins the rule down::

        soup-go cty unify '["map","dynamic"]' '["object",{"a":"string","b":"number"}]'
        -> ["map","string"]
        soup-go cty unify '["map","dynamic"]' '["object",{"a":["list","string"],"b":"number"}]'
        -> ["object",{"a":["list","string"],"b":"number"}]

    So the map wins when the object's attributes unify -- when it really is a
    map wearing an object's clothes -- and the object wins when they do not.
    Both orders of the arguments give the same answer there, so this is a
    property of the types and not of how they arrived.

    That first case never reaches here: `_unify_objects_as_maps` runs earlier
    and answers `map(string)` for it. Anything arriving at this function with
    both kinds present has already had map-ification tried and refused, and the
    structural candidate is the one go-cty keeps. Within each group the
    topological order is preserved, so nothing else is reordered.

    Held back when a bare `dynamic` is among the candidates, and the oracle is
    why. `_unify_objects_as_maps` gives up in that case -- the dynamic makes the
    collection stage unify to `dynamic` rather than to a map -- so its refusal
    stops meaning "these cannot be a map" and this function starts seeing pairs
    whose map-ification was never really tried::

        soup-go cty unify '"dynamic"' '["map","string"]' '["object",{"a":"number"}]'
        -> ["map","string"]

    go-cty maps that one, because `number` converts to `string`. Preferring the
    object there was wrong, and the generated unify sweep caught it.
    """
    order = sort_types(types)
    if any(isinstance(t, CtyDynamic) for t in types):
        return order
    structural = [i for i in order if isinstance(types[i], CtyObject | CtyTuple)]
    if not structural:
        return order

    # An object only wins for being a shape a map cannot hold. An *attribute-less*
    # object is not that: it converts to a map of anything, and go-cty says so --
    #
    #     soup-go cty unify '["object",{}]' '["map","string"]'  ->  ["map","string"]
    #
    # -- so preferring it there is wrong. `_unify_object_types_to_map` answers
    # None for an empty object because it has no attribute types to unify, which
    # reads the same as "these attributes share nothing" and is the opposite
    # fact. Distinguished here rather than there, because that function's None
    # is right for its own callers.
    #
    # Caught by the generated type-relation property test on
    # `list(set(object{}))` + `list(set(map(string)))`, one merge after the
    # preference order landed; the 1331-case sweep has no empty object in it.
    objects = tuple(t for t in types if isinstance(t, CtyObject))
    if objects and (
        any(not obj.attribute_types for obj in objects) or _unify_object_types_to_map(objects) is not None
    ):
        return order
    return structural + [i for i in order if not isinstance(types[i], CtyObject | CtyTuple)]


def _unify_by_preference(types: tuple[CtyType[Any], ...]) -> CtyType[Any] | None:
    """Take the most general candidate every other type can convert to."""
    from pyvider.cty.conversion.explicit import can_convert_unsafe

    for index in _preference_order(types):
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
    """The objects as one map first, then that map against the maps given.

    Two stages, as go-cty's `unifyObjectsAsMaps` (`convert/unify.go:192`): the
    objects' attribute types unify into a map element type among themselves,
    and only that map meets the real map types. Pooling every attribute type
    with every map element type in one unify let a `dynamic` attribute win the
    pool -- `map(list(string))` + `object({a: string, b: dynamic})` became
    `map(dynamic)` -- where go-cty unifies the object to `map(string)` first,
    then finds `list(string)` and `string` share nothing, and refuses.
    """
    objects = tuple(t for t in types if isinstance(t, CtyObject))
    as_map = _unify_object_types_to_map(objects)
    if as_map is None:
        return None
    mapped = tuple(as_map if isinstance(t, CtyObject) else t for t in types)
    unified = _unify_cached(mapped)
    return unified if isinstance(unified, CtyMap) else None


def _unify_object_types_to_map(objects: tuple[CtyObject, ...]) -> CtyMap[Any] | None:
    """Every attribute of every object, unified into one map element type.

    go-cty's `unifyObjectTypesToMap`: the fallback for objects whose attribute
    names differ, and the first stage of unifying objects with maps.
    """
    from pyvider.cty.conversion.explicit import can_convert_unsafe

    attribute_types = tuple(aty for obj in objects for aty in obj.attribute_types.values())
    element = _unify_cached(attribute_types)
    if element is None:
        return None
    result: CtyMap[Any] = CtyMap(element_type=element)
    if any(not obj.equal(result) and not can_convert_unsafe(obj, result) for obj in objects):
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
