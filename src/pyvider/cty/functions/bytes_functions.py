#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/bytes.go`.

`BytesCapsule` is this package's `cty.Capsule("bytes", reflect.TypeOf([]byte(nil)))`
(`bytes.go:15`), and it stands in a parameter's type slot exactly as go-cty's
does: `conformance_errors` answers a capsule by identity, so `bytes required, but
received string` comes from the framework rather than from a hand-rolled check.
"""

from __future__ import annotations

from typing import Any, cast

from pyvider.cty import CtyNumber, CtyValue
from pyvider.cty.config.defaults import (
    ERR_BYTESSLICE_NEGATIVE,
    ERR_BYTESSLICE_OFFSET_AND_LENGTH_MUST_BE_WHOLE,
    ERR_BYTESSLICE_OFFSET_PAST_END,
    ERR_BYTESSLICE_PAST_END,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._args import whole_number
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null
from pyvider.cty.types import BytesCapsule


@stdlib_function(
    "byteslen",
    params=[CtyParameter("buf", BytesCapsule, allow_dynamic_type=True)],
    returns=CtyNumber(),
    refine_result=refine_not_null,
    description="Returns the total number of bytes in the given buffer.",
)
def byteslen(buffer: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `BytesLenFunc` (`stdlib/bytes.go:32`)."""
    return cast(CtyValue[Any], CtyNumber().validate(len(cast(bytes, buffer.value))))


@stdlib_function(
    "bytesslice",
    params=[
        CtyParameter("buf", BytesCapsule, allow_dynamic_type=True),
        CtyParameter("offset", CtyNumber(), allow_dynamic_type=True),
        CtyParameter("length", CtyNumber(), allow_dynamic_type=True),
    ],
    returns=BytesCapsule,
    refine_result=refine_not_null,
    description="Extracts a subslice from the given buffer.",
)
def bytesslice(buffer: CtyValue[Any], offset: CtyValue[Any], length: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `BytesSliceFunc` (`stdlib/bytes.go:50`).

    The third argument is a *length*, not an end index. This took an end index
    until the oracle was extended to reach it, and the two spellings agree
    whenever the offset is zero -- which is why every test written from this
    side passed. go-cty computes `end := offset + length` at `stdlib/bytes.go:97`.

    The bounds are checked rather than clamped, for the same reason. Python
    slicing silently accepts everything: a past-the-end range yields a short
    buffer and a negative one counts back from the far end, so `bytesslice(buf,
    1, -2)` returned eight bytes where go-cty reports an error.

    Both numbers go through `whole_number` because go-cty reads them with
    `gocty.FromCtyValue` into a Go `int` (`bytes.go:77`), which refuses a
    fraction and anything outside the int64 range. `int(Decimal("0.5"))`
    silently truncated to 0 and sliced from the start of the buffer where the
    oracle answers `value must be a whole number, between
    -9223372036854775808 and 9223372036854775807`.
    """
    start = whole_number(offset, ERR_BYTESSLICE_OFFSET_AND_LENGTH_MUST_BE_WHOLE)
    count = whole_number(length, ERR_BYTESSLICE_OFFSET_AND_LENGTH_MUST_BE_WHOLE)
    if start < 0 or count < 0:
        raise CtyFunctionError(ERR_BYTESSLICE_NEGATIVE)

    buf = cast(bytes, buffer.value)
    if start > len(buf):
        raise CtyFunctionError(ERR_BYTESSLICE_OFFSET_PAST_END.format(offset=start, total=len(buf)))
    end = start + count
    if end > len(buf):
        raise CtyFunctionError(ERR_BYTESSLICE_PAST_END.format(offset=start, length=count, total=len(buf)))

    return BytesCapsule.validate(buf[start:end])


# 🌊🪢🔚
