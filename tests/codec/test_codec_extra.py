#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


import msgpack
import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.codec import (
    _convert_value_to_serializable,
    _msgpack_default_handler,
    cty_to_msgpack,
)


def test_serialize_dynamic_with_validated_value() -> None:
    """
    Tests that a CtyDynamic value, correctly created via its validator,
    serializes as expected.
    """
    dynamic_type = CtyDynamic()
    raw_value = {"key": "value"}
    # The correct pattern is to use the validator, which wraps the raw value
    # in a concrete CtyValue inside the CtyDynamic CtyValue.
    cty_val = dynamic_type.validate(raw_value)

    packed = cty_to_msgpack(cty_val, dynamic_type)
    unpacked = msgpack.unpackb(packed, raw=False)

    assert isinstance(unpacked, list)
    assert len(unpacked) == 2
    # A dict with string keys should be inferred as an object.
    assert unpacked[0] == b'["object",{"key":"string"}]'
    assert unpacked[1] == {"key": "value"}


def test_convert_value_to_serializable_with_raw_value() -> None:
    serializable = _convert_value_to_serializable("hello", CtyString())
    assert serializable == "hello"


def test_incorrect_container_type_raises_error() -> None:
    with pytest.raises(TypeError, match="Value for CtyObject must be a dict"):
        _convert_value_to_serializable(CtyValue(CtyObject({}), ["not", "a", "dict"]), CtyObject({}))

    with pytest.raises(TypeError, match="Value for CtyMap must be a dict"):
        _convert_value_to_serializable(
            CtyValue(CtyMap(element_type=CtyString()), ["not", "a", "dict"]),
            CtyMap(element_type=CtyString()),
        )

    with pytest.raises(TypeError, match="Value for CtyList or CtySet must be iterable"):
        _convert_value_to_serializable(
            CtyValue(CtyList(element_type=CtyString()), 123),
            CtyList(element_type=CtyString()),
        )

    with pytest.raises(TypeError, match="Value for CtyTuple must be a tuple"):
        _convert_value_to_serializable(
            CtyValue(CtyTuple(element_types=(CtyString(),)), ["not", "a", "tuple"]),
            CtyTuple(element_types=(CtyString(),)),
        )


def test_msgpack_default_handler_unsupported_type() -> None:
    class Unsupported:
        pass

    with pytest.raises(TypeError, match="Object of type Unsupported is not MessagePack serializable"):
        msgpack.packb(Unsupported(), default=_msgpack_default_handler)


# 🌊🪢🔚
