#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`timeadd` past the ends of `datetime`'s range refuses, inside the taxonomy.

An **accepted divergence**, recorded rather than fixed. Go's `time.Time` runs to
year 292277026596 and Python's `datetime` stops at 9999, so go-cty answers where
this refuses:

    timeadd("9999-12-31T23:59:59Z", "1h")   go-cty 10000-01-01T00:59:59Z
    timeadd("0001-01-01T00:00:00Z", "-1s")  go-cty 0000-12-31T23:59:59Z

Matching that means not using `datetime` -- an integer nanosecond count plus
civil-calendar conversion, which is what Go holds -- and no Terraform expression
can reach the boundary, since `timestamp()` cannot produce a year near it. The
two rows in `KNOWN_DIVERGENCES` are strict, so doing the replacement later
forces them out.

What was *not* acceptable is the shape of the refusal. `datetime` signals the
boundary with `OverflowError`, which is not a `CtyError`, so it escaped the
error taxonomy as a `CtyFunctionPanicError` -- an unhandled Python exception
reaching a provider from a function whose contract is to answer or refuse.

Not the same thing as the *duration* limit, which this package already gets
right: Go's `time.Duration` is int64 nanoseconds, and both refuse `2570000h`
while both accept `2560000h`.
"""

from __future__ import annotations

import pytest

from pyvider.cty import CtyString
from pyvider.cty.exceptions import CtyError, CtyFunctionError
from pyvider.cty.functions import timeadd


def add(timestamp: str, duration: str) -> str:
    return str(timeadd(CtyString().validate(timestamp), CtyString().validate(duration)).value)


@pytest.mark.parametrize(
    ("timestamp", "duration"),
    [
        pytest.param("9999-12-31T23:59:59Z", "1h", id="past-the-upper-end"),
        pytest.param("9999-12-31T23:59:59Z", "24h", id="well-past-the-upper-end"),
        pytest.param("0001-01-01T00:00:00Z", "-1s", id="before-the-lower-end"),
        pytest.param("0001-01-01T00:00:00Z", "-8760h", id="well-before-the-lower-end"),
    ],
)
def test_the_boundary_is_a_refusal_not_a_panic(timestamp: str, duration: str) -> None:
    """A `CtyFunctionError`, so `except CtyError` in a provider catches it."""
    with pytest.raises(CtyFunctionError, match="outside the representable range") as caught:
        add(timestamp, duration)

    assert isinstance(caught.value, CtyError)


def test_the_original_overflow_is_kept_as_the_cause() -> None:
    """Whoever debugs this should still be able to see where it came from."""
    with pytest.raises(CtyFunctionError) as caught:
        add("9999-12-31T23:59:59Z", "1h")

    assert isinstance(caught.value.__cause__, OverflowError)


def test_inside_the_range_is_unaffected() -> None:
    """Including right up against the boundary, which must still work."""
    assert add("9999-12-31T22:59:59Z", "1h") == "9999-12-31T23:59:59Z"
    assert add("0001-01-01T01:00:00Z", "-1h") == "0001-01-01T00:00:00Z"
    assert add("2026-01-01T00:00:00Z", "1h") == "2026-01-01T01:00:00Z"


def test_the_duration_limit_is_a_different_limit_and_already_matches() -> None:
    """int64 nanoseconds, as Go's `time.Duration` is -- not `timedelta`'s range.

    Checked against go-cty v1.19.0 through the oracle: both accept `2560000h`
    and both refuse `2570000h`, at the same cutoff.
    """
    assert add("2026-01-01T00:00:00Z", "2560000h") == "2318-01-17T16:00:00Z"

    with pytest.raises(CtyFunctionError):
        add("2026-01-01T00:00:00Z", "2570000h")


# 🐍🏗️🔚
