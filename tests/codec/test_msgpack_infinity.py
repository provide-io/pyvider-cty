#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Infinite numbers must serialize the way go-cty serializes them.

go-cty special-cases cty.PositiveInfinity / cty.NegativeInfinity in
msgpack/marshal.go and emits a float64 infinity rather than falling through to
its integer/string number encoding. Python reaches the same bytes without a
special case, because float(Decimal("Infinity")) is already inf -- these tests
pin that so the encoding cannot drift into a string or an overflow error.

The break these tests catch: a change to number encoding that routes infinity
down the large-number-as-string path, producing bytes Go cannot read back as a
number.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from pyvider.cty import CtyNumber
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack

# msgpack float64 (0xcb) followed by IEEE-754 +/- infinity, byte for byte what
# go-cty's enc.EncodeFloat64(math.Inf(...)) produces.
POSITIVE_INFINITY_BYTES = bytes.fromhex("cb7ff0000000000000")
NEGATIVE_INFINITY_BYTES = bytes.fromhex("cbfff0000000000000")


@pytest.mark.parametrize(
    ("raw", "expected_bytes"),
    [
        (Decimal("Infinity"), POSITIVE_INFINITY_BYTES),
        (Decimal("-Infinity"), NEGATIVE_INFINITY_BYTES),
    ],
    ids=["positive", "negative"],
)
def test_infinity_encodes_as_a_msgpack_float64(raw: Decimal, expected_bytes: bytes) -> None:
    value = CtyNumber().validate(raw)

    assert cty_to_msgpack(value, CtyNumber()) == expected_bytes


@pytest.mark.parametrize(
    "raw",
    [Decimal("Infinity"), Decimal("-Infinity")],
    ids=["positive", "negative"],
)
def test_infinity_survives_a_msgpack_round_trip(raw: Decimal) -> None:
    value = CtyNumber().validate(raw)

    restored = cty_from_msgpack(cty_to_msgpack(value, CtyNumber()), CtyNumber())

    assert restored.value == raw
