#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""and/or/not against `bool.go`, and range against `sequence.go`.

The truth tables and the ordinary range shapes are pinned against the live
oracle in the compatibility sweep. What is here is what the oracle harness
cannot express: unknowns, nulls and marks.
"""

from decimal import Decimal

import pytest

from pyvider.cty import CtyBool, CtyDynamic, CtyList, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import and_fn, not_fn, or_fn, range_fn

TRUE = CtyBool().validate(True)
FALSE = CtyBool().validate(False)
UNKNOWN = CtyValue.unknown(CtyBool())


def N(v: object) -> CtyValue[Decimal]:
    return CtyNumber().validate(v)


class TestLogicalOperators:
    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (TRUE, TRUE, True),
            (TRUE, FALSE, False),
            (FALSE, TRUE, False),
            (FALSE, FALSE, False),
        ],
    )
    def test_and(self, a: CtyValue[bool], b: CtyValue[bool], expected: bool) -> None:  # noqa: FBT001
        assert and_fn(a, b).value is expected

    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (TRUE, TRUE, True),
            (TRUE, FALSE, True),
            (FALSE, TRUE, True),
            (FALSE, FALSE, False),
        ],
    )
    def test_or(self, a: CtyValue[bool], b: CtyValue[bool], expected: bool) -> None:  # noqa: FBT001
        assert or_fn(a, b).value is expected

    def test_not(self) -> None:
        assert not_fn(TRUE).value is False
        assert not_fn(FALSE).value is True


class TestLogicalOperatorsDoNotShortCircuit:
    """`and(unknown, false)` is unknown, not false.

    go-cty's function framework returns an unknown result for any unknown
    argument before the implementation runs, so it never gets the chance to
    notice that one known operand already settles the answer. Matching that
    matters because a plan that answered `false` here and `unknown` in Terraform
    would disagree with itself.
    """

    @pytest.mark.parametrize(("a", "b"), [(UNKNOWN, FALSE), (FALSE, UNKNOWN), (UNKNOWN, UNKNOWN)])
    def test_and_stays_unknown(self, a: CtyValue[bool], b: CtyValue[bool]) -> None:
        assert and_fn(a, b).is_unknown

    @pytest.mark.parametrize(("a", "b"), [(UNKNOWN, TRUE), (TRUE, UNKNOWN), (UNKNOWN, UNKNOWN)])
    def test_or_stays_unknown(self, a: CtyValue[bool], b: CtyValue[bool]) -> None:
        assert or_fn(a, b).is_unknown

    def test_not_of_unknown(self) -> None:
        assert not_fn(UNKNOWN).is_unknown


class TestLogicalOperatorsReject:
    @pytest.mark.parametrize("bad", [CtyString().validate("true"), CtyNumber().validate(1)])
    def test_a_non_bool_argument(self, bad: CtyValue[object]) -> None:
        """go-cty does not coerce here: "true" is a string, not a bool."""
        with pytest.raises(CtyFunctionError, match="bool required"):
            not_fn(bad)
        with pytest.raises(CtyFunctionError, match="bool required"):
            and_fn(TRUE, bad)

    def test_a_null_argument(self) -> None:
        """None of these parameters is declared AllowNull, so go-cty refuses.

        This used to note that "several older functions in this package return
        unknown for a null instead". They no longer do: the policy moved to the
        framework, and 109 of 138 argument positions changed with it.
        """
        with pytest.raises(CtyFunctionError, match="must not be null"):
            not_fn(CtyValue.null(CtyBool()))
        with pytest.raises(CtyFunctionError, match="must not be null"):
            or_fn(TRUE, CtyValue.null(CtyBool()))

    def test_a_dynamic_wrapper_is_seen_through(self) -> None:
        assert not_fn(CtyDynamic().validate(True)).value is False

    def test_an_unsettled_dynamic_is_unknown_rather_than_unwrapped(self) -> None:
        """The unwrap loop needs both of its conditions.

        A mutation run turned its `and` into an `or` and nothing failed, because
        no test supplied a value that satisfies one condition and not the other.
        This is that value: its type is dynamic, but there is no inner CtyValue
        to descend into, so the loop must not run.
        """
        result = not_fn(CtyValue.unknown(CtyDynamic()))

        assert result.is_unknown
        assert result.type == CtyBool()


class TestLogicalOperatorMarks:
    def test_marks_propagate(self) -> None:
        assert "secret" in and_fn(TRUE.with_marks({"secret"}), TRUE).marks
        assert "secret" in not_fn(TRUE.with_marks({"secret"})).marks


class TestRangeDefaulting:
    """One and two arguments infer the step from the direction of travel."""

    def test_one_argument_counts_up_from_zero(self) -> None:
        assert range_fn(N(3)).raw_value == [0, 1, 2]

    def test_a_negative_end_counts_down(self) -> None:
        assert range_fn(N(-3)).raw_value == [0, -1, -2]

    def test_two_arguments(self) -> None:
        assert range_fn(N(1), N(5)).raw_value == [1, 2, 3, 4]

    def test_two_descending_arguments_step_by_minus_one(self) -> None:
        assert range_fn(N(5), N(1)).raw_value == [5, 4, 3, 2]

    def test_three_arguments(self) -> None:
        assert range_fn(N(1), N(5), N(2)).raw_value == [1, 3]
        assert range_fn(N(5), N(1), N(-2)).raw_value == [5, 3]

    def test_a_fractional_step(self) -> None:
        assert range_fn(N(0), N("1"), N("0.25")).raw_value == [
            Decimal("0"),
            Decimal("0.25"),
            Decimal("0.50"),
            Decimal("0.75"),
        ]

    def test_an_empty_range(self) -> None:
        empty = range_fn(N(0))

        assert empty.type == CtyList(element_type=CtyNumber())
        assert empty.raw_value == []


class TestRangeRejects:
    def test_no_arguments(self) -> None:
        with pytest.raises(CtyFunctionError, match="one, two, or three"):
            range_fn()

    def test_four_arguments(self) -> None:
        with pytest.raises(CtyFunctionError, match="one, two, or three"):
            range_fn(N(1), N(2), N(3), N(4))

    def test_a_step_of_zero(self) -> None:
        """go-cty's own guard for this never fires.

        It tests `step == cty.Zero`, comparing two structs that hold different
        big.Float pointers, so a zero step loops until the 1024 cap and reports
        that instead. Refused cleanly here -- both implementations refuse, only
        the message differs -- the same call already made for `indent`.
        """
        with pytest.raises(CtyFunctionError, match="step must not be zero"):
            range_fn(N(0), N(10), N(0))

    def test_a_step_pointing_away_from_the_end(self) -> None:
        with pytest.raises(CtyFunctionError, match="end must be less than start"):
            range_fn(N(1), N(5), N(-1))
        with pytest.raises(CtyFunctionError, match="end must be greater than start"):
            range_fn(N(5), N(1), N(1))

    def test_more_than_1024_values(self) -> None:
        """The result has to be buffered, so go-cty caps it rather than trusting the caller."""
        with pytest.raises(CtyFunctionError, match="more than 1024 values"):
            range_fn(N(0), N(2000))

    def test_a_non_number_argument(self) -> None:
        with pytest.raises(CtyFunctionError, match="must be numbers"):
            range_fn(CtyString().validate("3"))

    def test_a_null_argument(self) -> None:
        # The refusal now comes from the framework rather than from `range`'s
        # own type check, so the message names the argument instead.
        with pytest.raises(CtyFunctionError, match="must not be null"):
            range_fn(CtyValue.null(CtyNumber()))

    def test_an_unknown_argument_gives_an_unknown_list(self) -> None:
        result = range_fn(CtyValue.unknown(CtyNumber()))

        assert result.is_unknown
        assert result.type == CtyList(element_type=CtyNumber())


# 🌊🪢🔚
