#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""A refinement read off the wire is held to the same rules as one built here.

`RefinementBuilder` refuses a refinement no value can satisfy. The msgpack
decoder never went through it: it built the refinement record directly, so
`3 < x < 3`, `4 <= x <= 3` and a length bound of 5..3 decoded without complaint
into unknowns that compare unequal to every value they could have been, and a
bound's inclusive flag of `"yes"` was stored as its inclusivity.

go-cty decodes a number bound as a `[number, bool]` tuple and returns an error
for any other shape. It applies every entry through its `Refine()` builder
(`cty/msgpack/unknown.go:211`), which panics on the crossed bounds and on
`3 < x <= 3` -- but accepts `3 < x < 3`, because its bounds check compares
whether the two inclusivity flags are *equal* rather than whether both are
inclusive. Neither the panic nor the accepted empty range is a behaviour to
match. This raises `DeserializationError` for all of them.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import msgpack
import pytest

from pyvider.cty import CtyList, CtyNumber, CtyString
from pyvider.cty.codec import cty_from_msgpack
from pyvider.cty.exceptions import DeserializationError
from pyvider.cty.values import RefinedUnknownValue


def _refined(payload: dict[int, Any]) -> bytes:
    return msgpack.packb(msgpack.ExtType(12, msgpack.packb(payload)))


@pytest.mark.parametrize(
    ("wire", "message"),
    [
        # Byte for byte what go-cty's `msgpack.Marshal` writes for an unknown
        # number refined to 3 < x < 3, a range its own builder accepts.
        ("c7090c82039203c2049203c2", "number lower bound 3 excludes upper bound 3"),
        ("c7090c82039203c2049203c3", "number lower bound 3 excludes upper bound 3"),
        ("c7090c82039203c3049203c2", "number lower bound 3 excludes upper bound 3"),
        ("c7090c82039204c3049203c3", "number lower bound 4 is greater than upper bound 3"),
    ],
    ids=["3 < x < 3", "3 < x <= 3", "3 <= x < 3", "4 <= x <= 3"],
)
def test_a_number_range_holding_no_number_is_refused(wire: str, message: str) -> None:
    with pytest.raises(DeserializationError, match=message):
        cty_from_msgpack(bytes.fromhex(wire), CtyNumber())


@pytest.mark.parametrize(
    ("wire", "lower", "upper"),
    [
        ("c7090c82039203c3049203c3", (Decimal(3), True), (Decimal(3), True)),
        ("c7090c82039203c3049204c3", (Decimal(3), True), (Decimal(4), True)),
        ("c7090c82039203c2049204c2", (Decimal(3), False), (Decimal(4), False)),
    ],
    ids=["3 <= x <= 3", "3 <= x <= 4", "3 < x < 4"],
)
def test_a_number_range_holding_a_number_still_decodes(
    wire: str, lower: tuple[Decimal, bool], upper: tuple[Decimal, bool]
) -> None:
    result = cty_from_msgpack(bytes.fromhex(wire), CtyNumber())

    assert result.is_unknown
    assert isinstance(result.value, RefinedUnknownValue)
    assert (result.value.number_lower_bound, result.value.number_upper_bound) == (lower, upper)


def test_an_empty_range_nested_in_a_collection_is_refused() -> None:
    """The check lives where every refinement is decoded, not only at the top."""
    element = msgpack.ExtType(12, msgpack.packb({3: [3, False], 4: [3, False]}))

    with pytest.raises(DeserializationError, match="excludes upper bound"):
        cty_from_msgpack(msgpack.packb([element]), CtyList(element_type=CtyNumber()))


@pytest.mark.parametrize(
    "bound",
    [[3, "yes"], [3, 1], [3, None], [3], [3, True, False], 3],
    ids=["string flag", "integer flag", "nil flag", "no flag", "extra entry", "not an array"],
)
def test_a_number_bound_that_is_not_a_number_and_a_bool_is_refused(bound: Any) -> None:
    with pytest.raises(DeserializationError, match=r"must be \[number, bool\]"):
        cty_from_msgpack(_refined({3: bound}), CtyNumber())


def test_a_length_upper_bound_below_the_lower_bound_is_refused() -> None:
    with pytest.raises(
        DeserializationError, match="collection length upper bound 3 is less than lower bound 5"
    ):
        cty_from_msgpack(_refined({5: 5, 6: 3}), CtyList(element_type=CtyString()))


def test_equal_length_bounds_still_decode() -> None:
    result = cty_from_msgpack(_refined({5: 3, 6: 3}), CtyList(element_type=CtyString()))

    assert result.is_unknown
    assert isinstance(result.value, RefinedUnknownValue)
    assert (result.value.collection_length_lower_bound, result.value.collection_length_upper_bound) == (3, 3)
