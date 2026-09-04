#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""An extension the decoder does not understand is refused, not guessed at.

go-cty decides by *length* before code (`cty/msgpack/unknown.go`,
`unmarshalUnknownValue`): an extension body of one byte or less is a totally
unknown value whatever its code, a longer body demands code 0x0c "as an
additional signal that the body is intended to be a refinement map", and
anything else is

    return cty.DynamicVal, path.NewErrorf("unsupported extension type 0x%02x with len %d", typeCode, extLen)

A payload over 1 kiB is refused separately as "oversize unknown value
refinement", because a decoder that allocates whatever length the sender claims
is a memory-exhaustion lever for whoever is on the other end of the wire.

Accepting an unrecognised extension as an unrefined unknown turns a value the
sender meant as something else into a silently plausible one: the practitioner
sees "(known after apply)" for data that was never unknown.
"""

import msgpack
from msgpack import ExtType
import pytest

from pyvider.cty import CtyString
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import CtyError


@pytest.mark.parametrize("code", [0, 12, 1, 7, 127], ids=lambda c: f"code-{c}")
def test_a_short_body_is_a_totally_unknown_value_whatever_the_code(code: int) -> None:
    """One byte or fewer: go-cty returns cty.UnknownVal(ty) without reading it."""
    decoded = cty_from_msgpack(msgpack.packb(ExtType(code, b"\x00")), CtyString())

    assert decoded.is_unknown


@pytest.mark.parametrize("code", [0, 1, 7, 11, 13, 127], ids=lambda c: f"code-{c}")
def test_a_long_body_under_an_unknown_code_is_refused(code: int) -> None:
    """Only 0x0c may carry a refinement map; anything else is unsupported."""
    payload = msgpack.packb({1: False})
    assert len(payload) > 1

    with pytest.raises(CtyError, match=r"(?i)unsupported extension"):
        cty_from_msgpack(msgpack.packb(ExtType(code, payload)), CtyString())


def test_an_oversize_refinement_is_refused() -> None:
    """A sender that claims a huge refinement should not get the allocation."""
    oversize = msgpack.packb({2: "x" * 2048})
    assert len(oversize) > 1024

    with pytest.raises(CtyError, match=r"(?i)oversize"):
        cty_from_msgpack(msgpack.packb(ExtType(12, oversize)), CtyString())


def test_a_refinement_of_a_supported_shape_still_decodes() -> None:
    """The strictness must not cost the case the extension exists for."""
    payload = msgpack.packb({1: False, 2: "prefix-"})

    decoded = cty_from_msgpack(msgpack.packb(ExtType(12, payload)), CtyString())

    assert decoded.is_unknown


# 🐍🔚
