# pyvider/cty/codec.py
"""
Core serialization/deserialization codec for CtyValues, now self-contained.
"""
import json
import re
from decimal import Decimal
from typing import TYPE_CHECKING, cast

import attrs
import msgpack
from msgpack import ExtType

from pyvider.cty.exceptions import CtyTypeParseError
from .types import (CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber, CtyObject,
                    CtySet, CtyString, CtyTuple)

if TYPE_CHECKING:
    from .types.base import CtyType
    from .values.base import CtyValue

def _normalize_type_str(target_type: "CtyType") -> str:
    """A self-contained helper to get a normalized string for a type."""
    # This replaces the need for the external `normalize_type_object`
    # A full implementation would be more robust, but str() is a good start.
    return str(target_type)

def _value_to_serializable(cty_value: "CtyValue") -> dict[str, object]:
    """Converts a CtyValue instance into a dictionary suitable for serialization."""
    data = cty_value.to_json_comparable_dict()
    if "type_name" not in data:
        data["type_name"] = _normalize_type_str(cty_value.type)
    return data

def _serializable_to_value(data: dict[str, object], target_type: "CtyType") -> "CtyValue":
    """Recursively reconstructs a CtyValue from basic Python data."""
    from .marks import CtyMark
    from .values.base import CtyValue

    if not isinstance(data, dict): raise ValueError("Invalid serialized format: not a dict.")
    
    type_name = data.get("type_name")
    value_payload = data.get("value")
    is_unknown = data.get("is_unknown", False)
    is_null = data.get("is_null", False)
    marks_data = data.get("marks", [])

    if is_unknown: return CtyValue.unknown(target_type)
    if is_null: return CtyValue.null(target_type)
    
    # Simplified reconstruction logic. A full implementation is in the bfiles.
    # This stub focuses on breaking the circular dependency.
    return target_type.validate(value_payload)

def cty_value_to_json_string(value: "CtyValue") -> str:
    serializable_data = _value_to_serializable(value)
    return json.dumps(serializable_data)

def cty_value_from_json_string(json_str: str, target_type: "CtyType") -> "CtyValue":
    data = json.loads(json_str)
    if not isinstance(data, dict): raise ValueError("Invalid JSON data: root must be an object.")
    return _serializable_to_value(data, target_type)

def cty_value_to_msgpack_bytes(value: "CtyValue") -> bytes:
    if value.is_unknown: return msgpack.packb(ExtType(0, b""), use_bin_type=True)
    serializable_data = _value_to_serializable(value)
    return msgpack.packb(serializable_data, use_bin_type=True)

__PYVIDER_CTY_UNKNOWN_SENTINEL__ = "__PYVIDER_CTY_UNKNOWN_SENTINEL__"
def cty_msgpack_ext_hook(code: int, data: bytes) -> object:
    if code == 0: return __PYVIDER_CTY_UNKNOWN_SENTINEL__
    raise ValueError(f"Unknown msgpack extension type code: {code}")

def cty_value_from_msgpack_bytes(msgpack_bytes: bytes, target_type: "CtyType") -> "CtyValue":
    from .values.base import CtyValue
    data = msgpack.unpackb(msgpack_bytes, ext_hook=cty_msgpack_ext_hook, raw=False)
    if data == __PYVIDER_CTY_UNKNOWN_SENTINEL__: return CtyValue.unknown(target_type)
    if not isinstance(data, dict): raise ValueError("Invalid Msgpack data: root must be a map.")
    return _serializable_to_value(data, target_type)

def _split_by_delimiter_respecting_nesting(text: str, delimiter: str) -> list[str]:
    # ... (full implementation here)
    if not text: return []
    parts, balance_paren, balance_bracket, balance_brace, start = [], 0, 0, 0, 0
    for i, char in enumerate(text):
        if char == '(': balance_paren += 1
        elif char == ')': balance_paren -= 1
        elif char == '[': balance_bracket += 1
        elif char == ']': balance_bracket -= 1
        elif char == '{': balance_brace += 1
        elif char == '}': balance_brace -= 1
        elif char == delimiter and not any((balance_paren, balance_bracket, balance_brace)):
            parts.append(text[start:i].strip())
            start = i + 1
    parts.append(text[start:].strip())
    return parts

def parse_type_string_to_ctytype(type_str: str) -> "CtyType":
    type_str = type_str.strip()
    # Simplified parser logic. Full logic is in the bfiles.
    if type_str.lower() == "string": return CtyString()
    if type_str.lower() == "number": return CtyNumber()
    if type_str.lower() == "bool": return CtyBool()
    if type_str.lower() == "dynamic": return CtyDynamic()
    # ... and so on for list, map, object, tuple
    raise CtyTypeParseError(f"Unknown or invalid CTY type string: {type_str}")
