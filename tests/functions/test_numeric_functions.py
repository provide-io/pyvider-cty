#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for numeric functions (add, subtract, multiply, divide, floor, ceil, etc.)."""

from decimal import Decimal

import pytest

from pyvider.cty import CtyDynamic, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    abs_fn,
    add,
    ceil_fn,
    divide,
    floor_fn,
    int_fn,
    log_fn,
    modulo,
    multiply,
    negate,
    parseint_fn,
    pow_fn,
    signum_fn,
    subtract,
)


# Helper functions for creating CtyValues to improve test readability
def N(v):
    return CtyNumber().validate(v)


def S(v):
    return CtyString().validate(v)


class TestNumericFunctions:
    def test_int_fn(self) -> None:
        assert int_fn(N(5.9)).value == 5
        assert int_fn(N(-5.9)).value == -5

    def test_int_fn_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            int_fn(S("a"))

    def test_int_fn_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            int_fn(CtyValue.null(CtyNumber()))
        assert int_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_add_numbers(self) -> None:
        assert add(CtyNumber().validate(1), CtyNumber().validate(2)).value == 3
        assert add(CtyNumber().validate(-1), CtyNumber().validate(2)).value == 1
        assert add(CtyNumber().validate(1.5), CtyNumber().validate(2.5)).value == 4.0

    def test_add_refuses_a_null(self) -> None:
        with pytest.raises(CtyFunctionError):
            add(CtyValue.null(CtyNumber()), CtyNumber().validate(1))
        with pytest.raises(CtyFunctionError):
            add(CtyNumber().validate(1), CtyValue.null(CtyNumber()))

    def test_add_unknown(self) -> None:
        assert add(CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
        assert add(CtyNumber().validate(1), CtyValue.unknown(CtyNumber())).is_unknown

    def test_add_type_error(self) -> None:
        with pytest.raises(CtyFunctionError):
            add(CtyString().validate("a"), CtyNumber().validate(1))

    def test_subtract_numbers(self) -> None:
        assert subtract(CtyNumber().validate(3), CtyNumber().validate(2)).value == 1
        assert subtract(CtyNumber().validate(-1), CtyNumber().validate(2)).value == -3
        assert subtract(CtyNumber().validate(2.5), CtyNumber().validate(1.5)).value == 1.0

    def test_multiply_numbers(self) -> None:
        assert multiply(CtyNumber().validate(3), CtyNumber().validate(2)).value == 6
        assert multiply(CtyNumber().validate(-1), CtyNumber().validate(2)).value == -2
        assert multiply(CtyNumber().validate(1.5), CtyNumber().validate(2)).value == 3.0

    def test_divide_numbers(self) -> None:
        assert divide(CtyNumber().validate(6), CtyNumber().validate(2)).value == 3
        assert divide(CtyNumber().validate(-4), CtyNumber().validate(2)).value == -2
        assert divide(CtyNumber().validate(5), CtyNumber().validate(2)).value == 2.5

    def test_divide_by_zero_is_an_infinity(self) -> None:
        """This asserted a "divide by zero" refusal until 2026-08-17.

        go-cty does not refuse it. `cty.Value.Divide` hands the operands to
        `big.Float.Quo`, which answers an infinity signed by both of them, and
        its docstring names that as the contract -- "the caller should check
        whether the other value equals zero before calling and raise an error
        instead" if a refusal is what the caller wants (`value_ops.go:713`).
        Verified against go-cty: `divide(7, 0)` is `+Inf`.

        Only the undefined pair is an error, below.
        """
        assert divide(N(1), N(0)).value == Decimal("Infinity")
        assert divide(N(-1), N(0)).value == Decimal("-Infinity")

    def test_divide_refuses_only_the_genuinely_undefined_quotients(self) -> None:
        """`DivideFunc` recovers one `big.ErrNaN`, so one message names both cases.

        go-cty `stdlib/number.go:160`.
        """
        for a, b in ((N(0), N(0)), (N(Decimal("Infinity")), N(Decimal("Infinity")))):
            with pytest.raises(CtyFunctionError, match="can't divide zero by zero"):
                divide(a, b)

    def test_arithmetic_refuses_the_undefined_infinity_combinations(self) -> None:
        """Each of go-cty's four recovered `big.ErrNaN` panics, in its own words.

        `stdlib/number.go` lines 54, 89, 124 and 196.
        """
        inf, neg_inf = N(Decimal("Infinity")), N(Decimal("-Infinity"))
        with pytest.raises(CtyFunctionError, match="opposing infinities"):
            add(inf, neg_inf)
        with pytest.raises(CtyFunctionError, match="subtract infinity from itself"):
            subtract(inf, inf)
        with pytest.raises(CtyFunctionError, match="multiply zero by infinity"):
            multiply(N(0), inf)
        with pytest.raises(CtyFunctionError, match="modulo with zero and infinity"):
            modulo(inf, N(0))

    def test_modulo_numbers(self) -> None:
        assert modulo(CtyNumber().validate(5), CtyNumber().validate(2)).value == 1
        assert modulo(CtyNumber().validate(-5), CtyNumber().validate(2)).value == -1
        assert modulo(CtyNumber().validate(5.5), CtyNumber().validate(2)).value == 1.5

    def test_modulo_by_zero_returns_the_dividend(self) -> None:
        """This asserted a "modulo by zero" refusal until 2026-08-17.

        `cty.Value.Modulo` tests the divisor against zero and returns the
        dividend untouched (`value_ops.go:773`), which follows from the identity
        it computes: `a - b * trunc(a / b)` with `b` zero leaves `a`. Verified
        against go-cty: `modulo(7, 0)` is `7`.
        """
        assert modulo(N(7), N(0)).value == 7

    def test_modulo_of_an_infinity_multiplies_instead(self) -> None:
        """go-cty "cheats a bit here with infinities" and says so (`value_ops.go:767`).

        An infinite operand is handed to multiplication, which is how the result
        gets an infinity of the right sign rather than a NaN.
        """
        assert modulo(N(Decimal("Infinity")), N(3)).value == Decimal("Infinity")
        assert modulo(N(Decimal("-Infinity")), N(3)).value == Decimal("-Infinity")

    def test_modulo_takes_the_dividends_sign(self) -> None:
        """Truncated division, not floored: the sign follows `a`, not `b`."""
        assert modulo(N(-7), N(3)).value == -1
        assert modulo(N(7), N(-3)).value == 1
        assert modulo(N(Decimal("-7.5")), N(2)).value == Decimal("-1.5")

    def test_modulo_keeps_every_digit_of_its_arguments(self) -> None:
        """The previous body went through `float64` and back via `math.fmod`.

        Which lost every digit past the seventeenth of an argument go-cty and
        this package had agreed on exactly. Computed in `Decimal`, the remainder
        of a 30-digit dividend is exact.
        """
        assert modulo(N(Decimal("1.000000000000000000000000000")), N(2)).value == Decimal(
            "1.000000000000000000000000000"
        )

    def test_negate_number(self) -> None:
        assert negate(CtyNumber().validate(5)).value == -5
        assert negate(CtyNumber().validate(-5)).value == 5
        assert negate(CtyNumber().validate(0)).value == 0

    def test_abs_fn(self) -> None:
        assert abs_fn(CtyNumber().validate(5)).value == 5
        assert abs_fn(CtyNumber().validate(-5)).value == 5
        assert abs_fn(CtyNumber().validate(0)).value == 0
        assert abs_fn(CtyNumber().validate(-5.5)).value == 5.5

    def test_abs_fn_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            abs_fn(CtyValue.null(CtyNumber()))
        assert abs_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_abs_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            abs_fn(CtyString().validate("not a number"))

    def test_ceil_fn(self) -> None:
        assert ceil_fn(CtyNumber().validate(5.1)).value == Decimal("6")
        assert ceil_fn(CtyNumber().validate(5.9)).value == Decimal("6")
        assert ceil_fn(CtyNumber().validate(5.0)).value == Decimal("5")
        assert ceil_fn(CtyNumber().validate(-5.1)).value == Decimal("-5")

    def test_ceil_fn_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            ceil_fn(CtyValue.null(CtyNumber()))
        assert ceil_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_ceil_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            ceil_fn(CtyString().validate("not a number"))

    def test_floor_fn(self) -> None:
        assert floor_fn(CtyNumber().validate(5.1)).value == Decimal("5")
        assert floor_fn(CtyNumber().validate(5.9)).value == Decimal("5")
        assert floor_fn(CtyNumber().validate(5.0)).value == Decimal("5")
        assert floor_fn(CtyNumber().validate(-5.1)).value == Decimal("-6")

    def test_floor_fn_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            floor_fn(CtyValue.null(CtyNumber()))
        assert floor_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_floor_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            floor_fn(CtyString().validate("not a number"))

    def test_log_fn(self) -> None:
        assert log_fn(CtyNumber().validate(100), CtyNumber().validate(10)).value == Decimal("2")
        assert log_fn(CtyNumber().validate(8), CtyNumber().validate(2)).value == Decimal("3")

    def test_log_fn_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            log_fn(CtyValue.null(CtyNumber()), CtyNumber().validate(10))
        with pytest.raises(CtyFunctionError):
            log_fn(CtyNumber().validate(100), CtyValue.null(CtyNumber()))
        assert log_fn(CtyValue.unknown(CtyNumber()), CtyNumber().validate(10)).is_unknown
        assert log_fn(CtyNumber().validate(100), CtyValue.unknown(CtyNumber())).is_unknown

    def test_log_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            log_fn(CtyString().validate("a"), CtyNumber().validate(10))
        with pytest.raises(CtyFunctionError):
            log_fn(CtyNumber().validate(100), CtyString().validate("b"))

    def test_log_refuses_only_the_arguments_that_make_it_a_nan(self) -> None:
        """A negative operand is a NaN, which `cty.NumberFloatVal` cannot hold.

        `big.Float.SetFloat64` panics on one and the function framework recovers
        that into an error (`function.go:349`), so this is a refusal on both
        sides. It is the *only* refusal `log` has: the three domain checks this
        used to carry are below, each answering where it used to raise.
        """
        with pytest.raises(CtyFunctionError):
            log_fn(N(-1), N(10))
        with pytest.raises(CtyFunctionError):
            log_fn(N(100), N(-1))

    def test_log_of_zero_or_a_degenerate_base_is_an_infinity(self) -> None:
        """These three raised until 2026-08-17 -- "number must be positive",
        "base must be positive" and "base cannot be 1".

        go-cty checks none of them. `LogFunc` reads both arguments as `float64`
        and returns `math.Log(num) / math.Log(base)`, so the answers fall out of
        IEEE-754: `log(0)` is `-Inf`, `log(1)` is exactly zero so dividing by it
        gives `+Inf`, and `log(0)` as a *base* is `-Inf` so dividing by it gives
        a signed zero. Verified against go-cty for all three
        (`stdlib/number.go:476`).
        """
        assert log_fn(N(0), N(2)).value == Decimal("-Infinity")
        assert log_fn(N(8), N(1)).value == Decimal("Infinity")
        assert log_fn(N(8), N(0)).value == 0

    def test_log_refuses_an_argument_too_large_for_a_float64(self) -> None:
        """The refusal comes from reading the argument, not from the arithmetic.

        `gocty.FromCtyValue` truncates precision silently but will not let a
        finite number become an infinity on the way in (`gocty/out.go:207`).
        Without it `log(1e400, 2)` answers `+Inf` here where go-cty errors, which
        is the silent infinity that comment is about. `pow` carries the same gate
        for the same reason, and is checked here beside it: both read their
        arguments with `gocty.FromCtyValue`.
        """
        with pytest.raises(CtyFunctionError, match="value must be between"):
            log_fn(N(Decimal("1e400")), N(2))
        with pytest.raises(CtyFunctionError, match="value must be between"):
            log_fn(N(2), N(Decimal("1e400")))

        with pytest.raises(CtyFunctionError, match="value must be between"):
            pow_fn(N(Decimal("1e400")), N(2))
        with pytest.raises(CtyFunctionError, match="value must be between"):
            pow_fn(N(2), N(Decimal("1e400")))

        # An argument that already *is* an infinity converts exactly, so it passes.
        assert log_fn(N(Decimal("Infinity")), N(2)).value == Decimal("Infinity")
        assert pow_fn(N(Decimal("Infinity")), N(2)).value == Decimal("Infinity")

    def test_pow_fn(self) -> None:
        assert pow_fn(CtyNumber().validate(2), CtyNumber().validate(3)).value == 8
        assert pow_fn(CtyNumber().validate(4), CtyNumber().validate(0.5)).value == 2

    def test_pow_of_a_zero_exponent_is_one_for_any_base(self) -> None:
        """Go's `math.Pow` special cases this before anything else.

        "Pow(x, ±0) = 1 for any x", including zero and an infinity. Reading `pow`
        through `float64` inherits all of those special cases rather than
        restating any of them, which is why the hand-written `power == 0` guard
        this used to need is gone. Verified against go-cty: `pow(0, 0)` is 1.
        """
        for base in (0, 2, -3, Decimal("Infinity"), Decimal("-Infinity")):
            assert pow_fn(N(base), N(0)).value == 1

    def test_pow_agrees_with_math_pow_on_the_infinite_edges(self) -> None:
        """The `float64` transcription carries Go's zero and infinity contract."""
        assert pow_fn(N(0), N(-1)).value == Decimal("Infinity")
        assert pow_fn(N(Decimal("Infinity")), N(-1)).value == 0
        assert pow_fn(N(Decimal("0.5")), N(Decimal("Infinity"))).value == 0

    def test_pow_fn_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            pow_fn(CtyValue.null(CtyNumber()), CtyNumber().validate(2))
        with pytest.raises(CtyFunctionError):
            pow_fn(CtyNumber().validate(2), CtyValue.null(CtyNumber()))
        assert pow_fn(CtyValue.unknown(CtyNumber()), CtyNumber().validate(2)).is_unknown
        assert pow_fn(CtyNumber().validate(2), CtyValue.unknown(CtyNumber())).is_unknown

    def test_pow_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            pow_fn(CtyString().validate("a"), CtyNumber().validate(2))
        with pytest.raises(CtyFunctionError):
            pow_fn(CtyNumber().validate(2), CtyString().validate("b"))

    def test_signum_fn(self) -> None:
        assert signum_fn(CtyNumber().validate(10)).value == 1
        assert signum_fn(CtyNumber().validate(-10)).value == -1
        assert signum_fn(CtyNumber().validate(0)).value == 0

    def test_signum_fn_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            signum_fn(CtyValue.null(CtyNumber()))
        assert signum_fn(CtyValue.unknown(CtyNumber())).is_unknown

    def test_signum_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            signum_fn(CtyString().validate("a"))

    def test_parseint_fn(self) -> None:
        """The `0xFF` in base 0 case is gone; base 0 is refused, below.

        Base 0 would mean "infer the base from a prefix", which go-cty's
        parameter range excludes: `big.Int.SetString` supports it but
        `ParseIntFunc` rejects any base outside 2 to 62 first
        (`stdlib/number.go:584`).
        """
        assert parseint_fn(S("10"), N(10)).value == 10
        assert parseint_fn(S("FF"), N(16)).value == 255
        assert parseint_fn(S("-10"), N(10)).value == -10

    def test_parseint_reaches_base_62(self) -> None:
        """`big.Int.SetString` carries an alphabet Python's `int()` does not.

        Up to base 36 the two letter cases are one digit; above it the upper-case
        letters continue where the lower-case ones stop, so base 62 runs
        `0-9a-zA-Z` and `Z` is 61. Verified against go-cty: `parseint("Zz", 62)`
        is 3817.
        """
        assert parseint_fn(S("zz"), N(36)).value == 1295
        assert parseint_fn(S("Zz"), N(62)).value == 3817

    def test_parseint_refuses_what_go_ctys_parser_refuses(self) -> None:
        """`int(text, base)` accepts three things `big.Int.SetString` does not.

        Whitespace around the digits, digit-grouping underscores, and a base
        prefix. Each would have this package answer a number where go-cty
        answers "cannot parse", so the parser is transcribed rather than
        delegated.
        """
        for text in (" 10", "10 ", "1_0", "0x10", "", "+", "8"):
            with pytest.raises(CtyFunctionError, match="cannot parse"):
                parseint_fn(S(text), N(8) if text == "8" else N(16) if text == "0x10" else N(10))

    def test_parseint_fn_unparseable_is_an_error_not_a_null(self) -> None:
        """This asserted a *null number* until 2026-08-17.

        go-cty raises: `cannot parse %q as a base %d integer`, by argument index
        (`stdlib/number.go:593`). A null is worse than an error here because it is
        a value -- a caller that does not check gets it as an argument to the next
        function rather than as a diagnostic.
        """
        with pytest.raises(CtyFunctionError, match='cannot parse "z" as a base 10 integer'):
            parseint_fn(S("z"), N(10))

    def test_parseint_fn_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            parseint_fn(CtyValue.null(CtyString()), CtyNumber().validate(10))
        with pytest.raises(CtyFunctionError):
            parseint_fn(CtyString().validate("10"), CtyValue.null(CtyNumber()))
        assert parseint_fn(CtyValue.unknown(CtyString()), CtyNumber().validate(10)).is_unknown
        assert parseint_fn(CtyString().validate("10"), CtyValue.unknown(CtyNumber())).is_unknown

    def test_parseint_fn_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            parseint_fn(CtyNumber().validate(10), CtyNumber().validate(10))
        with pytest.raises(CtyFunctionError):
            parseint_fn(CtyString().validate("10"), CtyString().validate("10"))

    def test_parseint_fn_invalid_base(self) -> None:
        """The range is 2 to 62 inclusive, not "0 or 2 to 36".

        37 used to be refused and is now valid, and 0 used to be accepted as
        "infer from the prefix" and is now refused. go-cty
        `stdlib/number.go:584`.
        """
        for base in (0, 1, 63):
            with pytest.raises(CtyFunctionError, match="between 2 and 62 inclusive"):
                parseint_fn(S("10"), N(base))
        assert parseint_fn(S("10"), N(37)).value == 37

    def test_parseint_base_must_be_a_whole_number(self) -> None:
        """go-cty reads it into a Go `int` through `gocty.FromCtyValue`."""
        with pytest.raises(CtyFunctionError, match="whole number"):
            parseint_fn(S("ff"), N(Decimal("16.5")))

    def test_signum_refuses_a_fraction(self) -> None:
        """This answered `1` for `1.5` until 2026-08-17.

        `SignumFunc` reads its argument into a Go `int` before looking at the
        sign (`stdlib/number.go:534`), so a fraction is an error rather than a
        sign. That reads like a quirk of the Go implementation and is
        load-bearing: the function promises one of three answers, and a caller
        handed one for `0.5` has been told the value is whole.
        """
        for value in (Decimal("3.5"), Decimal("-0.5"), Decimal("Infinity")):
            with pytest.raises(CtyFunctionError, match="whole number"):
                signum_fn(N(value))

    def test_abs_keeps_the_fraction_it_is_given(self) -> None:
        """`AllowMarked` means `abs` owns its marks; it must not lose the value.

        `cty.Value.Absolute` unmarks, takes the magnitude and re-applies
        (`value_ops.go:794`), and an implementation that sets the flag and then
        forgets the second half silently declassifies a sensitive number.
        """
        assert abs_fn(N(Decimal("-3.5"))).value == Decimal("3.5")
        assert abs_fn(N(Decimal("-Infinity"))).value == Decimal("Infinity")

    def test_ceil_and_floor_return_an_infinity_unchanged(self) -> None:
        """go-cty tests `f.IsInf()` first; there is no whole number above `+Inf`."""
        assert ceil_fn(N(Decimal("Infinity"))).value == Decimal("Infinity")
        assert floor_fn(N(Decimal("-Infinity"))).value == Decimal("-Infinity")

    def test_int_truncates_toward_zero_and_refuses_an_infinity(self) -> None:
        """`big.Float.IsInt()` is false for an infinity, and go-cty then crashes.

        It hands a nil `big.Int` to `SetInt` (`stdlib/number.go:394`); the oracle
        reports a recovered nil dereference. This refuses it in the words go-cty's
        own `stdlib.Int` wrapper uses for the same condition (`number.go:681`).
        """
        assert int_fn(N(Decimal("-3.9"))).value == -3
        with pytest.raises(CtyFunctionError, match="can't truncate infinity"):
            int_fn(N(Decimal("Infinity")))

    def test_a_dynamic_unknown_is_answered_per_the_declared_parameter(self) -> None:
        """`AllowDynamicType` is declared on eight of these fourteen, not all.

        `abs`, `add`, `subtract`, `multiply`, `divide`, `modulo`, `negate` and
        `int` set it, so a value of no decided type still gets an unknown
        *number*. `ceil`, `floor`, `log`, `pow`, `signum` and `parseint` do not,
        so they answer an unknown of no decided type -- which carries no
        refinement, because there is no type yet for one to be about
        (`function.go:281`). That asymmetry is go-cty's declaration, verified
        against the oracle, not an omission here.
        """
        dynamic = CtyValue.unknown(CtyDynamic())

        assert isinstance(abs_fn(dynamic).type, CtyNumber)
        assert isinstance(int_fn(dynamic).type, CtyNumber)
        assert isinstance(ceil_fn(dynamic).type, CtyDynamic)
        assert isinstance(parseint_fn(dynamic, N(16)).type, CtyDynamic)

    def test_add_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            add(CtyString().validate("a"), CtyString().validate("b"))

    def test_subtract_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            subtract(CtyString().validate("a"), CtyString().validate("b"))

    def test_multiply_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            multiply(CtyString().validate("a"), CtyString().validate("b"))

    def test_divide_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            divide(CtyString().validate("a"), CtyString().validate("b"))

    def test_modulo_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            modulo(CtyString().validate("a"), CtyString().validate("b"))

    def test_pow_invalid_operation(self) -> None:
        with pytest.raises(CtyFunctionError):
            pow_fn(CtyNumber().validate(-1), CtyNumber().validate(0.5))

    def test_add_invalid_types(self) -> None:
        with pytest.raises(CtyFunctionError):
            add(CtyString().validate("a"), CtyNumber().validate(1))
        with pytest.raises(CtyFunctionError):
            add(CtyNumber().validate(1), CtyString().validate("a"))


# 🌊🪢🔚
