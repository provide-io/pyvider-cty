#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/bool.go`.

Named with an `_fn` suffix because `and`, `or` and `not` are Python keywords and
cannot be function names -- the same reason `max_fn` and `pow_fn` carry one.
"""

from __future__ import annotations

from typing import Any, cast

from pyvider.cty import CtyBool, CtyDynamic, CtyValue
from pyvider.cty.config.defaults import (
    ERR_BOOL_ARG_MUST_BE_BOOL,
    ERR_BOOL_ARG_MUST_NOT_BE_NULL,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._marks import preserve_marks


def _bool_arg(value: CtyValue[Any], func: str) -> bool | None:
    """One boolean argument, or None if it is unknown.

    Refuses a null, which is what go-cty's function framework does for any
    parameter not declared `AllowNull` -- and none of these are. Several older
    functions in this package return unknown for a null instead; that is
    recorded in the tracker as strictness work rather than copied here, since
    these three are new and have no callers to break.
    """
    inner = value
    while isinstance(inner.type, CtyDynamic) and isinstance(inner.value, CtyValue):
        inner = inner.value
    if not isinstance(inner.type, CtyBool | CtyDynamic):
        raise CtyFunctionError(ERR_BOOL_ARG_MUST_BE_BOOL.format(func=func, type=inner.type.ctype))
    if inner.is_null:
        raise CtyFunctionError(ERR_BOOL_ARG_MUST_NOT_BE_NULL.format(func=func))
    if inner.is_unknown:
        return None
    return cast(bool, inner.value)


@preserve_marks
def not_fn(val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `NotFunc`."""
    operand = _bool_arg(val, "not")
    if operand is None:
        return CtyValue.unknown(CtyBool())
    return cast(CtyValue[Any], CtyBool().validate(not operand))


@preserve_marks
def and_fn(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `AndFunc`.

    No short-circuit: `and(unknown, false)` is unknown, not false. go-cty's
    framework returns an unknown result for any unknown argument before the
    implementation is reached, so it never gets the chance to notice that one
    known operand already settles the answer.
    """
    left, right = _bool_arg(a, "and"), _bool_arg(b, "and")
    if left is None or right is None:
        return CtyValue.unknown(CtyBool())
    return cast(CtyValue[Any], CtyBool().validate(left and right))


@preserve_marks
def or_fn(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `OrFunc`. Does not short-circuit, for the reason `and_fn` gives."""
    left, right = _bool_arg(a, "or"), _bool_arg(b, "or")
    if left is None or right is None:
        return CtyValue.unknown(CtyBool())
    return cast(CtyValue[Any], CtyBool().validate(left or right))


# 🌊🪢🔚
