#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Until 2026-08-17 this suite asserted that numeric functions narrow
results from refinement bounds on unknown arguments. As of that date the
stdlib numeric functions were migrated onto a port of go-cty's
`cty/function` framework, and go-cty's arithmetic function parameters do
not set `AllowUnknown` (`cty/function/stdlib/number.go`). The framework
short-circuits before `Impl` runs whenever an argument is unknown
(`function.go:314`), returning an unknown of the declared return type with
no refinement carried over. This suite now asserts that deferral instead.
The comparison tests in this file are unaffected -- go-cty's comparison
functions do carry bound-based short-circuits inside their `Impl`, so
those still narrow."""

from decimal import Decimal

from pyvider.cty import CtyNumber, CtyValue
from pyvider.cty.functions import (
    abs_fn,
    divide,
    greater_than,
    less_than,
    multiply,
    negate,
)
from pyvider.cty.values.markers import RefinedUnknownValue


def refined_unknown_num(
    lower_bound: tuple[Decimal, bool] | None = None,
    upper_bound: tuple[Decimal, bool] | None = None,
) -> CtyValue:
    return CtyValue.unknown(
        CtyNumber(),
        value=RefinedUnknownValue(number_lower_bound=lower_bound, number_upper_bound=upper_bound),
    )


class TestRefinedUnknownsCoverage:
    def test_multiply_defers_even_when_zero_would_decide_it(self) -> None:
        """Until 2026-08-17 this asserted multiply(unknown, 0) is a known 0.

        go-cty's MultiplyFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown = refined_unknown_num(lower_bound=(Decimal("10"), True))
        known_zero = CtyNumber().validate(0)
        result = multiply(unknown, known_zero)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_multiply_defers_instead_of_inverting_bounds(self) -> None:
        """Until 2026-08-17 this asserted (unknown in [10, 20]) * -2 narrows
        to (unknown in [-40, -20]).

        go-cty's MultiplyFunc parameters do not set AllowUnknown
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
        known_neg_2 = CtyNumber().validate(-2)
        result = multiply(unknown_10_20, known_neg_2)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_divide_defers_instead_of_inverting_bounds(self) -> None:
        """Until 2026-08-17 this asserted (unknown in [10, 20]) / -2 narrows
        to (unknown in [-10, -5]).

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
        known_neg_2 = CtyNumber().validate(-2)
        result = divide(unknown_10_20, known_neg_2)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_negate_defers_even_with_only_one_bound(self) -> None:
        """Until 2026-08-17 this asserted -(unknown > 10) narrows to
        (unknown < -10).

        go-cty's NegateFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown_gt_10 = refined_unknown_num(lower_bound=(Decimal("10"), False))
        result = negate(unknown_gt_10)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_abs_defers_even_when_range_crosses_zero(self) -> None:
        """Until 2026-08-17 this asserted abs(unknown in [-10, 20]) narrows
        to (unknown in [0, 20]).

        go-cty's AbsoluteFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown_neg_pos = refined_unknown_num(
            lower_bound=(Decimal("-10"), True), upper_bound=(Decimal("20"), True)
        )
        result = abs_fn(unknown_neg_pos)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_abs_defers_even_with_only_lower_bound_positive(self) -> None:
        """Until 2026-08-17 this asserted abs(unknown > 10) is unchanged.

        go-cty's AbsoluteFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown_gt_10 = refined_unknown_num(lower_bound=(Decimal("10"), True))
        result = abs_fn(unknown_gt_10)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_abs_defers_even_with_only_upper_bound_negative(self) -> None:
        """Until 2026-08-17 this asserted abs(unknown < -10) narrows to
        (unknown > 10).

        go-cty's AbsoluteFunc parameters do not set AllowUnknown
        (`stdlib/number.go`), so the framework returns an unknown of the
        declared return type without calling Impl, and no bound arithmetic
        happens (`function.go:314`). The old answer was sound but is not
        go-cty's; the bound propagation this pinned lived in the stdlib
        function where go-cty puts it on Value's operators, which this
        package does not have.
        """
        unknown_lt_neg_10 = refined_unknown_num(upper_bound=(Decimal("-10"), True))
        result = abs_fn(unknown_lt_neg_10)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_compare_refined_to_known_upper_bound(self) -> None:
        """TDD: (unknown > 100) > 50 should be True."""
        unknown_gt_100 = refined_unknown_num(lower_bound=(Decimal("100"), False))
        known_50 = CtyNumber().validate(50)
        result = greater_than(unknown_gt_100, known_50)
        assert result.value is True

    def test_compare_refined_to_known_lower_bound(self) -> None:
        """TDD: (unknown < 10) < 20 should be True."""
        unknown_lt_10 = refined_unknown_num(upper_bound=(Decimal("10"), False))
        known_20 = CtyNumber().validate(20)
        result = less_than(unknown_lt_10, known_20)
        assert result.value is True

    def test_compare_two_refined_non_overlapping(self) -> None:
        """TDD: (unknown > 100) > (unknown < 50) should be True."""
        unknown_gt_100 = refined_unknown_num(lower_bound=(Decimal("100"), False))
        unknown_lt_50 = refined_unknown_num(upper_bound=(Decimal("50"), False))
        result = greater_than(unknown_gt_100, unknown_lt_50)
        assert result.value is True


# 🌊🪢🔚
