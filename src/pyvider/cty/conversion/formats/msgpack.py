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

from decimal import Decimal
from typing import ClassVar, TypeVar, cast

import msgpack

from pyvider.cty.codec import CtyTypeParseError  # Corrected import
from pyvider.cty.conversion.formats import FormatEncoder # Remove register_formatter
from pyvider.cty.conversion.wire import WireFormatType, WireFormatRegistry # Import WireFormatRegistry
from pyvider.cty.exceptions import EncodingError
from pyvider.cty.types import CtyType  # Added import
from pyvider.cty.values import CtyValue
from pyvider.telemetry import logger

T = TypeVar("T")


@WireFormatRegistry.register(WireFormatType.MSGPACK) # Use WireFormatRegistry
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
    def encode(cls, value: object, **options: object) -> bytes:
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
        preserve_type = options.get("preserve_type", True)
        use_bin_type = options.get("use_bin_type", True)

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
                value_dict, use_bin_type=use_bin_type, default=cls._msgpack_default
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
    def decode(cls, data: bytes, **options: object) -> object:
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
        preserve_type = options.get("preserve_type", True)
        raw = options.get("raw", False)

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
    def _value_to_dict(
        cls, value: CtyValue, preserve_type: bool = True
    ) -> dict[str, object]:
        """
        Convert a CTY value to a serializable dictionary.

        Args:
            value: The CTY value to convert
            preserve_type: Whether to include type information

        Returns:
            Serializable dictionary representation
        """
        logger.debug("🧩📝🔄 Converting CtyValue to dictionary for MessagePack")

        result = {}

        # Add type information
        if preserve_type:
            result[cls.TYPE_MARKER] = value.type.__class__.__name__

            # Add collection type details if applicable
            if hasattr(value.type, "element_type"):  # For CtyList, CtySet
                # Recursively get type information for nested types
                result[b"$E"] = cls._type_to_dict(value.type.element_type)
            elif hasattr(value.type, "value_type"):  # For CtyMap
                result[b"$K"] = cls._type_to_dict(value.type.key_type)
                result[b"$V"] = cls._type_to_dict(value.type.value_type)
            elif hasattr(value.type, "element_types"):  # For CtyTuple
                result[b"$ET"] = [
                    cls._type_to_dict(et) for et in value.type.element_types
                ]
            elif hasattr(value.type, "attribute_types"):  # For CtyObject
                result[b"$AT"] = {
                    name: cls._type_to_dict(attr_type)
                    for name, attr_type in value.type.attribute_types.items()
                }

        # Add state information
        if value.is_unknown:
            result[cls.UNKNOWN_MARKER] = True
            return result

        if value.is_null:
            result[cls.NULL_MARKER] = True
            return result

        # Add value based on type using match/case
        # Special handling for CtyDynamic wrapping a CtyValue
        if value.type.ctype == "dynamic" and isinstance(value.value, CtyValue):
            result["value"] = cls._value_to_dict(value.value, preserve_type)
        else:
            match value.value:
                case dict():
                    # For maps, convert keys and values
                    serialized_dict = {}
                    for k, v in value.value.items():
                        v_dict = (
                            cls._value_to_dict(v, preserve_type)
                            if isinstance(v, CtyValue)
                            else v
                        )
                        serialized_dict[k] = v_dict
                    result["value"] = serialized_dict

                case list():
                    # For lists, convert each element
                    result["value"] = [
                        cls._value_to_dict(v, preserve_type)
                        if isinstance(v, CtyValue)
                        else v
                        for v in value.value
                    ]

                case Decimal():
                    # Convert Decimal to string for MessagePack compatibility
                    result["value"] = str(value.value)

                case frozenset():  # Handle CtySet internal value
                    # Ensure elements within the set (now a list) are also processed if they are CtyValues
                    result["value"] = [
                        cls._value_to_dict(v, preserve_type)
                        if isinstance(v, CtyValue)
                        else v
                        for v in list(
                            value.value
                        )  # Convert frozenset to list then process
                    ]
                case _:  # Wildcard must be last
                    # Use the raw value for primitives
                    result["value"] = value.value

        # Add marks if present
        marks = getattr(value, "_marks", None)
        if marks:
            result[cls.MARKS_MARKER] = list(str(m) for m in marks)

        return result

    @classmethod
    def _type_to_dict(cls, cty_type_obj: CtyType) -> dict[str, object] | str:
        """
        Convert a CtyType object to a serializable dictionary or string representation.
        """
        type_name = cty_type_obj.__class__.__name__
        if hasattr(cty_type_obj, "element_type"):  # CtyList, CtySet
            return {
                cls.TYPE_MARKER: type_name,
                b"$E": cls._type_to_dict(cty_type_obj.element_type),
            }
        elif hasattr(cty_type_obj, "value_type"):  # CtyMap
            return {
                cls.TYPE_MARKER: type_name,
                b"$K": cls._type_to_dict(cty_type_obj.key_type),
                b"$V": cls._type_to_dict(cty_type_obj.value_type),
            }
        elif hasattr(cty_type_obj, "element_types"):  # CtyTuple
            return {
                cls.TYPE_MARKER: type_name,
                b"$ET": [cls._type_to_dict(et) for et in cty_type_obj.element_types],
            }
        elif hasattr(cty_type_obj, "attribute_types"):  # CtyObject
            return {
                cls.TYPE_MARKER: type_name,
                b"$AT": {
                    name: cls._type_to_dict(attr_type)
                    for name, attr_type in cty_type_obj.attribute_types.items()
                },
            }
        return type_name  # For primitive types or CtyDynamic

    @classmethod
    def _dict_to_value(
        cls, data: dict[str, object], preserve_type: bool = True
    ) -> CtyValue:
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
        logger.debug("🧩🔍🔄 Converting MessagePack dictionary to CtyValue")

        try:
            cty_value_intermediate = (
                None  # Ensure cty_value_intermediate is defined in all paths
            )

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
                    cty_value_intermediate = cty_value_intermediate.with_marks(
                        tuple(str(m) for m in marks_data)
                    )

            if cty_value_intermediate is None:  # Should not happen if logic is correct
                # Log details of data that caused failure
                logger.error(f"🧩🔍❌ Failed to create CtyValue. Data was: {data}")
                raise EncodingError(
                    "Failed to create CtyValue from dictionary data.",
                    encoding="msgpack",
                )

            return cty_value_intermediate

        except Exception as e:
            # Log details of data that caused failure, if not already an EncodingError with data
            if not (isinstance(e, EncodingError) and hasattr(e, "data") and e.data):
                logger.error(
                    f"🧩🔍❌ Error during CtyValue conversion. Data was: {data}",
                    exc_info=True,
                )
            else:
                logger.error(
                    f"🧩🔍❌ Error during CtyValue conversion: {e}", exc_info=True
                )
            raise EncodingError(
                f"Failed to convert dictionary to CtyValue: {e}", encoding="msgpack"
            ) from e

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
        if not isinstance(
            type_name_str, str
        ):  # Should only happen if preserve_type=False and $T is missing
            type_name_str = "CtyDynamic"

        initial_type_info = {"name": type_name_str}
        # Using arbitrary string keys like "$E", "$K", "$V" for collection type details
        if (type_name_str == "CtyList" and "$E" in data) or (
            type_name_str == "CtySet" and "$E" in data
        ):
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
        if not isinstance(
            type_name_str, str
        ):  # Should only happen if preserve_type=False and $T is missing
            type_name_str = "CtyDynamic"
        initial_type_info = {"name": type_name_str}
        # Using arbitrary string keys like "$E", "$K", "$V" for collection type details
        if (type_name_str == "CtyList" and "$E" in data) or (
            type_name_str == "CtySet" and "$E" in data
        ):
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
        type_name_bytes = data.get(cls.TYPE_MARKER)
        if isinstance(type_name_bytes, bytes):  # raw=True might make keys bytes
            type_name = type_name_bytes.decode("utf-8")
        elif isinstance(type_name_bytes, str):
            type_name = type_name_bytes
        else:  # Default or missing
            type_name = "CtyDynamic"

        # value_data could be under "value" or b"value" if raw=True
        value_data = data.get(
            "value", data.get(b"value")
        )  # Ensured byte key is also checked

        initial_type_info = {
            cls.TYPE_MARKER: type_name
        }  # Use actual $T marker, and type_name

        # Add collection details to initial_type_info using the keys _create_type_from_name expects
        # These keys ($E, $K, $V etc.) are typically bytes after raw msgpack unpack
        if type_name == "CtyList" or type_name == "CtySet":
            element_details = data.get(b"$E", data.get("$E"))
            if element_details is not None:
                initial_type_info[b"$E"] = element_details
        elif type_name == "CtyMap":
            key_details = data.get(b"$K", data.get("$K"))
            value_details = data.get(b"$V", data.get("$V"))
            if key_details is not None:
                initial_type_info[b"$K"] = key_details
            if value_details is not None:
                initial_type_info[b"$V"] = value_details
        elif type_name == "CtyTuple":
            et_details = data.get(b"$ET", data.get("$ET"))
            if et_details is not None:
                initial_type_info[b"$ET"] = et_details
        elif type_name == "CtyObject":
            at_details = data.get(b"$AT", data.get("$AT"))
            if at_details is not None:
                initial_type_info[b"$AT"] = at_details

        cty_type = cls._create_type_from_name(initial_type_info)

        # Use type_name directly from data for the match statement, as this is the serialized intent.
        match type_name:
            case "CtyString":
                if isinstance(value_data, bytes):
                    # If raw=True resulted in bytes for a CtyString type,
                    # the test expects it to become CtyDynamic with raw bytes.
                    from pyvider.cty.types import CtyDynamic

                    return CtyValue(CtyDynamic(), value_data)
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
                # cty_type is CtyList(element_type=...) created by _create_type_from_name
                # which correctly used data.get(b"$E") etc.
                elements = []
                if isinstance(value_data, list):
                    for item_data in value_data:
                        # If item_data is a dict representing a CtyValue, convert it
                        if isinstance(item_data, dict) and (
                            cls.TYPE_MARKER in item_data
                            or b"$T" in item_data  # Check both str and bytes keys
                            or cls.UNKNOWN_MARKER in item_data
                            or b"$U" in item_data
                            or cls.NULL_MARKER in item_data
                            or b"$N" in item_data
                        ):
                            elements.append(cls._dict_to_value(item_data))
                        else:  # Primitive or already converted
                            elements.append(item_data)
                return CtyValue(cty_type, elements)
            case "CtySet":
                # cty_type is CtySet(element_type=...)
                elements_for_set_validation = []
                if isinstance(value_data, list):
                    for item_data in value_data:
                        if isinstance(item_data, dict) and (
                            cls.TYPE_MARKER in item_data
                            or b"$T" in item_data
                            or cls.UNKNOWN_MARKER in item_data
                            or b"$U" in item_data
                            or cls.NULL_MARKER in item_data
                            or b"$N" in item_data
                        ):
                            elements_for_set_validation.append(
                                cls._dict_to_value(item_data)
                            )
                        else:
                            elements_for_set_validation.append(item_data)
                return cty_type.validate(
                    elements_for_set_validation
                )  # Use type's validate method
            case "CtyMap":
                # cty_type is CtyMap(key_type=..., value_type=...)
                items = {}
                if isinstance(value_data, dict):
                    for k_bytes_or_str, v_item_data in value_data.items():
                        # Key in msgpack dict could be bytes if raw=True
                        k_str = (
                            k_bytes_or_str.decode("utf-8")
                            if isinstance(k_bytes_or_str, bytes)
                            else k_bytes_or_str
                        )
                        if isinstance(v_item_data, dict) and (
                            cls.TYPE_MARKER in v_item_data
                            or b"$T" in v_item_data
                            or cls.UNKNOWN_MARKER in v_item_data
                            or b"$U" in v_item_data
                            or cls.NULL_MARKER in v_item_data
                            or b"$N" in v_item_data
                        ):
                            items[k_str] = cls._dict_to_value(v_item_data)
                        else:  # Primitive or already converted
                            items[k_str] = v_item_data
                return CtyValue(cty_type, items)
            case "CtyTuple":
                # cty_type is CtyTuple(element_types=[...])
                elements = []
                if isinstance(value_data, list):
                    for item_data in value_data:
                        if isinstance(item_data, dict) and (
                            cls.TYPE_MARKER in item_data
                            or b"$T" in item_data
                            or cls.UNKNOWN_MARKER in item_data
                            or b"$U" in item_data
                            or cls.NULL_MARKER in item_data
                            or b"$N" in item_data
                        ):
                            elements.append(cls._dict_to_value(item_data))
                        else:  # Primitive or already converted
                            elements.append(item_data)
                return CtyValue(cty_type, elements)
            case "CtyObject":
                # cty_type is CtyObject(attribute_types={...})
                attributes = {}
                if isinstance(value_data, dict):
                    for (
                        attr_name_bytes_or_str,
                        attr_val_item_data,
                    ) in value_data.items():
                        attr_name_str = (
                            attr_name_bytes_or_str.decode("utf-8")
                            if isinstance(attr_name_bytes_or_str, bytes)
                            else attr_name_bytes_or_str
                        )
                        if isinstance(attr_val_item_data, dict) and (
                            cls.TYPE_MARKER in attr_val_item_data
                            or b"$T" in attr_val_item_data
                            or cls.UNKNOWN_MARKER in attr_val_item_data
                            or b"$U" in attr_val_item_data
                            or cls.NULL_MARKER in attr_val_item_data
                            or b"$N" in attr_val_item_data
                        ):
                            attributes[attr_name_str] = cls._dict_to_value(
                                attr_val_item_data
                            )
                        else:  # Primitive or already converted
                            attributes[attr_name_str] = attr_val_item_data
                return CtyValue(cty_type, attributes)
            case "CtyDynamic":
                # If the declared type is CtyDynamic, the value_data might be a serialized CtyValue.
                # Attempt to deserialize it first.
                processed_value_data = value_data
                if isinstance(value_data, dict) and (
                    cls.TYPE_MARKER in value_data
                    or b"$T" in value_data  # Check both str and bytes keys
                    or cls.UNKNOWN_MARKER in value_data
                    or b"$U" in value_data
                    or cls.NULL_MARKER in value_data
                    or b"$N" in value_data
                ):
                    try:
                        # Try to convert dict back to CtyValue if it looks like one
                        processed_value_data = cls._dict_to_value(
                            value_data, preserve_type=True
                        )
                    except Exception:
                        # If it fails, proceed with value_data as is (it might be a raw dict for dynamic)
                        logger.debug(
                            f"🧩🔍🔄 CtyDynamic: Failed to deserialize inner value, using raw: {value_data}"
                        )
                        pass
                return cty_type.validate(
                    processed_value_data
                )  # CtyDynamic.validate will handle it
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

        value = data.get(
            "value", data.get(b"value")
        )  # Check for string "value" then bytes b"value"

        # Infer type from value using match/case
        match value:
            case bool():
                return CtyValue.bool(value)
            case int() | float():
                return CtyValue.number(value)
            case str():
                return CtyValue.string(value)
            case bytes():  # Handle bytes for raw=True decoding
                from pyvider.cty.types import CtyDynamic

                return CtyValue(CtyDynamic(), value)
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
                raise EncodingError(
                    f"Cannot infer type for value: {value}", encoding="msgpack"
                )

    @classmethod
    # TODO: This method has the same name as the one above.
    # This is a redefinition and relies on Python's runtime behavior for method overloading,
    # which can be confusing. Consider renaming for clarity.
    def _create_type_from_name(  # type: ignore[no-redef]
        cls, type_info_dict: dict[str | bytes, object] | str | bytes
    ) -> "CtyType":
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
        logger.debug(f"🧩🔍🔄 Creating type from info: {type_info_dict}")

        try:
            # Import all types
            from pyvider.cty.types import (
                CtyBool,
                CtyDynamic,
                CtyList,
                CtyMap,
                CtyNumber,
                CtyObject,
                CtySet,
                CtyString,
                CtyTuple,
                CtyType,
            )

            data_source: dict[str | bytes, object]  # Define data_source type hint

            if isinstance(type_info_dict, bytes):  # Handle bytes from raw unpacking
                type_name_str = type_info_dict.decode("utf-8")
                data_source = {}
            elif isinstance(type_info_dict, str):  # Primitive type name
                type_name_str = type_info_dict
                data_source = {}
            elif isinstance(type_info_dict, dict):  # Nested type structure
                # Distinguish between the {"name":...} structure from initial calls and {"$T":...} from serialized/recursive calls
                if (
                    "name" in type_info_dict
                    and cls.TYPE_MARKER not in type_info_dict
                    and cls.TYPE_MARKER.encode("utf-8") not in type_info_dict
                ):
                    type_name_str = type_info_dict["name"]
                else:  # It's a serialized type dict with cls.TYPE_MARKER (potentially as bytes)
                    type_name_candidate = type_info_dict.get(
                        cls.TYPE_MARKER,
                        type_info_dict.get(cls.TYPE_MARKER.encode("utf-8")),
                    )
                    if type_name_candidate is None:
                        type_name_candidate = "CtyDynamic"  # Default if no type marker

                    if isinstance(type_name_candidate, bytes):
                        type_name_str = type_name_candidate.decode("utf-8")
                    else:
                        type_name_str = str(type_name_candidate)  # Ensure string
                data_source = type_info_dict  # The dict itself contains further type info for collections
            else:
                logger.error(f"🧩🔍❌ Invalid type_info format: {type_info_dict}")
                raise EncodingError(
                    f"Invalid type_info format: {type_info_dict}", encoding="msgpack"
                )

            # Create appropriate type using match/case
            match type_name_str:
                case "CtyBool":
                    return CtyBool()
                case "CtyNumber":
                    return CtyNumber()
                case "CtyString":
                    return CtyString()
                case "CtyList":
                    element_type_info = data_source.get(b"$E", "CtyDynamic")
                    element_type = cls._create_type_from_name(
                        element_type_info
                    )  # Recursive call
                    return CtyList(element_type=element_type)
                case "CtyMap":
                    key_type_info = data_source.get(b"$K", "CtyString")
                    value_type_info = data_source.get(b"$V", "CtyDynamic")
                    key_type = cls._create_type_from_name(
                        key_type_info
                    )  # Recursive call
                    value_type = cls._create_type_from_name(
                        value_type_info
                    )  # Recursive call
                    return CtyMap(key_type=key_type, value_type=value_type)
                case "CtySet":
                    element_type_info = data_source.get(b"$E", "CtyDynamic")
                    element_type = cls._create_type_from_name(
                        element_type_info
                    )  # Recursive call
                    return CtySet(element_type=element_type)
                case "CtyTuple":
                    element_type_infos = data_source.get(b"$ET", [])
                    element_types = [
                        cls._create_type_from_name(eti) for eti in element_type_infos
                    ]  # Recursive calls
                    return CtyTuple(element_types=cast(list[CtyType], element_types))
                case "CtyObject":
                    attribute_type_infos = data_source.get(b"$AT", {})
                    attribute_types = {
                        (
                            name.decode("utf-8") if isinstance(name, bytes) else name
                        ): cls._create_type_from_name(ati)
                        for name, ati in attribute_type_infos.items()
                    }  # Recursive calls
                    return CtyObject(
                        attribute_types=cast(dict[str, CtyType], attribute_types)
                    )
                case "CtyDynamic":  # Explicitly CtyDynamic
                    return CtyDynamic()
                case _:  # Unrecognized type string
                    # If type_name_str was derived from a type marker but isn't a known Cty type string,
                    # it's an encoding error. Defaulting to CtyDynamic should only happen if no type was specified.
                    # This makes the type creation stricter.
                    if isinstance(type_info_dict, (str, bytes)) or (
                        isinstance(type_info_dict, dict)
                        and (
                            cls.TYPE_MARKER in type_info_dict
                            or cls.TYPE_MARKER.encode("utf-8") in type_info_dict
                        )
                    ):
                        raise EncodingError(
                            f"Unrecognized CTY type string: {type_name_str}",
                            encoding="msgpack",
                        )
                    return CtyDynamic()  # Fallback for truly unspecified types (e.g. if type_info_dict was None or empty dict without $T)

        except Exception as e:
            # Ensure that CtyTypeParseError from codec._parse_type_string is re-raised as EncodingError
            if isinstance(e, CtyTypeParseError):
                raise EncodingError(
                    f"Failed to parse type string in msgpack: {e}", encoding="msgpack"
                ) from e
            error_msg = f"Failed to create type from info {type_info_dict}: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)
            raise EncodingError(error_msg, encoding="msgpack") from e

    @staticmethod
    def _msgpack_default(obj: object) -> object:
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
        raise TypeError(
            f"Object of type {type(obj).__name__} is not MessagePack serializable"
        )

    @classmethod
    def marshal(
        cls,
        value: object,
        *,
        operation: object | None = None, # CTY OperationContext
        **options: object,
    ) -> bytes:
        """
        Marshals a Python/CTY value into MessagePack bytes using CTY conventions.
        """
        return cls.encode(value, **options)

    @classmethod
    def unmarshal(
        cls,
        data: bytes,
        expected_type: type | None = None, # CTY CtyType
        *,
        operation: object | None = None, # CTY OperationContext
        **options: object,
    ) -> object:
        """
        Unmarshals MessagePack bytes into a Python object/CtyValue using CTY conventions.
        """
        return cls.decode(data, **options)


# 🐍🏗️🐣
