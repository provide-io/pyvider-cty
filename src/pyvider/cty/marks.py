#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import Any

from attrs import define, field


def _convert_details(value: Any) -> frozenset[Any] | None:
    """Converter to ensure the 'details' field is always hashable."""
    if value is None:
        return None
    if isinstance(value, dict):
        return frozenset(value.items())
    if isinstance(value, list | set | tuple):
        return frozenset(value)
    return frozenset([value])


@define(frozen=True, slots=True)
class CtyMark:
    """
    Represents a mark that can be applied to a cty.Value.
    The 'details' attribute is automatically converted to a hashable frozenset.
    """

    name: str = field()
    details: frozenset[Any] | None = field(default=None, converter=_convert_details)

    def __repr__(self) -> str:
        if self.details is not None:
            return f"CtyMark({self.name!r}, {dict(self.details)!r})"
        return f"CtyMark({self.name!r})"

    def __str__(self) -> str:
        return self.name


# Raw Python containers that may hold marked CtyValues. Sets are here because a
# validated CtySet stores a frozenset; strings are deliberately absent, being
# iterable but incapable of carrying a mark.
_MARK_BEARING_SEQUENCES = (list, tuple, set, frozenset)

# Containers whose contents can change after a walk has looked at them. A memo
# taken over one of these could later under-report marks, so it is not taken.
# `FrozenDict` is deliberately excluded: map and object payloads are built as
# one precisely so this memo is safe for them, which is what keeps every
# stdlib call on an object off a full re-walk.
_MUTABLE_CONTAINERS = (dict, list, set, bytearray)


def _is_mutable_container(obj: Any) -> bool:
    from pyvider.cty.values.frozen import FrozenDict

    return isinstance(obj, _MUTABLE_CONTAINERS) and not isinstance(obj, FrozenDict)


def collect_marks_deep(value: Any) -> frozenset[Any]:
    """Every mark anywhere in `value`, at any depth.

    go-cty spells the equivalent `Value.UnmarkDeep`, and reaches for it in every
    place a value's sensitivity has to be judged as a whole. This is the single
    implementation of that walk: it previously existed three times over, in the
    function wrapper, the recursion guard and the set constructor, and each copy
    matched on a different set of container types. The one they all disagreed
    about was the set, whose payload is a frozenset rather than a tuple.

    Raw Python containers are walked as well as CtyValues, because `validate` is
    routinely handed a plain list or dict whose elements are already-validated
    marked values.

    Iterative by design. One caller is the recursion guard's stop path, reached
    precisely when a value was too deep or too cyclic to recurse over.

    The result is memoized on the CtyValue, which is what keeps the cost linear
    where it matters: the wrapper around every stdlib function asks this question
    about every argument, so without a memo an O(1) call like `length` pays a
    full walk of its input every time it is called.

    **The memo is only taken when the walk proves the whole subtree immutable.**
    Freezing an attrs class freezes the reference to `value`, not what it points
    at. A memo over something that can still change may be left
    under-reporting, and a memo that under-reports is a silent declassification:
    a value that has become sensitive still answering "not sensitive".

    That gate was removed once, for speed, on the stated grounds that nothing in
    the workspace mutates a payload in place. It was asserted without checking
    and was false, and the declassification was reproducible.

    Keeping the gate then cost maps and objects a full re-walk per stdlib call
    -- 12 ms for a 20k-entry map, and every Terraform resource is an object. So
    the invariant is now enforced instead of assumed: map and object payloads
    are built as `FrozenDict`, which refuses mutation while still being a
    `dict`, and are therefore memoizable. Raw lists and plain dicts handed
    straight to `validate` remain unmemoized, because those really can change.
    """
    from pyvider.cty.values import CtyValue

    if not isinstance(value, CtyValue):
        return _walk_marks(value)[0]
    if value._deep_marks is not None:
        return value._deep_marks
    marks, memoizable = _walk_marks(value)
    if memoizable:
        object.__setattr__(value, "_deep_marks", marks)
    return marks


def _push_children(current: Any, stack: list[Any], visited: set[int]) -> bool:
    """Queue a raw container's children, unless it has been seen before.

    Returns whether `current` can change behind a memo's back, which the caller
    accumulates to decide if the walk's result is safe to memoize.
    """
    current_id = id(current)
    if current_id not in visited:
        visited.add(current_id)
        if isinstance(current, dict):
            stack.extend(current.values())
        else:
            stack.extend(current)
    return _is_mutable_container(current)


def _walk_marks(root: Any) -> tuple[frozenset[Any], bool]:
    """The walk behind `collect_marks_deep`, without the memo.

    Returns the marks found, and whether the result is safe to memoize -- false
    if any container in the subtree can be mutated in place. A cached descendant
    counts as immutable without re-checking, since it could only have been
    cached by this same rule.

    Hot: it runs over every element of every collection argument to every stdlib
    function. Three things keep the constant down, and all three showed up as
    real time on a 200k-element list.

     - Cycle bookkeeping happens only for values that hold a container. A leaf
       cannot take part in a cycle, and leaves are nearly all of the work.
     - `marks |= ...` is guarded, because unioning an empty frozenset still
       allocates one, once per element.
     - The isinstance tuple is built once, not per iteration.
    """
    from pyvider.cty.values import CtyValue

    marks: frozenset[Any] = frozenset()
    visited: set[int] = set()
    stack: list[Any] = [root]
    memoizable = True
    nested = (CtyValue, dict, *_MARK_BEARING_SEQUENCES)

    while stack:
        current = stack.pop()

        if not isinstance(current, CtyValue):
            if isinstance(current, nested):
                memoizable &= not _push_children(current, stack, visited)
            continue

        # A descendant that already knows its own deep marks answers for its
        # whole subtree. This is what keeps the recursion guard's unwind linear:
        # each ancestor frame would otherwise re-walk the subtree its child just
        # walked, making the abort path O(depth x size).
        cached = current._deep_marks
        if cached is not None and current is not root:
            if cached:
                marks |= cached
            continue
        if current.marks:
            marks |= current.marks
        inner = current.value
        if isinstance(inner, nested):
            if _is_mutable_container(inner):
                memoizable = False
            # Identity, not equality: cycles are why the recursion guard exists,
            # and a shared subtree only needs collecting once.
            current_id = id(current)
            if current_id in visited:
                continue
            visited.add(current_id)
            stack.append(inner)

    return marks, memoizable


def unmark_deep(value: Any) -> tuple[Any, frozenset[Any]]:
    """`value` with every mark removed at any depth, and the marks removed.

    Mirrors go-cty's `Value.UnmarkDeep`.
    """
    return _strip(value), collect_marks_deep(value)


def _children(value: Any) -> tuple[Any, ...] | dict[str, Any] | None:
    """The nested values a container holds, or None for a leaf.

    Lists and tuples hold a tuple; a validated set holds a *frozenset*; maps and
    objects hold a dict; CtyDynamic wraps a single value. Primitives and capsules
    are leaves. Sets are snapshotted to a tuple so the order seen here is the
    order `_strip` rebuilds against.
    """
    from pyvider.cty.values import CtyValue

    if not isinstance(value, CtyValue) or value.is_null or value.is_unknown:
        return None
    inner = value.value
    if isinstance(inner, tuple):
        return inner
    if isinstance(inner, (frozenset, set)):
        return tuple(inner)
    if isinstance(inner, dict):
        return inner
    if isinstance(inner, CtyValue):
        return (inner,)
    return None


def _strip(value: Any) -> Any:
    """A copy of `value` with every mark removed, at any depth.

    Two shortcuts, both load-bearing. A value carrying no marks anywhere is
    already its own stripped form and is returned untouched rather than
    rebuilt. And the rebuilt copy is memoized, under the same immutability rule
    as the mark memo, because the function wrapper strips every marked argument
    on every call -- without this a marked 50k-element list cost 40 ms per
    stdlib call against 0.005 ms for the same list unmarked, and the memo that
    fixed the unmarked path did nothing for the marked one.
    """
    from pyvider.cty.values import CtyValue

    if not isinstance(value, CtyValue):
        return value

    if not collect_marks_deep(value):
        return value

    cached = value._stripped
    if cached is not None:
        return cached

    result = _strip_uncached(value)
    # `_deep_marks` is set only for a subtree the walk proved immutable, which
    # is exactly the condition under which this copy stays valid.
    if value._deep_marks is not None:
        object.__setattr__(value, "_stripped", result)
    return result


def _strip_uncached(value: Any) -> Any:
    """The rebuild behind `_strip`, without its shortcuts."""
    from attrs import evolve

    from pyvider.cty.values import CtyValue

    if not isinstance(value, CtyValue):
        return value

    children = _children(value)
    stripped = value.unmark()[0] if value.marks else value

    if children is None:
        return stripped

    # "Did anything change" is decided by identity, never by ==. CtyValue.__eq__
    # delegates to a CtyCapsuleWithOps' equal_fn, which compares payloads and
    # ignores marks entirely, so an equality check reports "unchanged" for a
    # capsule whose mark was just stripped and hands the caller back the marked
    # value. _strip returns the input object itself when it has nothing to do,
    # which makes `is` an exact test.
    if isinstance(children, dict):
        rebuilt_map = {k: _strip(v) for k, v in children.items()}
        if all(rebuilt_map[k] is v for k, v in children.items()):
            return stripped
        return evolve(stripped, value=rebuilt_map)

    if isinstance(stripped.value, CtyValue):
        rebuilt_inner = _strip(children[0])
        if rebuilt_inner is children[0]:
            return stripped
        return evolve(stripped, value=rebuilt_inner)

    rebuilt_seq = tuple(_strip(v) for v in children)
    if all(new is old for new, old in zip(rebuilt_seq, children, strict=True)):
        return stripped
    if isinstance(stripped.value, (frozenset, set)):
        # Rebuild as a set. Removing marks can make two elements that differed
        # only by their marks equal, so the unmarked set may be smaller -- which
        # is what an unmarked view of the set should be.
        return evolve(stripped, value=frozenset(rebuilt_seq))
    return evolve(stripped, value=rebuilt_seq)


# 🌊🪢🔚
