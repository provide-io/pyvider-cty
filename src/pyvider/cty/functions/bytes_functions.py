#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from typing import Any

from pyvider.cty import CtyNumber, CtyValue
from pyvider.cty.config.defaults import (
    ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE,
    ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER,
    ERR_BYTESSLICE_NEGATIVE,
    ERR_BYTESSLICE_OFFSET_PAST_END,
    ERR_BYTESSLICE_PAST_END,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.types import BytesCapsule


@stdlib_function("byteslen")
def byteslen(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(BytesCapsule):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=buffer.type.ctype)
        raise CtyFunctionError(error_message)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


@stdlib_function("bytesslice")
def bytesslice(buffer: CtyValue[Any], offset: CtyValue[Any], length: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `BytesSliceFunc`.

    The third argument is a *length*, not an end index. This took an end index
    until the oracle was extended to reach it, and the two spellings agree
    whenever the offset is zero -- which is why every test written from this
    side passed. go-cty computes `end := offset + length` at `stdlib/bytes.go:98`.

    The bounds are checked rather than clamped, for the same reason. Python
    slicing silently accepts everything: a past-the-end range yields a short
    buffer and a negative one counts back from the far end, so `bytesslice(buf,
    1, -2)` returned eight bytes where go-cty reports an error.
    """
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(offset.type, CtyNumber)
        or not isinstance(length.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or offset.is_unknown
        or offset.is_null
        or length.is_unknown
        or length.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start, count = int(offset.value), int(length.value)  # type: ignore[call-overload]
    if start < 0 or count < 0:
        raise CtyFunctionError(ERR_BYTESSLICE_NEGATIVE)

    buf: bytes = buffer.value  # type: ignore[assignment]
    if start > len(buf):
        raise CtyFunctionError(ERR_BYTESSLICE_OFFSET_PAST_END.format(offset=start, total=len(buf)))
    end = start + count
    if end > len(buf):
        raise CtyFunctionError(ERR_BYTESSLICE_PAST_END.format(offset=start, length=count, total=len(buf)))

    return BytesCapsule.validate(buf[start:end])


# 🌊🪢🔚
