#
# pyvider/cty/encoding/msgpack_serializer.py
#

"""
MessagePack serializer implementation for Cty values.

This module provides a MessagePack-based serializer that handles both standard
Python types and Cty types with type information preservation using MessagePack
extension types.
"""

import inspect
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, Final, List, Optional, Set, Tuple, Type, TypedDict, Union, cast

import attrs
import msgpack

from pyvider.cty.logger import logger
from pyvider.cty.encoding.protocols import TypedSerializerProtocol
from pyvider.cty.encoding.exceptions import (
    DeserializationError,
    InvalidFormatError,
    SerializationError,
    TypeMismatchError,
    UnsupportedTypeError,
)
from pyvider.cty.encoding.registry import register_serializer
from pyvider.cty.encoding.capsule_serializer import (
    prepare_capsule_value,
    process_capsule_value,
)

class CtyType(str, Enum):
    """Enumeration of Cty type names."""
    STRING = "string"
    NUMBER = "number"
    BOOL = "bool"
    LIST = "list"
    MAP = "map"
    SET = "set"
    TUPLE = "tuple"
    OBJECT = "object"
    DYNAMIC = "dynamic"
    NULL = "null"
    CAPSULE = "capsule"


class ValuePayload(TypedDict, total=False):
    """TypedDict for MessagePack encoded values."""
    type: bytes  # Encoded type information
    value: bytes  # Encoded value data
    is_known: bool  # Flag for known status
    is_null: bool  # Flag for null status
    marks: List[str]  # Optional marks


# Extension type codes for special Cty value representations
EXT_UNKNOWN: Final[int] = 0
EXT_NULL: Final[int] = 1
EXT_MARKED: Final[int] = 2
EXT_TYPE_HINT: Final[int] = 3
EXT_OBJECT: Final[int] = 4
EXT_TUPLE: Final[int] = 5
EXT_SET: Final[int] = 6

# Magic bytes for quickly identifying MessagePack format for Pyvider Cty values
# "PCTY" + version (1) = [80, 67, 84, 89, 1]
CTY_MAGIC_BYTES: Final[bytes] = bytes([80, 67, 84, 89, 1])

# Default encoder/decoder options
DEFAULT_ENCODE_OPTIONS: Final[Dict[str, Any]] = {
    "use_bin_type": True,
    "use_single_float": False,
    "datetime": True,
    "strict_types": True,
}

DEFAULT_DECODE_OPTIONS: Final[Dict[str, Any]] = {
    "raw": False,
    "use_list": True,
    "strict_map_key": False,
}


class ObjectDict(dict):
    """Dictionary with _is_object attribute for object serialization."""
    _is_object = True


@register_serializer
class MsgpackSerializer(TypedSerializerProtocol):
    """
    MessagePack serializer for Cty values.

    This serializer uses MessagePack as the underlying binary format and preserves
    type information using MessagePack extensions.
    """

    format_name: ClassVar[str] = "msgpack"

    @classmethod
    def supports_format(cls, data: bytes) -> bool:
        """
        Check if the data is valid MessagePack format.

        Args:
            data: The bytes data to check

        Returns:
            True if the data is valid MessagePack, False otherwise
        """
        logger.debug("🧮🔍🔄 Checking if data is MessagePack format")

        if not data:
            logger.debug("🧮🔍❌ Empty data")
            return False

        # Check for magic bytes first
        if len(data) >= len(CTY_MAGIC_BYTES) and data[:len(CTY_MAGIC_BYTES)] == CTY_MAGIC_BYTES:
            logger.debug("🧮🔍✅ Detected Pyvider Cty magic bytes")
            return True

        try:
            # Try to unpack the data
            msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)
            logger.debug("🧮🔍✅ Successfully unpacked as MessagePack")
            return True
        except Exception:
            # Try with smaller limits as a fallback
            try:
                msgpack.unpackb(
                    data[:min(20, len(data))],
                    max_str_len=1,
                    max_bin_len=1,
                    max_array_len=1,
                    max_map_len=1
                )
                logger.debug("🧮🔍✅ Successfully unpacked sample as MessagePack")
                return True
            except Exception:
                logger.debug("🧮🔍❌ Not valid MessagePack data")
                return False

    @classmethod
    def format_priority(cls) -> int:
        """
        Return the priority of this serializer for format auto-detection.

        Returns:
            Priority value
        """
        # Higher than JSON since binary format is more specific
        return 10

    def serialize(self, value: Any) -> bytes:
        """
        Serialize a value to MessagePack format.

        Args:
            value: The value to serialize

        Returns:
            MessagePack encoded data

        Raises:
            SerializationError: If serialization fails
        """
        logger.debug(f"🧮📤🔄 Serializing to MessagePack: {type(value).__name__}")

        try:
            # Check if it's a Cty value
            if hasattr(value, 'type') and hasattr(value, 'value'):
                logger.debug("🧮📤🔄 Unwrapping Cty value")
                cty_type = value.type
                actual_value = value.value

                # Handle special value states
                if hasattr(value, 'is_unknown') and value.is_unknown:
                    logger.debug("🧮📤ℹ️ Encoding unknown value")
                    type_hint = self._encode_type_hint(cty_type)
                    ext_data = msgpack.packb(type_hint, **DEFAULT_ENCODE_OPTIONS)
                    packed = msgpack.packb(
                        msgpack.ExtType(EXT_UNKNOWN, ext_data),
                        **DEFAULT_ENCODE_OPTIONS
                    )
                    return CTY_MAGIC_BYTES + packed

                if hasattr(value, 'is_null') and value.is_null:
                    logger.debug("🧮📤ℹ️ Encoding null value")
                    type_hint = self._encode_type_hint(cty_type)
                    packed = msgpack.packb(
                        msgpack.ExtType(EXT_NULL, type_hint),
                        **DEFAULT_ENCODE_OPTIONS
                    )
                    return CTY_MAGIC_BYTES + packed

                # Handle marked values
                if hasattr(value, '_marks') and value._marks:
                    logger.debug(f"🧮📤ℹ️ Encoding marked value with {len(value._marks)} marks")
                    # Use unmark method to get unmarked value and marks
                    try:
                        unmarked_value, marks = value.unmark()

                        # Serialize the unmarked value (without magic bytes)
                        unmarked_serialized = self.serialize(unmarked_value)
                        if unmarked_serialized.startswith(CTY_MAGIC_BYTES):
                            unmarked_serialized = unmarked_serialized[len(CTY_MAGIC_BYTES):]

                        data = {
                            "value": unmarked_serialized,
                            "marks": [str(mark) for mark in marks]
                        }
                        packed = msgpack.packb(
                            msgpack.ExtType(EXT_MARKED, msgpack.packb(data)),
                            **DEFAULT_ENCODE_OPTIONS
                        )
                        return CTY_MAGIC_BYTES + packed
                    except Exception as e:
                        logger.error(f"🧮📤❌ Error processing marked value: {e}")
                        raise

                # For collection types, process element values
                if hasattr(actual_value, '__iter__') and not isinstance(actual_value, (str, bytes)):
                    if isinstance(actual_value, dict):
                        # Handle dictionary/map values
                        try:
                            processed_value = {}
                            for k, v in actual_value.items():
                                # Extract the actual key and value
                                key = k.value if hasattr(k, 'value') else k
                                val = v.value if hasattr(v, 'value') else v
                                processed_value[str(key)] = val
                            return self.serialize_with_type(processed_value, cty_type)
                        except Exception as e:
                            logger.error(f"🧮📤❌ Error processing dictionary values: {e}")
                            raise
                    else:
                        # Handle list/set/tuple values
                        try:
                            processed_value = [
                                v.value if hasattr(v, 'value') else v
                                for v in actual_value
                            ]
                            return self.serialize_with_type(processed_value, cty_type)
                        except Exception as e:
                            logger.error(f"🧮📤❌ Error processing collection values: {e}")
                            raise

                # Serialize with type hint
                return self.serialize_with_type(actual_value, cty_type)

            # Handle regular Python types
            try:
                prepared_value = self._prepare_value(value)

                # Add magic bytes to identify Pyvider Cty MessagePack format
                result = CTY_MAGIC_BYTES + msgpack.packb(prepared_value, **DEFAULT_ENCODE_OPTIONS)
                logger.debug(f"🧮📤✅ Serialized {len(result)} bytes")
                return result
            except Exception as e:
                logger.error(f"🧮📤❌ Error preparing or packing value: {e}")
                raise

        except UnsupportedTypeError:
            # Re-raise UnsupportedTypeError without wrapping
            raise
        except SerializationError:
            # Re-raise SerializationError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to serialize to MessagePack: {e}"
            logger.error(f"🧮📤❌ {error_msg}")
            raise SerializationError(error_msg, value) from e

    def deserialize(self, data: bytes) -> Any:
        """
        Deserialize MessagePack data to a Python value.

        Args:
            data: The MessagePack data to deserialize

        Returns:
            Deserialized value

        Raises:
            DeserializationError: If deserialization fails
        """
        logger.debug(f"🧮📥🔄 Deserializing from MessagePack: {len(data)} bytes")

        try:
            # Skip magic bytes if present
            if len(data) >= len(CTY_MAGIC_BYTES) and data[:len(CTY_MAGIC_BYTES)] == CTY_MAGIC_BYTES:
                logger.debug("🧮📥ℹ️ Skipping magic bytes")
                data = data[len(CTY_MAGIC_BYTES):]

            # Custom extension type handler
            def ext_hook(code: int, data: bytes) -> Any:
                # Import here to avoid circular imports
                from pyvider.cty.values import CtyValue
                from pyvider.cty.types import (
                    CtyString, CtyNumber, CtyBool,
                    CtyList, CtyMap, CtySet,
                    CtyObject, CtyTuple, CtyDynamic
                )

                match code:
                    case EXT_UNKNOWN if True:
                        logger.debug("🧮📥ℹ️ Decoding unknown value")
                        try:
                            type_name = self._decode_type_hint(data)

                            # Create an unknown value based on the type hint
                            try:
                                # Get type from module
                                module = __import__("pyvider.cty")
                                type_class = getattr(module.cty, f"Cty{type_name.capitalize()}")
                                return CtyValue.unknown(type_=type_class())
                            except (ImportError, AttributeError) as e:
                                logger.warning(f"🧮📥⚠️ Could not create unknown value: {e}")
                                # Fallback for non-importable types
                                return {"_cty_unknown": True, "type_hint": type_name}
                        except Exception as e:
                            logger.error(f"🧮📥❌ Error decoding unknown value: {e}")
                            raise

                    case EXT_NULL if True:
                        logger.debug("🧮📥ℹ️ Decoding null value")
                        try:
                            type_name = self._decode_type_hint(data)

                            # Create a null value based on the type hint
                            try:
                                # Get type from module
                                module = __import__("pyvider.cty")
                                type_class = getattr(module.cty, f"Cty{type_name.capitalize()}")
                                return CtyValue.null(type_=type_class())
                            except (ImportError, AttributeError) as e:
                                logger.warning(f"🧮📥⚠️ Could not create null value: {e}")
                                # Fallback for non-importable types
                                return None
                        except Exception as e:
                            logger.error(f"🧮📥❌ Error decoding null value: {e}")
                            raise

                    case EXT_MARKED if True:
                        logger.debug("🧮📥ℹ️ Decoding marked value")
                        try:
                            marked_data = msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)

                            # Deserialize the inner value
                            value_data = marked_data["value"]
                            value = self.deserialize(CTY_MAGIC_BYTES + value_data)

                            # Apply marks
                            if isinstance(value, CtyValue) and "marks" in marked_data:
                                for mark in marked_data["marks"]:
                                    value = value.mark(mark)

                            return value
                        except Exception as e:
                            logger.error(f"🧮📥❌ Error decoding marked value: {e}")
                            raise

                    case EXT_OBJECT if True:
                        logger.debug("🧮📥ℹ️ Decoding object value")
                        try:
                            # Parse the object data
                            obj_data = msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)

                            # Process object attributes
                            processed_dict = {}
                            attribute_types = {}

                            for k, v in obj_data.items():
                                processed_val = self._process_value(v)
                                processed_dict[k] = processed_val

                                # Determine attribute type
                                if isinstance(processed_val, CtyValue):
                                    attribute_types[k] = processed_val.type
                                elif isinstance(processed_val, str):
                                    attribute_types[k] = CtyString()
                                elif isinstance(processed_val, (int, float, Decimal)):
                                    attribute_types[k] = CtyNumber()
                                elif isinstance(processed_val, bool):
                                    attribute_types[k] = CtyBool()
                                else:
                                    attribute_types[k] = CtyDynamic()

                            # Create the object value
                            object_type = CtyObject(attribute_types=attribute_types)

                            # Create a dictionary with _is_object attribute
                            dict_obj = ObjectDict(processed_dict)

                            return CtyValue(type_=object_type, value=dict_obj)
                        except Exception as e:
                            logger.error(f"🧮📥❌ Error decoding object value: {e}")
                            raise

                    case EXT_TUPLE if True:
                        logger.debug("🧮📥ℹ️ Decoding tuple value")
                        try:
                            # Parse the tuple data
                            tuple_data = msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)

                            # Process tuple elements
                            processed_items = []
                            element_types = []

                            for item in tuple_data:
                                processed_val = self._process_value(item)
                                processed_items.append(processed_val)

                                # Determine element type
                                if isinstance(processed_val, CtyValue):
                                    element_types.append(processed_val.type)
                                elif isinstance(processed_val, str):
                                    element_types.append(CtyString())
                                elif isinstance(processed_val, (int, float, Decimal)):
                                    element_types.append(CtyNumber())
                                elif isinstance(processed_val, bool):
                                    element_types.append(CtyBool())
                                else:
                                    element_types.append(CtyDynamic())

                            # Create the tuple value
                            tuple_type = CtyTuple(element_types=tuple(element_types))
                            return CtyValue(type_=tuple_type, value=tuple(processed_items))
                        except Exception as e:
                            logger.error(f"🧮📥❌ Error decoding tuple value: {e}")
                            raise

                    case EXT_SET if True:
                        logger.debug("🧮📥ℹ️ Decoding set value")
                        try:
                            # Parse the set data
                            set_data = msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)

                            # Process set elements
                            processed_items = []

                            for item in set_data:
                                processed_val = self._process_value(item)
                                processed_items.append(processed_val)

                            # Determine element type
                            element_type = CtyDynamic()
                            if processed_items:
                                if all(isinstance(item, CtyValue) for item in processed_items):
                                    element_type = processed_items[0].type
                                elif all(isinstance(item, str) for item in processed_items):
                                    element_type = CtyString()
                                elif all(isinstance(item, (int, float, Decimal)) for item in processed_items):
                                    element_type = CtyNumber()
                                elif all(isinstance(item, bool) for item in processed_items):
                                    element_type = CtyBool()

                            # Create the set value
                            set_type = CtySet(element_type=element_type)
                            return CtyValue(type_=set_type, value=set(processed_items))
                        except Exception as e:
                            logger.error(f"🧮📥❌ Error decoding set value: {e}")
                            raise

                # Return raw data for unknown extension types
                logger.debug(f"🧮📥⚠️ Unknown extension type code: {code}")
                return msgpack.ExtType(code, data)

            # Unpack the data
            decode_options = dict(DEFAULT_DECODE_OPTIONS)
            decode_options["ext_hook"] = ext_hook

            try:
                raw_value = msgpack.unpackb(data, **decode_options)

                # Process the value
                result = self._process_value(raw_value)
                logger.debug(f"🧮📥✅ Deserialized to {type(result).__name__}")
                return result
            except msgpack.exceptions.ExtraData as e:
                logger.warning(f"🧮📥⚠️ Extra data after unpacking: {e}")
                # Just use the first complete object and ignore extra data
                raw_value = msgpack.unpackb(data[:e.unpacked_size], **decode_options)
                result = self._process_value(raw_value)
                logger.debug(f"🧮📥✅ Deserialized (partial) to {type(result).__name__}")
                return result

        except DeserializationError:
            # Re-raise DeserializationError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to deserialize from MessagePack: {e}"
            logger.error(f"🧮📥❌ {error_msg}")
            raise DeserializationError(error_msg, data=data, format_name="msgpack") from e

    def serialize_with_type(self, value: Any, type_hint: Any = None) -> bytes:
        """
        Serialize a value with explicit type information.

        Args:
            value: The value to serialize
            type_hint: Optional type hint to guide serialization

        Returns:
            MessagePack data with type information

        Raises:
            SerializationError: If serialization fails
            UnsupportedTypeError: If the type is not supported
        """
        logger.debug(f"🧮📤🔄 Serializing with type: {type(value).__name__}, hint: {type_hint}")

        try:
            # Determine the CtyType
            cty_type = self._get_cty_type(value, type_hint)

            # Prepare the value based on its type
            prepared_value = self._prepare_typed_value(value, cty_type)

            # Encode type information
            type_data = msgpack.packb(cty_type.value, **DEFAULT_ENCODE_OPTIONS)

            # Create the typed value structure
            typed_value = {
                "type": type_data,
                "value": prepared_value
            }

            # Add magic bytes to identify Pyvider Cty MessagePack format
            result = CTY_MAGIC_BYTES + msgpack.packb(typed_value, **DEFAULT_ENCODE_OPTIONS)
            logger.debug(f"🧮📤✅ Serialized {len(result)} bytes with type {cty_type.value}")
            return result

        except UnsupportedTypeError:
            # Re-raise UnsupportedTypeError without wrapping
            raise
        except SerializationError:
            # Re-raise SerializationError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to serialize with type: {e}"
            logger.error(f"🧮📤❌ {error_msg}")
            raise SerializationError(error_msg, value) from e

    def deserialize_with_type(self, data: bytes, type_hint: Any = None) -> Any:
        """
        Deserialize MessagePack data with type information.

        Args:
            data: The MessagePack data to deserialize
            type_hint: Optional type hint to guide deserialization

        Returns:
            Deserialized value with preserved type information

        Raises:
            DeserializationError: If deserialization fails
            TypeMismatchError: If the decoded type doesn't match the expected type
        """
        logger.debug(f"🧮📥🔄 Deserializing with type: {len(data)} bytes, hint: {type_hint}")

        try:
            # Skip magic bytes if present
            if len(data) >= len(CTY_MAGIC_BYTES) and data[:len(CTY_MAGIC_BYTES)] == CTY_MAGIC_BYTES:
                logger.debug("🧮📥ℹ️ Skipping magic bytes")
                data = data[len(CTY_MAGIC_BYTES):]

            # Import here to avoid circular imports
            from pyvider.cty.values import CtyValue
            from pyvider.cty.types import (
                CtyString, CtyNumber, CtyBool,
                CtyList, CtyMap, CtySet,
                CtyObject, CtyTuple, CtyDynamic
            )

            # Unpack the data
            try:
                raw_value = msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)

                # Check for special states (extension types)
                if isinstance(raw_value, msgpack.ExtType):
                    match raw_value.code:
                        case EXT_UNKNOWN if True:
                            logger.debug("🧮📥ℹ️ Detected unknown value extension")
                            try:
                                if type_hint is not None:
                                    return CtyValue.unknown(type_=type_hint)

                                # Try to decode type name from extension data
                                type_name = self._decode_type_hint(raw_value.data)

                                # Create appropriate type
                                try:
                                    module = __import__("pyvider.cty")
                                    type_class = getattr(module.cty, f"Cty{type_name.capitalize()}")
                                    return CtyValue.unknown(type_=type_class())
                                except (ImportError, AttributeError) as e:
                                    logger.warning(f"🧮📥⚠️ Could not create type for unknown value: {e}")
                                    return {"_cty_unknown": True, "type": type_name}
                            except Exception as e:
                                logger.error(f"🧮📥❌ Error processing unknown value extension: {e}")
                                raise

                        case EXT_NULL if True:
                            logger.debug("🧮📥ℹ️ Detected null value extension")
                            try:
                                if type_hint is not None:
                                    return CtyValue.null(type_=type_hint)

                                # Try to decode type name from extension data
                                type_name = self._decode_type_hint(raw_value.data)

                                # Create appropriate type
                                try:
                                    module = __import__("pyvider.cty")
                                    type_class = getattr(module.cty, f"Cty{type_name.capitalize()}")
                                    return CtyValue.null(type_=type_class())
                                except (ImportError, AttributeError) as e:
                                    logger.warning(f"🧮📥⚠️ Could not create type for null value: {e}")
                                    return None
                            except Exception as e:
                                logger.error(f"🧮📥❌ Error processing null value extension: {e}")
                                raise

                        case EXT_MARKED if True:
                            logger.debug("🧮📥ℹ️ Detected marked value extension")
                            try:
                                # Unpack the extension data
                                marked_data = msgpack.unpackb(raw_value.data, **DEFAULT_DECODE_OPTIONS)

                                # Deserialize the inner value
                                value_data = marked_data["value"]
                                value = self.deserialize_with_type(CTY_MAGIC_BYTES + value_data, type_hint)

                                # Apply marks
                                if isinstance(value, CtyValue) and "marks" in marked_data:
                                    for mark in marked_data["marks"]:
                                        value = value.mark(mark)

                                return value
                            except Exception as e:
                                logger.error(f"🧮📥❌ Error processing marked value extension: {e}")
                                raise

                        case _:
                            # Handle other extension types
                            return self._process_value(raw_value)

                # Check for typed value structure
                if isinstance(raw_value, dict) and "type" in raw_value and "value" in raw_value:
                    # Extract type and value
                    type_data = raw_value["type"]
                    value = raw_value["value"]

                    try:
                        # Decode the type
                        type_str = msgpack.unpackb(type_data, **DEFAULT_DECODE_OPTIONS)
                        cty_type = CtyType(type_str)

                        # If we have a type_hint, verify type compatibility
                        if type_hint is not None:
                            expected_type = self._get_cty_type(None, type_hint)
                            if expected_type != cty_type:
                                error_msg = f"Expected {expected_type.value}, found {cty_type.value}"
                                logger.error(f"🧮📥❌ {error_msg}")
                                raise TypeMismatchError(expected_type, cty_type, data=data, format_name="msgpack")

                        # Process the value with the specified type
                        result = self._process_typed_value(value, cty_type)
                        logger.debug(f"🧮📥✅ Deserialized to {type(result).__name__} with type {cty_type.value}")
                        return result
                    except ValueError as e:
                        # Unknown type, fall back to regular processing
                        logger.warning(f"🧮📥⚠️ Unknown type, falling back to regular processing: {e}")
                        return self._process_value(value)

                # If type_hint is provided, use it for processing
                if type_hint is not None:
                    cty_type = self._get_cty_type(None, type_hint)
                    result = self._process_typed_value(raw_value, cty_type)
                    logger.debug(f"🧮📥✅ Deserialized to {type(result).__name__} with type hint")
                    return result

                # Otherwise, process as regular value
                result = self._process_value(raw_value)
                logger.debug(f"🧮📥✅ Deserialized to {type(result).__name__}")
                return result

            except msgpack.exceptions.ExtraData as e:
                logger.warning(f"🧮📥⚠️ Extra data after unpacking: {e}")
                # Just use the first complete object and ignore extra data
                raw_value = msgpack.unpackb(data[:e.unpacked_size], **DEFAULT_DECODE_OPTIONS)

                # Process as above but with the partial data
                if type_hint is not None:
                    cty_type = self._get_cty_type(None, type_hint)
                    result = self._process_typed_value(raw_value, cty_type)
                    logger.debug(f"🧮📥✅ Deserialized (partial) to {type(result).__name__} with type hint")
                    return result

                result = self._process_value(raw_value)
                logger.debug(f"🧮📥✅ Deserialized (partial) to {type(result).__name__}")
                return result

        except DeserializationError:
            # Re-raise DeserializationError without wrapping
            raise
        except TypeMismatchError:
            # Re-raise TypeMismatchError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to deserialize with type: {e}"
            logger.error(f"🧮📥❌ {error_msg}")
            raise DeserializationError(error_msg, data=data, format_name="msgpack") from e



    def _get_cty_type(self, value: Any, type_hint: Any = None) -> CtyType:
        """
        Determine the CtyType for a value.

        Args:
            value: The value to get the type for
            type_hint: Optional type hint

        Returns:
            CtyType

        Raises:
            UnsupportedTypeError: If the type is not supported
        """
        # If type_hint is a CtyType enum, use it directly
        if isinstance(type_hint, CtyType):
            return type_hint

        # If type_hint is a Cty type, extract the CtyType from it
        if type_hint is not None and hasattr(type_hint, '__class__'):
            # Check for Cty type naming conventions (CtyString, CtyNumber, etc.)
            type_class_name = type_hint.__class__.__name__
            if type_class_name.startswith('Cty'):
                type_name = type_class_name[3:].upper()
                try:
                    return CtyType[type_name]
                except KeyError:
                    logger.warning(f"🧮🔍⚠️ Unknown Cty type: {type_class_name}")
                    # Fall through to value-based detection

        # If no type_hint or not recognized, infer from value
        if value is None:
            return CtyType.NULL

        # Map Python types to CtyTypes using match/case
        match value:
            case str():
                return CtyType.STRING
            case bool():
                return CtyType.BOOL
            case int() | float() | Decimal():
                return CtyType.NUMBER
            case list() | tuple():
                # Determine if it's a tuple or list
                if isinstance(value, tuple) or getattr(value, '_is_tuple', False):
                    return CtyType.TUPLE
                return CtyType.LIST
            case set() | frozenset():
                return CtyType.SET
            case dict():
                # Check if it's an object or map
                if hasattr(value, '_is_object') and value._is_object:
                    return CtyType.OBJECT
                return CtyType.MAP
            case _:
                if hasattr(value, '__class__') and isinstance(getattr(value, 'type', None), CtyCapsule):
                    return CtyType.CAPSULE

                # Check for custom classes with known conversions
                if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    return CtyType.OBJECT

                # Unsupported type
                error_msg = f"Unsupported type for MessagePack serialization: {type(value).__name__}"
                logger.error(f"🧮📤❌ {error_msg}")
                raise UnsupportedTypeError(type(value), "msgpack", value)

    def _encode_type_hint(self, type_hint: Any) -> bytes:
        """
        Encode a type hint for MessagePack serialization.

        Args:
            type_hint: The type hint to encode

        Returns:
            Encoded type hint
        """
        # If it's a Cty type, extract the type name
        if hasattr(type_hint, '__class__'):
            type_class_name = type_hint.__class__.__name__
            if type_class_name.startswith('Cty'):
                type_name = type_class_name[3:].lower()
                return msgpack.packb(type_name, **DEFAULT_ENCODE_OPTIONS)

        # Default to dynamic type
        return msgpack.packb("dynamic", **DEFAULT_ENCODE_OPTIONS)

    def _decode_type_hint(self, data: bytes) -> str:
        """
        Decode a type hint from MessagePack serialization.

        Args:
            data: The encoded type hint

        Returns:
            Decoded type hint
        """
        try:
            return msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)
        except Exception as e:
            logger.warning(f"🧮🔍⚠️ Failed to decode type hint, defaulting to dynamic: {e}")
            return "dynamic"

    def _prepare_value(self, value: Any) -> Any:
        """
        Prepare a value for MessagePack serialization.

        Args:
            value: The value to prepare

        Returns:
            MessagePack-serializable value
        """
        # Handle None
        if value is None:
            return None

        # Use match/case for type-based handling
        match value:
            case str() | int() | float() | bool():
                return value
            case list() | tuple():
                result = [self._prepare_value(item) for item in value]
                # If it's a tuple, encode it as an extension type
                if isinstance(value, tuple):
                    return msgpack.ExtType(EXT_TUPLE, msgpack.packb(result, **DEFAULT_ENCODE_OPTIONS))
                return result
            case set() | frozenset():
                result = [self._prepare_value(item) for item in value]
                # Encode as an extension type
                return msgpack.ExtType(EXT_SET, msgpack.packb(result, **DEFAULT_ENCODE_OPTIONS))
            case dict():
                result = {str(k): self._prepare_value(v) for k, v in value.items()}
                # If it's marked as an object, encode it as an extension type
                if hasattr(value, '_is_object') and value._is_object:
                    return msgpack.ExtType(EXT_OBJECT, msgpack.packb(result, **DEFAULT_ENCODE_OPTIONS))
                return result
            case Decimal():
                # Preserve exact decimal representation as string
                return str(value)
            case _:
                # Handle attrs classes
                if hasattr(value, '__attrs_attrs__'):
                    result = {
                        field.name: self._prepare_value(getattr(value, field.name))
                        for field in attrs.fields(value.__class__)
                    }
                    # Encode as an object
                    return msgpack.ExtType(EXT_OBJECT, msgpack.packb(result, **DEFAULT_ENCODE_OPTIONS))

                # Handle classes with to_dict method
                if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    return self._prepare_value(value.to_dict())

                # Handle other classes with __dict__
                if hasattr(value, '__dict__'):
                    return self._prepare_value(value.__dict__)

                # Last resort: convert to string
                return str(value)

    def _prepare_typed_value(self, value: Any, cty_type: CtyType) -> Any:
        """
        Prepare a value for typed MessagePack serialization.

        Args:
            value: The value to prepare
            cty_type: The CtyType

        Returns:
            MessagePack-serializable value
        """
        match cty_type:
            case CtyType.NULL:
                return None
            case CtyType.STRING:
                return str(value) if value is not None else ""
            case CtyType.BOOL:
                return bool(value)
            case CtyType.NUMBER:
                if isinstance(value, Decimal):
                    # Preserve exact decimal representation as string
                    return str(value)
                return value
            case CtyType.LIST:
                return [self._prepare_value(item) for item in value]
            case CtyType.TUPLE:
                result = [self._prepare_value(item) for item in value]
                # Encode as an extension type
                return msgpack.ExtType(EXT_TUPLE, msgpack.packb(result, **DEFAULT_ENCODE_OPTIONS))
            case CtyType.SET:
                result = [self._prepare_value(item) for item in value]
                # Encode as an extension type
                return msgpack.ExtType(EXT_SET, msgpack.packb(result, **DEFAULT_ENCODE_OPTIONS))
            case CtyType.MAP:
                return {str(k): self._prepare_value(v) for k, v in value.items()}
            case CtyType.OBJECT:
                if isinstance(value, dict):
                    result = {str(k): self._prepare_value(v) for k, v in value.items()}
                    # Encode as an extension type
                    return msgpack.ExtType(EXT_OBJECT, msgpack.packb(result, **DEFAULT_ENCODE_OPTIONS))
                elif hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    return self._prepare_typed_value(value.to_dict(), cty_type)
                elif hasattr(value, '__dict__'):
                    return self._prepare_typed_value(value.__dict__, cty_type)
                else:
                    error_msg = f"Cannot convert {type(value).__name__} to object"
                    logger.error(f"🧮📤❌ {error_msg}")
                    raise UnsupportedTypeError(type(value), "msgpack", value)
            case CtyType.DYNAMIC:
                return self._prepare_value(value)

    def _process_value(self, value: Any) -> Any:
        """
        Process a deserialized MessagePack value.

        Args:
            value: The raw deserialized value

        Returns:
            Processed value
        """
        # Import here to avoid circular imports
        from pyvider.cty.values import CtyValue
        from pyvider.cty.types import (
            CtyString, CtyNumber, CtyBool,
            CtyList, CtyMap, CtySet,
            CtyObject, CtyTuple, CtyDynamic
        )

        # Handle extension types
        if isinstance(value, msgpack.ExtType):
            match value.code:
                case EXT_OBJECT if True:
                    logger.debug("🧮🔍ℹ️ Processing object extension")
                    try:
                        # Process as object
                        obj_data = msgpack.unpackb(value.data, **DEFAULT_DECODE_OPTIONS)

                        # Process object attributes
                        processed_dict = {}
                        attribute_types = {}

                        for k, v in obj_data.items():
                            processed_val = self._process_value(v)
                            processed_dict[k] = processed_val

                            # Determine attribute type
                            if isinstance(processed_val, CtyValue):
                                attribute_types[k] = processed_val.type
                            elif isinstance(processed_val, str):
                                attribute_types[k] = CtyString()
                            elif isinstance(processed_val, (int, float, Decimal)):
                                attribute_types[k] = CtyNumber()
                            elif isinstance(processed_val, bool):
                                attribute_types[k] = CtyBool()
                            else:
                                attribute_types[k] = CtyDynamic()

                        # Create the object value
                        object_type = CtyObject(attribute_types=attribute_types)
                        dict_obj = ObjectDict(processed_dict)

                        return CtyValue(type_=object_type, value=dict_obj)
                    except Exception as e:
                        logger.error(f"🧮🔍❌ Error processing object extension: {e}")
                        raise
                case EXT_TUPLE if True:
                    logger.debug("🧮🔍ℹ️ Processing tuple extension")
                    try:
                        # Process as tuple
                        tuple_data = msgpack.unpackb(value.data, **DEFAULT_DECODE_OPTIONS)

                        # Process tuple elements
                        processed_items = []
                        element_types = []

                        for item in tuple_data:
                            processed_val = self._process_value(item)
                            processed_items.append(processed_val)

                            # Determine element type
                            if isinstance(processed_val, CtyValue):
                                element_types.append(processed_val.type)
                            elif isinstance(processed_val, str):
                                element_types.append(CtyString())
                            elif isinstance(processed_val, (int, float, Decimal)):
                                element_types.append(CtyNumber())
                            elif isinstance(processed_val, bool):
                                element_types.append(CtyBool())
                            else:
                                element_types.append(CtyDynamic())

                        # Create the tuple value
                        tuple_type = CtyTuple(element_types=tuple(element_types))
                        return CtyValue(type_=tuple_type, value=tuple(processed_items))
                    except Exception as e:
                        logger.error(f"🧮🔍❌ Error processing tuple extension: {e}")
                        raise
                case EXT_SET if True:
                    logger.debug("🧮🔍ℹ️ Processing set extension")
                    try:
                        # Process as set
                        set_data = msgpack.unpackb(value.data, **DEFAULT_DECODE_OPTIONS)

                        # Process set elements
                        processed_items = []

                        for item in set_data:
                            processed_val = self._process_value(item)
                            processed_items.append(processed_val)

                        # Determine element type
                        element_type = CtyDynamic()
                        if processed_items:
                            if all(isinstance(item, CtyValue) for item in processed_items):
                                element_type = processed_items[0].type
                            elif all(isinstance(item, str) for item in processed_items):
                                element_type = CtyString()
                            elif all(isinstance(item, (int, float, Decimal)) for item in processed_items):
                                element_type = CtyNumber()
                            elif all(isinstance(item, bool) for item in processed_items):
                                element_type = CtyBool()

                        # Create the set value
                        set_type = CtySet(element_type=element_type)
                        return CtyValue(type_=set_type, value=set(processed_items))
                    except Exception as e:
                        logger.error(f"🧮🔍❌ Error processing set extension: {e}")
                        raise
                case _:
                    # Unknown extension type
                    logger.debug(f"🧮🔍ℹ️ Unknown extension type: {value.code}")
                    return value

        # Handle standard types
        match value:
            case None:
                return None
            case str():
                # Check if it's a decimal string
                try:
                    if value and '.' in value:
                        return Decimal(value)
                except:
                    pass
                return value
            case int() | float() | bool():
                return value
            case list():
                logger.debug("🧮🔍ℹ️ Processing list value")
                processed_list = [self._process_value(item) for item in value]

                # Create a CtyValue with a CtyList type if appropriate
                try:
                    if processed_list and all(isinstance(item, CtyValue) for item in processed_list):
                        # Get the element type from the first element
                        element_type = processed_list[0].type
                        # Create a CtyList type
                        list_type = CtyList(element_type=element_type)
                        # Create a CtyValue with the list type and processed elements
                        return CtyValue(type_=list_type, value=processed_list)
                    return processed_list
                except Exception as e:
                    logger.debug(f"🧮🔍⚠️ Could not create CtyList value: {e}")
                    return processed_list
            case dict():
                logger.debug("🧮🔍ℹ️ Processing dictionary value")
                # Process as a regular dict
                processed_dict = {k: self._process_value(v) for k, v in value.items()}

                # For object types, we need to set the _is_object attribute
                try:
                    # Check if we should treat this as an object
                    if "_is_object" in processed_dict and processed_dict["_is_object"]:
                        # Create a dictionary with _is_object attribute
                        dict_obj = ObjectDict({k: v for k, v in processed_dict.items() if k != "_is_object"})
                        return dict_obj

                    # Just return the processed dictionary
                    return processed_dict
                except Exception as e:
                    logger.debug(f"🧮🔍⚠️ Could not create structured value: {e}")
                    return processed_dict
            case _:
                # Unknown type
                logger.debug(f"🧮🔍ℹ️ Unknown value type: {type(value).__name__}")
                return value

    def _process_typed_value(self, value: Any, cty_type: CtyType) -> Any:
        """
        Process a deserialized value with type information.

        Args:
            value: The raw deserialized value
            cty_type: The CtyType

        Returns:
            Processed value with preserved type information
        """
        # Import here to avoid circular imports
        from pyvider.cty.values import CtyValue
        from pyvider.cty.types import (
            CtyString, CtyNumber, CtyBool,
            CtyList, CtyMap, CtySet,
            CtyObject, CtyTuple, CtyDynamic
        )

        match cty_type:
            case CtyType.NULL:
                return None
            case CtyType.STRING:
                string_val = str(value) if value is not None else ""
                return CtyValue(type_=CtyString(), value=string_val)
            case CtyType.BOOL:
                bool_val = bool(value)
                return CtyValue(type_=CtyBool(), value=bool_val)
            case CtyType.NUMBER:
                num_val = None
                if isinstance(value, str):
                    # Try to convert string to number (potential decimal value)
                    try:
                        if '.' in value:
                            num_val = Decimal(value)
                        else:
                            num_val = int(value)
                    except ValueError:
                        logger.warning(f"🧮🔍⚠️ Could not convert '{value}' to number, using default")
                        num_val = 0
                elif isinstance(value, (int, float, Decimal)):
                    num_val = value
                else:
                    num_val = 0

                return CtyValue(type_=CtyNumber(), value=num_val)
            case CtyType.LIST:
                processed_items = []

                # Handle different input types
                if isinstance(value, list):
                    processed_items = [self._process_value(item) for item in value]
                elif isinstance(value, msgpack.ExtType) and value.code == EXT_SET:
                    # Convert set to list
                    set_data = msgpack.unpackb(value.data, **DEFAULT_DECODE_OPTIONS)
                    processed_items = [self._process_value(item) for item in set_data]
                else:
                    if value is not None:
                        processed_items = [self._process_value(value)]

                # Determine element type
                element_type = CtyDynamic()
                if processed_items:
                    if all(isinstance(item, CtyValue) for item in processed_items):
                        element_type = processed_items[0].type
                    elif all(isinstance(item, str) for item in processed_items):
                        element_type = CtyString()
                    elif all(isinstance(item, (int, float, Decimal)) for item in processed_items):
                        element_type = CtyNumber()
                    elif all(isinstance(item, bool) for item in processed_items):
                        element_type = CtyBool()

                # Create the list value
                list_type = CtyList(element_type=element_type)
                return CtyValue(type_=list_type, value=processed_items)
            case CtyType.TUPLE:
                processed_items = []

                # Handle different input types
                if isinstance(value, msgpack.ExtType) and value.code == EXT_TUPLE:
                    # Process tuple data
                    tuple_data = msgpack.unpackb(value.data, **DEFAULT_DECODE_OPTIONS)
                    processed_items = [self._process_value(item) for item in tuple_data]
                elif isinstance(value, list):
                    processed_items = [self._process_value(item) for item in value]
                else:
                    if value is not None:
                        processed_items = [self._process_value(value)]

                # For tuples, we need the types of each element
                element_types = []
                for item in processed_items:
                    if isinstance(item, CtyValue):
                        element_types.append(item.type)
                    elif isinstance(item, str):
                        element_types.append(CtyString())
                    elif isinstance(item, (int, float, Decimal)):
                        element_types.append(CtyNumber())
                    elif isinstance(item, bool):
                        element_types.append(CtyBool())
                    else:
                        element_types.append(CtyDynamic())

                # Create the tuple value
                tuple_type = CtyTuple(element_types=tuple(element_types))
                return CtyValue(type_=tuple_type, value=tuple(processed_items))
            case CtyType.SET:
                processed_items = []

                # Handle different input types
                if isinstance(value, msgpack.ExtType) and value.code == EXT_SET:
                    # Process set data
                    set_data = msgpack.unpackb(value.data, **DEFAULT_DECODE_OPTIONS)
                    processed_items = [self._process_value(item) for item in set_data]
                elif isinstance(value, list):
                    processed_items = [self._process_value(item) for item in value]
                else:
                    if value is not None:
                        processed_items = [self._process_value(value)]

                # Determine element type
                element_type = CtyDynamic()
                if processed_items:
                    if all(isinstance(item, CtyValue) for item in processed_items):
                        element_type = processed_items[0].type
                    elif all(isinstance(item, str) for item in processed_items):
                        element_type = CtyString()
                    elif all(isinstance(item, (int, float, Decimal)) for item in processed_items):
                        element_type = CtyNumber()
                    elif all(isinstance(item, bool) for item in processed_items):
                        element_type = CtyBool()

                # Create the set value
                set_type = CtySet(element_type=element_type)
                return CtyValue(type_=set_type, value=set(processed_items))
            case CtyType.MAP:
                if isinstance(value, dict):
                    processed_dict = {}
                    for k, v in value.items():
                        processed_dict[k] = self._process_value(v)

                    # Determine value type
                    value_type = CtyDynamic()
                    if processed_dict:
                        values = list(processed_dict.values())
                        if all(isinstance(v, CtyValue) for v in values):
                            value_type = values[0].type

                    # Create the map value
                    map_type = CtyMap(key_type=CtyString(), value_type=value_type)
                    return CtyValue(type_=map_type, value=processed_dict)
                elif isinstance(value, msgpack.ExtType) and value.code == EXT_OBJECT:
                    # Convert object to map
                    obj_data = msgpack.unpackb(value.data, **DEFAULT_DECODE_OPTIONS)
                    processed_dict = {k: self._process_value(v) for k, v in obj_data.items()}

                    # Determine value type
                    value_type = CtyDynamic()
                    if processed_dict:
                        values = list(processed_dict.values())
                        if all(isinstance(v, CtyValue) for v in values):
                            value_type = values[0].type

                    # Create the map value
                    map_type = CtyMap(key_type=CtyString(), value_type=value_type)
                    return CtyValue(type_=map_type, value=processed_dict)
                else:
                    if value is not None:
                        return CtyValue(
                            type_=CtyMap(key_type=CtyString(), value_type=CtyDynamic()),
                            value={"value": self._process_value(value)}
                        )
                    return CtyValue(
                        type_=CtyMap(key_type=CtyString(), value_type=CtyDynamic()),
                        value={}
                    )
            case CtyType.OBJECT:
                if isinstance(value, msgpack.ExtType) and value.code == EXT_OBJECT:
                    # Process object data
                    obj_data = msgpack.unpackb(value.data, **DEFAULT_DECODE_OPTIONS)

                    # Process attributes
                    processed_dict = {}
                    attribute_types = {}

                    for k, v in obj_data.items():
                        processed_val = self._process_value(v)
                        processed_dict[k] = processed_val

                        # Determine attribute type
                        if isinstance(processed_val, CtyValue):
                            attribute_types[k] = processed_val.type
                        elif isinstance(processed_val, str):
                            attribute_types[k] = CtyString()
                        elif isinstance(processed_val, (int, float, Decimal)):
                            attribute_types[k] = CtyNumber()
                        elif isinstance(processed_val, bool):
                            attribute_types[k] = CtyBool()
                        else:
                            attribute_types[k] = CtyDynamic()

                    # Create the object type
                    object_type = CtyObject(attribute_types=attribute_types)
                    dict_obj = ObjectDict(processed_dict)

                    return CtyValue(type_=object_type, value=dict_obj)
                elif isinstance(value, dict):
                    # Process as object
                    processed_dict = {}
                    attribute_types = {}

                    for k, v in value.items():
                        processed_val = self._process_value(v)
                        processed_dict[k] = processed_val

                        # Determine attribute type
                        if isinstance(processed_val, CtyValue):
                            attribute_types[k] = processed_val.type
                        elif isinstance(processed_val, str):
                            attribute_types[k] = CtyString()
                        elif isinstance(processed_val, (int, float, Decimal)):
                            attribute_types[k] = CtyNumber()
                        elif isinstance(processed_val, bool):
                            attribute_types[k] = CtyBool()
                        else:
                            attribute_types[k] = CtyDynamic()

                    # Create the object type
                    object_type = CtyObject(attribute_types=attribute_types)
                    dict_obj = ObjectDict(processed_dict)

                    return CtyValue(type_=object_type, value=dict_obj)
                else:
                    if value is not None:
                        # Create a simple object with a "value" attribute
                        object_type = CtyObject(attribute_types={"value": CtyDynamic()})
                        dict_obj = ObjectDict({"value": self._process_value(value)})

                        return CtyValue(type_=object_type, value=dict_obj)

                    return CtyValue(
                        type_=CtyObject(attribute_types={}),
                        value=ObjectDict({})
                    )
            case CtyType.DYNAMIC:
                # Process any value
                return self._process_value(value)


# Shorthand functions for use in modules that don't need the full class interface

def serialize(value: Any) -> bytes:
    """
    Serialize a value to MessagePack format.

    Args:
        value: The value to serialize

    Returns:
        MessagePack encoded data
    """
    serializer = MsgpackSerializer()
    return serializer.serialize(value)

def deserialize(data: bytes) -> Any:
    """
    Deserialize MessagePack data to a Python value.

    Args:
        data: The MessagePack data to deserialize

    Returns:
        Deserialized value
    """
    serializer = MsgpackSerializer()
    return serializer.deserialize(data)

def marshal(value: Any) -> bytes:
    """
    Marshal a Cty value to MessagePack format, preserving type information.

    This function creates a complete representation of the value including
    its type, so that it can be unmarshaled back to an equivalent value.

    Args:
        value: The Cty value to marshal

    Returns:
        MessagePack encoded data with type information
    """
    try:
        # Verify it's a Cty value
        if not hasattr(value, 'type') or not hasattr(value, 'value'):
            raise ValueError("Not a valid Cty value")

        cty_type = value.type

        # Encode type and value
        type_data = msgpack.packb(cty_type.__class__.__name__, **DEFAULT_ENCODE_OPTIONS)

        # Create payload based on value state
        payload: ValuePayload = {
            "type": type_data,
            "is_known": not getattr(value, 'is_unknown', False),
            "is_null": getattr(value, 'is_null', False)
        }

        # Handle null value
        if payload["is_null"]:
            return CTY_MAGIC_BYTES + msgpack.packb(payload, **DEFAULT_ENCODE_OPTIONS)

        # Handle unknown value
        if not payload["is_known"]:
            return CTY_MAGIC_BYTES + msgpack.packb(payload, **DEFAULT_ENCODE_OPTIONS)

        # Handle marked value
        marks = getattr(value, '_marks', None)
        if marks:
            payload["marks"] = [str(mark) for mark in marks]

        # Serialize the value
        serializer = MsgpackSerializer()
        # Skip magic bytes in the inner value
        value_serialized = serializer.serialize(value.value)
        if value_serialized.startswith(CTY_MAGIC_BYTES):
            value_serialized = value_serialized[len(CTY_MAGIC_BYTES):]
        payload["value"] = value_serialized

        # Add magic bytes and marshal the payload
        result = CTY_MAGIC_BYTES + msgpack.packb(payload, **DEFAULT_ENCODE_OPTIONS)
        return result
    except Exception as e:
        raise SerializationError(f"Failed to marshal value: {e}", value) from e

def unmarshal(data: bytes) -> Any:
    """
    Unmarshal MessagePack data to a Cty value, using embedded type information.

    This function recreates a Cty value from its marshaled representation,
    including reinstating its type, marks, and special states like null or unknown.

    Args:
        data: The MessagePack data to unmarshal

    Returns:
        Unmarshaled Cty value
    """
    try:
        # Skip magic bytes if present
        if len(data) >= len(CTY_MAGIC_BYTES) and data[:len(CTY_MAGIC_BYTES)] == CTY_MAGIC_BYTES:
            data = data[len(CTY_MAGIC_BYTES):]

        # Unpack the payload
        payload = msgpack.unpackb(data, **DEFAULT_DECODE_OPTIONS)

        # Import here to avoid circular imports
        from pyvider.cty.values import CtyValue
        import importlib

        # Get type information
        type_name = msgpack.unpackb(payload["type"], **DEFAULT_DECODE_OPTIONS)

        # Try to import the type class
        try:
            # Attempt to get type class from pyvider.cty
            module = importlib.import_module("pyvider.cty")
            type_class = getattr(module, type_name)
            cty_type = type_class()
        except (ImportError, AttributeError) as e:
            # Fallback to dynamic type if import fails
            logger.warning(f"🧮🔍⚠️ Could not import type {type_name}, using dynamic: {e}")
            from pyvider.cty import CtyDynamic
            cty_type = CtyDynamic()

        # Check for null or unknown values
        is_null = payload.get("is_null", False)
        is_known = payload.get("is_known", True)

        if is_null:
            return CtyValue(type_=cty_type, is_null=True)

        if not is_known:
            return CtyValue(type_=cty_type, is_unknown=True)

        # Get value data
        value_data = payload.get("value")
        if value_data is None:
            return CtyValue(type_=cty_type, value=None)

        # Deserialize the value
        serializer = MsgpackSerializer()
        value = serializer.deserialize(CTY_MAGIC_BYTES + value_data)

        # Create the Cty value
        result = CtyValue(type_=cty_type, value=value)

        # Apply marks if present
        marks = payload.get("marks", [])
        for mark in marks:
            result = result.mark(mark)

        return result
    except Exception as e:
        raise DeserializationError(f"Failed to unmarshal value: {e}", data=data, format_name="msgpack") from e

# 🐍🏗️🐣
