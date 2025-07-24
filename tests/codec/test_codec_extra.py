import msgpack
import pytest
from decimal import Decimal

from pyvider.cty import (
    CtyList,
    CtyMap,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyValue,
    CtyDynamic,
    CtySet,
)
from pyvider.cty.codec import (
    _convert_value_to_serializable,
    _msgpack_default_handler,
    cty_to_msgpack,
)


def test_serialize_dynamic_with_raw_python_value():
    # This test covers the case where a raw python value is passed to _serialize_dynamic
    dynamic_type = CtyDynamic()
    raw_value = {"key": "value"}
    cty_val = CtyValue(dynamic_type, raw_value)

    # When cty_to_msgpack is called, it will internally call _serialize_dynamic
    # with a CtyValue that wraps the raw python dict. The logic inside _serialize_dynamic
    # should handle this by inferring the type.
    packed = cty_to_msgpack(cty_val, dynamic_type)
    unpacked = msgpack.unpackb(packed, raw=False)

    # We expect it to be serialized as a dynamic value, which is a two-element list.
    # The first element is the type spec, the second is the serialized value.
    assert isinstance(unpacked, list)
    assert len(unpacked) == 2
    # CORRECTED: A dict with uniform value types should be inferred as a map.
    assert b'["map", "string"]' == unpacked[0]
    assert unpacked[1] == {"key": "value"}


def test_convert_value_to_serializable_with_raw_value():
    # This covers the case where a raw value is passed to _convert_value_to_serializable
    # instead of a CtyValue instance.
    serializable = _convert_value_to_serializable("hello", CtyString())
    assert serializable == "hello"


def test_incorrect_container_type_raises_error():
    # Covers the TypeError branches for wrong container types.
    with pytest.raises(TypeError, match="Value for CtyObject must be a dict"):
        _convert_value_to_serializable(
            CtyValue(CtyObject({}), ["not", "a", "dict"]), CtyObject({})
        )

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


def test_msgpack_default_handler_unsupported_type():
    # Covers the TypeError in the default handler
    class Unsupported:
        pass

    with pytest.raises(
        TypeError, match="Object of type Unsupported is not MessagePack serializable"
    ):
        msgpack.packb(Unsupported(), default=_msgpack_default_handler)
