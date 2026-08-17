#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Until 2026-08-17 this suite verified that numeric functions propagate or
resolve refined unknown value constraints. As of that date the stdlib
numeric functions were migrated onto a port of go-cty's `cty/function`
framework, and go-cty's arithmetic function parameters do not set
`AllowUnknown` (`cty/function/stdlib/number.go`). The framework
short-circuits before `Impl` runs whenever an argument is unknown
(`function.go:314`), returning an unknown of the declared return type with
no refinement carried over. This suite now verifies that deferral."""

from decimal import Decimal

from pyvider.cty import CtyNumber, CtyValue
from pyvider.cty.functions import abs_fn, divide, negate, subtract
from pyvider.cty.values.markers import RefinedUnknownValue


def refined_unknown_num(
    lower_bound: tuple[Decimal, bool] | None = None,
    upper_bound: tuple[Decimal, bool] | None = None,
) -> CtyValue:
    return CtyValue.unknown(
        CtyNumber(),
        value=RefinedUnknownValue(number_lower_bound=lower_bound, number_upper_bound=upper_bound),
    )


class TestRefinedUnknownPropagation:
    def test_subtract_defers_instead_of_adjusting_bounds(self) -> None:
        """Until 2026-08-17 this asserted (unknown in [10, 20]) - 5 narrows
        to (unknown in [5, 15]).

        go-cty's SubtractFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        known_5 = CtyNumber().validate(5)
        result = subtract(unknown_10_20, known_5)

        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_divide_defers_instead_of_scaling_bounds(self) -> None:
        """Until 2026-08-17 this asserted (unknown in [10, 20]) / 2 narrows
        to (unknown in [5, 10]).

        go-cty's DivideFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        known_2 = CtyNumber().validate(2)
        result = divide(unknown_10_20, known_2)

        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_negate_defers_instead_of_swapping_and_inverting_bounds(self) -> None:
        """Until 2026-08-17 this asserted -(unknown in [10, 20]) narrows to
        (unknown in [-20, -10]).

        go-cty's NegateFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        result = negate(unknown_10_20)

        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_abs_defers_instead_of_yielding_positive_bounds(self) -> None:
        """Until 2026-08-17 this asserted abs(unknown < 0) narrows to
        (unknown > 0).

        go-cty's AbsoluteFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown_neg = refined_unknown_num(
            lower_bound=(Decimal("-20"), True), upper_bound=(Decimal("-10"), True)
        )
        result = abs_fn(unknown_neg)

        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)


# 🌊🪢🔚
