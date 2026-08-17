#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `EqualFunc`/`NotEqualFunc` and the six comparisons in `number.go`.

`stdlib/general.go:11` and `stdlib/number.go:208`. The two groups declare
opposite parameter shapes, and that contrast is the whole content of this
module: equality is defined on *any* value including nulls, unknowns and values
of no decided type, while an ordering comparison is defined only on numbers and
refuses a null outright.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Any, cast

from pyvider.cty import CtyBool, CtyDynamic, CtyNumber, CtyValue
from pyvider.cty.config.defaults import COMPARISON_OPS_MAP, ERR_MIN_ONE_ARG
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null
from pyvider.cty.values.markers import RefinedUnknownValue


def _any_value(name: str) -> CtyParameter:
    """The parameter `equal` and `notequal` both declare twice over.

    Any type, and defined on a null, on an unknown and on `cty.DynamicVal`,
    because answering for those is the entire job: a function whose purpose is
    to compare two values cannot short-circuit the cases where one of them is
    not yet a value. Four of the five permissive flags in go-cty's whole stdlib
    parameter set are on these two functions (`stdlib/general.go:13`).
    """
    return CtyParameter(
        name,
        CtyDynamic(),
        allow_null=True,
        allow_unknown=True,
        allow_dynamic_type=True,
    )


def _number_operand(name: str) -> CtyParameter:
    """The parameter all four ordering comparisons declare twice over.

    A number, seen even when unknown or dynamically typed -- go-cty answers
    definitely from the refinement bounds where it can -- and seen *marked*,
    because `Value.GreaterThan` and friends propagate marks themselves rather
    than leaving it to the framework (`stdlib/number.go:210`).

    `AllowNull` is absent, so the framework refuses a null before the body runs.
    That is the parity fix here: this package used to answer `unknown` for
    `greaterthan(null, 1)`, which claims the comparison might yet succeed.
    """
    return CtyParameter(
        name,
        CtyNumber(),
        allow_unknown=True,
        allow_dynamic_type=True,
        allow_marked=True,
    )


@stdlib_function(
    "equal",
    params=[_any_value("a"), _any_value("b")],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Returns true if the two given values are equal, or false otherwise.",
)
def equal(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `EqualFunc` (`stdlib/general.go:11`).

    Three-valued, through `CtyValue.equals`, which is go-cty's `Value.Equals`.

    One deliberate divergence lives underneath, in `values/equality.py`: for an
    object or map holding both an unknown member and a member that definitely
    differs, go-cty's `Equals` answers `false` or `unknown` depending on Go's
    randomized map iteration order, and this library answers `false`
    deterministically -- the more informative of go-cty's two answers rather
    than a third one. Recorded in `.provide/GO-CTY-PARITY.md` rather than
    called fixed, because matching a coin flip is not parity.
    """
    return a.equals(b)


@stdlib_function(
    "notequal",
    params=[_any_value("a"), _any_value("b")],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Returns false if the two given values are equal, or true otherwise.",
)
def not_equal(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `NotEqualFunc`: `args[0].Equals(args[1]).Not()` (`general.go:57`).

    `Not` of an undecided answer is still undecided, which is why the unknown
    is returned rather than negated.
    """
    result = a.equals(b)
    if result.is_unknown:
        return result
    return CtyBool().validate(not result.value)


# A bound as `(value, inclusive)`, or `None` for "no bound in that direction".
_Bound = tuple[Decimal, bool] | None

# Which certainty settles each operator, and which one refutes it. `>` is true
# once the whole of `a` is above the whole of `b`, and false once the whole of
# `a` is at or below it; `>=` moves the boundary into the true case, and `<`
# and `<=` are the mirror image.
_DECISION: dict[str, tuple[str, str]] = {
    ">": ("gt", "le"),
    ">=": ("ge", "lt"),
    "<": ("lt", "ge"),
    "<=": ("le", "gt"),
}


def _bounds(value: CtyValue[Any]) -> tuple[_Bound, _Bound]:
    """A number value's range, as `(lower, upper)`. go-cty's `Value.Range`.

    A known number is the degenerate range `[v, v]`, which is what lets one
    piece of arithmetic serve both a known and an unknown operand. An unrefined
    unknown -- and `cty.DynamicVal`, which reaches here because the parameter
    admits it -- has no bounds at all.
    """
    if not value.is_unknown:
        exact = (cast(Decimal, value.value), True)
        return exact, exact
    refinement = value.value if isinstance(value.value, RefinedUnknownValue) else None
    if refinement is None:
        return None, None
    return refinement.number_lower_bound, refinement.number_upper_bound


def _above(lower: _Bound, upper: _Bound) -> bool:
    """Whether everything at or above `lower` is strictly above `upper`."""
    if lower is None or upper is None:
        return False
    low, low_inclusive = lower
    high, high_inclusive = upper
    return low > high or (low == high and not (low_inclusive and high_inclusive))


def _at_least(lower: _Bound, upper: _Bound) -> bool:
    """Whether everything at or above `lower` is at or above `upper`.

    Inclusivity cannot change this one: if the two bounds coincide then either
    side being exclusive only pushes the values further apart in the direction
    the answer already went.
    """
    if lower is None or upper is None:
        return False
    return lower[0] >= upper[0]


def _decide(a: CtyValue[Any], b: CtyValue[Any], op: str) -> bool | None:
    """What the two ranges settle, or `None` if they settle nothing.

    go-cty's `LessThan` and `GreaterThan` each consult both `Range`s and can
    return a *known* answer from unknown operands; `LessThanOrEqualTo` and
    `GreaterThanOrEqualTo` are `LessThan(x).Or(Equals(x))`, the same question
    with the boundary counted as agreement (`value_ops.go:1367`, `:1443`).

    go-cty's own comment there notes it treats every bound as exclusive and is
    therefore more conservative than it needs to be. This does not: the
    inclusive flag each bound already carries is honoured, so `<= 10` compared
    against `10` is decided rather than declined.
    """
    a_low, a_high = _bounds(a)
    b_low, b_high = _bounds(b)
    certain = {
        "gt": _above(a_low, b_high),
        "ge": _at_least(a_low, b_high),
        "lt": _above(b_low, a_high),
        "le": _at_least(b_low, a_high),
    }
    settles, refutes = _DECISION[op]
    if certain[settles]:
        return True
    if certain[refutes]:
        return False
    return None


def _compare(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:
    """One ordering comparison, as go-cty's `Value` operators compute it.

    Both parameters declare `AllowMarked`, so propagating marks is this
    function's job rather than the framework's -- and go-cty's operators do it
    by unmarking, recursing and re-applying the union (`value_ops.go:1367`). A
    number has no nesting, so a shallow unmark here is the same thing as the
    deep one the framework would otherwise have done.
    """
    if a.marks or b.marks:
        bare_a, a_marks = a.unmark()
        bare_b, b_marks = b.unmark()
        return _compare(bare_a, bare_b, op).with_marks(a_marks | b_marks)

    if a.is_unknown or b.is_unknown:
        decided = _decide(a, b, op)
        if decided is None:
            # The framework's `refine_result` supplies the `RefineNotNull` that
            # go-cty applies to this short-circuit.
            return CtyValue.unknown(CtyBool())
        return CtyBool().validate(decided)

    return CtyBool().validate(COMPARISON_OPS_MAP[op](a.value, b.value))


@stdlib_function(
    "greaterthan",
    params=[_number_operand("a"), _number_operand("b")],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Returns true if and only if the second number is greater than the first.",
)
def greater_than(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `GreaterThanFunc` (`stdlib/number.go:208`).

    The description is go-cty's own, and it has the operands the wrong way
    round -- the implementation is `args[0].GreaterThan(args[1])`. Copied
    verbatim anyway: a paraphrase would be a divergence nobody checks, and the
    place to fix the prose is upstream.
    """
    return _compare(a, b, ">")


@stdlib_function(
    "greaterthanorequalto",
    params=[_number_operand("a"), _number_operand("b")],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Returns true if and only if the second number is greater than or equal to the first.",
)
def greater_than_or_equal_to(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `GreaterThanOrEqualToFunc` (`stdlib/number.go:233`)."""
    return _compare(a, b, ">=")


@stdlib_function(
    "lessthan",
    params=[_number_operand("a"), _number_operand("b")],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Returns true if and only if the second number is less than the first.",
)
def less_than(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `LessThanFunc` (`stdlib/number.go:258`)."""
    return _compare(a, b, "<")


@stdlib_function(
    "lessthanorequalto",
    params=[_number_operand("a"), _number_operand("b")],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Returns true if and only if the second number is less than or equal to the first.",
)
def less_than_or_equal_to(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `LessThanOrEqualToFunc` (`stdlib/number.go:283`)."""
    return _compare(a, b, "<=")


def _numeric_key(value: CtyValue[Any]) -> Decimal:
    return cast(Decimal, value.value)


def _extreme(args: Sequence[CtyValue[Any]], op: str) -> CtyValue[Any]:
    """The greatest or the smallest of the given numbers.

    go-cty seeds with an infinity and replaces it only when an argument
    *strictly* beats the incumbent, so a tie keeps the earliest argument --
    which is exactly what Python's `max`/`min` with a key already do
    (`stdlib/number.go:335`).

    Every argument is a known, non-null number by the time this runs: the
    variadic parameter declares neither `AllowNull` nor `AllowUnknown`, so the
    framework has already refused the one and short-circuited the other.
    """
    if not args:
        raise CtyFunctionError(ERR_MIN_ONE_ARG.format(op=op))
    if op == "max":
        return max(args, key=_numeric_key)
    return min(args, key=_numeric_key)


@stdlib_function(
    "max",
    var_param=CtyParameter("numbers", CtyNumber(), allow_dynamic_type=True),
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the numerically greatest of all of the given numbers.",
)
def max_fn(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MaxFunc` (`stdlib/number.go:351`)."""
    return _extreme(args, "max")


@stdlib_function(
    "min",
    var_param=CtyParameter("numbers", CtyNumber(), allow_dynamic_type=True),
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the numerically smallest of all of the given numbers.",
)
def min_fn(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MinFunc` (`stdlib/number.go:325`)."""
    return _extreme(args, "min")


# 🌊🪢🔚
