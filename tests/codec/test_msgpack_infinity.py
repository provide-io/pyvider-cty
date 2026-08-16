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
from typing import Any

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtySet, CtyString
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


class TestNumberEncodingMatchesGoCty:
    """go-cty emits a float64 only when the conversion is exact.

    `cty/msgpack/marshal.go:92`:

        else if fv, acc := bf.Float64(); acc == big.Exact && !bf.IsInt() {
            enc.EncodeFloat64(fv)
        } else {
            enc.EncodeString(bf.Text('f', -1))
        }

    0.1 has no exact float64 representation, so go-cty writes the string "0.1".
    Writing the float anyway put bytes on the wire that read back as
    0.1000000000000000055511151231257827 -- a different number than was
    written, which is a perpetual diff on every non-integer attribute, and a
    byte-for-byte disagreement with the implementation this one has to match.

    The break these tests catch: deciding exactness from `str(float(d))`, the
    shortest round-tripping repr, which says "0.1" and hides the loss.
    """

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("1.5", b"\xcb\x3f\xf8\x00\x00\x00\x00\x00\x00"),
            ("2.25", b"\xcb\x40\x02\x00\x00\x00\x00\x00\x00"),
            ("0.5", b"\xcb\x3f\xe0\x00\x00\x00\x00\x00\x00"),
        ],
    )
    def test_exactly_representable_fractions_are_floats(self, text: str, expected: bytes) -> None:
        assert cty_to_msgpack(CtyNumber().validate(Decimal(text)), CtyNumber()) == expected

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("0.1", b"\xa30.1"),
            ("0.3", b"\xa30.3"),
            ("-0.0001", b"\xa7-0.0001"),
            ("3.14159", b"\xa73.14159"),
        ],
    )
    def test_inexact_fractions_are_decimal_strings(self, text: str, expected: bytes) -> None:
        assert cty_to_msgpack(CtyNumber().validate(Decimal(text)), CtyNumber()) == expected

    @pytest.mark.parametrize("text", ["0.1", "0.3", "-0.0001", "3.14159", "1.5", "2.25", "42", "-17"])
    def test_every_number_round_trips_to_itself(self, text: str) -> None:
        """The property that actually matters: what is read equals what was written."""
        original = Decimal(text)
        packed = cty_to_msgpack(CtyNumber().validate(original), CtyNumber())

        assert cty_from_msgpack(packed, CtyNumber()).value == original


class TestDeeplyNestedTypeEquality:
    """Comparing two deeply nested types must not exhaust the stack.

    `equal` recursed through each container's element type, so a sufficiently
    nested type raised RecursionError out of anything that compared two of them
    -- including `CtyValue.equals`. Pre-existing; the linear chain is now walked.
    """

    @pytest.mark.parametrize("container", [CtyList, CtySet, CtyMap])
    def test_a_deeply_nested_type_compares_without_recursing(self, container: type) -> None:
        left: Any = CtyString()
        right: Any = CtyString()
        for _ in range(3000):
            left = container(element_type=left)
            right = container(element_type=right)

        assert left.equal(right)

    def test_a_mismatch_deep_in_the_chain_is_still_found(self) -> None:
        """Flattening must not turn the comparison into "both are lists"."""
        left = CtyList(element_type=CtyList(element_type=CtyString()))
        right = CtyList(element_type=CtyList(element_type=CtyNumber()))

        assert not left.equal(right)
