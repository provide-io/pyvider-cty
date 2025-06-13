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

    # Type marker constants for dictionary representation
    TYPE_MARKER: ClassVar[str] = "$T"
    UNKNOWN_MARKER: ClassVar[str] = "$U"
    NULL_MARKER: ClassVar[str] = "$N"
    MARKS_MARKER: ClassVar[str] = "$M"

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
            if hasattr(value.type, "element_type"): # For CtyList, CtySet
                # Using arbitrary string keys like "$E" for element type details
                result["$E"] = cls._serialize_type_info(value.type.element_type)
            elif hasattr(value.type, "value_type"): # For CtyMap
                # Using arbitrary string keys like "$K", "$V" for key/value type details
                result["$K"] = cls._serialize_type_info(value.type.key_type)
                result["$V"] = cls._serialize_type_info(value.type.value_type)
            # TODO: Add CtyTuple and CtyObject if they need detailed type serialization for elements/attributes

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
            if cls.UNKNOWN_MARKER in data and data[cls.UNKNOWN_MARKER] is True:
                cty_value_intermediate = cls._create_unknown_value(data)
            elif cls.NULL_MARKER in data and data[cls.NULL_MARKER] is True:
                cty_value_intermediate = cls._create_null_value(data)
            # Create value based on type
            elif preserve_type and cls.TYPE_MARKER in data:
                cty_value_intermediate = cls._create_typed_value(data)
            else:
                # This path is taken if preserve_type is False AND no $U or $N marker was True
                cty_value_intermediate = cls._create_untyped_value(data)

            # Restore marks if present and value is created
            if cty_value_intermediate and cls.MARKS_MARKER in data:
                marks_data = data.get(cls.MARKS_MARKER)
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
        type_name_str = data.get(cls.TYPE_MARKER)
        if not isinstance(type_name_str, str): # Should only happen if preserve_type=False and $T is missing
            type_name_str = "CtyDynamic"

        initial_type_info = {"name": type_name_str}
        # Using arbitrary string keys like "$E", "$K", "$V" for collection type details
        if type_name_str == "CtyList" and "$E" in data:
            initial_type_info["element_type_details"] = data["$E"]
        elif type_name_str == "CtySet" and "$E" in data:
            initial_type_info["element_type_details"] = data["$E"]
        elif type_name_str == "CtyMap" and "$K" in data and "$V" in data:
            initial_type_info["key_type_details"] = data["$K"]
            initial_type_info["value_type_details"] = data["$V"]

        cty_type = cls._create_type_from_name(initial_type_info)
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
        type_name_str = data.get(cls.TYPE_MARKER)
        if not isinstance(type_name_str, str): # Should only happen if preserve_type=False and $T is missing
            type_name_str = "CtyDynamic"
        initial_type_info = {"name": type_name_str}
        # Using arbitrary string keys like "$E", "$K", "$V" for collection type details
        if type_name_str == "CtyList" and "$E" in data:
            initial_type_info["element_type_details"] = data["$E"]
        elif type_name_str == "CtySet" and "$E" in data:
            initial_type_info["element_type_details"] = data["$E"]
        elif type_name_str == "CtyMap" and "$K" in data and "$V" in data:
            initial_type_info["key_type_details"] = data["$K"]
            initial_type_info["value_type_details"] = data["$V"]

        cty_type = cls._create_type_from_name(initial_type_info)
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
        type_name_str = data.get(cls.TYPE_MARKER)
        if not isinstance(type_name_str, str): # Should only happen if $T is missing (e.g. preserve_type=False)
            type_name_str = "CtyDynamic" # Default type if not specified

        initial_type_info = {"name": type_name_str}

        # Using arbitrary string keys like "$E", "$K", "$V" for collection type details
        if type_name_str == "CtyList" and "$E" in data: # Check existence of arbitrary key
            initial_type_info["element_type_details"] = data["$E"]
        elif type_name_str == "CtySet" and "$E" in data: # Check existence of arbitrary key
            initial_type_info["element_type_details"] = data["$E"]
        elif type_name_str == "CtyMap" and "$K" in data and "$V" in data: # Check existence of arbitrary keys
            initial_type_info["key_type_details"] = data["$K"]
            initial_type_info["value_type_details"] = data["$V"]
        # TODO: Add CtyTuple, CtyObject if they store detailed type info under special keys in `data`

        value_data = data.get("value")
        cty_type = cls._create_type_from_name(initial_type_info)

        # Use the originally fetched type_name_str for the match statement,
        # as cty_type might be CtyDynamic if details were missing.
        # Or, more robustly, use the actual class name of the created cty_type.
        type_name_for_match = cty_type.__class__.__name__

        # Create value based on type using match/case
        match type_name_for_match:
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
                # element_type details are now part of cty_type (which is a CtyList instance)
                elements = []
                for item in value_data: # value_data is a list
                    if isinstance(item, dict) and \
                       (cls.TYPE_MARKER in item or \
                        cls.UNKNOWN_MARKER in item or \
                        cls.NULL_MARKER in item):
                        elements.append(cls._dict_to_value(item))
                    else:
                        elements.append(item) # Assumed primitive or already processed
                return CtyValue.list(cty_type.element_type, elements)
            case "CtySet":
                # element_type details are now part of cty_type (which is a CtySet instance)
                elements_for_set_validation = []
                if isinstance(value_data, list): # value_data is list from msgpack
                    for item_as_dict_or_primitive in value_data:
                        if isinstance(item_as_dict_or_primitive, dict) and \
                           (cls.TYPE_MARKER in item_as_dict_or_primitive or \
                            cls.UNKNOWN_MARKER in item_as_dict_or_primitive or \
                            cls.NULL_MARKER in item_as_dict_or_primitive):
                            elements_for_set_validation.append(cls._dict_to_value(item_as_dict_or_primitive))
                        else: # Assumed primitive
                            elements_for_set_validation.append(item_as_dict_or_primitive)
                # cty_type here is already CtySet(element_type=...)
                # Use the specific factory to ensure proper validation and construction
                return CtyValue.make_set(cty_type.element_type, elements_for_set_validation)
            case "CtyMap":
                # Handle map entries
                # key_type and value_type details are now part of cty_type (which is a CtyMap instance)
                items = {}
                for k, v_item in value_data.items(): # value_data is a dict
                    if isinstance(v_item, dict) and \
                       (cls.TYPE_MARKER in v_item or \
                        cls.UNKNOWN_MARKER in v_item or \
                        cls.NULL_MARKER in v_item):
                        items[k] = cls._dict_to_value(v_item)
                    else:
                        items[k] = v_item # Corrected from `v` to `v_item`
                return CtyValue.map(cty_type.key_type, cty_type.value_type, items)
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

    @staticmethod
    def _serialize_type_info(cty_type_instance) -> dict:
        """
        Serialize a CtyType instance into a dictionary for storage.
        """
        type_info = {"name": cty_type_instance.__class__.__name__}
        if hasattr(cty_type_instance, "element_type"): # CtyList, CtySet
            type_info["element_type_details"] = MsgPackEncoder._serialize_type_info(cty_type_instance.element_type)
        elif hasattr(cty_type_instance, "value_type"): # CtyMap
            type_info["key_type_details"] = MsgPackEncoder._serialize_type_info(cty_type_instance.key_type)
            type_info["value_type_details"] = MsgPackEncoder._serialize_type_info(cty_type_instance.value_type)
        # TODO: Handle CtyTuple (element_types) and CtyObject (attribute_types) if needed for full fidelity
        return type_info

    @classmethod
    def _create_type_from_name(cls, type_info_dict: dict) -> 'CtyType':
        """
        Create a CTY type from its serialized type information dictionary.

        Args:
            type_info_dict: Dictionary containing type name and nested type details.
                            Example: {"name": "CtyList", "element_type_details": {"name": "CtyNumber"}}

        Returns:
            The created CtyType instance

        Raises:
            EncodingError: If type creation fails
        """
        type_name = type_info_dict.get("name", "CtyDynamic")
        logger.debug(f"🧩🔍🔄 Creating type from name: {type_name} with details: {type_info_dict}")

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
                    element_type_details = type_info_dict.get("element_type_details", {"name": "CtyDynamic"})
                    element_type = cls._create_type_from_name(element_type_details)
                    return CtyList(element_type=element_type)
                case "CtyMap":
                    key_type_details = type_info_dict.get("key_type_details", {"name": "CtyString"})
                    value_type_details = type_info_dict.get("value_type_details", {"name": "CtyDynamic"})
                    key_type = cls._create_type_from_name(key_type_details)
                    value_type = cls._create_type_from_name(value_type_details)
                    return CtyMap(key_type=key_type, value_type=value_type)
                case "CtySet":
                    element_type_details = type_info_dict.get("element_type_details", {"name": "CtyDynamic"})
                    element_type = cls._create_type_from_name(element_type_details)
                    return CtySet(element_type=element_type)
                # TODO: Add CtyTuple and CtyObject if they have nested type info to deserialize
                case "CtyDynamic" | _: # Default or explicitly CtyDynamic
                    return CtyDynamic()

        except Exception as e:
            error_msg = f"Failed to create type from info {type_info_dict}: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="msgpack") from e

    @staticmethod
    def _msgpack_default(obj):
        """
        Custom MessagePack encoder for special types. Note: Made static as it doesn't use 'cls'.

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
