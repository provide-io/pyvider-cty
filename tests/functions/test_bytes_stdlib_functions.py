#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for bytes functions (byteslen, bytesslice)."""

import pytest

from pyvider.cty import BytesCapsule, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import SIGNATURES, byteslen, bytesslice
from pyvider.cty.values.markers import RefinedUnknownValue


# Helper functions for creating CtyValues to improve test readability
def S(v):
    return CtyString().validate(v)


def N(v):
    return CtyNumber().validate(v)


class TestBytesFunctions:
    def test_byteslen(self) -> None:
        assert byteslen(BytesCapsule.validate(b"hello")).value == 5

    def test_bytesslice(self) -> None:
        """The third argument is a length, not an end index.

        This asserted `bytesslice(b"hello", 1, 4) == b"ell"`, which is what an
        end index gives. go-cty computes `end := offset + length`
        (`stdlib/bytes.go:98`), so that call returns `b"ello"` and it is
        `(1, 3)` that yields `b"ell"`. The two spellings agree whenever the
        offset is zero, which is how this went unnoticed.
        """
        assert bytesslice(BytesCapsule.validate(b"hello"), N(1), N(3)).value == b"ell"
        assert bytesslice(BytesCapsule.validate(b"hello"), N(1), N(4)).value == b"ello"
        assert bytesslice(BytesCapsule.validate(b"hello"), N(0), N(5)).value == b"hello"
        assert bytesslice(BytesCapsule.validate(b"hello"), N(5), N(0)).value == b""

    def test_bytesslice_refuses_a_fraction(self) -> None:
        """go-cty reads both numbers into a Go `int`, which refuses a fraction.

        Added 2026-08-17. `gocty.FromCtyValue(args[1], &offset)`
        (`stdlib/bytes.go:77`) is what turns the argument into an index, and the
        oracle answers `value must be a whole number, between
        -9223372036854775808 and 9223372036854775807`. `int(Decimal("0.5"))`
        truncated to 0 instead and sliced from the start of the buffer, so
        `bytesslice(b"hello", 0.5, 2)` returned `b"he"` where go-cty refuses.
        """
        buf = BytesCapsule.validate(b"hello")

        for offset, length in (("0.5", "2"), ("1", "2.5"), (2**70, "1")):
            with pytest.raises(CtyFunctionError, match="whole number"):
                bytesslice(buf, N(offset), N(length))

    def test_bytesslice_bounds_are_checked_not_clamped(self) -> None:
        """Python slicing accepts everything; go-cty refuses.

        A past-the-end range silently yields a short buffer, and a negative one
        counts back from the far end -- `bytesslice(b"hello", 1, -2)` returned
        `b"el"` rather than an error.
        """
        buf = BytesCapsule.validate(b"hello")

        for offset, length in ((6, 0), (0, 6), (3, 3), (-1, 2), (1, -2)):
            with pytest.raises(CtyFunctionError):
                bytesslice(buf, N(offset), N(length))

    def test_byteslen_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            byteslen(S("hello"))

    def test_byteslen_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            byteslen(CtyValue.null(BytesCapsule))
        assert byteslen(CtyValue.unknown(BytesCapsule)).is_unknown

    def test_bytesslice_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            bytesslice(S("hello"), N(0), N(1))
        with pytest.raises(CtyFunctionError):
            bytesslice(BytesCapsule.validate(b"hello"), S("0"), N(1))
        with pytest.raises(CtyFunctionError):
            bytesslice(BytesCapsule.validate(b"hello"), N(0), S("1"))

    def test_bytesslice_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            bytesslice(CtyValue.null(BytesCapsule), N(0), N(1))
        assert bytesslice(CtyValue.unknown(BytesCapsule), N(0), N(1)).is_unknown
        with pytest.raises(CtyFunctionError):
            bytesslice(BytesCapsule.validate(b"hello"), CtyValue.null(CtyNumber()), N(1))
        assert bytesslice(BytesCapsule.validate(b"hello"), CtyValue.unknown(CtyNumber()), N(1)).is_unknown
        with pytest.raises(CtyFunctionError):
            bytesslice(BytesCapsule.validate(b"hello"), N(0), CtyValue.null(CtyNumber()))
        assert bytesslice(BytesCapsule.validate(b"hello"), N(0), CtyValue.unknown(CtyNumber())).is_unknown


class TestBytesUnknownAnswers:
    """An unknown answer is typed by the return type, and refined not-null.

    Added 2026-08-17. Both functions declare `RefineResult: refineNonNull`
    (`stdlib/bytes.go:42` and `70`) and this package declared neither, so an
    unknown answer said only "unknown" where go-cty's says "unknown, and not
    null". The type was also wider than it needed to be: `byteslen` returned an
    unknown of *dynamic* type from its own body, where the declared return type
    settles it as a number without any value being known.
    """

    def test_byteslen_of_an_unknown_buffer_is_an_unknown_number(self) -> None:
        result = byteslen(CtyValue.unknown(BytesCapsule))

        assert result.type == CtyNumber()
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_bytesslice_of_an_unknown_buffer_is_an_unknown_buffer(self) -> None:
        result = bytesslice(CtyValue.unknown(BytesCapsule), N(0), N(1))

        assert result.type.equal(BytesCapsule)
        assert result.value == RefinedUnknownValue(is_known_null=False)

    def test_the_signatures_predict_the_return_types(self) -> None:
        """A capsule type stands in a parameter and a return slot like any other."""
        assert SIGNATURES["byteslen"].return_type([BytesCapsule]) == CtyNumber()
        assert (
            SIGNATURES["bytesslice"].return_type([BytesCapsule, CtyNumber(), CtyNumber()]).equal(BytesCapsule)
        )


# 🌊🪢🔚
