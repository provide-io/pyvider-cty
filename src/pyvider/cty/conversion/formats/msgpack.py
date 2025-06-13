#
# pyvider/cty/conversion/formats/msgpack.py
#

"""
MessagePack encoder for CTY wire format.

This module provides a comprehensive implementation of the FormatEncoder
interface for MessagePack serialization. It handles conversion between CTY values
and MessagePack-encoded bytes with full preservation of type information, state,
and other metadata.

The implementation emphasizes compact binary representation while maintaining
the same fidelity as the JSON encoder, with specialized encoding for CTY-specific
types and thorough error handling.
"""

import msgpack
from decimal import Decimal
from typing import ClassVar, Type, TypeVar, cast

from attrs import define, field

from pyvider.telemetry import logger
from pyvider.cty.conversion.wire import WireFormatType
from pyvider.cty.exceptions import EncodingError
from pyvider.cty.values import CtyValue
from pyvider.cty.conversion.formats import FormatEncoder, register_formatter

T = TypeVar('T')

@register_formatter(WireFormatType.MSGPACK)
class MsgPackEncoder(FormatEncoder):
    """
    MessagePack encoder implementation for CTY wire format.

    This class handles serialization and deserialization between CTY values
    and MessagePack-encoded bytes. It provides a compact binary representation
    with full preservation of type information, state, and marks.

    The encoder uses a similar structure to the JSON encoder but optimized
    for MessagePack's binary format, with specialized handling for CTY-specific
    concepts.
    """

    # Type marker constants for binary format
    TYPE_MARKER: ClassVar[bytes] = b"$T"
    UNKNOWN_MARKER: ClassVar[bytes] = b"$U"
    NULL_MARKER: ClassVar[bytes] = b"$N"
    MARKS_MARKER: ClassVar[bytes] = b"$M"

    @classmethod
    def format_type(cls) -> WireFormatType:
        """
        Get the wire format type for this encoder.

        Returns:
            WireFormatType.MSGPACK
        """
        return WireFormatType.MSGPACK

    @classmethod
    def encode(cls, value: object, **options) -> bytes:
        """
        Encode a CTY value to MessagePack bytes.

        Converts a CTY value to a MessagePack-encoded byte string, preserving
        type information, value state (known/unknown/null), and marks.

        Args:
            value: The value to encode (CtyValue or compatible)
            **options: Encoding options including:
                - preserve_type: Whether to include type information (default: True)
                - use_bin_type: Whether to use binary type (default: True)

        Returns:
            MessagePack-encoded bytes

        Raises:
            EncodingError: If encoding fails
        """
        logger.debug(f"🧩📝🔄 Encoding to MessagePack: {type(value).__name__}")

        # Process options
        preserve_type = options.get('preserve_type', True)
        use_bin_type = options.get('use_bin_type', True)

        try:
            # Ensure we have a CtyValue
            if not isinstance(value, CtyValue):
                error_msg = f"Expected CtyValue, got {type(value).__name__}"
                logger.error(f"🧩📝❌ {error_msg}")
                raise TypeError(error_msg)

            # Convert to serializable dictionary
            value_dict = cls._value_to_dict(value, preserve_type=preserve_type)

            # Encode to MessagePack
            msgpack_bytes = msgpack.packb(
                value_dict,
                use_bin_type=use_bin_type,
                default=cls._msgpack_default
            )

            logger.debug(f"🧩📝✅ Encoded to {len(msgpack_bytes)} bytes of MessagePack")
            return msgpack_bytes

        except Exception as e:
            if isinstance(e, EncodingError):
                raise

            error_msg = f"Failed to encode to MessagePack: {e}"
            logger.error(f"🧩📝❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="msgpack", data=value) from e

    @classmethod
    def decode(cls, data: bytes, **options) -> object:
        """
        Decode MessagePack bytes to a CTY value.

        Converts MessagePack-encoded bytes back into a CTY value, restoring
        type information, value state, and marks if present.

        Args:
            data: The MessagePack bytes to decode
            **options: Decoding options including:
                - preserve_type: Whether to restore type information (default: True)
                - raw: Whether raw bytes should be returned as bytes (default: False)

        Returns:
            The decoded CTY value

        Raises:
            EncodingError: If decoding fails
        """
        logger.debug(f"🧩🔍🔄 Decoding from MessagePack: {len(data)} bytes")

        # Process options
        preserve_type = options.get('preserve_type', True)
        raw = options.get('raw', False)

        try:
            # Decode MessagePack
            try:
                msgpack_dict = msgpack.unpackb(data, raw=raw)
            except Exception as e:
                error_msg = f"Invalid MessagePack: {e}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(error_msg, encoding="msgpack", data=data) from e

            # Convert from dictionary to CtyValue
            result = cls._dict_to_value(msgpack_dict, preserve_type=preserve_type)

            logger.debug(f"🧩🔍✅ Decoded MessagePack to {type(result).__name__}")
            return result

        except Exception as e:
            if isinstance(e, EncodingError):
                raise

            error_msg = f"Failed to decode from MessagePack: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="msgpack", data=data) from e

    @classmethod
    def _value_to_dict(cls, value: CtyValue, preserve_type: bool = True) -> dict[str, object]:
        """
        Convert a CTY value to a serializable dictionary.

        Args:
            value: The CTY value to convert
            preserve_type: Whether to include type information

        Returns:
            Serializable dictionary representation
        """
        logger.debug(f"🧩📝🔄 Converting CtyValue to dictionary for MessagePack")

        result = {}

        # Add type information
        if preserve_type:
            result[cls.TYPE_MARKER] = value.type.__class__.__name__

            # Add collection type details if applicable
            if hasattr(value.type, "element_type"):
                result[b"$E"] = value.type.element_type.__class__.__name__
            elif hasattr(value.type, "value_type"):
                result[b"$K"] = value.type.key_type.__class__.__name__
                result[b"$V"] = value.type.value_type.__class__.__name__

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
                # Convert Decimal to string for MessagePack compatibility
                result["value"] = str(value.value)

            case frozenset(): # Handle CtySet internal value
                # Ensure elements within the set (now a list) are also processed if they are CtyValues
                result["value"] = [
                    cls._value_to_dict(v, preserve_type) if isinstance(v, CtyValue) else v
                    for v in list(value.value) # Convert frozenset to list then process
                ]
            case _: # Wildcard must be last
                # Use the raw value for primitives
                result["value"] = value.value

        # Add marks if present
        marks = getattr(value, "_marks", None)
        if marks:
            result[cls.MARKS_MARKER] = list(str(m) for m in marks)

        return result

    @classmethod
    def _dict_to_value(cls, data: dict[str, object], preserve_type: bool = True) -> CtyValue:
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
        logger.debug(f"🧩🔍🔄 Converting MessagePack dictionary to CtyValue")

        try:
            cty_value_intermediate = None # Ensure cty_value_intermediate is defined in all paths
            # Handle special states
            if cls.UNKNOWN_MARKER in data:
                cty_value_intermediate = cls._create_unknown_value(data)
            elif cls.NULL_MARKER in data:
                cty_value_intermediate = cls._create_null_value(data)
            # Create value based on type
            elif preserve_type and cls.TYPE_MARKER in data:
                cty_value_intermediate = cls._create_typed_value(data)
            else:
                cty_value_intermediate = cls._create_untyped_value(data)

            # Restore marks if present and value is created
            if cty_value_intermediate and cls.MARKS_MARKER in data:
                marks_data = data.get(cls.MARKS_MARKER) # Use .get for safety
                if isinstance(marks_data, list):
                    # Assuming marks are strings, if not, adjust Mark class or storage
                    cty_value_intermediate = cty_value_intermediate.with_marks(tuple(str(m) for m in marks_data))

            if cty_value_intermediate is None: # Should not happen if logic is correct
                # Log details of data that caused failure
                logger.error(f"🧩🔍❌ Failed to create CtyValue. Data was: {data}")
                raise EncodingError("Failed to create CtyValue from dictionary data.", encoding="msgpack")

            return cty_value_intermediate

        except Exception as e:
            # Log details of data that caused failure, if not already an EncodingError with data
            if not (isinstance(e, EncodingError) and hasattr(e, 'data') and e.data):
                 logger.error(f"🧩🔍❌ Error during CtyValue conversion. Data was: {data}", exc_info=True)
            else:
                 logger.error(f"🧩🔍❌ Error during CtyValue conversion: {e}", exc_info=True)
            raise EncodingError(f"Failed to convert dictionary to CtyValue: {e}", encoding="msgpack") from e

    @classmethod
    def _create_unknown_value(cls, data: dict[str, object]) -> CtyValue:
        """
        Create an unknown CTY value from dictionary data.

        Args:
            data: Dictionary containing type information

        Returns:
            Unknown CtyValue of the specified type
        """
        logger.debug("🧩🔍🔄 Creating unknown CtyValue from MessagePack data")

        # Get type information
        type_name = data.get(cls.TYPE_MARKER, "CtyDynamic")

        # Create appropriate CtyType
        cty_type = cls._create_type_from_name(type_name, data)

        # Create unknown value
        return CtyValue.unknown(cty_type)

    @classmethod
    def _create_null_value(cls, data: dict[str, object]) -> CtyValue:
        """
        Create a null CTY value from dictionary data.

        Args:
            data: Dictionary containing type information

        Returns:
            Null CtyValue of the specified type
        """
        logger.debug("🧩🔍🔄 Creating null CtyValue from MessagePack data")

        # Get type information
        type_name = data.get(cls.TYPE_MARKER, "CtyDynamic")

        # Create appropriate CtyType
        cty_type = cls._create_type_from_name(type_name, data)

        # Create null value
        return CtyValue.null(cty_type)

    @classmethod
    def _create_typed_value(cls, data: dict[str, object]) -> CtyValue:
        """
        Create a typed CTY value from dictionary data.

        Args:
            data: Dictionary containing type and value information

        Returns:
            CtyValue of the specified type with the given value
        """
        logger.debug("🧩🔍🔄 Creating typed CtyValue from MessagePack data")

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
                    data.get(b"$E", "CtyDynamic"), {})
                elements = []
                for item in value_data:
                    if isinstance(item, dict) and (cls.TYPE_MARKER in item or 
                                                  cls.UNKNOWN_MARKER in item or 
                                                  cls.NULL_MARKER in item):
                        elements.append(cls._dict_to_value(item))
                    else:
                        elements.append(item)
                return CtyValue.list(element_type, elements)
            case "CtySet":
                element_type = cls._create_type_from_name(
                    data.get(b"$E", "CtyDynamic"), {})
                elements_for_set_validation = []
                if isinstance(value_data, list): # value_data is list from msgpack (e.g., list of dicts or primitives)
                    for item_as_dict_or_primitive in value_data:
                        if isinstance(item_as_dict_or_primitive, dict) and \
                           (cls.TYPE_MARKER in item_as_dict_or_primitive or \
                            cls.UNKNOWN_MARKER in item_as_dict_or_primitive or \
                            cls.NULL_MARKER in item_as_dict_or_primitive):
                            elements_for_set_validation.append(cls._dict_to_value(item_as_dict_or_primitive))
                        else: # Assumed primitive, suitable for element_type.validate() by CtySet.validate
                            elements_for_set_validation.append(item_as_dict_or_primitive)
                # cty_type here is already CtySet(element_type=element_type)
                return CtyValue(cty_type, elements_for_set_validation)
            case "CtyMap":
                # Handle map entries
                key_type = cls._create_type_from_name(
                    data.get(b"$K", "CtyString"), {})
                value_type = cls._create_type_from_name(
                    data.get(b"$V", "CtyDynamic"), {})
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
    def _create_untyped_value(cls, data: dict[str, object]) -> CtyValue:
        """
        Create an untyped CTY value from dictionary data.

        This method infers the appropriate type based on the value.

        Args:
            data: Dictionary containing value information

        Returns:
            CtyValue with inferred type
        """
        logger.debug("🧩🔍🔄 Creating untyped CtyValue from MessagePack data")

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
                raise EncodingError(f"Cannot infer type for value: {value}", encoding="msgpack")

    @classmethod
    def _create_type_from_name(cls, type_name: str, data: dict[str, object]) -> 'CtyType':
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
                    element_type_name = data.get(b"$E", "CtyDynamic")
                    element_type = cls._create_type_from_name(element_type_name, {})
                    return CtyList(element_type=element_type)
                case "CtyMap":
                    key_type_name = data.get(b"$K", "CtyString")
                    value_type_name = data.get(b"$V", "CtyDynamic")
                    key_type = cls._create_type_from_name(key_type_name, {})
                    value_type = cls._create_type_from_name(value_type_name, {})
                    return CtyMap(key_type=key_type, value_type=value_type)
                case "CtySet":
                    element_type_name = data.get(b"$E", "CtyDynamic")
                    element_type = cls._create_type_from_name(element_type_name, {})
                    return CtySet(element_type=element_type)
                case "CtyDynamic" | _:
                    return CtyDynamic()

        except Exception as e:
            error_msg = f"Failed to create type from name {type_name}: {e}"
            logger.error(f"🧩🔍❌ {error_msg}")
            raise EncodingError(error_msg, encoding="msgpack") from e

    @classmethod
    def _msgpack_default(cls, obj):
        """
        Custom MessagePack encoder for special types.

        Args:
            obj: The object to encode

        Returns:
            MessagePack-serializable representation

        Raises:
            TypeError: If object cannot be encoded
        """
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not MessagePack serializable")

# 🐍🏗️🐣
