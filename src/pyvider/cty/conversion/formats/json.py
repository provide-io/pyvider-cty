#
# pyvider/cty/conversion/formats/json.py
#

"""
JSON encoder for CTY wire format.

This module provides a comprehensive implementation of the FormatEncoder
interface for JSON serialization. It handles conversion between CTY values
and JSON-encoded bytes with full preservation of type information, state,
and other metadata.

The implementation supports both compact and pretty-printed output,
custom encoders for CTY-specific types, and robust error handling.
"""

import json
from decimal import Decimal
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar, Union, cast

from attrs import define, field

from pyvider.telemetry import logger
from pyvider.core.conversion.wire_format import WireFormatType
from pyvider.cty.exceptions import EncodingError
from pyvider.cty.values import CtyValue
# Import Cty types for type checking
from pyvider.cty.types import CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtyDynamic, CtySet, CtyObject, CtyTuple # Added all types for _create_type_from_name
from pyvider.cty.conversion.formats.base import FormatEncoder, register_formatter

T = TypeVar('T')

@register_formatter(WireFormatType.JSON)
class JsonEncoder(FormatEncoder):
    """
    JSON encoder implementation for CTY wire format.

    This class handles serialization and deserialization between CTY values
    and JSON-encoded bytes. It includes special handling for CTY-specific
    concepts like unknown values, null values, marks, and type information.

    The encoder supports both compact and pretty-printed output, and includes
    comprehensive validation and error handling.
    """

    # Type marker constants for encoding
    TYPE_MARKER: ClassVar[str] = "type"
    UNKNOWN_MARKER: ClassVar[str] = "is_unknown"
    NULL_MARKER: ClassVar[str] = "is_null"
    MARKS_MARKER: ClassVar[str] = "marks"

    @classmethod
    def format_type(cls) -> WireFormatType:
        """
        Get the wire format type for this encoder.

        Returns:
            WireFormatType.JSON
        """
        return WireFormatType.JSON

    @classmethod
    def encode(cls, value: Any, **options) -> bytes:
        """
        Encode a CTY value to JSON bytes.
        """
        logger.debug(f"🧩📝🔄 Encoding to JSON: {type(value).__name__}")
        indent = options.get('indent')
        sort_keys = options.get('sort_keys', False)
        preserve_type = options.get('preserve_type', True)
        compact = options.get('compact', True)

        try:
            if not isinstance(value, CtyValue):
                error_msg = f"Expected CtyValue, got {type(value).__name__}"
                logger.error(f"🧩📝❌ {error_msg}")
                raise TypeError(error_msg)
            value_dict = cls._value_to_dict(value, preserve_type=preserve_type)
            json_bytes = json.dumps(
                value_dict,
                indent=None if compact else indent,
                sort_keys=sort_keys,
                default=cls._json_default
            ).encode('utf-8')
            logger.debug(f"🧩📝✅ Encoded to {len(json_bytes)} bytes of JSON")
            return json_bytes
        except Exception as e:
            if isinstance(e, EncodingError): raise
            error_msg = f"Failed to encode to JSON: {e}"
            logger.error(f"🧩📝❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="json", data=value) from e

    @classmethod
    def decode(cls, data: bytes, **options) -> Any:
        """
        Decode JSON bytes to a CTY value.
        """
        logger.debug(f"🧩🔍🔄 Decoding from JSON: {len(data)} bytes")
        preserve_type = options.get('preserve_type', True)
        try:
            try:
                json_dict = json.loads(data)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON: {e}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(error_msg, encoding="json", data=data) from e
            result = cls._dict_to_value(json_dict, preserve_type=preserve_type)
            logger.debug(f"🧩🔍✅ Decoded JSON to {type(result).__name__}")
            return result
        except Exception as e:
            if isinstance(e, EncodingError): raise
            error_msg = f"Failed to decode from JSON: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="json", data=data) from e

    @classmethod
    def _value_to_dict(cls, value: CtyValue, preserve_type: bool = True) -> Dict[str, Any]:
        result = {}
        if preserve_type:
            result[cls.TYPE_MARKER] = value.type.__class__.__name__
            if hasattr(value.type, "element_type") and value.type.element_type is not None:
                result["element_type"] = value.type.element_type.__class__.__name__
            elif hasattr(value.type, "value_type"): # CtyMap
                result["key_type"] = value.type.key_type.__class__.__name__
                result["value_type"] = value.type.value_type.__class__.__name__

        if value.is_unknown:
            result[cls.UNKNOWN_MARKER] = True
            return result
        if value.is_null:
            result[cls.NULL_MARKER] = True
            return result

        raw_internal_value = value.value
        is_current_value_collection = isinstance(value.type, (CtyList, CtyMap))

        def recursively_encode_value(item: Any, is_direct_collection_member: bool = False) -> Any:
            # Types are already imported at module level. No need for local import here if module level is sufficient.
            # from pyvider.cty.types import CtyDynamic, CtyString, CtyNumber, CtyBool

            logger.debug(f"RECURSE_ENCODE: item={item!r}, item_type={type(item)!r}, is_direct_collection_member={is_direct_collection_member}")

            if isinstance(item, CtyValue):
                # Handle unknown and null CtyValues first
                if item.is_unknown:
                    logger.debug(f"RECURSE_ENCODE: item is unknown.")
                    temp_res = {cls.UNKNOWN_MARKER: True}
                    if preserve_type: # preserve_type is from the outer scope
                        temp_res[cls.TYPE_MARKER] = item.type.__class__.__name__
                    return temp_res
                if item.is_null:
                    logger.debug(f"RECURSE_ENCODE: item is null.")
                    temp_res = {cls.NULL_MARKER: True}
                    if preserve_type: # preserve_type is from the outer scope
                        temp_res[cls.TYPE_MARKER] = item.type.__class__.__name__
                    return temp_res

                logger.debug(f"RECURSE_ENCODE: CtyValue detected. item.type={item.type!r}, item.value={item.value!r}, item.is_unknown={item.is_unknown}, item.is_null={item.is_null}")

                # Now, the simplification logic
                if is_direct_collection_member:
                    logger.debug(f"RECURSE_ENCODE: is_direct_collection_member is True. item.type={item.type!r}")
                    actual_value = item.value # Raw Python value
                    logger.debug(f"RECURSE_ENCODE: actual_value={actual_value!r}, type(actual_value)={type(actual_value)!r}")

                    is_item_type_dynamic = isinstance(item.type, CtyDynamic)
                    logger.debug(f"RECURSE_ENCODE: isinstance(item.type, CtyDynamic) = {is_item_type_dynamic}")

                    is_actual_value_primitive = isinstance(actual_value, (str, int, float, bool, Decimal))
                    logger.debug(f"RECURSE_ENCODE: isinstance(actual_value, PyPrimitive) = {is_actual_value_primitive}")

                    if is_item_type_dynamic and is_actual_value_primitive:
                        logger.debug(f"RECURSE_ENCODE: Simplifying CtyDynamic with primitive.")
                        if isinstance(actual_value, Decimal):
                            return str(actual_value)
                        return actual_value

                    is_item_type_primitive = isinstance(item.type, (CtyString, CtyNumber, CtyBool))
                    logger.debug(f"RECURSE_ENCODE: isinstance(item.type, CtyPrimitive) = {is_item_type_primitive}")

                    if is_item_type_primitive:
                        logger.debug(f"RECURSE_ENCODE: Simplifying direct CtyPrimitive.")
                        if isinstance(actual_value, Decimal):
                            return str(actual_value)
                        return actual_value

                    logger.debug(f"RECURSE_ENCODE: Did not meet simplification criteria for direct collection member.")

                logger.debug(f"RECURSE_ENCODE: Defaulting to full cls._value_to_dict for CtyValue item: {item!r}")
                return cls._value_to_dict(item, preserve_type) # Fallback

            elif isinstance(item, dict):
                logger.debug(f"RECURSE_ENCODE: item is dict, processing items...")
                return {k: recursively_encode_value(v, is_direct_collection_member=(is_current_value_collection and isinstance(value.type, CtyMap))) for k, v in item.items()}
            elif isinstance(item, (list, tuple)):
                logger.debug(f"RECURSE_ENCODE: item is list/tuple, processing elements...")
                return [recursively_encode_value(elem, is_direct_collection_member=(is_current_value_collection and isinstance(value.type, CtyList))) for elem in item]
            elif isinstance(item, Decimal):
                logger.debug(f"RECURSE_ENCODE: item is Decimal, converting to str.")
                return str(item)

            logger.debug(f"RECURSE_ENCODE: item is raw primitive, returning as is: {item!r}")
            return item

        result["value"] = recursively_encode_value(raw_internal_value, is_direct_collection_member=is_current_value_collection)

        if value._marks:
            result[cls.MARKS_MARKER] = sorted([str(m) for m in value._marks])
        return result

    @classmethod
    def _dict_to_value(cls, data: Dict[str, Any], preserve_type: bool = True) -> CtyValue:
        # ... (rest of the file is unchanged from previous correct state) ...
        logger.debug(f"🧩🔍🔄 Converting dictionary to CtyValue")

        try:
            if data.get(cls.UNKNOWN_MARKER, False):
                return cls._create_unknown_value(data)
            if data.get(cls.NULL_MARKER, False):
                return cls._create_null_value(data)
            if preserve_type and cls.TYPE_MARKER in data:
                return cls._create_typed_value(data)
            else:
                return cls._create_untyped_value(data)
        except Exception as e:
            error_msg = f"Failed to convert dictionary to CtyValue: {e}"
            logger.error(f"🧩🔍❌ {error_msg}")
            raise EncodingError(error_msg, encoding="json") from e

    @classmethod
    def _create_unknown_value(cls, data: Dict[str, Any]) -> CtyValue:
        logger.debug("🧩🔍🔄 Creating unknown CtyValue")
        type_name = data.get(cls.TYPE_MARKER, "CtyDynamic")
        cty_type = cls._create_type_from_name(type_name, data)
        return CtyValue.unknown(cty_type)

    @classmethod
    def _create_null_value(cls, data: Dict[str, Any]) -> CtyValue:
        logger.debug("🧩🔍🔄 Creating null CtyValue")
        type_name = data.get(cls.TYPE_MARKER, "CtyDynamic")
        cty_type = cls._create_type_from_name(type_name, data)
        return CtyValue.null(cty_type)

    @classmethod
    def _create_typed_value(cls, data: Dict[str, Any]) -> CtyValue:
        logger.debug("🧩🔍🔄 Creating typed CtyValue")
        type_name = data.get(cls.TYPE_MARKER, "CtyDynamic")
        value_data = data.get("value")
        cty_type = cls._create_type_from_name(type_name, data)
        match type_name:
            case "CtyString": return CtyValue.string(value_data)
            case "CtyNumber":
                if isinstance(value_data, str): return CtyValue.number(Decimal(value_data))
                return CtyValue.number(value_data)
            case "CtyBool": return CtyValue.bool(value_data)
            case "CtyList":
                element_type = cls._create_type_from_name(data.get("element_type", "CtyDynamic"), {})
                elements = []
                if isinstance(value_data, list):
                    for item in value_data:
                        if isinstance(item, dict) and (cls.TYPE_MARKER in item or cls.UNKNOWN_MARKER in item or cls.NULL_MARKER in item):
                            elements.append(cls._dict_to_value(item))
                        else: elements.append(item)
                return CtyValue.list(element_type, elements)
            case "CtyMap":
                key_type = cls._create_type_from_name(data.get("key_type", "CtyString"), {})
                value_type = cls._create_type_from_name(data.get("value_type", "CtyDynamic"), {})
                items = {}
                if isinstance(value_data, dict):
                    for k, v in value_data.items():
                        if isinstance(v, dict) and (cls.TYPE_MARKER in v or cls.UNKNOWN_MARKER in v or cls.NULL_MARKER in v):
                            items[k] = cls._dict_to_value(v)
                        else: items[k] = v
                return CtyValue.map(key_type, value_type, items)
            case _: return cty_type.validate(value_data)

    @classmethod
    def _create_untyped_value(cls, data: Dict[str, Any]) -> CtyValue:
        logger.debug("🧩🔍🔄 Creating untyped CtyValue")
        value = data.get("value")
        match value:
            case bool(): return CtyValue.bool(value)
            case int() | float(): return CtyValue.number(value)
            case str(): return CtyValue.string(value)
            case list(): return CtyValue.list(CtyDynamic(), value)
            case dict(): return CtyValue.map(CtyString(), CtyDynamic(), value)
            case None: return CtyValue.null(CtyDynamic())
            case _:
                error_msg = f"Cannot infer type for value: {value}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(f"Cannot infer type for value: {value}", encoding="json")

    @classmethod
    def _create_type_from_name(cls, type_name: str, data: Dict[str, Any]) -> 'CtyType':
        logger.debug(f"🧩🔍🔄 Creating type from name: {type_name}")
        try:
            from pyvider.cty.types import CtySet, CtyObject, CtyTuple # Already imported: CtyBool, CtyNumber, CtyString, CtyList, CtyMap, CtyDynamic
            match type_name:
                case "CtyBool": return CtyBool()
                case "CtyNumber": return CtyNumber()
                case "CtyString": return CtyString()
                case "CtyList":
                    element_type_name = data.get("element_type", "CtyDynamic")
                    element_type = cls._create_type_from_name(element_type_name, {})
                    return CtyList(element_type=element_type)
                case "CtyMap":
                    key_type_name = data.get("key_type", "CtyString")
                    value_type_name = data.get("value_type", "CtyDynamic")
                    key_type = cls._create_type_from_name(key_type_name, {})
                    value_type = cls._create_type_from_name(value_type_name, {})
                    return CtyMap(key_type=key_type, value_type=value_type)
                case "CtySet":
                    element_type_name = data.get("element_type", "CtyDynamic")
                    element_type = cls._create_type_from_name(element_type_name, {})
                    return CtySet(element_type=element_type)
                case "CtyDynamic" | _: return CtyDynamic()
        except Exception as e:
            error_msg = f"Failed to create type from name {type_name}: {e}"
            logger.error(f"🧩🔍❌ {error_msg}")
            raise EncodingError(error_msg, encoding="json") from e

    @classmethod
    def _json_default(cls, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

# 🐍🏗️🐣
