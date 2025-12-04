#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from decimal import Decimal

import msgpack

from pyvider.cty import CtyList, CtyNumber, CtyString, CtyValue
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.values import RefinedUnknownValue


def test_deserialize_refined_unknown_non_null() -> None:
    """Verifies deserializing an unknown value that is known to not be null."""
    refinements = {1: False}  # Key 1: nullness, Value: False (not null)
    ext_payload = msgpack.packb(refinements)
    packed_data = msgpack.packb(msgpack.ExtType(12, ext_payload))
    result = cty_from_msgpack(packed_data, CtyNumber())
    assert result.is_unknown
    assert isinstance(result.value, RefinedUnknownValue)
    assert result.value.is_known_null is False


def test_deserialize_refined_unknown_string_prefix() -> None:
    """Verifies deserializing an unknown string with a known prefix."""
    refinements = {2: "arn:aws:"}  # Key 2: string_prefix
    ext_payload = msgpack.packb(refinements)
    packed_data = msgpack.packb(msgpack.ExtType(12, ext_payload))
    result = cty_from_msgpack(packed_data, CtyString())
    assert result.is_unknown
    assert isinstance(result.value, RefinedUnknownValue)
    assert result.value.string_prefix == "arn:aws:"


def test_deserialize_refined_unknown_number_bounds() -> None:
    """Verifies deserializing an unknown number with lower and upper bounds."""
    # Represents a number >= 10 and < 100.5
    refinements = {
        3: [b"10", True],  # Key 3: lower_bound, [value, inclusive]
        4: [b"100.5", False],  # Key 4: upper_bound, [value, exclusive]
    }
    ext_payload = msgpack.packb(refinements)
    packed_data = msgpack.packb(msgpack.ExtType(12, ext_payload))
    result = cty_from_msgpack(packed_data, CtyNumber())
    assert result.is_unknown
    assert isinstance(result.value, RefinedUnknownValue)
    assert result.value.number_lower_bound == (Decimal("10"), True)
    assert result.value.number_upper_bound == (Decimal("100.5"), False)


def test_deserialize_refined_unknown_collection_length_bounds() -> None:
    """Verifies deserializing an unknown list with length bounds."""
    refinements = {
        5: 1,  # Key 5: collection_length_lower_bound
        6: 10,  # Key 6: collection_length_upper_bound
    }
    ext_payload = msgpack.packb(refinements)
    packed_data = msgpack.packb(msgpack.ExtType(12, ext_payload))
    result = cty_from_msgpack(packed_data, CtyList(element_type=CtyString()))
    assert result.is_unknown
    assert isinstance(result.value, RefinedUnknownValue)
    assert result.value.collection_length_lower_bound == 1
    assert result.value.collection_length_upper_bound == 10


def test_serialize_refined_unknown_value() -> None:
    """Verifies that a RefinedUnknownValue object is correctly serialized."""
    # GIVEN a refined unknown value object
    refined_val = CtyValue(
        vtype=CtyNumber(),
        is_unknown=True,
        value=RefinedUnknownValue(number_lower_bound=(Decimal(0), True)),
    )

    # WHEN it is serialized
    packed_bytes = cty_to_msgpack(refined_val, CtyNumber())

    # THEN it should be a msgpack ExtType 12 with the correct payload
    unpacked = msgpack.unpackb(packed_bytes, raw=False, strict_map_key=False)
    assert isinstance(unpacked, msgpack.ExtType)
    assert unpacked.code == 12

    payload = msgpack.unpackb(unpacked.data, raw=False, strict_map_key=False)
    assert payload == {3: [b"0", True]}


# 🌊🪢🔚
