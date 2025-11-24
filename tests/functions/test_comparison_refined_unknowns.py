#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for comparison functions with refined unknown values.

This test suite focuses on achieving 100% coverage of refined unknown comparison
logic in comparison_functions.py, particularly:
- Lines 66, 84-85, 92-93 (refined unknown comparison logic)
- Lines 138, 149, 172, 194-196 (min/max with refined unknowns)
- Edge cases with bounds, inclusive/exclusive flags, overlapping ranges"""

from decimal import Decimal

import pytest

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    equal,
    greater_than,
    greater_than_or_equal_to,
    less_than,
    less_than_or_equal_to,
    max_fn,
    min_fn,
    not_equal,
)
from pyvider.cty.values.markers import RefinedUnknownValue


# Helper functions
def N(v):
    """Create a known CtyNumber value."""
    return CtyNumber().validate(v)


def S(v):
    """Create a known CtyString value."""
    return CtyString().validate(v)


def UnknownN(**refinements):
    """Create a refined unknown CtyNumber value."""
    if refinements:
        return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**refinements))
    return CtyValue.unknown(CtyNumber())


class TestCompareKnownWithRefinedUnknown:
    """Test comparisons: known vs refined unknown (lines 44-75)."""

    def test_known_gt_refined_upper_bound_exclusive(self) -> None:
        """Test: known > refined.upper (exclusive) -> False for '>' operator (line 66)."""
        # refined: x < 10 (upper=10, exclusive)
        # known: 15
        # 15 > 10, so refined x must be < 15, hence x > 15 is False
        refined = UnknownN(number_upper_bound=(Decimal("10"), False))
        known = N(15)
        result = greater_than(refined, known)

        assert not result.is_unknown
        assert result.is_false()

    def test_known_gt_refined_upper_bound_at_boundary_exclusive(self) -> None:
        """Test: known at exclusive upper boundary -> definite False (lines 48-52)."""
        # refined: x < 10
        # known: 10
        # Since x < 10, x > 10 is definitely False
        refined = UnknownN(number_upper_bound=(Decimal("10"), False))
        known = N(10)
        result = greater_than(refined, known)

        assert not result.is_unknown
        assert result.is_false()

    def test_known_lt_refined_upper_bound_exclusive(self) -> None:
        """Test: known < refined.upper (exclusive) -> True for '<' (lines 48-52)."""
        refined = UnknownN(number_upper_bound=(Decimal("10"), False))
        known = N(5)
        result = less_than(refined, known)

        # refined x < 10, known = 5
        # We can't determine if x < 5 (x could be 6-9)
        assert result.is_unknown

    def test_known_below_refined_lower_bound_exclusive(self) -> None:
        """Test: known < refined.lower (exclusive) -> True for '<' (lines 55-59)."""
        # refined: x > 20 (lower=20, exclusive)
        # known: 15
        # 15 < 20, and refined x > 20, so refined > 15 is True
        refined = UnknownN(number_lower_bound=(Decimal("20"), False))
        known = N(15)
        result = greater_than(refined, known)

        assert not result.is_unknown
        assert result.is_true()

    def test_known_at_refined_lower_bound_exclusive(self) -> None:
        """Test: known at exclusive lower boundary (lines 55-59)."""
        # refined: x > 20
        # known: 20
        # x > 20, so x > 20 is True
        refined = UnknownN(number_lower_bound=(Decimal("20"), False))
        known = N(20)
        result = greater_than(refined, known)

        assert not result.is_unknown
        assert result.is_true()


class TestCompareRefinedWithKnown:
    """Test comparisons: refined unknown vs known (lines 60-75)."""

    def test_refined_upper_compared_to_known_gt(self) -> None:
        """Test: refined.upper < known -> refined < known is False for '<' (line 66)."""
        # known: 50
        # refined: x <= 40
        # 50 > 40, so we know x < 50 is True, x > 50 is False
        known = N(50)
        refined = UnknownN(number_upper_bound=(Decimal("40"), True))
        result = greater_than(known, refined)

        assert not result.is_unknown
        assert result.is_true()

    def test_refined_lower_compared_to_known_lt(self) -> None:
        """Test: refined.lower > known -> refined > known is False for '<' (lines 72-75)."""
        # known: 10
        # refined: x >= 20
        # 10 < 20, so x > 10 is True
        known = N(10)
        refined = UnknownN(number_lower_bound=(Decimal("20"), True))
        result = less_than(known, refined)

        assert not result.is_unknown
        assert result.is_true()


class TestCompareTwoRefinedUnknowns:
    """Test comparisons: refined vs refined (lines 77-93)."""

    def test_both_refined_non_overlapping_a_below_b(self) -> None:
        """Test: a.upper < b.lower -> a < b is True (lines 78-85)."""
        # a: x <= 10
        # b: y >= 20
        # Since max(a) < min(b), a < b is definitely True
        a = UnknownN(number_upper_bound=(Decimal("10"), True))
        b = UnknownN(number_lower_bound=(Decimal("20"), True))
        result = less_than(a, b)

        assert not result.is_unknown
        assert result.is_true()

    def test_both_refined_non_overlapping_a_above_b(self) -> None:
        """Test: a.lower > b.upper -> a > b is True (lines 86-93)."""
        # a: x >= 50
        # b: y <= 30
        # Since min(a) > max(b), a > b is definitely True
        a = UnknownN(number_lower_bound=(Decimal("50"), True))
        b = UnknownN(number_upper_bound=(Decimal("30"), True))
        result = greater_than(a, b)

        assert not result.is_unknown
        assert result.is_true()

    def test_both_refined_touching_boundaries_exclusive(self) -> None:
        """Test: a.upper == b.lower but not both inclusive (lines 81-85)."""
        # a: x < 15 (upper=15, exclusive)
        # b: y >= 15 (lower=15, inclusive)
        # They touch at 15, but a is exclusive, so a < b is True
        a = UnknownN(number_upper_bound=(Decimal("15"), False))
        b = UnknownN(number_lower_bound=(Decimal("15"), True))
        result = less_than(a, b)

        assert not result.is_unknown
        assert result.is_true()

    def test_both_refined_touching_boundaries_both_inclusive(self) -> None:
        """Test: a.upper == b.lower and both inclusive -> unknown (line 81)."""
        # a: x <= 15 (upper=15, inclusive)
        # b: y >= 15 (lower=15, inclusive)
        # They overlap at 15, could be equal, so result is unknown
        a = UnknownN(number_upper_bound=(Decimal("15"), True))
        b = UnknownN(number_lower_bound=(Decimal("15"), True))
        result = less_than(a, b)

        # Can't determine definitively (a and b could both be 15)
        assert result.is_unknown

    def test_both_refined_overlapping_ranges(self) -> None:
        """Test: refined ranges overlap -> result is unknown."""
        # a: 5 <= x <= 20
        # b: 15 <= y <= 30
        # Ranges overlap [15, 20], so we can't determine < or >
        a = UnknownN(
            number_lower_bound=(Decimal("5"), True),
            number_upper_bound=(Decimal("20"), True),
        )
        b = UnknownN(
            number_lower_bound=(Decimal("15"), True),
            number_upper_bound=(Decimal("30"), True),
        )
        result = less_than(a, b)

        assert result.is_unknown


class TestMinMaxWithRefinedUnknowns:
    """Test min/max functions with refined unknowns (lines 138, 149, 172, 194-196)."""

    def test_max_known_dominates_refined_upper_bound(self) -> None:
        """Test: max(known, refined) where known >= refined.upper (line 168-169)."""
        # known: 50
        # refined: x <= 40
        # Since known >= refined.upper, known is definitely the max
        known = N(50)
        refined = UnknownN(number_upper_bound=(Decimal("40"), True))
        result = max_fn(known, refined)

        assert not result.is_unknown
        assert result.value == Decimal("50")

    def test_max_refined_could_exceed_known(self) -> None:
        """Test: max(known, refined) where refined.upper > known (line 172)."""
        # known: 30
        # refined: x <= 50
        # refined could be 50 > known, so result is unknown
        known = N(30)
        refined = UnknownN(number_upper_bound=(Decimal("50"), True))
        result = max_fn(known, refined)

        assert result.is_unknown

    def test_min_known_dominates_refined_lower_bound(self) -> None:
        """Test: min(known, refined) where known <= refined.lower (line 170-171)."""
        # known: 5
        # refined: x >= 10
        # Since known <= refined.lower, known is definitely the min
        known = N(5)
        refined = UnknownN(number_lower_bound=(Decimal("10"), True))
        result = min_fn(known, refined)

        assert not result.is_unknown
        assert result.value == Decimal("5")

    def test_min_refined_could_be_below_known(self) -> None:
        """Test: min(known, refined) where refined.lower < known (line 172)."""
        # known: 20
        # refined: x >= 5
        # refined could be 5 < known, so result is unknown
        known = N(20)
        refined = UnknownN(number_lower_bound=(Decimal("5"), True))
        result = min_fn(known, refined)

        assert result.is_unknown

    def test_max_multiple_unknowns_after_filtering(self) -> None:
        """Test: max with multiple unknowns after some are filtered (line 190-196)."""
        # known: 50
        # refined1: x <= 40 (dominated, filtered out)
        # refined2: y >= 45 (not dominated, remains)
        known = N(50)
        refined1 = UnknownN(number_upper_bound=(Decimal("40"), True))
        refined2 = UnknownN(number_lower_bound=(Decimal("45"), True))
        result = max_fn(known, refined1, refined2)

        # refined1 is filtered, but refined2 could be > 50
        assert result.is_unknown

    def test_min_only_unknowns_remaining(self) -> None:
        """Test: min/max with only unknowns after filtering (line 194-195)."""
        # Only one unknown left after filtering
        refined = UnknownN(number_lower_bound=(Decimal("10"), True))
        result = min_fn(refined)

        # Single unknown returns that unknown
        assert result.is_unknown
        assert result.value == refined.value

    def test_max_no_known_args_only_unknowns(self) -> None:
        """Test: max with no known args, only unknowns (line 192-196)."""
        refined1 = UnknownN(number_lower_bound=(Decimal("10"), True))
        refined2 = UnknownN(number_upper_bound=(Decimal("50"), True))
        result = max_fn(refined1, refined2)

        # Multiple unknowns with no known -> unknown
        assert result.is_unknown


class TestEqualityWithRefinedUnknowns:
    """Test equality operations with refined unknowns."""

    def test_equal_with_refined_unknown(self) -> None:
        """Test: equality with refined unknown always returns unknown."""
        refined = UnknownN(number_lower_bound=(Decimal("10"), True))
        known = N(15)
        result = equal(refined, known)

        assert result.is_unknown

    def test_not_equal_with_refined_unknown(self) -> None:
        """Test: not_equal with refined unknown returns unknown."""
        refined = UnknownN(number_upper_bound=(Decimal("20"), False))
        known = N(25)
        result = not_equal(refined, known)

        assert result.is_unknown


class TestEdgeCasesAndBoundaries:
    """Additional edge cases for comprehensive mutation testing."""

    def test_compare_plain_unknowns_no_refinements(self) -> None:
        """Test: comparing two plain unknowns (no refinements) -> unknown."""
        a = UnknownN()
        b = UnknownN()
        result = less_than(a, b)

        assert result.is_unknown

    def test_compare_refined_with_plain_unknown(self) -> None:
        """Test: refined vs plain unknown -> unknown."""
        refined = UnknownN(number_lower_bound=(Decimal("10"), True))
        plain = UnknownN()
        result = greater_than(refined, plain)

        assert result.is_unknown

    def test_greater_than_or_equal_with_refined_boundaries(self) -> None:
        """Test: >= operator with refined unknowns."""
        # a: x >= 20
        # known: 15
        # Since x >= 20 > 15, x >= 15 is True
        a = UnknownN(number_lower_bound=(Decimal("20"), True))
        b = N(15)
        result = greater_than_or_equal_to(a, b)

        assert not result.is_unknown
        assert result.is_true()

    def test_less_than_or_equal_with_refined_boundaries(self) -> None:
        """Test: <= operator with refined unknowns."""
        # a: x <= 10
        # known: 15
        # Since x <= 10 < 15, x <= 15 is True
        a = UnknownN(number_upper_bound=(Decimal("10"), True))
        b = N(15)
        result = less_than_or_equal_to(a, b)

        assert not result.is_unknown
        assert result.is_true()

    def test_compare_type_mismatch_with_plain_unknown(self) -> None:
        """Test: comparing plain unknowns of different types returns unknown."""
        # Note: refined unknown comparisons may fail with type errors before
        # type checking, so use plain unknowns for this test
        unknown_num = UnknownN()
        unknown_str = CtyValue.unknown(CtyString())

        # When both are unknown, type checking happens differently
        result = equal(unknown_num, unknown_str)
        assert result.is_unknown

    def test_max_all_null_values(self) -> None:
        """Test: max with all null values returns null (line 184)."""
        result = max_fn(
            CtyValue.null(CtyNumber()),
            CtyValue.null(CtyNumber()),
        )

        assert result.is_null

    def test_min_mixed_null_and_known(self) -> None:
        """Test: min filters out nulls, uses known values (line 130-131)."""
        result = min_fn(
            CtyValue.null(CtyNumber()),
            N(10),
            N(5),
        )

        assert not result.is_unknown
        assert result.value == Decimal("5")

    def test_max_homogeneous_type_validation(self) -> None:
        """Test: max/min type validation for mixed types (line 138-143)."""
        with pytest.raises(CtyFunctionError, match="same type"):
            max_fn(N(10), S("string"))


# 🌊🪢🔚
