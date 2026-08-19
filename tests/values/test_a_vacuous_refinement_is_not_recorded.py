#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A refinement that rules nothing out is not written to the wire.

go-cty does not record one, and the difference is visible in bytes. An empty
string prefix is true of every string; a collection length lower bound of 0 is
true of every collection. go-cty writes a bare unknown for either -- the three
bytes `d40000` -- where this package wrote a refinement map carrying the vacuous
entry, and `not_null` alongside one wrote two entries against go-cty's one.

Only reachable through the public refinement API: no stdlib function emits a
degenerate prefix (`format("%s", unknown)` refines to not-null and nothing
else). A provider computing a prefix that turns out empty is the shape that
reaches it.

Found 2026-08-19 by fuzzing refinement builders against the live harness and
comparing encoded bytes. The differential cases live in `tests/compatibility/`;
these run without a Go toolchain.

The empty *number range* is here too, and go-cty is no guide for it: `3 < x <= 3`
is unsatisfiable, this package accepted it and wrote it to the wire, and go-cty
**panics** on the same input. `lower > upper` was already refused, so the check
simply did not cover the case where the bounds are equal and one of them
excludes the value.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtyString, CtyValue
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.refinement import CtyRefinementError, refine

S = CtyString()
N = CtyNumber()
LIST = CtyList(element_type=S)
MAP = CtyMap(element_type=S)

# go-cty's bytes for an unrefined unknown, checked against the harness.
BARE_UNKNOWN = "d40000"
# ...and for an unknown refined with nothing but not-null.
NOT_NULL_ONLY = "c7030c8101c2"


class TestAVacuousRefinementIsDropped:
    def test_an_empty_string_prefix_leaves_a_bare_unknown(self) -> None:
        built = refine(CtyValue.unknown(S)).string_prefix_full("").new_value()

        assert cty_to_msgpack(built, S).hex() == BARE_UNKNOWN

    def test_an_empty_prefix_does_not_survive_alongside_not_null(self) -> None:
        """The shape that made the difference two entries wide instead of one."""
        built = refine(CtyValue.unknown(S)).string_prefix_full("").not_null().new_value()

        assert cty_to_msgpack(built, S).hex() == NOT_NULL_ONLY

    @pytest.mark.parametrize(("label", "cty_type"), [("list", LIST), ("map", MAP)])
    def test_a_length_lower_bound_of_zero_leaves_a_bare_unknown(self, label: str, cty_type: object) -> None:
        built = refine(CtyValue.unknown(cty_type)).collection_length_lower_bound(0).new_value()  # type: ignore[arg-type]

        assert cty_to_msgpack(built, cty_type).hex() == BARE_UNKNOWN, label  # type: ignore[arg-type]

    def test_a_zero_lower_bound_does_not_survive_alongside_a_real_upper_one(self) -> None:
        """go-cty writes the upper bound alone: `c7030c810605`."""
        built = (
            refine(CtyValue.unknown(LIST))
            .collection_length_lower_bound(0)
            .collection_length_upper_bound(5)
            .new_value()
        )

        assert cty_to_msgpack(built, LIST).hex() == "c7030c810605"


class TestARefinementThatRulesSomethingOutIsKept:
    """The drop must be about vacuity, not about the entry's kind."""

    def test_a_real_prefix_is_recorded(self) -> None:
        built = refine(CtyValue.unknown(S)).string_prefix_full("a").new_value()

        assert cty_to_msgpack(built, S).hex() == "d60c8102a161"

    def test_a_real_length_lower_bound_is_recorded(self) -> None:
        built = (
            refine(CtyValue.unknown(LIST))
            .collection_length_lower_bound(1)
            .collection_length_upper_bound(5)
            .new_value()
        )

        assert cty_to_msgpack(built, LIST).hex() == "c7050c8205010605"

    def test_an_exact_length_of_zero_is_still_recorded(self) -> None:
        """`length == 0` is not vacuous -- it rules out every non-empty value.

        The drop happens after the collapse check, so this keeps its upper bound
        of 0 and matches go-cty's `c7030c810600` rather than becoming bare.
        """
        built = refine(CtyValue.unknown(LIST)).collection_length(0).new_value()

        assert cty_to_msgpack(built, LIST).hex() == "c7030c810600"


class TestAnEmptyNumberRangeIsRefused:
    @pytest.mark.parametrize(
        ("label", "lower_inclusive", "upper_inclusive"),
        [
            ("3 < x <= 3", False, True),
            ("3 <= x < 3", True, False),
            ("3 < x < 3", False, False),
        ],
    )
    def test_equal_bounds_that_exclude_the_value_are_refused(
        self, label: str, lower_inclusive: bool, upper_inclusive: bool
    ) -> None:
        builder = refine(CtyValue.unknown(N)).number_range_lower_bound(Decimal(3), inclusive=lower_inclusive)

        with pytest.raises(CtyRefinementError, match="excludes"):
            builder.number_range_upper_bound(Decimal(3), inclusive=upper_inclusive)

    def test_equal_inclusive_bounds_are_still_accepted(self) -> None:
        """`3 <= x <= 3` is satisfiable, and go-cty collapses it to a known 3."""
        built = (
            refine(CtyValue.unknown(N))
            .not_null()
            .number_range_lower_bound(Decimal(3), inclusive=True)
            .number_range_upper_bound(Decimal(3), inclusive=True)
            .new_value()
        )

        assert built.is_unknown is False
        assert built.value == Decimal(3)
        assert cty_to_msgpack(built, N).hex() == "03"

    def test_an_ordinary_open_range_is_still_accepted(self) -> None:
        built = (
            refine(CtyValue.unknown(N))
            .number_range_lower_bound(Decimal(1), inclusive=False)
            .number_range_upper_bound(Decimal(5), inclusive=False)
            .new_value()
        )

        assert built.is_unknown is True


# 🌊🪢🔚
