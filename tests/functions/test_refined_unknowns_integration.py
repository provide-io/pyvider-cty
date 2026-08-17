#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""TDD Test Suite for Standard Library Functions with Refined Unknowns.

This suite defines the expected behavior for functions when they operate on
refined unknown values. The goal is for functions to leverage the refinement
constraints to produce a more precise result (i.e., a known value) where possible."""

from decimal import Decimal

from pyvider.cty import (
    CtyList,
    CtyNumber,
    CtyString,
    CtyValue,
)
from pyvider.cty.functions import (
    add,
    greater_than,
    length,
    less_than,
    max_fn,
    min_fn,
    multiply,
)
from pyvider.cty.values.markers import RefinedUnknownValue


# Helper for creating a refined unknown number value
def refined_unknown_num(
    lower_bound: tuple[Decimal, bool] | None = None,
    upper_bound: tuple[Decimal, bool] | None = None,
) -> CtyValue:
    return CtyValue.unknown(
        CtyNumber(),
        value=RefinedUnknownValue(number_lower_bound=lower_bound, number_upper_bound=upper_bound),
    )


# Helper for creating a refined unknown list value
def refined_unknown_list(lower_bound: int | None = None, upper_bound: int | None = None) -> CtyValue:
    return CtyValue.unknown(
        CtyList(element_type=CtyString()),
        value=RefinedUnknownValue(
            collection_length_lower_bound=lower_bound,
            collection_length_upper_bound=upper_bound,
        ),
    )


class TestRefinedUnknownsIntegration:
    """Tests that standard functions correctly use refinement data."""

    def test_max_fn_defers_to_an_unknown_however_refined(self) -> None:
        """Until 2026-08-17 this asserted `max(unknown < 10, 20)` is `20`.

        go-cty's `MaxFunc` variadic parameter sets only `AllowDynamicType`
        (`stdlib/number.go:354`) -- not `AllowUnknown` -- so the framework
        returns an unknown of the declared return type without calling `Impl`,
        and no refinement is consulted. The old answer was sound but is not
        go-cty's, and Terraform reports "known after apply" here. The ordering
        comparisons below keep their bound-aware answers, because go-cty
        consults the ranges there (`value_ops.go:1367`).
        """
        unknown_lt_10 = refined_unknown_num(upper_bound=(Decimal("10"), False))
        known_20 = CtyNumber().validate(20)
        result = max_fn(unknown_lt_10, known_20)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())

    def test_min_fn_defers_to_an_unknown_however_refined(self) -> None:
        """Until 2026-08-17 this asserted `min(unknown > 100, 50)` is `50`.

        Same declaration as `max` above: `MinFunc`'s variadic parameter does not
        admit an unknown either (`stdlib/number.go:328`).
        """
        unknown_gt_100 = refined_unknown_num(lower_bound=(Decimal("100"), False))
        known_50 = CtyNumber().validate(50)
        result = min_fn(unknown_gt_100, known_50)
        assert result.is_unknown is True
        assert result.type.equal(CtyNumber())

    def test_less_than_with_refined_unknown(self) -> None:
        # An unknown number that is definitely less than 10
        unknown_lt_10 = refined_unknown_num(upper_bound=(Decimal("10"), False))
        known_20 = CtyNumber().validate(20)
        # (unknown < 10) < 20 should be True.
        result = less_than(unknown_lt_10, known_20)
        assert result.is_unknown is False
        assert result.value is True

    def test_greater_than_with_refined_unknown(self) -> None:
        # An unknown number that is definitely greater than 100
        unknown_gt_100 = refined_unknown_num(lower_bound=(Decimal("100"), False))
        known_50 = CtyNumber().validate(50)
        # (unknown > 100) > 50 should be True.
        result = greater_than(unknown_gt_100, known_50)
        assert result.is_unknown is False
        assert result.value is True

    def test_length_with_refined_unknown_list(self) -> None:
        # An unknown list that is known to have exactly 3 elements.
        unknown_list_len_3 = refined_unknown_list(lower_bound=3, upper_bound=3)
        result = length(unknown_list_len_3)
        assert result.is_unknown is False
        assert result.value == 3

    def test_length_with_unrefined_unknown_list_is_unknown(self) -> None:
        # An unknown list with an unknown length.
        unknown_list = CtyValue.unknown(CtyList(element_type=CtyString()))
        result = length(unknown_list)
        assert result.is_unknown is True


class TestRefinedUnknownsNumericIntegration:
    """The arithmetic functions defer to an unknown; they do not narrow it.

    Until 2026-08-17 this class asserted bound propagation -- `add(>0, >0)`
    is `>0`, `multiply([10,20], 2)` is `[20,40]`. go-cty's arithmetic function
    parameters do not set `AllowUnknown` (`stdlib/number.go`), so the framework
    returns an unknown of the return type without calling the implementation
    (`function.go:314`) and no bound arithmetic happens. go-cty does propagate
    bounds -- but on `cty.Value`'s operators, a surface this package does not
    have; the stdlib functions never see the refinement.
    """

    def test_add_defers_to_an_unknown_however_refined(self) -> None:
        unknown_pos_1 = refined_unknown_num(lower_bound=(Decimal("0"), False))
        unknown_pos_2 = refined_unknown_num(lower_bound=(Decimal("0"), False))

        result = add(unknown_pos_1, unknown_pos_2)

        assert result.is_unknown
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_multiply_defers_to_an_unknown_however_refined(self) -> None:
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        known_2 = CtyNumber().validate(2)

        result = multiply(unknown_10_20, known_2)

        assert result.is_unknown
        assert result.type.equal(CtyNumber())
        assert result.value == RefinedUnknownValue(is_known_null=False)


class TestRefinedUnknownsComparisonCoverage:
    """Tests for uncovered branches in comparison functions."""

    def test_compare_two_refined_unknowns_can_resolve(self) -> None:
        """
        Tests that comparing two refined unknowns can resolve to a known bool.
        e.g., (unknown < 10) < (unknown > 20) must be True.
        """
        unknown_lt_10 = refined_unknown_num(upper_bound=(Decimal("10"), False))
        unknown_gt_20 = refined_unknown_num(lower_bound=(Decimal("20"), False))

        result = less_than(unknown_lt_10, unknown_gt_20)
        assert result.is_unknown is False
        assert result.value is True

    def test_compare_refined_unknown_with_value_inside_range_is_unknown(self) -> None:
        """
        Tests that comparing a refined unknown with a known value inside its
        bounds correctly results in an unknown boolean.
        """
        # An unknown number between 10 and 20.
        unknown_10_20 = refined_unknown_num(
            lower_bound=(Decimal("10"), True), upper_bound=(Decimal("20"), True)
        )
        known_15 = CtyNumber().validate(15)

        result = less_than(unknown_10_20, known_15)
        assert result.is_unknown is True


# 🌊🪢🔚
