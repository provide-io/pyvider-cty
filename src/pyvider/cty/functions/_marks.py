#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Mark propagation for stdlib functions.

go-cty handles this in its `cty/function` framework: a parameter declared
without `AllowMarked` has its marks stripped before `Impl` runs, and the union
of every argument's marks is re-applied to the result. Function implementations
therefore never see or manage marks themselves.

pyvider.cty has no function framework yet (#12). This decorator is the seam it
will fill in behind: the stdlib functions are written mark-unaware, exactly as
go-cty's `Impl` functions are, and the wrapper owns the policy.
"""

from __future__ import annotations

from collections.abc import Callable
import functools
from typing import Any, ParamSpec, TypeVar

from attrs import evolve

from pyvider.cty.values import CtyValue

P = ParamSpec("P")
R = TypeVar("R")


def _children(value: CtyValue[Any]) -> tuple[Any, ...] | dict[str, Any] | None:
    """The nested CtyValues a container holds, or None for a leaf.

    Lists, sets and tuples hold a tuple of values; maps and objects hold a dict;
    CtyDynamic wraps a single value. Primitives and capsules are leaves.
    """
    if value.is_null or value.is_unknown:
        return None
    inner = value.value
    if isinstance(inner, tuple):
        return inner
    if isinstance(inner, dict):
        return inner
    if isinstance(inner, CtyValue):
        return (inner,)
    return None


def _marks_deep(value: CtyValue[Any]) -> frozenset[Any]:
    """Every mark anywhere in a possibly-nested value.

    go-cty spells this `Value.UnmarkDeep`. pyvider.cty has no deep mark
    operations yet (#8); when they land, this collapses into a call to them.
    """
    marks = value.marks
    children = _children(value)
    if children is None:
        return marks
    values = children.values() if isinstance(children, dict) else children
    for child in values:
        if isinstance(child, CtyValue):
            marks |= _marks_deep(child)
    return marks


def _collect(args: tuple[Any, ...], kwargs: dict[str, Any]) -> frozenset[Any]:
    """Union of every mark carried anywhere inside the CtyValue arguments."""
    marks: frozenset[Any] = frozenset()
    for arg in (*args, *kwargs.values()):
        if isinstance(arg, CtyValue):
            marks |= _marks_deep(arg)
    return marks


def _strip(value: Any) -> Any:
    """A copy of `value` with every mark removed, at any depth."""
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
    return evolve(stripped, value=rebuilt_seq)


def preserve_marks(fn: Callable[P, R]) -> Callable[P, R]:
    """Strip marks from arguments, then re-apply their union to the result.

    Mirrors go-cty's default parameter behaviour (`AllowMarked` unset). The
    wrapped function is called with unmarked arguments so it cannot be confused
    by them, and never has to remember to propagate them.
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        marks = _collect(args, kwargs)
        if not marks:
            return fn(*args, **kwargs)

        result = fn(
            *(_strip(a) for a in args),
            **{k: _strip(v) for k, v in kwargs.items()},
        )
        if isinstance(result, CtyValue):
            return result.with_marks(marks)
        return result

    return wrapper


# 🌊🪢🔚
