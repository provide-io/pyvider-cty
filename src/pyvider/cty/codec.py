from decimal import Decimal
import json
from typing import Any

import msgpack

from .conversion import encode_cty_type_to_wire_json
from .exceptions import DeserializationError
from .types import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyTuple,
    CtyType,
)
from .values import CtyValue
from .values.markers import UNREFINED_UNKNOWN, RefinedUnknownValue, UnknownValue


def _ext_hook(code: int, data: bytes) -> Any:
    if code == 0:
        return UNREFINED_UNKNOWN
    if code == 12:
        try:
            payload = msgpack.unpackb(data, raw=False, strict_map_key=False)
            refinements = {}
            if 1 in payload:
                refinements["is_known_null"] = payload[1]
            if 2 in payload:
                refinements["string_prefix"] = payload[2]
            if 3 in payload:
                refinements["number_lower_bound"] = (
                    Decimal(payload[3][0].decode("utf-8")),
                    payload[3][1],
                )
            if 4 in payload:
                refinements["number_upper_bound"] = (
                    Decimal(payload[4][0].decode("utf-8")),
                    payload[4][1],
                )
            if 5 in payload:
                refinements["collection_length_lower_bound"] = payload[5]
            if 6 in payload:
                refinements["collection_length_upper_bound"] = payload[6]
            return RefinedUnknownValue(**refinements)
        except Exception as e:
            raise DeserializationError(
                f"Failed to decode refined unknown payload: {e}"
            ) from e
    return msgpack.ExtType(code, data)


def _convert_value_to_serializable(
    value: "CtyValue[Any]", schema: "CtyType[Any]"
) -> Any:
    if not isinstance(value, CtyValue):
        value = schema.validate(value)

    if value.is_unknown:
        if isinstance(value.value, RefinedUnknownValue):
            payload = {}
            if value.value.is_known_null is not None:
                payload[1] = value.value.is_known_null
            if value.value.string_prefix is not None:
                payload[2] = value.value.string_prefix
            if value.value.number_lower_bound is not None:
                num, inclusive = value.value.number_lower_bound
                payload[3] = [str(num).encode("utf-8"), inclusive]
            if value.value.number_upper_bound is not None:
                num, inclusive = value.value.number_upper_bound
                payload[4] = [str(num).encode("utf-8"), inclusive]
            if value.value.collection_length_lower_bound is not None:
                payload[5] = value.value.collection_length_lower_bound
            if value.value.collection_length_upper_bound is not None:
                payload[6] = value.value.collection_length_upper_bound
            if not payload:
                return msgpack.ExtType(0, b"")
            packed_payload = msgpack.packb(payload)
            return msgpack.ExtType(12, packed_payload)
        return msgpack.ExtType(0, b"")

    if value.is_null:
        return None

    if isinstance(schema, CtyDynamic):
        inner_value = value.value if isinstance(value.type, CtyDynamic) else value
        actual_type = inner_value.type
        type_spec_json = encode_cty_type_to_wire_json(actual_type)
        type_spec_bytes = json.dumps(type_spec_json).encode("utf-8")
        serializable_inner = _convert_value_to_serializable(inner_value, actual_type)
        return [type_spec_bytes, serializable_inner]

    inner_val = value.value
    if isinstance(schema, CtyObject):
        return {
            k: _convert_value_to_serializable(v, schema.attribute_types[k])
            for k, v in inner_val.items()
        }
    if isinstance(schema, CtyMap):
        return {
            k: _convert_value_to_serializable(v, schema.element_type)
            for k, v in inner_val.items()
        }
    if isinstance(schema, CtyList | CtySet):
        items = (
            sorted(list(inner_val), key=repr)
            if isinstance(schema, CtySet)
            else inner_val
        )
        return [
            _convert_value_to_serializable(item, schema.element_type) for item in items
        ]
    if isinstance(schema, CtyTuple):
        return [
            _convert_value_to_serializable(item, schema.element_types[i])
            for i, item in enumerate(inner_val)
        ]

    if isinstance(inner_val, Decimal):
        return str(inner_val)

    return inner_val


def _msgpack_default_handler(obj: Any) -> Any:
    """
    A handler for msgpack to serialize types it doesn't know,
    like arbitrarily large Python integers.
    """
    if isinstance(obj, int):
        # If an integer is too large for msgpack's native types,
        # it will be passed to this handler. We serialize it as a string
        # to maintain precision, which aligns with go-cty's behavior.
        return str(obj)
    raise TypeError(
        f"Object of type {type(obj).__name__} is not MessagePack serializable"
    )


def cty_to_msgpack(value: "CtyValue[Any]", schema: "CtyType[Any]") -> bytes:
    serializable_data = _convert_value_to_serializable(value, schema)
    # THE FIX: Use the `default` parameter to handle large integers.
    return msgpack.packb(
        serializable_data, default=_msgpack_default_handler, use_bin_type=True
    )


def _unpacked_to_cty(data: Any, schema: "CtyType[Any]") -> "CtyValue[Any]":
    if isinstance(data, UnknownValue):
        return CtyValue.unknown(schema, value=data)
    if data is None:
        return CtyValue.null(schema)
    return schema.validate(data)


def cty_from_msgpack(data: bytes, cty_type: "CtyType[Any]") -> "CtyValue[Any]":
    if not data:
        return CtyValue.null(cty_type)
    raw_unpacked = msgpack.unpackb(
        data, ext_hook=_ext_hook, raw=False, strict_map_key=False
    )
    return _unpacked_to_cty(raw_unpacked, cty_type)
