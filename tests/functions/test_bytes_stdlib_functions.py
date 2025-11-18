#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
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
        assert bytesslice(BytesCapsule.validate(b"hello"), N(1), N(4)).value == b"ell"

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
