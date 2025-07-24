from decimal import Decimal
import json
from typing import Any

import msgpack  # type: ignore

from .conversion import encode_cty_type_to_wire_json
from .exceptions import CtyValidationError, DeserializationError
from .parser import parse_tf_type_to_ctytype
from pyvider.telemetry import logger
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
            
            def _decode_num(val: Any) -> Decimal:
                if isinstance(val, bytes):
                    return Decimal(val.decode('utf-8'))
                return Decimal(val)

            if 3 in payload:
                refinements["number_lower_bound"] = (_decode_num(payload[3][0]), payload[3][1])
            if 4 in payload:
                refinements["number_upper_bound"] = (_decode_num(payload[4][0]), payload[4][1])
            if 5 in payload:
                refinements["collection_length_lower_bound"] = payload[5]
            if 6 in payload:
                refinements["collection_length_upper_bound"] = payload[6]
            return RefinedUnknownValue(**refinements)
        except Exception as e:
            raise DeserializationError(f"Failed to decode refined unknown payload: {e}") from e
    return msgpack.ExtType(code, data)


def _serialize_unknown(value: "CtyValue[Any]") -> Any:
    if not isinstance(value.value, RefinedUnknownValue):
        return msgpack.ExtType(0, b"")
    payload: dict[int, Any] = {}
    if value.value.is_known_null is not None: payload[1] = value.value.is_known_null
    if value.value.string_prefix is not None: payload[2] = value.value.string_prefix
    if value.value.number_lower_bound is not None:
        num, inclusive = value.value.number_lower_bound
        payload[3] = [str(num).encode("utf-8"), inclusive]
    if value.value.number_upper_bound is not None:
        num, inclusive = value.value.number_upper_bound
        payload[4] = [str(num).encode("utf-8"), inclusive]
    if value.value.collection_length_lower_bound is not None: payload[5] = value.value.collection_length_lower_bound
    if value.value.collection_length_upper_bound is not None: payload[6] = value.value.collection_length_upper_bound
    if not payload: return msgpack.ExtType(0, b"")
    packed_payload = msgpack.packb(payload)
    return msgpack.ExtType(12, packed_payload)


def _serialize_dynamic(value: "CtyValue[Any]") -> list[Any]:
    inner_value = value.value
    if not isinstance(inner_value, CtyValue):
        from .conversion.raw_to_cty import infer_cty_type_from_raw
        inferred_type = infer_cty_type_from_raw(inner_value)
        inner_value = inferred_type.validate(inner_value)

    actual_type = inner_value.type
    serializable_inner = _convert_value_to_serializable(inner_value, actual_type)
    
    type_spec_json = encode_cty_type_to_wire_json(actual_type)
    type_spec_bytes = json.dumps(type_spec_json).encode("utf-8")
    return [type_spec_bytes, serializable_inner]


def _convert_value_to_serializable(value: "CtyValue[Any]", schema: "CtyType[Any]") -> Any:
    if not isinstance(value, CtyValue): value = schema.validate(value)
    if value.is_unknown: return _serialize_unknown(value)
    if value.is_null:
        if isinstance(schema, CtyMap | CtyObject):
            return {}
        if isinstance(schema, CtyList | CtySet):
            return []
        return None
    if isinstance(schema, CtyDynamic): return _serialize_dynamic(value)
    inner_val = value.value
    if isinstance(schema, CtyObject):
        if not isinstance(inner_val, dict): raise TypeError("Value for CtyObject must be a dict")
        return {k: _convert_value_to_serializable(v, schema.attribute_types[k]) for k, v in inner_val.items()}
    if isinstance(schema, CtyMap):
        if not isinstance(inner_val, dict): raise TypeError("Value for CtyMap must be a dict")
        return {k: _convert_value_to_serializable(v, schema.element_type) for k, v in inner_val.items()}
    if isinstance(schema, CtyList | CtySet):
        if not hasattr(inner_val, "__iter__"): raise TypeError("Value for CtyList or CtySet must be iterable")
        items = sorted(list(inner_val), key=repr) if isinstance(schema, CtySet) else inner_val
        return [_convert_value_to_serializable(item, schema.element_type) for item in items]
    if isinstance(schema, CtyTuple):
        if not isinstance(inner_val, tuple): raise TypeError("Value for CtyTuple must be a tuple")
        return [_convert_value_to_serializable(item, schema.element_types[i]) for i, item in enumerate(inner_val)]
    if isinstance(inner_val, Decimal): return str(inner_val)
    return inner_val


def _msgpack_default_handler(obj: Any) -> str:
    if isinstance(obj, int): return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not MessagePack serializable")


def cty_to_msgpack(value: "CtyValue[Any]", schema: "CtyType[Any]") -> bytes:
    serializable_data = _convert_value_to_serializable(value, schema)
    return msgpack.packb(serializable_data, default=_msgpack_default_handler, use_bin_type=True)


def _unpacked_to_cty(data: Any, schema: "CtyType[Any]") -> "CtyValue[Any]":
    if isinstance(data, UnknownValue): return CtyValue.unknown(schema, value=data)
    if data is None: return CtyValue.null(schema)
    return schema.validate(data)


def cty_from_msgpack(data: bytes, cty_type: "CtyType[Any]") -> "CtyValue[Any]":
    if not data: return CtyValue.null(cty_type)
    raw_unpacked = msgpack.unpackb(data, ext_hook=_ext_hook, raw=False, strict_map_key=False)
    
    if isinstance(cty_type, CtyDynamic):
        if isinstance(raw_unpacked, list) and len(raw_unpacked) == 2 and isinstance(raw_unpacked[0], bytes):
            try:
                type_spec = json.loads(raw_unpacked[0].decode("utf-8"))
                # Let CtyValidationError from parsing or validation propagate up.
                actual_type = parse_tf_type_to_ctytype(type_spec)
                inner_value = actual_type.validate(raw_unpacked[1])
                return CtyValue(vtype=cty_type, value=inner_value)
            except json.JSONDecodeError as e:
                # Fallback only for malformed JSON in the type spec.
                logger.debug(
                    "Dynamic value deserialization failed due to invalid JSON type spec, falling back to inference.",
                    exc_info=e,
                )
    
    return _unpacked_to_cty(raw_unpacked, cty_type)
