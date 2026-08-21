#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`cty_from_msgpack` raises only `CtyError` subclasses.

Bytes that are not a valid MessagePack payload raise `DeserializationError`,
with the msgpack library's own exception chained as the cause. A payload that
decodes but does not fit the type raises the type's `CtyValidationError`, as it
always did. Before, the first family leaked `msgpack.FormatError`,
`msgpack.ExtraData` and a bare `ValueError`, so a caller wanting to catch every
decode failure had to catch `Exception`.
"""

import msgpack
import pytest

from pyvider.cty import CtyDynamic, CtyString
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import CtyError, CtyValidationError, DeserializationError

MALFORMED = {
    "reserved byte": b"\xc1",
    "truncated array": b"\x92\xa1a",
    "trailing bytes": b"\xa1a\xa1b",
    "invalid utf-8 in a string": b"\xa1\xff",
}


@pytest.mark.parametrize("data", MALFORMED.values(), ids=MALFORMED.keys())
def test_malformed_bytes_raise_deserialization_error(data: bytes) -> None:
    with pytest.raises(DeserializationError) as info:
        cty_from_msgpack(data, CtyString())
    assert isinstance(info.value.__cause__, (msgpack.UnpackException, ValueError))


def test_a_dynamic_header_that_is_not_utf8_raises_deserialization_error() -> None:
    packed = msgpack.packb([b"\xff\xfe", "x"])
    with pytest.raises(DeserializationError):
        cty_from_msgpack(packed, CtyDynamic())


def test_a_payload_that_does_not_fit_the_type_is_still_a_validation_error() -> None:
    with pytest.raises(CtyValidationError):
        cty_from_msgpack(b"\x01", CtyString())


@pytest.mark.parametrize("data", [*MALFORMED.values(), b"\x01", b""])
def test_every_failure_is_a_cty_error(data: bytes) -> None:
    with pytest.raises(CtyError):
        cty_from_msgpack(data, CtyString())
