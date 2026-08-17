#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Visiting and rebuilding a nested value, mirroring go-cty's `cty/walk.go`.

Three entry points, in the order most callers want them:

  - `deep_values` yields every value inside a value, itself first. This is the
    ergonomic one, and go-cty says so too -- it added `DeepValues` once Go grew
    iterators and tells new callers to prefer it over `Walk`.
  - `walk` is the same traversal with a callback that can decline to descend.
    Pruning is the one thing a plain generator cannot express.
  - `transform` rebuilds a value bottom-up, which is how you make what looks
    like a deep mutation of an immutable structure.

**All three are iterative.** A recursive version of exactly this shape lives in
pyvider's `conversion/marshaler.py`, whose own comment records that it "did
raise RecursionError at a nesting depth pyvider-cty advertises as supported,
once a realistic handler stack was underneath it". The stack here is a list.

Deliberately not merged with the mark walk in `pyvider.cty.marks`, despite that
module's history of duplicated traversals being the root cause of a whole bug
class. The two answer different questions: the mark walk also descends raw
Python containers, because `validate` is routinely handed a bare list or dict,
and it memoizes its answer on the value. This one visits only `CtyValue`s and
has a path to report. Merging them would mean the raw-container case grows a
path it cannot describe.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any, cast

from attrs import evolve

from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep, PathStep
from pyvider.cty.types import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyTuple,
    CtyType,
)
from pyvider.cty.values import CtyValue

__all__ = ["deep_values", "transform", "walk"]

# The callback shapes. `walk`'s answers "descend into this?"; `transform`'s
# returns the replacement for the value it was handed.
WalkFn = Callable[[CtyPath, CtyValue[Any]], bool]
TransformFn = Callable[[CtyPath, CtyValue[Any]], CtyValue[Any]]


def _unwrap_dynamic(value: CtyValue[Any]) -> CtyValue[Any]:
    """The value a CtyDynamic wrapper stands in front of.

    A dynamic wrapper is transparent to traversal: it is a statement about how
    the value was typed, not a level of nesting a caller would want a path step
    for. `IndexStep` and `KeyStep` already unwrap it in their own `apply`, so
    treating it as transparent here is what keeps the emitted paths applicable.
    """
    while isinstance(value.type, CtyDynamic) and isinstance(value.value, CtyValue):
        value = value.value
    return value


def _child_steps(value: CtyValue[Any]) -> list[tuple[PathStep, CtyValue[Any]]]:
    """The values one level inside `value`, each with the step that reaches it.

    Empty for a leaf, and for a null or unknown value of any type -- there is
    nothing inside either one to visit, which is go-cty's rule as well.
    """
    inner = _unwrap_dynamic(value)
    if inner.is_null or inner.is_unknown:
        return []

    vtype = inner.type
    # Attribute and key order is *sorted*, which is go-cty's rule and its
    # reason: "we iterate the keys in a predictable lexicographical order so
    # that results will always be stable given the same input map". Declared
    # order and insertion order are both properties of how a value was built
    # rather than of the value, so a traversal that used them could visit the
    # same logical value in two different orders in one process.
    if isinstance(vtype, CtyObject):
        payload = cast(Mapping[str, CtyValue[Any]], inner.value)
        # Driven by the type's attributes rather than the payload's keys, so a
        # stray key cannot smuggle in a step.
        return [
            (GetAttrStep(name), payload[name]) for name in sorted(vtype.attribute_types) if name in payload
        ]
    if isinstance(vtype, CtyMap):
        payload = cast(Mapping[str, CtyValue[Any]], inner.value)
        return [(KeyStep(key), payload[key]) for key in sorted(payload)]
    if isinstance(vtype, CtyList | CtyTuple):
        elements = cast(Sequence[CtyValue[Any]], inner.value)
        return [(IndexStep(i), element) for i, element in enumerate(elements)]
    if isinstance(vtype, CtySet):
        # A set element is addressed by itself -- go-cty spells this as an
        # IndexStep whose key is the element, "with the idea that a set element
        # effectively acts as its own key in the set". pyvider splits go-cty's
        # one IndexStep into an int-keyed IndexStep and a KeyStep, so the
        # key-addressed half is the one that fits.
        #
        # Sorted because a frozenset has no order to report, and a traversal
        # whose output changes between runs is not one you can test or diff.
        elements = sorted(cast(Any, inner.value), key=lambda element: element._canonical_sort_key())
        return [(KeyStep(element), element) for element in elements]
    return []


def deep_values(value: CtyValue[Any]) -> Iterator[tuple[CtyPath, CtyValue[Any]]]:
    """Every value within `value`, itself first, then its contents recursively.

    go-cty's `DeepValues`. Unlike go-cty's, the yielded paths are ordinary
    values with no lifetime rule attached: go-cty reuses one backing array and
    warns that a path "may not be used after that function returns", which is a
    caution about its own allocation strategy rather than about paths.
    """
    stack: list[tuple[CtyPath, CtyValue[Any]]] = [(CtyPath.empty(), value)]
    while stack:
        path, current = stack.pop()
        yield path, current
        # Reversed so that popping restores the natural order.
        for step, child in reversed(_child_steps(current)):
            stack.append((path.with_step(step), child))


def walk(value: CtyValue[Any], visit: WalkFn) -> None:
    """`deep_values`, but `visit` decides whether to descend into each value.

    go-cty's `Walk`. Return False from `visit` to skip the contents of the value
    just visited; the traversal continues with its siblings.
    """
    stack: list[tuple[CtyPath, CtyValue[Any]]] = [(CtyPath.empty(), value)]
    while stack:
        path, current = stack.pop()
        if not visit(path, current):
            continue
        for step, child in reversed(_child_steps(current)):
            stack.append((path.with_step(step), child))


def _rebuilt_type(original: CtyType[Any], children: list[CtyValue[Any]]) -> CtyType[Any]:
    """The type the rebuilt container should be validated against.

    A tuple's type is a statement about each of its elements, so a transform
    that changes an element's type changes the tuple's type with it -- that is
    what go-cty's `TupleVal` does when it derives the type from the elements it
    was given. Every other container names its element type once, so the
    original type is kept and a type-changing transform is refused by
    validation. go-cty reaches the same outcome by panicking, and its docs say
    so: "this function can panic if such invariants are violated".
    """
    if isinstance(original, CtyTuple):
        return CtyTuple(element_types=tuple(child.type for child in children))
    return original


def _payload_key(step: PathStep) -> Any:
    """The dict key a step stands for, when rebuilding an object or a map."""
    if isinstance(step, GetAttrStep):
        return step.name
    if isinstance(step, KeyStep):
        return step.key
    raise TypeError(f"cannot rebuild a keyed container from {type(step).__name__}")


def _rebuild(
    original: CtyValue[Any],
    child_steps: list[tuple[PathStep, CtyValue[Any]]],
    children: list[CtyValue[Any]],
) -> CtyValue[Any]:
    """`original` with its contents replaced by `children`.

    `child_steps` are what `_child_steps` produced for `original`, passed in
    rather than recomputed -- a second walk here would double the cost of every
    transform, which is how `flatten` earned a 117% regression.

    A container whose children all came back unchanged is returned as it is.
    Most transforms touch a few leaves and leave everything above them alone,
    and rebuilding those meant re-validating the whole structure: an identity
    transform over a 10k-object list cost 166 ms of pure copying.

    The test is identity, not equality, for the reason `marks._strip` gives:
    `CtyValue.__eq__` delegates to a capsule's `equal_fn`, which compares
    payloads and ignores marks, so `==` can call a value unchanged when its
    marks have in fact changed. `is` cannot be fooled that way.
    """
    if all(new is old for new, (_step, old) in zip(children, child_steps, strict=True)):
        return original

    inner = _unwrap_dynamic(original)
    vtype = inner.type

    payload: Any
    if isinstance(vtype, CtyObject | CtyMap):
        payload = dict(zip((_payload_key(step) for step, _ in child_steps), children, strict=True))
    else:
        payload = children

    rebuilt = _rebuilt_type(vtype, children).validate(payload)
    # Marks live on the value, so a rebuild has to put the container's own back.
    # Element marks travel with the elements, except on a set, where `validate`
    # hoists them onto the set exactly as go-cty's `SetVal` does.
    if inner.marks:
        rebuilt = rebuilt.with_marks(inner.marks)
    if inner is original:
        return rebuilt
    # Put the dynamic wrapper back on, since the caller's value was typed that
    # way and a transform is not supposed to retype what it did not touch.
    return evolve(original, value=rebuilt)


def transform(value: CtyValue[Any], fn: TransformFn) -> CtyValue[Any]:
    """`value` with `fn` applied to every value inside it, innermost first.

    go-cty's `Transform`. Children are visited before the container, so `fn`
    sees a container already built from its transformed contents -- which is
    what makes this usable for deep edits of an immutable structure.

    `fn` is responsible for preserving invariants. Changing the type of a list
    element, or of an object attribute, is refused by the rebuild.
    """
    # A frame is either a value to visit (`pending` is None) or a container
    # waiting on its children, carrying the steps and originals that produced
    # them. `done` is the result stack: each finished value is pushed, and a
    # rebuild pops back exactly as many children as it pushed.
    Frame = tuple[CtyPath, CtyValue[Any], list[tuple[PathStep, CtyValue[Any]]] | None]
    todo: list[Frame] = [(CtyPath.empty(), value, None)]
    done: list[CtyValue[Any]] = []

    while todo:
        path, current, pending = todo.pop()
        if pending is not None:
            children = [done.pop() for _ in range(len(pending))][::-1]
            done.append(fn(path, _rebuild(current, pending, children)))
            continue

        child_steps = _child_steps(current)
        if not child_steps:
            done.append(fn(path, current))
            continue

        todo.append((path, current, child_steps))
        for step, child in reversed(child_steps):
            todo.append((path.with_step(step), child, None))

    return done.pop()


# 🌊🪢🔚
