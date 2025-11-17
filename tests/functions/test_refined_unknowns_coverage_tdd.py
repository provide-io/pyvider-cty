#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD: This suite adds targeted tests for all unexercised branches in the
refined unknown propagation logic of numeric and comparison functions."""

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
    def test_multiply_by_zero_is_zero(self) -> None:
        """TDD: unknown * 0 should be a known 0."""
        unknown = refined_unknown_num(lower_bound=(Decimal("10"), True))
        known_zero = CtyNumber().validate(0)
        result = multiply(unknown, known_zero)
        assert not result.is_unknown
        assert result.value == 0

    def test_multiply_by_negative_inverts_bounds(self) -> None:
        """TDD: (unknown in [10, 20]) * -2 should be (unknown in [-40, -20])."""
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        known_neg_2 = CtyNumber().validate(-2)
        result = multiply(unknown_10_20, known_neg_2)
        assert result.is_unknown
        assert result.value.number_lower_bound == (Decimal("-40"), True)
        assert result.value.number_upper_bound == (Decimal("-20"), True)

    def test_divide_by_negative_inverts_bounds(self) -> None:
        """TDD: (unknown in [10, 20]) / -2 should be (unknown in [-10, -5])."""
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        known_neg_2 = CtyNumber().validate(-2)
        result = divide(unknown_10_20, known_neg_2)
        assert result.is_unknown
        assert result.value.number_lower_bound == (Decimal("-10"), True)
        assert result.value.number_upper_bound == (Decimal("-5"), True)

    def test_negate_with_only_one_bound(self) -> None:
        """TDD: -(unknown > 10) should be (unknown < -10)."""
        unknown_gt_10 = refined_unknown_num(lower_bound=(Decimal("10"), False))
        result = negate(unknown_gt_10)
        assert result.is_unknown
        assert result.value.number_lower_bound is None
        assert result.value.number_upper_bound == (Decimal("-10"), False)

    def test_abs_with_range_crossing_zero(self) -> None:
        """TDD: abs(unknown in [-10, 20]) should be (unknown in [0, 20])."""
        unknown_neg_pos = refined_unknown_num(
            lower_bound=(Decimal("-10"), True), upper_bound=(Decimal("20"), True)
        )
        result = abs_fn(unknown_neg_pos)
        assert result.is_unknown
        assert result.value.number_lower_bound == (Decimal("0"), True)
        assert result.value.number_upper_bound == (Decimal("20"), True)

    def test_abs_with_only_lower_bound_positive(self) -> None:
        """TDD: abs(unknown > 10) should be unchanged."""
        unknown_gt_10 = refined_unknown_num(lower_bound=(Decimal("10"), True))
        result = abs_fn(unknown_gt_10)
        assert result.is_unknown
        assert result.value.number_lower_bound == (Decimal("10"), True)
        assert result.value.number_upper_bound is None

    def test_abs_with_only_upper_bound_negative(self) -> None:
        """TDD: abs(unknown < -10) should be (unknown > 10)."""
        unknown_lt_neg_10 = refined_unknown_num(upper_bound=(Decimal("-10"), True))
        result = abs_fn(unknown_lt_neg_10)
        assert result.is_unknown
        assert result.value.number_lower_bound == (Decimal("10"), True)
        assert result.value.number_upper_bound is None

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
