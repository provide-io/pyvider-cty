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

The deep walk itself lives in `pyvider.cty.marks`, shared with the recursion
guard and the set constructor.
"""

from __future__ import annotations

from collections.abc import Callable
import functools
from typing import Any, ParamSpec, TypeVar

from pyvider.cty.marks import _strip, collect_marks_deep
from pyvider.cty.values import CtyValue

P = ParamSpec("P")
R = TypeVar("R")


# Payload types that can hide a mark below the top level. A CtyValue holding
# anything else is a leaf, and its own `marks` is the whole answer.
_NESTING_PAYLOADS = (CtyValue, dict, list, tuple, set, frozenset)


def _arg_marks(arg: Any) -> frozenset[Any]:
    """Marks anywhere in one argument, avoiding the walk for leaves.

    This runs on every argument of every stdlib call, so the common case -- an
    unmarked scalar -- must not pay for the general machinery. Setting up the
    walk (stack, visited set, memo write) costs more than the two attribute
    reads that answer the question outright.
    """
    if not isinstance(arg, CtyValue):
        return frozenset()
    if not isinstance(arg.value, _NESTING_PAYLOADS):
        return arg.marks
    return collect_marks_deep(arg)


def _collect(args: tuple[Any, ...], kwargs: dict[str, Any]) -> frozenset[Any]:
    """Union of every mark carried anywhere inside the CtyValue arguments.

    `args` and `kwargs` are walked separately rather than merged, because
    merging allocates a tuple on every stdlib call and the stdlib functions are
    positional -- kwargs is almost always empty.
    """
    marks: frozenset[Any] = frozenset()
    for arg in args:
        arg_marks = _arg_marks(arg)
        if arg_marks:
            marks |= arg_marks
    if kwargs:
        for arg in kwargs.values():
            arg_marks = _arg_marks(arg)
            if arg_marks:
                marks |= arg_marks
    return marks


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
