#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import Any

from attrs import define, evolve, field

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.values import CtyValue
from pyvider.cty.values.frozen import FrozenDict


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

# Every payload type that can hold a mark below the top level. A CtyValue whose
# payload is anything else is a leaf, and its own `marks` is the whole answer.
_NESTED = (CtyValue, dict, *_MARK_BEARING_SEQUENCES)

# Containers whose contents can change after a walk has looked at them. A memo
# taken over one of these could later under-report marks, so it is not taken.
# `FrozenDict` is deliberately excluded: map and object payloads are built as
# one precisely so this memo is safe for them, which is what keeps every
# stdlib call on an object off a full re-walk.
_MUTABLE_CONTAINERS = (dict, list, set, bytearray)


def _is_mutable_container(obj: Any) -> bool:
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

    if not isinstance(value, CtyValue):
        return _walk_marks(value)[0]
    cached = value._deep_marks
    if cached is not None:
        return cached
    if not isinstance(value.value, _NESTED):
        # A leaf. Setting up the walk -- a frozenset, a set, a list and one
        # iteration -- costs more than the answer, and this runs twice per
        # argument of every stdlib call (once to collect, once to strip). A leaf
        # payload is immutable, so the memo is safe by the rule below.
        marks = value.marks
        object.__setattr__(value, "_deep_marks", marks)
        return marks
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
     - The isinstance tuple is a module constant, not built per call.
    """

    marks: frozenset[Any] = frozenset()
    visited: set[int] = set()
    stack: list[Any] = [root]
    memoizable = True
    nested = _NESTED

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

    if not isinstance(value, CtyValue):
        return None
    # Deliberately not skipped for `is_unknown`. A container flags itself
    # unknown as soon as any element is unknown while keeping the rest of its
    # elements, so bailing here left `_strip` unable to descend -- `unmark_deep`
    # then reported an unknown container's deep marks without removing them,
    # and `contains` gave a different answer for the same data depending on
    # whether an element was marked. A genuinely unknown value holds a marker
    # object rather than a container, and falls through the type tests below.
    inner = value.value
    # `list` as well as `tuple`. `validate` is routinely handed a raw list whose
    # elements are already-validated marked values, and a directly-constructed
    # CtyValue keeps it. _walk_marks already descended into lists, so the two
    # halves of unmark_deep disagreed about what a container is: it reported
    # marks it had not removed, and equality -- which trusts unmark_deep to have
    # cleaned both sides -- then hit a still-marked element and raised a bare
    # ValueError out of value_range.
    if isinstance(inner, tuple | list):
        return tuple(inner)
    if isinstance(inner, (frozenset, set)):
        return tuple(inner)
    if isinstance(inner, dict):
        return inner
    if isinstance(inner, CtyValue):
        return (inner,)
    return None


# Marks the point in the strip stack where a node's children are all resolved.
_STRIP_POST = object()

# Returned by `_resolve_or_children` for a node whose children must be walked.
_DESCEND = object()


def _already_stripped(value: Any) -> Any | None:
    """`value`'s stripped form if it is known *without walking*, else None.

    Deliberately memo-only. `collect_marks_deep` memoizes the node it was asked
    about and not the descendants it visited -- by design, since the recursion
    guard calls it bottom-up as it unwinds and each level memoizes itself. A
    top-down walk gets the opposite: asking it per node re-walks each subtree
    its parent has just walked, which made the strip O(n^2) in the depth. At
    5000 levels that is 9.6 s of re-walking, and it was only invisible before
    because the recursion limit stopped the walk at 330.

    So the descent reads the memo directly and treats "not known" as "descend".
    Descending into an already-clean subtree costs one visit per node; asking
    the question properly costs a walk per node.
    """
    if value._deep_marks == frozenset():
        return value
    return value._stripped


def _stripped_without_descending(value: Any) -> Any | None:
    """The entry-point shortcut, which *is* allowed to walk.

    Two of them, both load-bearing. A value carrying no marks anywhere is
    already its own stripped form and is returned untouched rather than rebuilt.
    And a rebuilt copy is memoized, under the same immutability rule as the mark
    memo, because the function wrapper strips every marked argument on every
    call -- without this a marked 50k-element list cost 40 ms per stdlib call
    against 0.005 ms for the same list unmarked, and the memo that fixed the
    unmarked path did nothing for the marked one.

    The walk here is what makes the unmarked fast path free, and it is affordable
    exactly once: the wrapper strips whole arguments, so this runs per argument
    rather than per element.
    """
    if not collect_marks_deep(value):
        return value
    return value._stripped


def _strip(value: Any) -> Any:
    """A copy of `value` with every mark removed, at any depth.

    Iterative, over an explicit stack, for the reason `collect_marks_deep` is:
    the two have to agree about how deep a value can be. `_strip` and
    `_strip_uncached` used to call each other, so every level of nesting cost two
    Python frames against CPython's 1000-frame ceiling and the strip gave out at
    **330 levels where validate accepts 450 and the collector survives 900+**. A
    value this package had just accepted could not be unmarked, and it failed as
    a bare `RecursionError` -- not a `CtyError` -- out of `length()`, `upper()`
    and every other stdlib function, since the framework strips every argument
    before the implementation runs.

    Post-order: a node is pushed back under `_STRIP_POST` and its children on
    top, so by the time the sentinel is reached every child has an entry in
    `results`. Nothing is collected mid-walk -- `children_of` holds each
    snapshot and the caller holds the root -- so keying by `id()` is safe.
    """

    if not isinstance(value, CtyValue):
        return value

    shortcut = _stripped_without_descending(value)
    if shortcut is not None:
        return shortcut

    results: dict[int, Any] = {}
    children_of: dict[int, Any] = {}
    # The nodes between the root and the cursor. A child already on it is a
    # cycle, which the recursive version met as a RecursionError and an
    # iterative one would otherwise meet as a hang.
    on_path: set[int] = set()
    stack: list[Any] = [value]

    while stack:
        node = stack.pop()

        if node is _STRIP_POST:
            _finish(stack.pop(), children_of, results, on_path)
            continue

        node_id = id(node)
        if node_id in results:
            continue

        resolved, children = _resolve_or_children(node)
        if resolved is not _DESCEND:
            results[node_id] = resolved
            continue

        if node_id in on_path:
            raise CtyValidationError(
                "cannot unmark a value that contains itself",
                value=node,
                type_name=type(node.type).__name__,
            )

        on_path.add(node_id)
        children_of[node_id] = children
        stack.append(node)
        stack.append(_STRIP_POST)
        stack.extend(children.values() if isinstance(children, dict) else children)

    return results[id(value)]


def _resolve_or_children(node: Any) -> tuple[Any, Any]:
    """`(stripped, None)` when `node` needs no descent, else `(_DESCEND, children)`.

    Returns the children rather than letting the caller ask again, so a set --
    whose `_children` snapshot fixes the order the rebuild runs against -- is
    read exactly once.
    """

    if not isinstance(node, CtyValue):
        return node, None

    shortcut = _already_stripped(node)
    if shortcut is not None:
        return shortcut, None

    children = _children(node)
    if children is None:
        return (node.unmark()[0] if node.marks else node), None

    return _DESCEND, children


def _finish(node: Any, children_of: dict[int, Any], results: dict[int, Any], on_path: set[int]) -> None:
    """Rebuild `node` now that every child has an entry in `results`."""
    node_id = id(node)
    on_path.discard(node_id)
    rebuilt = _rebuild(node, children_of[node_id], results)
    results[node_id] = rebuilt
    # `_deep_marks` is set only for a subtree the walk proved immutable, which
    # is exactly the condition under which this copy stays valid.
    if node._deep_marks is not None:
        object.__setattr__(node, "_stripped", rebuilt)


def _rebuild(value: Any, children: Any, results: dict[int, Any]) -> Any:
    """One node reassembled from its children's already-stripped forms.

    `children` is the snapshot taken when the node was pushed rather than a
    second `_children` call, so a set is rebuilt against the order it was read
    in.
    """
    stripped = value.unmark()[0] if value.marks else value

    # "Did anything change" is decided by identity, never by ==. CtyValue.__eq__
    # delegates to a CtyCapsuleWithOps' equal_fn, which compares payloads and
    # ignores marks entirely, so an equality check reports "unchanged" for a
    # capsule whose mark was just stripped and hands the caller back the marked
    # value. A node with nothing to do resolves to the input object itself,
    # which makes `is` an exact test.
    if isinstance(children, dict):
        rebuilt_map = {k: results[id(v)] for k, v in children.items()}
        if all(rebuilt_map[k] is v for k, v in children.items()):
            return stripped
        # Rebuilt frozen when the source was. `_strip` memoizes and hands every
        # caller the same object, so a plain dict here reintroduced exactly the
        # mutable shared payload FrozenDict exists to prevent -- and left the
        # stripped copy unmemoizable, so the marked path kept paying full price.
        payload = FrozenDict(rebuilt_map) if isinstance(children, FrozenDict) else rebuilt_map
        return evolve(stripped, value=payload)

    if isinstance(stripped.value, CtyValue):
        rebuilt_inner = results[id(children[0])]
        if rebuilt_inner is children[0]:
            return stripped
        return evolve(stripped, value=rebuilt_inner)

    rebuilt_seq = tuple(results[id(v)] for v in children)
    if all(new is old for new, old in zip(rebuilt_seq, children, strict=True)):
        return stripped
    if isinstance(stripped.value, (frozenset, set)):
        # Rebuild as a set. Removing marks can make two elements that differed
        # only by their marks equal, so the unmarked set may be smaller -- which
        # is what an unmarked view of the set should be.
        return evolve(stripped, value=frozenset(rebuilt_seq))
    return evolve(stripped, value=rebuilt_seq)


# 🌊🪢🔚
