#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Comparison functions given refined unknown values.

The four ordering comparisons can answer definitely from the refinement bounds,
which is go-cty's behaviour too (`value_ops.go:1367`): `LessThan` and
`GreaterThan` consult both operands' `Range` before giving up. What is covered
here is every shape those bounds can take -- one side known, both refined,
bounds that touch, bounds that overlap, and the inclusive/exclusive flag on each
of them.

`min` and `max` are the opposite case and the class below says why: go-cty's
parameters do not admit an unknown at all, so no bound can be consulted."""

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
    """An unknown argument makes `min`/`max` undecided, however it is refined.

    Until 2026-08-17 these asserted the opposite for the cases a bound settles:
    `max(50, unknown <= 40)` answered `50`, and `min(unknown >= 10)` answered
    the argument back with its refinement intact.

    go-cty's `MinFunc` and `MaxFunc` declare one variadic parameter that sets
    only `AllowDynamicType` (`stdlib/number.go:328`, `:354`) -- no
    `AllowUnknown` -- so the function framework returns an unknown of the
    declared return type without ever calling `Impl`, and the body it guards is
    written on the assumption that every argument is a known number
    (`:335`, `:361`). There is no counterpart in go-cty to a bound-aware
    `min`/`max` at all.

    This is a *loss of precision*, and a deliberate one: the previous answers
    were sound, just not go-cty's, and Terraform would report "known after
    apply" where this package reported a number. The ordering comparisons keep
    their bound-aware answers, because there go-cty consults the ranges too
    (`value_ops.go:1367`).
    """

    def test_max_defers_even_when_a_bound_settles_the_answer(self) -> None:
        known = N(50)
        refined = UnknownN(number_upper_bound=(Decimal("40"), True))

        result = max_fn(known, refined)

        assert result.is_unknown
        assert result.type.equal(CtyNumber())

    def test_max_refined_could_exceed_known(self) -> None:
        known = N(30)
        refined = UnknownN(number_upper_bound=(Decimal("50"), True))

        assert max_fn(known, refined).is_unknown

    def test_min_defers_even_when_a_bound_settles_the_answer(self) -> None:
        known = N(5)
        refined = UnknownN(number_lower_bound=(Decimal("10"), True))

        result = min_fn(known, refined)

        assert result.is_unknown
        assert result.type.equal(CtyNumber())

    def test_min_refined_could_be_below_known(self) -> None:
        known = N(20)
        refined = UnknownN(number_lower_bound=(Decimal("5"), True))

        assert min_fn(known, refined).is_unknown

    def test_max_with_several_unknowns_is_undecided(self) -> None:
        known = N(50)
        refined1 = UnknownN(number_upper_bound=(Decimal("40"), True))
        refined2 = UnknownN(number_lower_bound=(Decimal("45"), True))

        assert max_fn(known, refined1, refined2).is_unknown

    def test_the_short_circuit_discards_the_argument_refinement(self) -> None:
        """The result is an unknown *number*, not the argument handed back.

        go-cty's short-circuit is `cty.UnknownVal(retType)` refined only by the
        function's own `RefineResult`, which here is `refineNonNull`
        (`function.go:281`). The argument's bounds describe the argument, and
        `min` of one number happens to coincide with it -- but `min` of two
        would not, so the framework cannot carry them across in general and
        go-cty does not.
        """
        refined = UnknownN(number_lower_bound=(Decimal("10"), True))

        result = min_fn(refined)

        assert result.is_unknown
        assert result.type.equal(CtyNumber())
        assert result.value != refined.value

    def test_max_no_known_args_only_unknowns(self) -> None:
        refined1 = UnknownN(number_lower_bound=(Decimal("10"), True))
        refined2 = UnknownN(number_upper_bound=(Decimal("50"), True))

        assert max_fn(refined1, refined2).is_unknown


class TestEqualityWithRefinedUnknowns:
    """Equality consults the refinement bounds, as go-cty's does.

    These asserted "always returns unknown" until `Value.Range` landed, which is
    what the bounds are *for*: an unknown constrained below 20 is definitely not
    25, however it resolves. Only an exclusion is usable -- passing the bounds is
    not equality -- so the within-bounds case below is still undecided.
    """

    def test_a_candidate_inside_the_bounds_stays_unknown(self) -> None:
        """15 satisfies `>= 10`, so it is not ruled out -- and not confirmed."""
        refined = UnknownN(number_lower_bound=(Decimal("10"), True))

        assert equal(refined, N(15)).is_unknown

    def test_a_candidate_the_bounds_exclude_is_definitely_unequal(self) -> None:
        """`< 20` rules out 25, so `not_equal` is definitely true.

        Note the bound is *exclusive*, which this also exercises: the pair
        `(20, False)` means strictly less than 20.
        """
        refined = UnknownN(number_upper_bound=(Decimal("20"), False))

        result = not_equal(refined, N(25))

        assert not result.is_unknown
        assert result.value is True

    def test_the_exclusive_bound_itself_is_excluded(self) -> None:
        """`< 20` means 20 is not a candidate either."""
        refined = UnknownN(number_upper_bound=(Decimal("20"), False))

        assert equal(refined, N(20)).value is False


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

    def test_max_refuses_null_values(self) -> None:
        """These used to return a null, and to *filter nulls out*.

        `min(null, 10, 5)` answered 5, which is a computed result from data one
        of whose members was definitely absent. go-cty declares neither
        parameter AllowNull and refuses the call.
        """
        with pytest.raises(CtyFunctionError):
            max_fn(CtyValue.null(CtyNumber()), CtyValue.null(CtyNumber()))

    def test_min_refuses_a_null_among_known_values(self) -> None:
        with pytest.raises(CtyFunctionError):
            min_fn(CtyValue.null(CtyNumber()), N(10), N(5))

    def test_max_refuses_a_non_number(self) -> None:
        """The refusal now comes from the parameter, so its wording changed.

        Until 2026-08-17 this matched "same type", from a body that accepted any
        homogeneous argument list and so allowed strings. go-cty's variadic
        parameter is `cty.Number` (`stdlib/number.go:330`), and the framework
        reports non-conformance per argument by position rather than as a
        statement about the list as a whole.
        """
        with pytest.raises(CtyFunctionError, match="number"):
            max_fn(N(10), S("string"))


# 🌊🪢🔚
