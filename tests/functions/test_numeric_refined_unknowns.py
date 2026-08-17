#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""What the numeric stdlib functions answer for a *refined* unknown argument.

Until 2026-08-17 this file asserted that they narrowed one: that
`add(5, unknown >= 10)` came back as `unknown >= 15`, that
`abs(unknown in [-15, 10])` came back as `unknown in [0, 15]`, and so on across
`add`, `subtract`, `multiply`, `divide`, `negate` and `abs`. It does not, and
neither does go-cty.

The reason is one declared flag. `cty.Value.Add`, `Value.Multiply` and
`Value.Absolute` really do narrow a refined operand -- `value_ops.go:623`, `683`
and `802` -- but reaching that code needs the *function* to let an unknown
through to its implementation, and in `stdlib/number.go` no arithmetic function
does. `AllowUnknown: true` appears exactly four times in that file, on
`GreaterThanFunc` (208), `GreaterThanOrEqualToFunc` (233), `LessThanFunc` (258)
and `LessThanOrEqualToFunc` (283) -- the comparisons, which live in
`comparison_functions.py` and do still resolve from bounds. Every arithmetic
function short-circuits in `Function.Call` before `Impl` runs (`function.go:314`)
and returns `cty.UnknownVal(cty.Number)` carrying only `RefineResult`, which for
all twenty functions in the file is `refineNonNull`.

Verified against the live oracle rather than read off the source. Given a
refined unknown, `soup-go cty call` answers `{"is_known_null": false}` and
nothing else for `abs`, `add`, `negate` and `multiply` alike.

So the narrowing is not lost, it is in the wrong place: `cty.Value`'s arithmetic
operators are where go-cty keeps it, and this package has no equivalent surface
yet. The argument shapes the old tests drove are kept below, now asserting the
answer go-cty gives for each.
"""

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


def N(v):
    """Create a known CtyNumber value."""
    return CtyNumber().validate(v)


def UnknownN(**refinements):
    """Create a refined unknown CtyNumber value."""
    if refinements:
        return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**refinements))
    return CtyValue.unknown(CtyNumber())


def assert_only_not_null(result) -> None:
    """The whole answer go-cty gives: an unknown number, promised non-null.

    Asserted as the *complete* refinement rather than as "not null is present",
    so a bound that reappeared would fail here instead of passing unnoticed.
    """
    assert result.is_unknown
    assert isinstance(result.type, CtyNumber), "the short-circuit is typed by the return type"
    assert result.value == RefinedUnknownValue(is_known_null=False)


LOWER_10 = {"number_lower_bound": (Decimal("10"), True)}
UPPER_20 = {"number_upper_bound": (Decimal("20"), False)}
BOTH_10_20 = {**LOWER_10, "number_upper_bound": (Decimal("20"), True)}

# Every argument shape the narrowing tests used to drive, one per row.
CASES = [
    ("add(5, >=10)", lambda: add(N(5), UnknownN(**LOWER_10))),
    ("add(5, <20)", lambda: add(N(5), UnknownN(**UPPER_20))),
    ("add(>=10, 3)", lambda: add(UnknownN(**LOWER_10), N(3))),
    ("add(>=10, >=10)", lambda: add(UnknownN(**LOWER_10), UnknownN(**LOWER_10))),
    ("add([10,20], [10,20])", lambda: add(UnknownN(**BOTH_10_20), UnknownN(**BOTH_10_20))),
    ("add(unknown, unknown)", lambda: add(UnknownN(), UnknownN())),
    ("subtract([10,20], 5)", lambda: subtract(UnknownN(**BOTH_10_20), N(5))),
    ("subtract(50, <20)", lambda: subtract(N(50), UnknownN(**UPPER_20))),
    ("subtract(>=10, >=10)", lambda: subtract(UnknownN(**LOWER_10), UnknownN(**LOWER_10))),
    ("multiply(2, >=10)", lambda: multiply(N(2), UnknownN(**LOWER_10))),
    ("multiply([10,20], -2)", lambda: multiply(UnknownN(**BOTH_10_20), N(-2))),
    ("divide([10,20], 2)", lambda: divide(UnknownN(**BOTH_10_20), N(2))),
    ("divide([10,20], -2)", lambda: divide(UnknownN(**BOTH_10_20), N(-2))),
    ("negate([10,20])", lambda: negate(UnknownN(**BOTH_10_20))),
    ("negate(>=10)", lambda: negate(UnknownN(**LOWER_10))),
    ("negate(unknown)", lambda: negate(UnknownN())),
    ("abs([10,20])", lambda: abs_fn(UnknownN(**BOTH_10_20))),
    ("abs(>=10)", lambda: abs_fn(UnknownN(**LOWER_10))),
    ("abs(<20)", lambda: abs_fn(UnknownN(**UPPER_20))),
    (
        "abs([-15,10])",
        lambda: abs_fn(
            UnknownN(
                number_lower_bound=(Decimal("-15"), True),
                number_upper_bound=(Decimal("10"), False),
            )
        ),
    ),
    ("abs(unknown)", lambda: abs_fn(UnknownN())),
]


@pytest.mark.parametrize(("label", "call"), CASES, ids=[label for label, _ in CASES])
def test_an_unknown_operand_discards_its_refinements(label: str, call) -> None:
    """Each of these narrowed the result until 2026-08-17. See the module docstring."""
    assert_only_not_null(call())


class TestKnownArgumentsThatUsedToShortCircuit:
    """Two answers the old propagation reached without computing anything."""

    def test_multiplying_by_a_known_zero_is_still_unknown(self) -> None:
        """This asserted a known `0` until 2026-08-17.

        `cty.Value.Multiply` does answer zero for a zero factor, but only on the
        branch it takes when the *other* factor is unknown (`value_ops.go:679`) --
        and `MultiplyFunc` never reaches its implementation with an unknown
        argument, so that branch is unreachable through the function. Verified
        against go-cty: `multiply(0, unknown)` is an unknown number.

        The distinction is real rather than pedantic: the other factor could turn
        out to be an infinity, and `0 * Infinity` is an error, not zero.
        """
        assert_only_not_null(multiply(UnknownN(**LOWER_10), N(0)))
        assert_only_not_null(multiply(N(0), UnknownN()))

    def test_dividing_a_refined_unknown_by_zero_is_unknown_not_an_error(self) -> None:
        """This asserted a "divide by zero" refusal until 2026-08-17.

        Neither half of that survives: go-cty does not refuse a zero divisor at
        all -- it answers an infinity -- and with an unknown dividend it never
        looks at the divisor, because the result is undecided either way.
        """
        assert_only_not_null(divide(UnknownN(**LOWER_10), N(0)))


class TestEdgeCases:
    def test_type_errors_with_refined_unknowns(self) -> None:
        """A wrongly typed argument is refused before the refinement is consulted."""
        with pytest.raises(CtyFunctionError):
            add(UnknownN(**LOWER_10), CtyString().validate("not a number"))

    def test_a_null_is_refused_even_beside_a_refined_unknown(self) -> None:
        """This used to assert that a null "propagates to unknown".

        It does not propagate to anything now -- `add` declares neither
        parameter AllowNull, so the call is refused before the refinement is
        ever consulted.
        """
        with pytest.raises(CtyFunctionError):
            add(CtyValue.null(CtyNumber()), UnknownN(**LOWER_10))

    def test_a_marked_unknown_loses_its_mark(self) -> None:
        """Pinned because it is a mark leak, and it is go-cty's mark leak.

        `abs` and `negate` set `AllowMarked`, which means the framework does not
        collect their arguments' marks for re-application -- the implementation
        is expected to, and `cty.Value.Absolute` does. But when the argument is
        *unknown* the implementation never runs: `Function.Call` short-circuits
        and returns `cty.UnknownVal(expectedType).WithMarks(resultMarks...)` with
        `resultMarks` empty (`function.go:339`). Verified against the oracle,
        which reports no marks for `abs` of a marked unknown and
        `["sensitive"]` for `abs` of a marked known.

        Recorded here rather than fixed. Diverging from go-cty on which values
        carry a sensitivity mark is not a decision this migration gets to make on
        its own, and a silent difference is worse than a documented one.
        """
        from pyvider.cty.marks import CtyMark

        sensitive = CtyMark("sensitive")

        assert abs_fn(N(-3).mark(sensitive)).marks == frozenset({sensitive})
        assert abs_fn(UnknownN().mark(sensitive)).marks == frozenset()
        assert negate(UnknownN().mark(sensitive)).marks == frozenset()


# 🌊🪢🔚
