#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD: This suite adds targeted tests for all unexercised branches in the
refined unknown propagation logic of comparison functions."""

from decimal import Decimal

from pyvider.cty import CtyNumber, CtyValue
from pyvider.cty.functions import greater_than, less_than
from pyvider.cty.values.markers import RefinedUnknownValue


def refined_unknown_num(
    lower_bound: tuple[Decimal, bool] | None = None,
    upper_bound: tuple[Decimal, bool] | None = None,
) -> CtyValue:
    return CtyValue.unknown(
        CtyNumber(),
        value=RefinedUnknownValue(number_lower_bound=lower_bound, number_upper_bound=upper_bound),
    )


class TestRefinedUnknownComparisonCoverage:
    def test_compare_known_to_refined_upper_bound_greater(self) -> None:
        """TDD: 50 > (unknown < 20) should be True."""
        known_50 = CtyNumber().validate(50)
        unknown_lt_20 = refined_unknown_num(upper_bound=(Decimal("20"), False))
        result = greater_than(known_50, unknown_lt_20)
        assert not result.is_unknown and result.value is True

    def test_compare_known_to_refined_lower_bound_less(self) -> None:
        """TDD: 10 < (unknown > 50) should be True."""
        known_10 = CtyNumber().validate(10)
        unknown_gt_50 = refined_unknown_num(lower_bound=(Decimal("50"), False))
        result = less_than(known_10, unknown_gt_50)
        assert not result.is_unknown and result.value is True

    def test_compare_two_refined_overlapping_is_unknown(self) -> None:
        """TDD: (unknown in [10,30]) > (unknown in [20,40]) should be Unknown."""
        unknown_10_30 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("30"), True)
        )
        unknown_20_40 = refined_unknown_num(
            lower_bound=(Decimal("20"), True), upper_bound=(Decimal("40"), True)
        )
        result = greater_than(unknown_10_30, unknown_20_40)
        assert result.is_unknown

    def test_compare_refined_to_known_upper_bound_less_false(self) -> None:
        """TDD: (unknown > 100) < 50 should be False."""
        unknown_gt_100 = refined_unknown_num(lower_bound=(Decimal("100"), False))
        known_50 = CtyNumber().validate(50)
        result = less_than(unknown_gt_100, known_50)
        assert not result.is_unknown and result.value is False

    def test_compare_refined_to_known_lower_bound_greater_false(self) -> None:
        """TDD: (unknown < 10) > 20 should be False."""
        unknown_lt_10 = refined_unknown_num(upper_bound=(Decimal("10"), False))
        known_20 = CtyNumber().validate(20)
        result = greater_than(unknown_lt_10, known_20)
        assert not result.is_unknown and result.value is False


# 🌊🪢🔚
