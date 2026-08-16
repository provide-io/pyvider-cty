#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for bytes functions (byteslen, bytesslice)."""

import pytest

from pyvider.cty import BytesCapsule, CtyNumber, CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import byteslen, bytesslice


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

    def test_byteslen_null_unknown(self) -> None:
        assert byteslen(CtyValue.null(BytesCapsule)).is_unknown
        assert byteslen(CtyValue.unknown(BytesCapsule)).is_unknown

    def test_bytesslice_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            bytesslice(S("hello"), N(0), N(1))
        with pytest.raises(CtyFunctionError):
            bytesslice(BytesCapsule.validate(b"hello"), S("0"), N(1))
        with pytest.raises(CtyFunctionError):
            bytesslice(BytesCapsule.validate(b"hello"), N(0), S("1"))

    def test_bytesslice_null_unknown(self) -> None:
        assert bytesslice(CtyValue.null(BytesCapsule), N(0), N(1)).is_unknown
        assert bytesslice(CtyValue.unknown(BytesCapsule), N(0), N(1)).is_unknown
        assert bytesslice(BytesCapsule.validate(b"hello"), CtyValue.null(CtyNumber()), N(1)).is_unknown
        assert bytesslice(BytesCapsule.validate(b"hello"), CtyValue.unknown(CtyNumber()), N(1)).is_unknown
        assert bytesslice(BytesCapsule.validate(b"hello"), N(0), CtyValue.null(CtyNumber())).is_unknown
        assert bytesslice(BytesCapsule.validate(b"hello"), N(0), CtyValue.unknown(CtyNumber())).is_unknown


# 🌊🪢🔚
