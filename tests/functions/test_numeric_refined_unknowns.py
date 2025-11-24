#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for numeric functions with refined unknown values.

This test suite focuses on achieving 100% coverage of refined unknown arithmetic
operations in numeric_functions.py, particularly:
- Lines 35-41, 46-52, 63, 98-104 (addition refinement propagation)
- Lines in subtraction, multiplication, division refinement logic
- Edge cases with bounds, inclusive/exclusive flags, and special values"""

from decimal import Decimal

import pytest

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    abs_fn,
    add,
    divide,
    multiply,
    negate,
    subtract,
)
from pyvider.cty.values.markers import RefinedUnknownValue


# Helper functions
def N(v):
    """Create a known CtyNumber value."""
    return CtyNumber().validate(v)


def UnknownN(**refinements):
    """Create a refined unknown CtyNumber value."""
    if refinements:
        return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**refinements))
    return CtyValue.unknown(CtyNumber())


class TestAdditionRefinedUnknowns:
    """Test addition with refined unknown values - covers lines 35-67."""

    def test_add_known_with_refined_lower_bound(self) -> None:
        """Test: known + refined_unknown with lower bound (lines 35-39)."""
        # val_a is known (5), ref_b has lower bound >= 10 (inclusive)
        a = N(5)
        b = UnknownN(number_lower_bound=(Decimal("10"), True))
        result = add(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result should be >= 15 (5 + 10)
        assert result.value.number_lower_bound == (Decimal("15"), True)

    def test_add_known_with_refined_upper_bound(self) -> None:
        """Test: known + refined_unknown with upper bound (lines 40-44)."""
        a = N(5)
        b = UnknownN(number_upper_bound=(Decimal("20"), False))
        result = add(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result should be < 25 (5 + 20, exclusive)
        assert result.value.number_upper_bound == (Decimal("25"), False)

    def test_add_refined_with_known_lower_bound(self) -> None:
        """Test: refined_unknown + known (lines 46-50)."""
        a = UnknownN(number_lower_bound=(Decimal("10"), True))
        b = N(3)
        result = add(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result should be >= 13
        assert result.value.number_lower_bound == (Decimal("13"), True)

    def test_add_refined_with_known_upper_bound(self) -> None:
        """Test: refined_unknown + known with upper bound (lines 51-55)."""
        a = UnknownN(number_upper_bound=(Decimal("100"), True))
        b = N(50)
        result = add(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        assert result.value.number_upper_bound == (Decimal("150"), True)

    def test_add_two_refined_lower_bounds(self) -> None:
        """Test: refined + refined with both lower bounds (lines 57-61)."""
        a = UnknownN(number_lower_bound=(Decimal("5"), True))
        b = UnknownN(number_lower_bound=(Decimal("10"), False))
        result = add(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Lower bound: 5 + 10 = 15, inclusive=False (True AND False)
        assert result.value.number_lower_bound == (Decimal("15"), False)

    def test_add_two_refined_upper_bounds(self) -> None:
        """Test: refined + refined with both upper bounds (lines 62-66)."""
        a = UnknownN(number_upper_bound=(Decimal("20"), True))
        b = UnknownN(number_upper_bound=(Decimal("30"), True))
        result = add(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Upper bound: 20 + 30 = 50, inclusive=True (True AND True)
        assert result.value.number_upper_bound == (Decimal("50"), True)

    def test_add_both_refined_with_all_bounds(self) -> None:
        """Test: Both refined unknowns with lower and upper bounds."""
        a = UnknownN(
            number_lower_bound=(Decimal("5"), True),
            number_upper_bound=(Decimal("10"), False),
        )
        b = UnknownN(
            number_lower_bound=(Decimal("2"), False),
            number_upper_bound=(Decimal("8"), True),
        )
        result = add(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Lower: 5 + 2 = 7 (inclusive=False)
        assert result.value.number_lower_bound == (Decimal("7"), False)
        # Upper: 10 + 8 = 18 (inclusive=False because 10 is exclusive)
        assert result.value.number_upper_bound == (Decimal("18"), False)


class TestSubtractionRefinedUnknowns:
    """Test subtraction with refined unknowns - covers lines 70-108."""

    def test_subtract_refined_minus_known_lower_bound(self) -> None:
        """Test: refined - known with lower bound (lines 76-80)."""
        a = UnknownN(number_lower_bound=(Decimal("20"), True))
        b = N(5)
        result = subtract(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result >= 15 (20 - 5)
        assert result.value.number_lower_bound == (Decimal("15"), True)

    def test_subtract_refined_minus_known_upper_bound(self) -> None:
        """Test: refined - known with upper bound (lines 81-85)."""
        a = UnknownN(number_upper_bound=(Decimal("100"), False))
        b = N(10)
        result = subtract(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result < 90 (100 - 10)
        assert result.value.number_upper_bound == (Decimal("90"), False)

    def test_subtract_known_minus_refined_upper_bound(self) -> None:
        """Test: known - refined with upper bound creates lower bound (lines 87-91)."""
        a = N(50)
        b = UnknownN(number_upper_bound=(Decimal("20"), True))
        result = subtract(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result >= 30 (50 - 20)
        assert result.value.number_lower_bound == (Decimal("30"), True)

    def test_subtract_known_minus_refined_lower_bound(self) -> None:
        """Test: known - refined with lower bound creates upper bound (lines 92-96)."""
        a = N(50)
        b = UnknownN(number_lower_bound=(Decimal("10"), False))
        result = subtract(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result <= 40 (50 - 10)
        assert result.value.number_upper_bound == (Decimal("40"), False)

    def test_subtract_both_refined_lower_bound(self) -> None:
        """Test: refined - refined with bounds (lines 98-102)."""
        a = UnknownN(number_lower_bound=(Decimal("30"), True))
        b = UnknownN(number_upper_bound=(Decimal("10"), True))
        result = subtract(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result >= 20 (30 - 10)
        assert result.value.number_lower_bound == (Decimal("20"), True)

    def test_subtract_both_refined_upper_bound(self) -> None:
        """Test: refined - refined upper bound (lines 103-107)."""
        a = UnknownN(number_upper_bound=(Decimal("50"), False))
        b = UnknownN(number_lower_bound=(Decimal("5"), True))
        result = subtract(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result < 45 (50 - 5), exclusive because a is exclusive
        assert result.value.number_upper_bound == (Decimal("45"), False)


class TestMultiplicationRefinedUnknowns:
    """Test multiplication with refined unknowns - covers lines 111-140."""

    def test_multiply_known_positive_with_refined_lower(self) -> None:
        """Test: positive known * refined (lines 118-123)."""
        a = N(2)
        b = UnknownN(number_lower_bound=(Decimal("10"), True))
        result = multiply(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result >= 20 (2 * 10)
        assert result.value.number_lower_bound == (Decimal("20"), True)

    def test_multiply_known_positive_with_refined_upper(self) -> None:
        """Test: positive known * refined with upper bound (lines 124-128)."""
        a = N(3)
        b = UnknownN(number_upper_bound=(Decimal("15"), False))
        result = multiply(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result < 45 (3 * 15)
        assert result.value.number_upper_bound == (Decimal("45"), False)

    def test_multiply_known_negative_with_refined_bounds(self) -> None:
        """Test: negative known * refined (bounds flip) (lines 129-139)."""
        a = N(-2)
        b = UnknownN(
            number_lower_bound=(Decimal("10"), True),
            number_upper_bound=(Decimal("20"), False),
        )
        result = multiply(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Bounds flip for negative multiplier
        # New lower: upper * -2 = 20 * -2 = -40 (exclusive)
        assert result.value.number_lower_bound == (Decimal("-40"), False)
        # New upper: lower * -2 = 10 * -2 = -20 (inclusive)
        assert result.value.number_upper_bound == (Decimal("-20"), True)

    def test_multiply_refined_with_known_positive(self) -> None:
        """Test: refined * positive known."""
        a = UnknownN(number_lower_bound=(Decimal("5"), True))
        b = N(4)
        result = multiply(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        assert result.value.number_lower_bound == (Decimal("20"), True)

    def test_multiply_by_zero_known(self) -> None:
        """Test: multiply by zero (early return in multiply function)."""
        a = UnknownN(number_lower_bound=(Decimal("10"), True))
        b = N(0)
        result = multiply(a, b)

        # Should return exactly zero, not unknown
        assert not result.is_unknown
        assert result.value == Decimal("0")


class TestDivisionRefinedUnknowns:
    """Test division with refined unknowns - covers lines 143-169."""

    def test_divide_refined_by_known_positive(self) -> None:
        """Test: refined / positive known (lines 147-157)."""
        a = UnknownN(number_lower_bound=(Decimal("20"), True))
        b = N(2)
        result = divide(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result >= 10 (20 / 2)
        assert result.value.number_lower_bound == (Decimal("10"), True)

    def test_divide_refined_by_known_positive_upper_bound(self) -> None:
        """Test: refined / positive known with upper bound (lines 153-157)."""
        a = UnknownN(number_upper_bound=(Decimal("100"), False))
        b = N(5)
        result = divide(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Result < 20 (100 / 5)
        assert result.value.number_upper_bound == (Decimal("20"), False)

    def test_divide_refined_by_known_negative(self) -> None:
        """Test: refined / negative known (bounds flip) (lines 158-168)."""
        a = UnknownN(
            number_lower_bound=(Decimal("10"), True),
            number_upper_bound=(Decimal("20"), True),
        )
        b = N(-2)
        result = divide(a, b)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Bounds flip for negative divisor
        # New lower: upper / -2 = 20 / -2 = -10
        assert result.value.number_lower_bound == (Decimal("-10"), True)
        # New upper: lower / -2 = 10 / -2 = -5
        assert result.value.number_upper_bound == (Decimal("-5"), True)

    def test_divide_by_zero_with_unknown(self) -> None:
        """Test: division by zero still raises error even with unknowns."""
        a = UnknownN(number_lower_bound=(Decimal("10"), True))
        b = N(0)
        with pytest.raises(CtyFunctionError, match="divide by zero"):
            divide(a, b)


class TestNegateRefinedUnknowns:
    """Test negate with refined unknowns - covers lines 263-280."""

    def test_negate_refined_with_both_bounds(self) -> None:
        """Test: negate refined unknown (bounds swap and flip sign)."""
        a = UnknownN(
            number_lower_bound=(Decimal("5"), True),
            number_upper_bound=(Decimal("10"), False),
        )
        result = negate(a)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Lower becomes -upper: -10 (exclusive)
        assert result.value.number_lower_bound == (Decimal("-10"), False)
        # Upper becomes -lower: -5 (inclusive)
        assert result.value.number_upper_bound == (Decimal("-5"), True)

    def test_negate_refined_only_lower(self) -> None:
        """Test: negate with only lower bound."""
        a = UnknownN(number_lower_bound=(Decimal("7"), False))
        result = negate(a)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Only upper bound in result: -7 (exclusive)
        assert result.value.number_upper_bound == (Decimal("-7"), False)
        assert result.value.number_lower_bound is None

    def test_negate_refined_only_upper(self) -> None:
        """Test: negate with only upper bound."""
        a = UnknownN(number_upper_bound=(Decimal("15"), True))
        result = negate(a)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Only lower bound in result: -15 (inclusive)
        assert result.value.number_lower_bound == (Decimal("-15"), True)
        assert result.value.number_upper_bound is None

    def test_negate_unrefined_unknown(self) -> None:
        """Test: negate unknown without refinements."""
        a = UnknownN()
        result = negate(a)

        assert result.is_unknown
        # Should return plain unknown, not refined
        assert not isinstance(result.value, RefinedUnknownValue)


class TestAbsRefinedUnknowns:
    """Test abs_fn with refined unknowns - covers lines 292-317."""

    def test_abs_refined_all_positive(self) -> None:
        """Test: abs(refined) where lower >= 0 (returns input unchanged)."""
        a = UnknownN(
            number_lower_bound=(Decimal("5"), True),
            number_upper_bound=(Decimal("10"), False),
        )
        result = abs_fn(a)

        assert result.is_unknown
        # Should return the input unchanged
        assert result.value == a.value

    def test_abs_refined_all_negative(self) -> None:
        """Test: abs(refined) where upper <= 0 (flip both bounds)."""
        a = UnknownN(
            number_lower_bound=(Decimal("-10"), True),
            number_upper_bound=(Decimal("-5"), False),
        )
        result = abs_fn(a)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Lower: -upper = -(-5) = 5 (exclusive)
        assert result.value.number_lower_bound == (Decimal("5"), False)
        # Upper: -lower = -(-10) = 10 (inclusive)
        assert result.value.number_upper_bound == (Decimal("10"), True)

    def test_abs_refined_crosses_zero(self) -> None:
        """Test: abs(refined) where range crosses zero (lines 304-308)."""
        a = UnknownN(
            number_lower_bound=(Decimal("-15"), True),
            number_upper_bound=(Decimal("10"), False),
        )
        result = abs_fn(a)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # Lower becomes 0 (inclusive)
        assert result.value.number_lower_bound == (Decimal("0"), True)
        # Upper becomes max(abs(-15), abs(10)) = 15
        assert result.value.number_upper_bound == (Decimal("15"), True)

    def test_abs_refined_only_lower_positive(self) -> None:
        """Test: abs with only lower bound >= 0 (lines 309-310)."""
        a = UnknownN(number_lower_bound=(Decimal("8"), True))
        result = abs_fn(a)

        assert result.is_unknown
        # Should return unchanged
        assert result.value == a.value

    def test_abs_refined_only_upper_negative(self) -> None:
        """Test: abs with only upper bound <= 0 (lines 311-312)."""
        a = UnknownN(number_upper_bound=(Decimal("-3"), False))
        result = abs_fn(a)

        assert result.is_unknown
        assert isinstance(result.value, RefinedUnknownValue)
        # New lower: -upper = 3 (exclusive)
        assert result.value.number_lower_bound == (Decimal("3"), False)


class TestEdgeCases:
    """Additional edge cases for comprehensive mutation testing."""

    def test_add_unrefined_unknowns(self) -> None:
        """Test: adding two plain unknowns returns plain unknown."""
        a = UnknownN()
        b = UnknownN()
        result = add(a, b)

        assert result.is_unknown
        # Should return plain unknown (no refinements)
        assert not isinstance(result.value, RefinedUnknownValue)

    def test_multiply_refined_by_zero_boundary(self) -> None:
        """Test: multiply when known_val equals POSITIVE_BOUNDARY."""
        # This tests the boundaries of the conditionals in multiply
        a = N(0)  # Exactly at zero boundary
        b = UnknownN(number_lower_bound=(Decimal("10"), True))
        result = multiply(a, b)

        # Should return zero (early exit in multiply)
        assert not result.is_unknown
        assert result.value == Decimal("0")

    def test_type_errors_with_refined_unknowns(self) -> None:
        """Test: type errors still raised for refined unknowns."""
        a = UnknownN(number_lower_bound=(Decimal("5"), True))
        b = CtyString().validate("not a number")

        with pytest.raises(CtyFunctionError):
            add(a, b)

    def test_null_propagation_with_refined_unknowns(self) -> None:
        """Test: null values propagate to unknown even with refinements."""
        a = CtyValue.null(CtyNumber())
        b = UnknownN(number_lower_bound=(Decimal("10"), True))
        result = add(a, b)

        assert result.is_unknown
        # Null + refined = plain unknown (not refined)


# 🌊🪢🔚
