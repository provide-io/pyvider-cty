#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/number.go`, declared rather than re-derived.

Fourteen of the twenty functions in that file live here; the four comparisons
and `min`/`max` live in `comparison_functions.py`. Every declaration below is a
field-by-field transcription of a `function.Spec`, and the bodies are what is
left once the framework owns arity, nullness, unknowns, the dynamic wrapper and
the marks.

Two things about that file are worth stating once rather than at each function.

**Its arithmetic does not refuse an infinity or a division by zero.** `7 / 0` is
`+Inf`, `7 % 0` is `7`, and `log(0, 2)` is `-Inf`. Only the genuinely undefined
combinations are errors, and go-cty reaches them by recovering a `big.ErrNaN`
panic out of `big.Float` -- which is why `divide`'s message names *two* cases at
once. `Decimal` raises where `big.Float` panics, so each of those recoveries is
transcribed as an `except` clause carrying go-cty's own wording.

**None of these fourteen sets `AllowUnknown`.** In `number.go` that flag appears
only on the four comparison functions (208, 233, 258, 283). So although
`cty.Value.Add` and `cty.Value.Absolute` narrow a refined unknown argument into
a refined unknown result, the *stdlib functions* never see the unknown at all:
the framework short-circuits and they answer an unknown number refined only
not-null. Confirmed against the live oracle, which answers
`{"is_known_null": false}` and nothing more for `abs`, `add`, `negate` and
`multiply` given a refined unknown.

The one deliberate divergence left in place is precision. go-cty holds a number
in a 512-bit `big.Float` and computes `log` and `pow` in `float64` first; this
package holds a `Decimal` in a 155-digit context (`_GO_BIG_FLOAT_DIGITS`, the
widest a 512-bit float can spell). Both of those two are therefore
transcribed *through* `float64`, because go-cty's answer for them is the
`float64` one -- infinities, range refusals and rounding artefacts included --
and a more accurate answer is a different answer. `divide` stays in `Decimal`,
where neither side is reading a `float64` and the two contexts simply differ.

Two residues of that are recorded as xfails in
`tests/compatibility/test_stdlib_sweep.py`: a number this package computed in
`float64` is written to the wire as text where go-cty writes a `float64`, because
a `Decimal` does not record that it came from one; and Go's `math.Pow` is not
correctly rounded where the libm behind Python's is, which puts them three ULPs
apart at `pow(10, 308)`.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from decimal import (
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    Decimal,
    DivisionByZero,
    InvalidOperation,
    localcontext,
)
import math
import sys
from typing import Any, cast

from pyvider.cty import CtyDynamic, CtyNumber, CtyString, CtyType, CtyValue
from pyvider.cty.config.defaults import ERR_PARSEINT_BASE_NOT_WHOLE, ERR_SIGNUM_NOT_WHOLE
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._args import whole_number
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyArgumentError, CtyParameter, refine_not_null

# `big.Int.SetString` accepts bases 2 through 62 (`math/big/intconv.go`), which
# is wider than Python's `int(str, base)` -- hence `_set_string` below.
_MIN_BASE = 2
_MAX_BASE = 62
_BASE_36 = 36

# go-cty's refusal when a number will not fit a Go `float64`, built rather than
# quoted: it is `math.MaxFloat64` printed by Go's `%f`, which is that float's
# *exact* binary value -- 309 digits -- and six zeros after the point
# (`gocty/out.go:211`). Spelling it out by hand would be 700 characters nobody
# could check.
_MAX_FLOAT64 = Decimal(sys.float_info.max)
_FLOAT64_RANGE_MESSAGE = (
    f"value must be between -{_MAX_FLOAT64:f}.000000 and {_MAX_FLOAT64:f}.000000 inclusive"
)


# go-cty computes in the 512-bit `big.Float` it holds every number in, so
# `add(2**100, 1)` comes back with its last digit intact. A `Decimal` computes in
# the ambient context instead, and this package took its default of 28
# significant digits: the same call answered 1267650600228229401496703205000
# here -- the last four digits invented, in a value that goes straight to
# Terraform state. `divide`, `multiply`, `subtract`, `abs` and `negate` all did
# it, and `modulo` did something worse, raising `DivisionImpossible` out of the
# implementation where go-cty answered. Found 2026-08-19 by the stdlib fuzz, on
# arguments no hand-written row had ever used.
#
# floor(512 * log10 2) + 1 = 155 is the widest a 512-bit float can spell, so
# computing at that width agrees with go-cty wherever go-cty is exact *and*
# rounds where it rounds: `add(1e200, 1)` is 1e200 on both sides, because the
# exact answer needs 201 significant digits and neither model has them. Past
# that width the two disagree in their last digits whatever precision is set --
# go-cty rounds in binary and a Decimal rounds in decimal -- which is the
# representation divergence recorded against `divide(1,3)` in the sweep.
_GO_BIG_FLOAT_DIGITS = 155


@contextmanager
def _at_go_width(extra: int = 0) -> Iterator[None]:
    """Compute at the width go-cty's `big.Float` computes at.

    `extra` widens it for `modulo` alone, whose `Decimal` implementation needs
    room for the *quotient* rather than for the answer: `a % b` raises
    `DivisionImpossible` when the integer part of `a / b` does not fit the
    context, and raising out of a function go-cty answers is worse than
    disagreeing with it in a digit.
    """
    with localcontext() as ctx:
        ctx.prec = _GO_BIG_FLOAT_DIGITS + max(extra, 0)
        yield


def _quotient_width(a: Decimal, b: Decimal) -> int:
    """How much wider than the model `a % b` needs its context to be.

    The integer part of `a / b` has `a.adjusted() - b.adjusted() + 1` digits at
    most; one more for the rounding step. Zero when that already fits.
    """
    if not a.is_finite() or not b.is_finite() or b == 0:
        return 0
    return max(a.adjusted() - b.adjusted() + 2 - _GO_BIG_FLOAT_DIGITS, 0)


def _numbers(*values: CtyValue[Any]) -> tuple[Decimal, ...]:
    """The payloads of number arguments, which the framework has already checked."""
    return tuple(cast(Decimal, value.value) for value in values)


def _float64(value: Decimal) -> float:
    """A number argument as a Go `float64`, or go-cty's refusal.

    `gocty.FromCtyValue` truncates precision silently and then refuses exactly
    one thing: a *finite* number whose `float64` form is an infinity. Its comment
    says why -- "we allow the precision to be truncated as part of our
    conversion, but we don't want to silently introduce infinities"
    (`gocty/out.go:207`). An argument that already is an infinity converts
    exactly and passes, which is how `log` answers for one.
    """
    result = float(value)
    if math.isinf(result) and value.is_finite():
        raise CtyFunctionError(_FLOAT64_RANGE_MESSAGE)
    return result


def _go_log(number: float) -> float:
    """Go's `math.Log`, which answers where Python's raises.

    `math.Log(0)` is `-Inf` and `math.Log(-1)` is `NaN` in Go; Python raises
    `ValueError` for both. `log` depends on the difference: go-cty answers
    negative infinity for `log(0, 2)` rather than refusing it.
    """
    if number > 0.0:
        return math.log(number)
    return -math.inf if number == 0.0 else math.nan


def _go_quotient(numerator: float, denominator: float) -> float:
    """IEEE-754 float division, which Go performs and Python refuses.

    Python raises `ZeroDivisionError` where Go answers an infinity, and `log`
    needs that answer: `math.Log(1)` is exactly zero, so go-cty's
    `math.Log(8) / math.Log(1)` is `+Inf` rather than an error.
    """
    if denominator != 0.0:
        return numerator / denominator
    if numerator == 0.0 or math.isnan(numerator):
        return math.nan
    return math.copysign(math.inf, numerator) * math.copysign(1.0, denominator)


def _odd_integer(number: float) -> bool:
    """Whether Go's `math.Pow` would treat this exponent as an odd integer.

    Go's contract distinguishes those from every other exponent in four of its
    special cases, all of them about the *sign* of a zero or an infinity:
    "Pow(±0, y) = ±Inf for y an odd integer < 0".
    """
    return math.isfinite(number) and number == int(number) and int(number) % 2 != 0


def _go_pow(base: float, exponent: float) -> float:
    """Go's `math.Pow`, which answers where Python's raises.

    Two families, told apart here rather than by the exception, because CPython
    reports the second and third as the same `ValueError`:

      * A finite result too large for a `float64`. Go returns an infinity of the
        matching sign; CPython raises `OverflowError`. This is the case that used
        to reach callers as an unhandled `decimal.Overflow`.
      * A zero base under a negative exponent. Go: an infinity, negative only
        for a negative zero raised to an odd integer power.
      * A finite negative base under a finite non-integer exponent. Go: NaN,
        which `_number_from_float` then turns into the refusal go-cty reaches by
        recovering the `Float.SetFloat64(NaN)` panic.
    """
    try:
        return math.pow(base, exponent)
    except OverflowError:
        return -math.inf if base < 0.0 and _odd_integer(exponent) else math.inf
    except ValueError:
        if base == 0.0:
            negative = math.copysign(1.0, base) < 0.0 and _odd_integer(exponent)
            return -math.inf if negative else math.inf
        return math.nan


def _number_from_float(result: float, what: str) -> CtyValue[Any]:
    """go-cty's `cty.NumberFloatVal`, which cannot represent a NaN.

    `big.Float.SetFloat64` panics on a NaN and the function framework turns that
    panic into an ordinary error (`function.go:349`), so a NaN is a refusal on
    both sides. Only the wording differs: go-cty's carries a Go stack trace.

    Spelled through `str()` rather than `Decimal(result)` so the answer is the
    seventeen digits the float actually names, not the exact binary expansion
    behind them -- which is what makes it comparable with go-cty's.
    """
    if math.isnan(result):
        raise CtyFunctionError(f"{what}: result is not a number")
    return CtyNumber().validate(Decimal(str(result)))


def _digit(char: str, base: int) -> int | None:
    """One digit's value under `big.Int.SetString`'s alphabet, or `None`.

    Up to base 36 the two letter cases are the same digit; above it the
    upper-case letters continue where the lower-case ones stop, so base 62 runs
    `0-9a-zA-Z`. `math/big/intconv.go`.
    """
    if "0" <= char <= "9":
        return ord(char) - ord("0")
    if "a" <= char <= "z":
        return ord(char) - ord("a") + 10
    if "A" <= char <= "Z":
        return ord(char) - ord("A") + (10 if base <= _BASE_36 else _BASE_36)
    return None


def _set_string(text: str, base: int) -> int | None:
    """Go's `big.Int.SetString` for an explicit base, or `None` for a refusal.

    Not `int(text, base)`. Python's builtin stops at base 36, and in the bases it
    does share it accepts three things Go's parser rejects for an explicit base:
    surrounding whitespace, digit-grouping underscores, and a `0x`-style prefix.
    Each of those would have this package answer a number where go-cty answers
    "cannot parse".
    """
    negative = text.startswith("-")
    digits = text[1:] if negative or text.startswith("+") else text
    if not digits:
        return None
    total = 0
    for char in digits:
        value = _digit(char, base)
        if value is None or value >= base:
            return None
        total = total * base + value
    return -total if negative else total


@stdlib_function(
    "abs",
    params=[CtyParameter("num", CtyNumber(), allow_dynamic_type=True, allow_marked=True)],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description=(
        "If the given number is negative then returns its positive equivalent, "
        "or otherwise returns the given number unchanged."
    ),
)
def abs_fn(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `AbsoluteFunc` (`stdlib/number.go:13`).

    `AllowMarked` is set because `cty.Value.Absolute` owns the marks itself
    (`value_ops.go:794`): it unmarks, takes the magnitude, and re-applies. The
    net effect is the framework's default, so the flag only matters in that the
    implementation must not forget the second half.
    """
    number, marks = input_val.unmark()
    # `copy_abs`, which only clears the sign. `abs` is a context operation and
    # rounds, which is the same fault the width of `_at_go_width` exists to
    # avoid -- and it would round *before* anything could widen the context.
    magnitude = cast(Decimal, number.value).copy_abs()
    return CtyNumber().validate(magnitude).with_marks(marks)


@stdlib_function(
    "add",
    params=[
        CtyParameter("a", CtyNumber(), allow_dynamic_type=True),
        CtyParameter("b", CtyNumber(), allow_dynamic_type=True),
    ],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the sum of the two given numbers.",
)
def add(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `AddFunc` (`stdlib/number.go:30`)."""
    a_val, b_val = _numbers(a, b)
    try:
        with _at_go_width():
            return CtyNumber().validate(a_val + b_val)
    except InvalidOperation as exc:
        # go-cty recovers `big.ErrNaN` out of `big.Float.Add` here, for exactly
        # this case, and reports it in these words (`number.go:54`).
        raise CtyFunctionError("can't compute sum of opposing infinities") from exc


@stdlib_function(
    "subtract",
    params=[
        CtyParameter("a", CtyNumber(), allow_dynamic_type=True),
        CtyParameter("b", CtyNumber(), allow_dynamic_type=True),
    ],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the difference between the two given numbers.",
)
def subtract(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SubtractFunc` (`stdlib/number.go:65`)."""
    a_val, b_val = _numbers(a, b)
    try:
        with _at_go_width():
            return CtyNumber().validate(a_val - b_val)
    except InvalidOperation as exc:
        raise CtyFunctionError("can't subtract infinity from itself") from exc


@stdlib_function(
    "multiply",
    params=[
        CtyParameter("a", CtyNumber(), allow_dynamic_type=True),
        CtyParameter("b", CtyNumber(), allow_dynamic_type=True),
    ],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the product of the two given numbers.",
)
def multiply(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MultiplyFunc` (`stdlib/number.go:100`).

    No zero short-circuit. `cty.Value.Multiply` does return zero for a zero
    factor, but only on the branch it takes when the *other* factor is unknown
    (`value_ops.go:679`) -- and this function never reaches the implementation
    with an unknown argument. So `multiply(0, unknown)` is an unknown number,
    which is also what the oracle answers, and `multiply(0, Infinity)` is the
    error below rather than zero.
    """
    a_val, b_val = _numbers(a, b)
    try:
        with _at_go_width():
            return CtyNumber().validate(a_val * b_val)
    except InvalidOperation as exc:
        raise CtyFunctionError("can't multiply zero by infinity") from exc


@stdlib_function(
    "divide",
    params=[
        CtyParameter("a", CtyNumber(), allow_dynamic_type=True),
        CtyParameter("b", CtyNumber(), allow_dynamic_type=True),
    ],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Divides the first given number by the second.",
)
def divide(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `DivideFunc` (`stdlib/number.go:136`).

    Division by zero is not an error. `big.Float.Quo` answers an infinity signed
    by the two operands, and `cty.Value.Divide` documents that as the contract --
    "the caller should check whether the other value equals zero before calling
    and raise an error instead" if it wants one (`value_ops.go:713`). Only
    `0 / 0` and `Infinity / Infinity` are undefined, and those are the pair
    go-cty's one message names.
    """
    a_val, b_val = _numbers(a, b)
    try:
        with _at_go_width():
            return CtyNumber().validate(a_val / b_val)
    except DivisionByZero:
        signed = a_val.is_signed() != b_val.is_signed()
        return CtyNumber().validate(Decimal("-Infinity") if signed else Decimal("Infinity"))
    except InvalidOperation as exc:
        raise CtyFunctionError("can't divide zero by zero or infinity by infinity") from exc


@stdlib_function(
    "modulo",
    params=[
        CtyParameter("a", CtyNumber(), allow_dynamic_type=True),
        CtyParameter("b", CtyNumber(), allow_dynamic_type=True),
    ],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Divides the first given number by the second and then returns the remainder.",
)
def modulo(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ModuloFunc` (`stdlib/number.go:172`).

    `cty.Value.Modulo` (`value_ops.go:755`) does three things in order that a
    reading of the name would not predict, and all three are transcribed: an
    infinite operand is handed to multiplication, which is how it gets an
    infinity of the right sign; a zero divisor returns the dividend untouched
    rather than raising; and the remainder itself is the truncated-division one,
    taking the dividend's sign, which is what `Decimal`'s `%` already computes.

    Computed in `Decimal` rather than through `math.fmod`. The previous body went
    via `float64` and back, which lost every digit past the seventeenth of an
    argument both implementations had agreed on exactly.
    """
    a_val, b_val = _numbers(a, b)
    if not a_val.is_finite() or not b_val.is_finite():
        try:
            with _at_go_width():
                return CtyNumber().validate(a_val * b_val)
        except InvalidOperation as exc:
            raise CtyFunctionError("can't use modulo with zero and infinity") from exc
    if b_val == 0:
        # go-cty returns the dividend untouched rather than raising.
        return a
    if a_val.is_zero():
        # The sign of a zero remainder is decided by IEEE, not by the dividend.
        # go-cty computes `a - b*trunc(a/b)`, and for a zero dividend the
        # subtrahend is a zero carrying the *divisor's* sign: `-0 - (+0)` is
        # `-0` and `-0 - (-0)` is `+0`. So `modulo(-0.0, 1)` is `-0` and
        # `modulo(-0.0, -1)` is `+0`, which no rule about the dividend alone
        # produces. Found 2026-08-19 by the stdlib fuzz, twice -- the first fix
        # here looked only at the dividend.
        negative = a_val.is_signed() and not b_val.is_signed()
        return CtyNumber().validate(Decimal("-0") if negative else Decimal(0))
    with _at_go_width(_quotient_width(a_val, b_val)):
        remainder = a_val % b_val
    # A zero remainder is `+0`, whatever the dividend's sign. go-cty computes
    # `a - b*trunc(a/b)`, and a `big.Float` subtraction of equal magnitudes is
    # `+0` under round-to-nearest; `Decimal.__mod__` gives the remainder the
    # *dividend's* sign, so `modulo(-1, 1)` was `-0` here and `0` there.
    return CtyNumber().validate(Decimal(0) if remainder.is_zero() else remainder)


@stdlib_function(
    "negate",
    params=[CtyParameter("num", CtyNumber(), allow_dynamic_type=True, allow_marked=True)],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Multiplies the given number by -1.",
)
def negate(a: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `NegateFunc` (`stdlib/number.go:308`).

    `AllowMarked` for the same reason as `abs`: `cty.Value.Negate` unmarks and
    re-applies (`value_ops.go:652`), so the implementation owns the marks.
    """
    number, marks = a.unmark()
    # `copy_negate`, not unary minus. A `big.Float` negation flips the sign bit,
    # so go-cty's `negate(0)` is `-0`; Python's `-Decimal(0)` is the arithmetic
    # `0 - 0`, which the decimal specification defines as `+0`. The sign of a
    # zero survives the wire on both sides, so the two wrote different bytes for
    # the same call. Found 2026-08-19 by the stdlib fuzz.
    negated = cast(Decimal, number.value).copy_negate()
    return CtyNumber().validate(negated).with_marks(marks)


@stdlib_function(
    "int",
    params=[CtyParameter("num", CtyNumber(), allow_dynamic_type=True)],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Discards any fractional portion of the given number.",
)
def int_fn(val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `IntFunc` (`stdlib/number.go:377`).

    Truncates toward zero, so `-3.9` is `-3`. An argument that is already whole
    comes back as itself rather than as a fresh value of the same magnitude,
    which is go-cty's `if bf.IsInt() { return args[0] }`.

    `IsInt()` is false for an infinity, and go-cty then hands a nil `big.Int` to
    `SetInt` and crashes -- the oracle reports a recovered nil dereference. This
    refuses it instead, in the words go-cty's own `stdlib.Int` wrapper uses for
    the same condition (`number.go:681`).
    """
    number = cast(Decimal, val.value)
    if not number.is_finite():
        raise CtyFunctionError("can't truncate infinity to an integer")
    truncated = number.to_integral_value(rounding=ROUND_DOWN)
    if number == truncated:
        return val
    # `+ 0` on a zero result, which is not a no-op: truncating -0.5 leaves a
    # `Decimal("-0")`, and go-cty truncates through a `big.Int`, which has no
    # signed zero -- `int(-0.5)` is `+0` there. Only the truncating branch; an
    # argument that is already whole comes back untouched on both sides, `-0.0`
    # included.
    return CtyNumber().validate(Decimal(0) if truncated.is_zero() else truncated)


@stdlib_function(
    "ceil",
    params=[CtyParameter("num", CtyNumber())],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the smallest whole number that is greater than or equal to the given value.",
)
def ceil_fn(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `CeilFunc` (`stdlib/number.go:401`).

    An infinity is returned unchanged -- go-cty tests `f.IsInf()` first, because
    there is no whole number above `+Inf` to round to. Note there is no
    `AllowDynamicType` here where `abs` and `int` have one; that is go-cty's
    declaration, not an omission.
    """
    number = cast(Decimal, input_val.value)
    if not number.is_finite():
        return input_val
    rounded = number.to_integral_value(rounding=ROUND_CEILING)
    # go-cty rounds through a `big.Int` and has no signed zero there, so a
    # zero answer is `+0` however the argument was signed -- and unlike `int`,
    # there is no shortcut returning an already-whole argument untouched, so
    # `ceil(-0.0)` is `0` rather than `-0` (`stdlib/number.go:418`).
    return CtyNumber().validate(Decimal(0) if rounded.is_zero() else rounded)


@stdlib_function(
    "floor",
    params=[CtyParameter("num", CtyNumber())],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the greatest whole number that is less than or equal to the given value.",
)
def floor_fn(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `FloorFunc` (`stdlib/number.go:432`)."""
    number = cast(Decimal, input_val.value)
    if not number.is_finite():
        return input_val
    rounded = number.to_integral_value(rounding=ROUND_FLOOR)
    # go-cty rounds through a `big.Int` and has no signed zero there, so a
    # zero answer is `+0` however the argument was signed -- and unlike `int`,
    # there is no shortcut returning an already-whole argument untouched, so
    # `ceil(-0.0)` is `0` rather than `-0` (`stdlib/number.go:418`).
    return CtyNumber().validate(Decimal(0) if rounded.is_zero() else rounded)


@stdlib_function(
    "log",
    params=[CtyParameter("num", CtyNumber()), CtyParameter("base", CtyNumber())],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the logarithm of the given number in the given base.",
)
def log_fn(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `LogFunc` (`stdlib/number.go:462`).

    Nothing about the domain is checked, because go-cty checks nothing: it reads
    both arguments as `float64` and divides one `math.Log` by the other. So
    `log(0, 2)` is `-Inf`, `log(8, 1)` is `+Inf`, `log(8, 0)` is zero, and only
    `log(-1, 2)` -- the one that is genuinely NaN -- is refused. This replaces
    three hand-written domain refusals that went the other way on all four.

    An argument too large for a `float64` is the other refusal, and it comes from
    reading the argument rather than from the arithmetic: see `_float64`. `pow`
    reads its arguments the same way and so makes the same refusal.
    """
    num, base = _numbers(num_val, base_val)
    return _number_from_float(_go_quotient(_go_log(_float64(num)), _go_log(_float64(base))), "log")


@stdlib_function(
    "pow",
    params=[CtyParameter("num", CtyNumber()), CtyParameter("power", CtyNumber())],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the given number raised to the given power (exponentiation).",
)
def pow_fn(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `PowFunc` (`stdlib/number.go:492`).

    Read through `float64` exactly as `log` is, because go-cty's `Impl` reads
    both arguments with `gocty.FromCtyValue` into a `float64` and returns
    `cty.NumberFloatVal(math.Pow(...))`. Nothing in that path is a `big.Float`
    computation, so keeping `pow` in `Decimal` was not a more-precise version of
    go-cty's answer but a different function, and it diverged in three ways at
    once. Verified against v1.19.0:

        pow(10, 308) -> 10000000000000006...  (the float64 value, not 1e308)
        pow(10, 400) -> +Inf                  (Decimal: exactly 1e400)
        pow(1e400, 2) -> the float64-range refusal, which `Decimal` never made

    The third is the one that mattered: `pow(10, 1000000)` raised
    `decimal.Overflow`, which is not a `CtyError`, so it escaped the taxonomy as
    a `CtyFunctionPanicError`.
    """
    num, power = _numbers(num_val, power_val)
    return _number_from_float(_go_pow(_float64(num), _float64(power)), "pow")


@stdlib_function(
    "signum",
    params=[CtyParameter("num", CtyNumber())],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description=(
        "Returns 0 if the given number is zero, 1 if the given number is positive, "
        "or -1 if the given number is negative."
    ),
)
def signum_fn(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SignumFunc` (`stdlib/number.go:523`).

    Reads its argument into a Go `int` before looking at the sign, so a fraction
    is an error rather than a sign -- `signum(1.5)` is refused, where this
    package used to answer `1`. That reads like a quirk and is load-bearing: the
    function promises three possible answers, and a caller that gets one for
    `0.5` has been told the value is a whole one.
    """
    number = whole_number(input_val, ERR_SIGNUM_NOT_WHOLE)
    if number < 0:
        return CtyNumber().validate(Decimal(-1))
    if number > 0:
        return CtyNumber().validate(Decimal(1))
    return CtyNumber().validate(Decimal(0))


def _parseint_return_type(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
    """go-cty's `ParseIntFunc.Type` (`stdlib/number.go:563`).

    The first parameter is declared `DynamicPseudoType` so that the refusal comes
    from here, by argument index, rather than from a framework conformance check
    against a declared type that is not the real requirement.
    """
    if not isinstance(args[0].type, CtyString):
        raise CtyArgumentError(0, f"first argument must be a string, not {args[0].type.ctype}")
    return CtyNumber()


@stdlib_function(
    "parseint",
    params=[CtyParameter("number", CtyDynamic()), CtyParameter("base", CtyNumber())],
    type_func=_parseint_return_type,
    refine_result=refine_not_null,
    description=(
        "Parses the given string as a number of the given base, or raises an error "
        "if the string contains invalid characters."
    ),
)
def parseint_fn(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ParseIntFunc` (`stdlib/number.go:550`).

    Two things this used to get wrong. The base range is 2 to 62 inclusive, not
    "0 or 2 to 36": `big.Int.SetString` carries an alphabet twice the size of
    Python's, and base 0 -- which would mean "infer from a `0x` prefix" -- is
    refused outright. And an unparseable string is an *error*, where this
    returned a null number, which is a value a caller would then compute with.
    """
    base = whole_number(base_val, ERR_PARSEINT_BASE_NOT_WHOLE)
    if not _MIN_BASE <= base <= _MAX_BASE:
        raise CtyArgumentError(1, f"base must be a whole number between {_MIN_BASE} and {_MAX_BASE} inclusive")
    text = cast(str, str_val.value)
    parsed = _set_string(text, base)
    if parsed is None:
        raise CtyArgumentError(0, f'cannot parse "{text}" as a base {base} integer')
    return CtyNumber().validate(Decimal(parsed))


# 🌊🪢🔚
