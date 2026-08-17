#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/bool.go`.

Named with an `_fn` suffix because `and`, `or` and `not` are Python keywords and
cannot be function names -- the same reason `max_fn` and `pow_fn` carry one.

Every parameter here is declared `AllowMarked`, so these bodies own mark
propagation rather than leaving it to the framework -- which is exactly what
`cty.Value.Not`, `And` and `Or` do: unmark, compute, re-apply
(`value_ops.go:1305`).
"""

from __future__ import annotations

from typing import Any, cast

from pyvider.cty import CtyBool, CtyValue
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null


def _answer(result: bool, marks: frozenset[Any]) -> CtyValue[Any]:
    """A boolean result carrying the marks its operands brought."""
    return cast(CtyValue[Any], CtyBool().validate(result).with_marks(marks))


@stdlib_function(
    "not",
    params=[CtyParameter("val", CtyBool(), allow_dynamic_type=True, allow_marked=True)],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Applies the logical NOT operation to the given boolean value.",
)
def not_fn(val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `NotFunc` (`stdlib/bool.go:8`), whose body is `args[0].Not()`."""
    operand, marks = val.unmark()
    return _answer(not operand.value, marks)


@stdlib_function(
    "and",
    params=[
        CtyParameter("a", CtyBool(), allow_dynamic_type=True, allow_marked=True),
        CtyParameter("b", CtyBool(), allow_dynamic_type=True, allow_marked=True),
    ],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Applies the logical AND operation to the given boolean values.",
)
def and_fn(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `AndFunc` (`stdlib/bool.go:25`), whose body is `args[0].And(args[1])`.

    No short-circuit: `and(false, unknown)` is unknown, not false. `cty.Value.And`
    *does* return `False` outright when either operand is known false
    (`value_ops.go:1332`), but neither parameter here declares `AllowUnknown`, so
    the framework answers `unknown(bool)` before the implementation is reached
    and that branch is unreachable through `AndFunc`. Confirmed against the
    oracle, which answers unknown-and-not-null for `and(false, unknown)`.
    Matching it matters because a plan that answered `false` here and `unknown`
    in Terraform would disagree with itself.
    """
    left, left_marks = a.unmark()
    right, right_marks = b.unmark()
    return _answer(bool(left.value and right.value), left_marks | right_marks)


@stdlib_function(
    "or",
    params=[
        CtyParameter("a", CtyBool(), allow_dynamic_type=True, allow_marked=True),
        CtyParameter("b", CtyBool(), allow_dynamic_type=True, allow_marked=True),
    ],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Applies the logical OR operation to the given boolean values.",
)
def or_fn(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `OrFunc` (`stdlib/bool.go:48`). Does not short-circuit, per `and_fn`."""
    left, left_marks = a.unmark()
    right, right_marks = b.unmark()
    return _answer(bool(left.value or right.value), left_marks | right_marks)


# 🌊🪢🔚
