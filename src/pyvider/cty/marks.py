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

    **The memo assumes a CtyValue's payload is never mutated in place.** That is
    a contract, not something the type system enforces: freezing an attrs class
    freezes the reference to `value`, not what it points at, and maps and objects
    hold a plain dict. The same contract already underpins `__eq__`, `__hash__`
    and `_canonical_sort_key`, all of which read payload contents -- mutating a
    payload has never been supported.

    An earlier version of this skipped the memo for any subtree containing a
    mutable container, so that a stale answer was impossible by construction.
    That was measured on maps of 10-1000 entries and looked free. It is not: the
    cost is linear per call, and a 20k-entry map went from 0.003 ms to 2.7 ms on
    every stdlib call taking it as an argument -- a 96,000% regression on
    `length()`. Correctness by construction was not worth that, given the
    mutation it defended against has no caller anywhere in the workspace.

    If that defence is wanted back, the way to get it is to make map and object
    payloads genuinely immutable -- a `dict` subclass that refuses mutation
    keeps every `isinstance(x, dict)` check working -- rather than to give up
    the memo.
    """
    from pyvider.cty.values import CtyValue

    if not isinstance(value, CtyValue):
        return _walk_marks(value)
    if value._deep_marks is not None:
        return value._deep_marks
    marks = _walk_marks(value)
    object.__setattr__(value, "_deep_marks", marks)
    return marks


def _push_children(current: Any, stack: list[Any], visited: set[int]) -> None:
    """Queue a raw container's children, unless it has been seen before."""
    current_id = id(current)
    if current_id in visited:
        return
    visited.add(current_id)
    if isinstance(current, dict):
        stack.extend(current.values())
    else:
        stack.extend(current)


def _walk_marks(root: Any) -> frozenset[Any]:
    """The walk behind `collect_marks_deep`, without the memo.

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
    nested = (CtyValue, dict, *_MARK_BEARING_SEQUENCES)

    while stack:
        current = stack.pop()

        if not isinstance(current, CtyValue):
            if isinstance(current, nested):
                _push_children(current, stack, visited)
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
            # Identity, not equality: cycles are why the recursion guard exists,
            # and a shared subtree only needs collecting once.
            current_id = id(current)
            if current_id in visited:
                continue
            visited.add(current_id)
            stack.append(inner)

    return marks


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
    """A copy of `value` with every mark removed, at any depth."""
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
