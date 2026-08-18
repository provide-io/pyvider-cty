#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`pow` reads its arguments through `float64`, because go-cty's `PowFunc` does.

    Impl: func(args []cty.Value, retType cty.Type) (ret cty.Value, err error) {
        var num float64
        if err := gocty.FromCtyValue(args[0], &num); err != nil { ... }
        var power float64
        if err := gocty.FromCtyValue(args[1], &power); err != nil { ... }
        return cty.NumberFloatVal(math.Pow(num, power)), nil
    }

    -- go-cty v1.19.0, cty/function/stdlib/number.go:506

Nothing in that path is a `big.Float` computation, so holding the arithmetic in
`Decimal` was not a more precise version of go-cty's answer -- it was a
different function, and it diverged in three ways at once. The third was a
crash: `Decimal` raises `decimal.Overflow`, which is not a `CtyError`, so
`pow(10, 1000000)` escaped the error taxonomy as a `CtyFunctionPanicError`.

Every expectation below was read off go-cty v1.19.0 through the soup-go oracle,
including `-8 ** 0.5` and `-0.0 ** -1`. An earlier version of this docstring
said those two needed a hand-written Go program because they were "not
expressible in the oracle's JSON" -- they are ordinary JSON numbers, and had
been run through the oracle before that sentence was written. Both are sweep
rows now, so the claim is checked rather than asserted.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from pyvider.cty import CtyNumber
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import pow_fn


def N(value: object) -> object:
    return CtyNumber().validate(Decimal(str(value)))


class TestOverflowIsAnInfinity:
    """A finite result too large for a `float64` is `±Inf`, not a crash."""

    def test_a_large_positive_exponent_overflows_to_infinity(self) -> None:
        """`Decimal` raised `decimal.Overflow` here, outside the CtyError tree."""
        assert pow_fn(N(10), N(1000000)).value == Decimal("Infinity")

    def test_overflow_just_past_the_float64_range_is_also_infinity(self) -> None:
        """10^400 is finite and exactly representable in `Decimal`. Not in Go."""
        assert pow_fn(N(10), N(400)).value == Decimal("Infinity")

    def test_an_odd_power_of_a_negative_base_overflows_negative(self) -> None:
        """Go's `math.Pow` keeps the sign, so the infinity has to as well."""
        assert pow_fn(N(-10), N(401)).value == Decimal("-Infinity")

    def test_an_even_power_of_a_negative_base_overflows_positive(self) -> None:
        assert pow_fn(N(-10), N(400)).value == Decimal("Infinity")

    def test_underflow_is_zero(self) -> None:
        """`Decimal` answered 1E-1000000, a number no `float64` can hold."""
        assert pow_fn(N(10), N(-1000000)).value == 0


class TestTheFloat64RangeGate:
    """`gocty.FromCtyValue` refuses to let a finite argument become an infinity."""

    def test_a_base_too_large_for_a_float64_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError, match="value must be between"):
            pow_fn(N(Decimal("1e400")), N(2))

    def test_an_exponent_too_large_for_a_float64_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError, match="value must be between"):
            pow_fn(N(2), N(Decimal("1e400")))

    def test_an_argument_that_already_is_an_infinity_passes(self) -> None:
        """It converts exactly, so the gate has nothing to object to."""
        assert pow_fn(N(Decimal("Infinity")), N(2)).value == Decimal("Infinity")


class TestGoZeroAndSignContract:
    """The special cases `math.Pow` documents, which the transcription inherits."""

    def test_a_zero_base_under_a_negative_exponent_is_positive_infinity(self) -> None:
        """Python's `math.pow` raises `ValueError` for this. Go answers `+Inf`."""
        assert pow_fn(N(0), N(-1)).value == Decimal("Infinity")
        assert pow_fn(N(0), N(-2)).value == Decimal("Infinity")

    def test_a_negative_zero_base_keeps_its_sign_for_an_odd_exponent(self) -> None:
        """ "Pow(±0, y) = ±Inf for y an odd integer < 0"; `+Inf` otherwise."""
        assert pow_fn(N("-0.0"), N(-1)).value == Decimal("-Infinity")
        assert pow_fn(N("-0.0"), N(-2)).value == Decimal("Infinity")

    def test_a_negative_base_under_a_fractional_exponent_is_refused(self) -> None:
        """Go's `math.Pow` answers NaN, and `cty.NumberFloatVal` cannot hold one.

        go-cty reaches the refusal by recovering the `Float.SetFloat64(NaN)`
        panic in its function framework; this reaches it from
        `_number_from_float`. Both are errors, which is the comparison the
        sweep makes.
        """
        with pytest.raises(CtyFunctionError, match="not a number"):
            pow_fn(N(-8), N("0.5"))

    def test_a_zero_exponent_is_one_for_every_base(self) -> None:
        for base in (0, 2, -3, Decimal("Infinity"), Decimal("-Infinity")):
            assert pow_fn(N(base), N(0)).value == 1


class TestTheOrdinaryAnswersAreUnchanged:
    def test_whole_powers_stay_whole(self) -> None:
        assert pow_fn(N(2), N(3)).value == 8
        assert pow_fn(N(2), N(10)).value == 1024

    def test_a_square_root_is_the_float64_one(self) -> None:
        """17 significant digits, which is go-cty's answer rather than a rounding of it."""
        assert pow_fn(N(2), N("0.5")).value == Decimal("1.4142135623730951")

    def test_a_float64_rounding_artefact_is_reproduced_rather_than_avoided(self) -> None:
        """`1.1 ** 2` is not 1.21 in `float64`, and go-cty says so."""
        assert pow_fn(N("1.1"), N(2)).value == Decimal("1.2100000000000002")


# 🐍🏗️🔚
