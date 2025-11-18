#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD: Verifies that numeric functions consistently propagate or resolve
refined unknown value constraints."""

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
    def test_subtract_from_refined_unknown_adjusts_bounds(self) -> None:
        """TDD: (unknown in [10, 20]) - 5 should be (unknown in [5, 15])."""
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        known_5 = CtyNumber().validate(5)
        result = subtract(unknown_10_20, known_5)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        assert result.value.number_lower_bound == (Decimal("5"), True)
        assert result.value.number_upper_bound == (Decimal("15"), True)

    def test_divide_refined_unknown_by_positive_scales_bounds(self) -> None:
        """TDD: (unknown in [10, 20]) / 2 should be (unknown in [5, 10])."""
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        known_2 = CtyNumber().validate(2)
        result = divide(unknown_10_20, known_2)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        assert result.value.number_lower_bound == (Decimal("5"), True)
        assert result.value.number_upper_bound == (Decimal("10"), True)

    def test_negate_refined_unknown_swaps_and_inverts_bounds(self) -> None:
        """TDD: -(unknown in [10, 20]) should be (unknown in [-20, -10])."""
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        result = negate(unknown_10_20)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        assert result.value.number_lower_bound == (Decimal("-20"), True)
        assert result.value.number_upper_bound == (Decimal("-10"), True)

    def test_abs_on_refined_negative_unknown_yields_positive(self) -> None:
        """TDD: abs(unknown < 0) should be (unknown > 0)."""
        unknown_neg = refined_unknown_num(
            lower_bound=(Decimal("-20"), True), upper_bound=(Decimal("-10"), True)
        )
        result = abs_fn(unknown_neg)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        assert result.value.number_lower_bound == (Decimal("10"), True)
        assert result.value.number_upper_bound == (Decimal("20"), True)


# 🌊🪢🔚
