#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Marks separated from a value and put back, with their locations kept.

go-cty spells these `UnmarkDeepWithPaths` and `MarkWithPaths`. `collect_marks_deep`
already answers "is anything in here sensitive", which is the right question for
a stdlib function deciding what to put on its result. It is the wrong question
for a *round trip*, because it returns the union and discards where each mark
was -- so a caller who strips marks to serialize cannot put them back.

That round trip is not hypothetical here. `cty_to_msgpack` raises on a marked
value, matching go-cty, so anything carrying marks to the wire has to strip them
first. Without these two functions every caller writes the walk itself, which is
how the same walk came to exist in three divergent copies before.

The location is a `CtyPath`, made hashable in phase 3, so a plain
`dict[CtyPath, frozenset]` stands in for go-cty's `[]PathValueMarks` and no new
container type is needed.
"""

from __future__ import annotations

from typing import Any, cast

from pyvider.cty.path import CtyPath, GetAttrStep, IndexStep, KeyStep
from pyvider.cty.types import CtyDynamic, CtyList, CtyMap, CtyObject, CtySet, CtyTuple
from pyvider.cty.values import CtyValue

__all__ = ["PathMarks", "mark_with_paths", "unmark_deep_with_paths"]

PathMarks = dict[CtyPath, frozenset[Any]]
"""Where each set of marks was found. go-cty's `[]PathValueMarks`."""


def unmark_deep_with_paths(value: CtyValue[Any], /) -> tuple[CtyValue[Any], PathMarks]:
    """Strip every mark in `value`, returning the bare value and where they were.

    The inverse of `mark_with_paths`, and the pair is what makes a
    strip-serialize-restore round trip lossless.
    """
    found: PathMarks = {}
    stripped = _strip(value, CtyPath.empty(), found)
    return stripped, found


def mark_with_paths(value: CtyValue[Any], path_marks: PathMarks, /) -> CtyValue[Any]:
    """Re-apply marks recorded by `unmark_deep_with_paths`.

    A path that no longer resolves is skipped rather than raising. The value may
    legitimately have changed shape between the two calls -- that is what a
    round trip through the wire does to an unknown -- and failing the whole
    restore because one location moved would lose every other mark with it.
    """
    if not path_marks:
        # go-cty's own fast path: nothing to apply, so do not rebuild the value.
        return value
    result = value
    for path, marks in path_marks.items():
        result = _apply(result, path.steps, marks)
    return result


def _strip(value: CtyValue[Any], path: CtyPath, found: PathMarks) -> CtyValue[Any]:
    if value.marks:
        found[path] = frozenset(value.marks)
        value = value.unmark()[0]

    # Checked before the payload, not through it. An unknown collection's
    # payload is an `UnrefinedUnknownValue`, not `None`, so testing only for
    # `None` reaches the descent below and tries to iterate it.
    if value.is_null or value.is_unknown:
        return value

    payload = value.value
    if payload is None:
        return value

    if isinstance(value.type, CtyDynamic) and isinstance(payload, CtyValue):
        # This package wraps a dynamic value in a CtyValue whose payload is
        # another CtyValue; go-cty has no such wrapper. Without this branch the
        # walk stopped at the wrapper and reported no marks for anything inside
        # it, so a strip-serialize-restore round trip -- the reason this module
        # exists -- handed the codec a value it then refused. The inner value's
        # marks are recorded at this same path, because the wrapper is
        # representation rather than structure.
        inner = _strip(payload, path, found)
        return value if inner is payload else _evolved(value, inner)

    if isinstance(value.type, CtyList | CtyTuple):
        elements = cast("tuple[CtyValue[Any], ...]", payload)
        rebuilt = tuple(
            _strip(element, path.index_step(index), found) for index, element in enumerate(elements)
        )
        # Identity, not equality. CtyValue.__eq__ delegates to a capsule's
        # equal_fn, which compares payloads and can ignore marks entirely, so
        # `==` reported "unchanged" for an element whose mark had just been
        # stripped and handed back the marked original -- while `found` recorded
        # the mark as removed. _strip returns its input unchanged when it has
        # nothing to do, which makes `is` exact where `==` is not.
        unchanged = len(rebuilt) == len(elements) and all(
            new is old for new, old in zip(rebuilt, elements, strict=True)
        )
        return value if unchanged else _evolved(value, rebuilt)

    if isinstance(value.type, CtyMap | CtyObject):
        items = cast("dict[str, CtyValue[Any]]", payload)
        step = GetAttrStep if isinstance(value.type, CtyObject) else KeyStep
        rebuilt_map = {
            key: _strip(element, path.with_step(step(key)), found) for key, element in items.items()
        }
        unchanged_map = rebuilt_map.keys() == items.keys() and all(
            rebuilt_map[key] is items[key] for key in items
        )
        return value if unchanged_map else _evolved(value, rebuilt_map)

    if isinstance(value.type, CtySet):
        # A set's elements are not addressable by a stable path: marking one
        # changes it, and a set keys its elements by value, so the path recorded
        # on the way out would not resolve on the way back in. CtySet.validate
        # already enforces the invariant that elements carry no marks -- it
        # hoists them onto the set, as go-cty's SetVal does -- so this hoists
        # any that a directly-constructed value still has, rather than dropping
        # them. Less precise than go-cty, and in the safe direction: a mark is
        # never lost, only recorded higher up than where it sat.
        return _hoist_set_marks(value, path, found)

    return value


def _hoist_set_marks(value: CtyValue[Any], path: CtyPath, found: PathMarks) -> CtyValue[Any]:
    elements = cast("tuple[CtyValue[Any], ...]", value.value)
    element_marks: frozenset[Any] = frozenset()
    rebuilt = []
    for element in elements:
        bare, marks = element.unmark()
        element_marks |= marks
        rebuilt.append(bare)
    if not element_marks:
        return value
    found[path] = found.get(path, frozenset()) | element_marks
    # A tuple, not a frozenset. The payload is canonically ordered and may hold
    # two unknowns that compare equal to each other, so rebuilding it as a
    # frozenset would both lose the order and silently drop one of them.
    # Stripping marks cannot reorder it: `_canonical_sort_key` is mark-blind.
    return _evolved(value, tuple(rebuilt))


def _evolved(value: CtyValue[Any], payload: Any) -> CtyValue[Any]:
    from attrs import evolve

    return evolve(value, value=payload)


def _apply(value: CtyValue[Any], steps: tuple[Any, ...], marks: frozenset[Any]) -> CtyValue[Any]:
    if not steps:
        return value.with_marks(marks)

    head, rest = steps[0], steps[1:]
    if value.is_null or value.is_unknown:
        return value
    payload = value.value
    if payload is None:
        return value

    # See through the dynamic wrapper, as _strip now does. The path recorded on
    # the way out does not mention the wrapper -- it is representation, not
    # structure -- so the way back in has to skip it too, or a strip/restore
    # round trip silently returns an unmarked value while reporting success.
    if isinstance(value.type, CtyDynamic) and isinstance(payload, CtyValue):
        rebuilt = _apply(payload, steps, marks)
        return value if rebuilt is payload else _evolved(value, rebuilt)

    if isinstance(head, IndexStep) and isinstance(payload, tuple):
        if not 0 <= head.index < len(payload):
            return value
        elements = list(payload)
        elements[head.index] = _apply(elements[head.index], rest, marks)
        return _evolved(value, tuple(elements))

    if isinstance(head, GetAttrStep | KeyStep) and isinstance(payload, dict):
        key = head.name if isinstance(head, GetAttrStep) else head.key
        if key not in payload:
            return value
        updated = dict(payload)
        updated[key] = _apply(updated[key], rest, marks)
        return _evolved(value, updated)

    return value


# 🌊🪢🔚
