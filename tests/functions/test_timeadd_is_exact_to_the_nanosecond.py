#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`timeadd` rounds nothing: the instant carries its own nanoseconds.

Go holds a `time.Time` to nanosecond resolution and a `time.Duration` *is* an
int64 count of nanoseconds. A Python `datetime` resolves to microseconds, and
this package used to meet Go's resolution twice on the way through -- once
parsing the timestamp's fraction, once turning the duration into a `timedelta`
-- so the last three digits of a nine-digit fraction were dropped before the
arithmetic began.

The first half was fixed on 2026-08-19 by flooring the signed nanosecond count
rather than truncating its magnitude, which put negative sub-microsecond shifts
back on the right side of the second boundary. The second half was left
recorded: a *timestamp* written with sub-microsecond digits was still truncated,
so `timeadd("...00.000000001Z", "-1ns")` answered a second earlier than go-cty.

Both are closed now. The instant is parsed as a whole-second `datetime` plus an
integer nanosecond remainder, the shift is an integer nanosecond count, and the
two are added before the calendar is consulted -- so nothing is rounded at any
point. Only the calendar range is still a `datetime` limitation, and that is a
separately recorded divergence with its own strict xfails in the sweep.

Every expectation here was read from `soup-go cty call timeadd` against go-cty
v1.19.0; these run without a Go toolchain.
"""

from __future__ import annotations

import pytest

from pyvider.cty import CtyString
from pyvider.cty.functions import STDLIB
from pyvider.cty.functions.datetime_functions import (
    _parse_duration_nanoseconds,
    _parse_rfc3339_parts,
)

S = CtyString()


def timeadd(timestamp: str, duration: str) -> str:
    return str(STDLIB["timeadd"](S.validate(timestamp), S.validate(duration)).value)


class TestASubMicrosecondTimestamp:
    """The residual, which is what this file exists for."""

    def test_a_nanosecond_taken_off_a_nanosecond_is_the_same_second(self) -> None:
        """Truncating the fraction made this the *previous* second: the 1ns in
        the timestamp was lost, so the -1ns had nothing to cancel against."""
        assert timeadd("0002-01-01T00:00:00.000000001Z", "-1ns") == "0002-01-01T00:00:00Z"

    def test_two_nanoseconds_taken_off_one_does_cross_the_boundary(self) -> None:
        """The rule has to stay exact in both directions, or it has just moved
        the off-by-one somewhere else."""
        assert timeadd("0002-01-01T00:00:00.000000001Z", "-2ns") == "0001-12-31T23:59:59Z"

    def test_a_nanosecond_added_to_the_last_one_rolls_the_second_over(self) -> None:
        assert timeadd("0002-01-01T00:00:00.999999999Z", "1ns") == "0002-01-01T00:00:01Z"

    def test_two_halves_of_a_second_make_a_whole_one(self) -> None:
        assert timeadd("0002-01-01T00:00:00.5Z", "0.5s") == "0002-01-01T00:00:01Z"

    def test_a_fraction_below_a_nanosecond_is_truncated_as_go_truncates_it(self) -> None:
        """Go reads nine digits and stops, so a tenth digit changes nothing."""
        assert _parse_rfc3339_parts("0002-01-01T00:00:00.0000000019Z")[1] == 1


class TestTheDurationSideStaysFixed:
    """The 2026-08-19 half, which must not regress while the other is closed."""

    @pytest.mark.parametrize(
        ("duration", "expected"),
        [
            ("-1ns", "0001-12-31T23:59:59Z"),
            ("-1500ns", "0001-12-31T23:59:59Z"),
            ("1ns", "0002-01-01T00:00:00Z"),
            ("1500ns", "0002-01-01T00:00:00Z"),
            ("1h", "0002-01-01T01:00:00Z"),
            ("-1h", "0001-12-31T23:00:00Z"),
            ("0", "0002-01-01T00:00:00Z"),
        ],
    )
    def test_a_shift_from_a_whole_second(self, duration: str, expected: str) -> None:
        assert timeadd("0002-01-01T00:00:00Z", duration) == expected


class TestTheParsers:
    """The pieces, so a failure names which one moved."""

    @pytest.mark.parametrize(
        ("duration", "nanoseconds"),
        [
            ("1ns", 1),
            ("-1ns", -1),
            ("1500ns", 1500),
            ("-1500ns", -1500),
            ("1us", 1_000),
            ("1ms", 1_000_000),
            ("1s", 1_000_000_000),
            ("1m", 60_000_000_000),
            ("1h", 3_600_000_000_000),
            ("0", 0),
            ("-0", 0),
            ("1h30m", 5_400_000_000_000),
            ("0.5s", 500_000_000),
        ],
    )
    def test_a_duration_is_an_integer_count_of_nanoseconds(self, duration: str, nanoseconds: int) -> None:
        assert _parse_duration_nanoseconds(duration) == nanoseconds

    @pytest.mark.parametrize(
        ("timestamp", "nanoseconds"),
        [
            ("2020-01-02T03:04:05Z", 0),
            ("2020-01-02T03:04:05.1Z", 100_000_000),
            ("2020-01-02T03:04:05.000000001Z", 1),
            ("2020-01-02T03:04:05.123456789Z", 123_456_789),
            ("2020-01-02T03:04:05.999999999Z", 999_999_999),
        ],
    )
    def test_a_timestamps_fraction_survives_to_the_last_digit(self, timestamp: str, nanoseconds: int) -> None:
        assert _parse_rfc3339_parts(timestamp)[1] == nanoseconds

    def test_the_whole_second_part_carries_no_fraction_of_its_own(self) -> None:
        """The split is the point: leaving microseconds on the `datetime` too
        would count the same fraction twice."""
        moment, _ = _parse_rfc3339_parts("2020-01-02T03:04:05.123456789Z")

        assert moment.microsecond == 0


class TestWhatDidNotChange:
    def test_an_offset_timestamp_still_parses(self) -> None:
        assert timeadd("2020-01-02T03:04:05+02:00", "1h") == "2020-01-02T04:04:05+02:00"

    def test_the_calendar_range_is_still_a_recorded_divergence(self) -> None:
        """Go's `time.Time` runs to year 292277026596 and `datetime` stops at
        9999. Closing that needs civil-calendar arithmetic on the nanosecond
        count, not only the nanosecond count -- and it refuses cleanly rather
        than escaping as a panic, which is the part that mattered."""
        from pyvider.cty.exceptions import CtyFunctionError

        with pytest.raises(CtyFunctionError, match="outside the representable range"):
            timeadd("9999-12-31T23:59:59Z", "1h")


# 🌊🪢🔚
