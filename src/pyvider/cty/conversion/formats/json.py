#!/usr/bin/env python3
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
from pyvider.cty.conversion.formats import FormatEncoder, register_formatter

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

        Converts a CTY value to a JSON-encoded byte string, preserving
        type information, value state (known/unknown/null), and marks.

        Args:
            value: The value to encode (CtyValue or compatible)
            **options: Encoding options including:
                - indent: JSON indentation level (default: None)
                - sort_keys: Whether to sort dictionary keys (default: False)
                - preserve_type: Whether to include type information (default: True)
                - compact: Whether to use compact output (default: True)

        Returns:
            JSON-encoded bytes

        Raises:
            EncodingError: If encoding fails
        """
        logger.debug(f"🧩📝🔄 Encoding to JSON: {type(value).__name__}")

        # Process options
        indent = options.get('indent')
        sort_keys = options.get('sort_keys', False)
        preserve_type = options.get('preserve_type', True)
        compact = options.get('compact', True)

        try:
            # Ensure we have a CtyValue
            if not isinstance(value, CtyValue):
                error_msg = f"Expected CtyValue, got {type(value).__name__}"
                logger.error(f"🧩📝❌ {error_msg}")
                raise TypeError(error_msg)

            # Convert to serializable dictionary
            value_dict = cls._value_to_dict(value, preserve_type=preserve_type)

            # Encode to JSON
            json_bytes = json.dumps(
                value_dict,
                indent=None if compact else indent,
                sort_keys=sort_keys,
                default=cls._json_default
            ).encode('utf-8')

            logger.debug(f"🧩📝✅ Encoded to {len(json_bytes)} bytes of JSON")
            return json_bytes

        except Exception as e:
            if isinstance(e, EncodingError):
                raise

            error_msg = f"Failed to encode to JSON: {e}"
            logger.error(f"🧩📝❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="json", data=value) from e

    @classmethod
    def decode(cls, data: bytes, **options) -> Any:
        """
        Decode JSON bytes to a CTY value.

        Converts JSON-encoded bytes back into a CTY value, restoring
        type information, value state, and marks if present.

        Args:
            data: The JSON bytes to decode
            **options: Decoding options including:
                - preserve_type: Whether to restore type information (default: True)

        Returns:
            The decoded CTY value

        Raises:
            EncodingError: If decoding fails
        """
        logger.debug(f"🧩🔍🔄 Decoding from JSON: {len(data)} bytes")

        # Process options
        preserve_type = options.get('preserve_type', True)

        try:
            # Decode JSON
            try:
                json_dict = json.loads(data)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON: {e}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(error_msg, encoding="json", data=data) from e

            # Convert from dictionary to CtyValue
            result = cls._dict_to_value(json_dict, preserve_type=preserve_type)

            logger.debug(f"🧩🔍✅ Decoded JSON to {type(result).__name__}")
            return result

        except Exception as e:
            if isinstance(e, EncodingError):
                raise

            error_msg = f"Failed to decode from JSON: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="json", data=data) from e

    @classmethod
    def _value_to_dict(cls, value: CtyValue, preserve_type: bool = True) -> Dict[str, Any]:
        """
        Convert a CTY value to a serializable dictionary.

        Args:
            value: The CTY value to convert
            preserve_type: Whether to include type information

        Returns:
            Serializable dictionary representation
        """
        logger.debug(f"🧩📝🔄 Converting CtyValue to dictionary")

        result = {}

        # Add type information
        if preserve_type:
            result[cls.TYPE_MARKER] = value.type.__class__.__name__

            # Add collection type details if applicable
            if hasattr(value.type, "element_type"):
                result["element_type"] = value.type.element_type.__class__.__name__
            elif hasattr(value.type, "value_type"):
                result["key_type"] = value.type.key_type.__class__.__name__
                result["value_type"] = value.type.value_type.__class__.__name__

        # Add state information
        if value.is_unknown:
            result[cls.UNKNOWN_MARKER] = True
            return result

        if value.is_null:
            result[cls.NULL_MARKER] = True
            return result

        # Add value based on type using match/case
        match value.value:
            case dict():
                # For maps, convert keys and values
                serialized_dict = {}
                for k, v in value.value.items():
                    v_dict = cls._value_to_dict(v, preserve_type) if isinstance(v, CtyValue) else v
                    serialized_dict[k] = v_dict
                result["value"] = serialized_dict

            case list():
                # For lists, convert each element
                result["value"] = [
                    cls._value_to_dict(v, preserve_type) if isinstance(v, CtyValue) else v
                    for v in value.value
                ]

            case Decimal():
                # Convert Decimal to string for JSON compatibility
                result["value"] = str(value.value)

            case _:
                # Use the raw value for primitives
                result["value"] = value.value

        # Add marks if present
        marks = getattr(value, "_marks", None)
        if marks:
            result[cls.MARKS_MARKER] = list(str(m) for m in marks)

        return result

    @classmethod
    def _dict_to_value(cls, data: Dict[str, Any], preserve_type: bool = True) -> CtyValue:
        """
        Convert a dictionary to a CTY value.

        Args:
            data: The dictionary to convert
            preserve_type: Whether to restore type information

        Returns:
            Restored CTY value

        Raises:
            EncodingError: If conversion fails
        """
        logger.debug(f"🧩🔍🔄 Converting dictionary to CtyValue")

        try:
            # Handle special states
            if data.get(cls.UNKNOWN_MARKER, False):
                return cls._create_unknown_value(data)

            if data.get(cls.NULL_MARKER, False):
                return cls._create_null_value(data)

            # Create value based on type
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
        """
        Create an unknown CTY value from dictionary data.

        Args:
            data: Dictionary containing type information

        Returns:
            Unknown CtyValue of the specified type
        """
        logger.debug("🧩🔍🔄 Creating unknown CtyValue")

        # Get type information
        type_name = data.get(cls.TYPE_MARKER, "CtyDynamic")

        # Create appropriate CtyType
        cty_type = cls._create_type_from_name(type_name, data)

        # Create unknown value
        return CtyValue.unknown(cty_type)

    @classmethod
    def _create_null_value(cls, data: Dict[str, Any]) -> CtyValue:
        """
        Create a null CTY value from dictionary data.

        Args:
            data: Dictionary containing type information

        Returns:
            Null CtyValue of the specified type
        """
        logger.debug("🧩🔍🔄 Creating null CtyValue")

        # Get type information
        type_name = data.get(cls.TYPE_MARKER, "CtyDynamic")

        # Create appropriate CtyType
        cty_type = cls._create_type_from_name(type_name, data)

        # Create null value
        return CtyValue.null(cty_type)

    @classmethod
    def _create_typed_value(cls, data: Dict[str, Any]) -> CtyValue:
        """
        Create a typed CTY value from dictionary data.

        Args:
            data: Dictionary containing type and value information

        Returns:
            CtyValue of the specified type with the given value
        """
        logger.debug("🧩🔍🔄 Creating typed CtyValue")

        # Get type information
        type_name = data.get(cls.TYPE_MARKER, "CtyDynamic")
        value_data = data.get("value")

        # Create appropriate CtyType
        cty_type = cls._create_type_from_name(type_name, data)

        # Create value based on type using match/case
        match type_name:
            case "CtyString":
                return CtyValue.string(value_data)
            case "CtyNumber":
                # Handle numeric conversions
                if isinstance(value_data, str):
                    from decimal import Decimal
                    return CtyValue.number(Decimal(value_data))
                return CtyValue.number(value_data)
            case "CtyBool":
                return CtyValue.bool(value_data)
            case "CtyList":
                # Handle list elements
                element_type = cls._create_type_from_name(
                    data.get("element_type", "CtyDynamic"), {})
                elements = []
                for item in value_data:
                    if isinstance(item, dict) and (cls.TYPE_MARKER in item or 
                                                  cls.UNKNOWN_MARKER in item or 
                                                  cls.NULL_MARKER in item):
                        elements.append(cls._dict_to_value(item))
                    else:
                        elements.append(item)
                return CtyValue.list(element_type, elements)
            case "CtyMap":
                # Handle map entries
                key_type = cls._create_type_from_name(
                    data.get("key_type", "CtyString"), {})
                value_type = cls._create_type_from_name(
                    data.get("value_type", "CtyDynamic"), {})
                items = {}
                for k, v in value_data.items():
                    if isinstance(v, dict) and (cls.TYPE_MARKER in v or 
                                               cls.UNKNOWN_MARKER in v or 
                                               cls.NULL_MARKER in v):
                        items[k] = cls._dict_to_value(v)
                    else:
                        items[k] = v
                return CtyValue.map(key_type, value_type, items)
            case _:
                # For other types, validate raw value against type
                return cty_type.validate(value_data)

    @classmethod
    def _create_untyped_value(cls, data: Dict[str, Any]) -> CtyValue:
        """
        Create an untyped CTY value from dictionary data.

        This method infers the appropriate type based on the value.

        Args:
            data: Dictionary containing value information

        Returns:
            CtyValue with inferred type
        """
        logger.debug("🧩🔍🔄 Creating untyped CtyValue")

        value = data.get("value")

        # Infer type from value using match/case
        match value:
            case bool():
                return CtyValue.bool(value)
            case int() | float():
                return CtyValue.number(value)
            case str():
                return CtyValue.string(value)
            case list():
                # Handle list with inferred element type
                from pyvider.cty.types import CtyDynamic
                return CtyValue.list(CtyDynamic(), value)
            case dict():
                # Handle dict with inferred key/value types
                from pyvider.cty.types import CtyDynamic, CtyString
                return CtyValue.map(CtyString(), CtyDynamic(), value)
            case None:
                # Null value with dynamic type
                from pyvider.cty.types import CtyDynamic
                return CtyValue.null(CtyDynamic())
            case _:
                error_msg = f"Cannot infer type for value: {value}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(f"Cannot infer type for value: {value}", encoding="json")

    @classmethod
    def _create_type_from_name(cls, type_name: str, data: Dict[str, Any]) -> 'CtyType':
        """
        Create a CTY type from its name.

        Args:
            type_name: The name of the type to create
            data: Additional type information

        Returns:
            The created CtyType

        Raises:
            EncodingError: If type creation fails
        """
        logger.debug(f"🧩🔍🔄 Creating type from name: {type_name}")

        try:
            # Import all types
            from pyvider.cty.types import (
                CtyBool, CtyNumber, CtyString,
                CtyList, CtyMap, CtySet,
                CtyObject, CtyTuple, CtyDynamic,
            )

            # Create appropriate type using match/case
            match type_name:
                case "CtyBool":
                    return CtyBool()
                case "CtyNumber":
                    return CtyNumber()
                case "CtyString":
                    return CtyString()
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
                case "CtyDynamic" | _:
                    return CtyDynamic()

        except Exception as e:
            error_msg = f"Failed to create type from name {type_name}: {e}"
            logger.error(f"🧩🔍❌ {error_msg}")
            raise EncodingError(error_msg, encoding="json") from e

    @classmethod
    def _json_default(cls, obj):
        """
        Custom JSON encoder for special types.

        Args:
            obj: The object to encode

        Returns:
            JSON-serializable representation

        Raises:
            TypeError: If object cannot be encoded
        """
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

# 🐍🏗️🐣
