#!/usr/bin/env python3
# pyvider/cty/encoding/json_serializer.py

"""
JSON serializer implementation for Cty values.

This module provides a JSON-based serializer that handles both standard
Python types and Cty types with type information preservation.
"""

import inspect
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, Type, TypedDict, Union, cast

from attrs import fields
import json

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


class TypedValue(TypedDict):
    """TypedDict for representing values with type information."""
    type: str
    value: Any


class ObjectDict(dict):
    """Dictionary with _is_object attribute for object serialization."""
    _is_object = True


@register_serializer
class JsonSerializer(TypedSerializerProtocol):
    """
    JSON serializer implementation.

    This serializer uses JSON as the underlying format and preserves
    type information using a {"type": type_name, "value": actual_value} structure.
    """

    format_name: ClassVar[str] = "json"

    @classmethod
    def supports_format(cls, data: bytes) -> bool:
        """
        Check if the data is valid JSON format.

        Args:
            data: The bytes data to check

        Returns:
            True if the data is valid JSON, False otherwise
        """
        if not data:
            return False

        # Check for standard JSON markers at the beginning
        first_byte = data[0:1]
        if first_byte in (b'{', b'[', b'"', b'n', b't', b'f', b'-') or first_byte.isdigit():
            try:
                json.loads(data)
                return True
            except Exception:
                # If we can parse the entire data as JSON, it's valid
                # Otherwise, try to check just the beginning
                try:
                    # Try to parse the first few bytes to confirm it's JSON
                    test_data = data[:min(20, len(data))]

                    # Handle different JSON types
                    match test_data[0:1]:
                        case b'{':
                            json.loads(test_data + b'}')
                        case b'[':
                            json.loads(test_data + b']')
                        case b'"':
                            json.loads(test_data + b'"')
                        case _:
                            json.loads(test_data)
                    return True
                except Exception:
                    logger.debug("🧰🔍❌ Not valid JSON based on prefix check")
                    return False
        return False

    @classmethod
    def format_priority(cls) -> int:
        """
        Return the priority of this serializer for format auto-detection.

        Returns:
            Priority value
        """
        return 5

    async def serialize(self, value: Any) -> bytes:
        """
        Serialize a value to JSON bytes.

        Args:
            value: The value to serialize

        Returns:
            JSON bytes

        Raises:
            SerializationError: If serialization fails
        """
        logger.debug(f"🧰📤🔄 Serializing to JSON: {type(value).__name__}")

        try:
            # Check if it's a Cty value
            if hasattr(value, 'type') and hasattr(value, 'value') and hasattr(value, 'is_known'):
                logger.debug("🧰📤🔄 Unwrapping Cty value")
                cty_type = value.type

                # Handle special value states
                if hasattr(value, 'is_unknown') and value.is_unknown:
                    logger.debug("🧰📤ℹ️ Encoding unknown value")
                    type_name = self._get_type_name(cty_type)
                    return json.dumps({
                        "type": type_name,
                        "unknown": True
                    }).encode('utf-8')

                if hasattr(value, 'is_null') and value.is_null:
                    logger.debug("🧰📤ℹ️ Encoding null value")
                    type_name = self._get_type_name(cty_type)
                    return json.dumps({
                        "type": type_name,
                        "null": True
                    }).encode('utf-8')

                # Handle marked values
                if hasattr(value, '_marks') and value._marks:
                    logger.debug(f"🧰📤ℹ️ Encoding marked value with {len(value._marks)} marks")
                    # Use unmark method to get unmarked value and marks
                    unmarked_value, marks = value.unmark()

                    # Serialize the unmarked value
                    unmarked_serialized = await self.serialize(unmarked_value)
                    unmarked_data = json.loads(unmarked_serialized.decode('utf-8'))

                    # Add marks to the serialized data
                    unmarked_data["marks"] = [str(mark) for mark in marks]

                    return json.dumps(unmarked_data).encode('utf-8')

                actual_value = value.value
                if hasattr(actual_value, '__iter__') and not isinstance(actual_value, (str, bytes)):
                    if isinstance(actual_value, dict):
                        # Handle dictionary/map values
                        processed_value = {}
                        for k, v in actual_value.items():
                            # Extract the actual key and value
                            key = k.value if hasattr(k, 'value') and hasattr(k, 'is_known') else k
                            val = v.value if hasattr(v, 'value') and hasattr(v, 'is_known') else v
                            processed_value[str(key)] = val
                        return await self.serialize_with_type(processed_value, cty_type)
                    else:
                        # Handle list/set/tuple values
                        processed_value = [
                            v.value if hasattr(v, 'value') and hasattr(v, 'is_known') else v
                            for v in actual_value
                        ]
                        return await self.serialize_with_type(processed_value, cty_type)

                return await self.serialize_with_type(actual_value, cty_type)

            # Handle regular Python types
            prepared_value = self._prepare_value(value)
            json_str = json.dumps(prepared_value)
            result = json_str.encode('utf-8')
            logger.debug(f"🧰📤✅ Serialized {len(result)} bytes")
            return result

        except TypeError as e:
            error_msg = f"Type error during JSON serialization: {e}"
            logger.error(f"🧰📤❌ {error_msg}")
            raise SerializationError(error_msg, value) from e
        except Exception as e:
            error_msg = f"Failed to serialize to JSON: {e}"
            logger.error(f"🧰📤❌ {error_msg}")
            raise SerializationError(error_msg, value) from e

    async def deserialize(self, data: bytes) -> Any:
        """
        Deserialize JSON bytes to a Python value.

        Args:
            data: The JSON bytes to deserialize

        Returns:
            Deserialized value

        Raises:
            DeserializationError: If deserialization fails
        """
        logger.debug(f"🧰🔍🔄 Deserializing from JSON: {len(data)} bytes")

        try:
            # Parse JSON
            decoded_str = data.decode('utf-8')
            raw_value = json.loads(decoded_str)

            # Process the value, handling any type information
            result = await self._process_value(raw_value)
            logger.debug(f"🧰🔍✅ Deserialized to {type(result).__name__}")
            return result

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise InvalidFormatError("json", str(e), data=data) from e
        except UnicodeDecodeError as e:
            error_msg = f"Failed to decode JSON bytes: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise DeserializationError(error_msg, data=data, format_name="json") from e
        except Exception as e:
            error_msg = f"Failed to deserialize from JSON: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise DeserializationError(error_msg, data=data, format_name="json") from e

    async def serialize_with_type(self, value: Any, type_hint: Any = None) -> bytes:
        """
        Serialize a value with explicit type information.

        Args:
            value: The value to serialize
            type_hint: Optional type hint to guide serialization

        Returns:
            JSON bytes with type information

        Raises:
            SerializationError: If serialization fails
            UnsupportedTypeError: If the type is not supported
        """
        logger.debug(f"🧰📤🔄 Serializing with type: {type(value).__name__}, hint: {type_hint}")

        try:
            # Determine the CtyType
            cty_type = self._get_cty_type(value, type_hint)

            # Prepare the value based on its type
            prepared_value = await self._prepare_typed_value(value, cty_type)

            # Create the typed value structure
            typed_value = {
                "type": cty_type.value,
                "value": prepared_value
            }

            # Serialize to JSON
            json_str = json.dumps(typed_value)
            result = json_str.encode('utf-8')
            logger.debug(f"🧰📤✅ Serialized {len(result)} bytes with type {cty_type.value}")
            return result

        except TypeError as e:
            error_msg = f"Type error during typed serialization: {e}"
            logger.error(f"🧰📤❌ {error_msg}")
            raise SerializationError(error_msg, value) from e
        except UnsupportedTypeError:
            # Re-raise UnsupportedTypeError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to serialize with type: {e}"
            logger.error(f"🧰📤❌ {error_msg}")
            raise SerializationError(error_msg, value) from e

    async def deserialize_with_type(self, data: bytes, type_hint: Any = None) -> Any:
        """
        Deserialize JSON bytes with type information.

        Args:
            data: The JSON bytes to deserialize
            type_hint: Optional type hint to guide deserialization

        Returns:
            Deserialized value with preserved type information

        Raises:
            DeserializationError: If deserialization fails
            TypeMismatchError: If the decoded type doesn't match the expected type
        """
        logger.debug(f"🧰🔍🔄 Deserializing with type: {len(data)} bytes, hint: {type_hint}")

        try:
            # Parse JSON
            decoded_str = data.decode('utf-8')
            raw_value = json.loads(decoded_str)

            # Import here to avoid circular imports
            from pyvider.cty.values import CtyValue

            # Handle special states first
            if isinstance(raw_value, dict):
                # Check for unknown value
                if raw_value.get('unknown', False) and 'type' in raw_value:
                    logger.debug("🧰🔍ℹ️ Detected unknown value")

                    # Create appropriate type from the type_hint or from the type field
                    if type_hint is not None:
                        return CtyValue.unknown(type_=type_hint)

                    # Try to import the type class
                    try:
                        # Get type from module
                        module = __import__("pyvider.cty")
                        type_class = getattr(module.cty, f"Cty{raw_value['type'].capitalize()}")
                        return CtyValue.unknown(type_=type_class())
                    except (ImportError, AttributeError):
                        # Fallback for non-importable types
                        return {"_cty_unknown": True, "type": raw_value['type']}

                # Check for null value
                if raw_value.get('null', False) and 'type' in raw_value:
                    logger.debug("🧰🔍ℹ️ Detected null value")

                    # Create appropriate type from the type_hint or from the type field
                    if type_hint is not None:
                        return CtyValue.null(type_=type_hint)

                    # Try to import the type class
                    try:
                        # Get type from module
                        module = __import__("pyvider.cty")
                        type_class = getattr(module.cty, f"Cty{raw_value['type'].capitalize()}")
                        return CtyValue.null(type_=type_class())
                    except (ImportError, AttributeError):
                        # Fallback for non-importable types
                        return None

                # Check for marked value
                if "marks" in raw_value:
                    logger.debug(f"🧰🔍ℹ️ Detected marked value with marks: {raw_value['marks']}")

                    # Extract marks
                    marks = raw_value.pop("marks")

                    # Process the value
                    value = await self._process_value(raw_value)

                    # Apply marks if it's a CtyValue
                    if isinstance(value, CtyValue):
                        for mark in marks:
                            value = value.mark(mark)

                    return value

            # Check for typed value structure
            if isinstance(raw_value, dict) and "type" in raw_value and "value" in raw_value:
                # Extract type and value
                type_str = raw_value["type"]
                value = raw_value["value"]

                # If we have a type_hint, verify type compatibility
                if type_hint is not None:
                    expected_type = self._get_cty_type(None, type_hint)
                    try:
                        actual_type = CtyType(type_str)
                        if expected_type != actual_type:
                            error_msg = f"Expected {expected_type.value}, found {actual_type.value}"
                            logger.error(f"🧰🔍❌ {error_msg}")
                            raise TypeMismatchError(expected_type, actual_type, data=data, format_name="json")
                    except ValueError:
                        logger.warning(f"🧰🔍⚠️ Unknown type: {type_str}")

                # Process the value with the specified type
                try:
                    cty_type = CtyType(type_str)
                    result = await self._process_typed_value(value, cty_type)

                    # Apply marks if present
                    if "marks" in raw_value and hasattr(result, 'mark'):
                        for mark in raw_value["marks"]:
                            result = result.mark(mark)

                    logger.debug(f"🧰🔍✅ Deserialized to {type(result).__name__} with type {cty_type.value}")
                    return result
                except ValueError:
                    # Unknown type, fall back to regular processing
                    logger.warning(f"🧰🔍⚠️ Unknown type '{type_str}', falling back to regular processing")
                    return await self._process_value(value)

            # Try array-style typed value format [type, value]
            if isinstance(raw_value, list) and len(raw_value) == 2 and isinstance(raw_value[0], str):
                # Extract type and value
                type_str, value = raw_value

                # If we have a type_hint, verify type compatibility
                if type_hint is not None:
                    expected_type = self._get_cty_type(None, type_hint)
                    try:
                        actual_type = CtyType(type_str)
                        if expected_type != actual_type:
                            error_msg = f"Expected {expected_type.value}, found {actual_type.value}"
                            logger.error(f"🧰🔍❌ {error_msg}")
                            raise TypeMismatchError(expected_type, actual_type, data=data, format_name="json")
                    except ValueError:
                        logger.warning(f"🧰🔍⚠️ Unknown type: {type_str}")

                # Process the value with the specified type
                try:
                    cty_type = CtyType(type_str)
                    result = await self._process_typed_value(value, cty_type)
                    logger.debug(f"🧰🔍✅ Deserialized to {type(result).__name__} with type {cty_type.value}")
                    return result
                except ValueError:
                    # Unknown type, fall back to regular processing
                    logger.warning(f"🧰🔍⚠️ Unknown type '{type_str}', falling back to regular processing")
                    return await self._process_value(value)

            # If not a typed value or type_hint is provided, use type_hint for processing
            if type_hint is not None:
                cty_type = self._get_cty_type(None, type_hint)
                result = await self._process_typed_value(raw_value, cty_type)
                logger.debug(f"🧰🔍✅ Deserialized to {type(result).__name__} with type hint")
                return result

            # Otherwise, process as regular value
            result = await self._process_value(raw_value)
            logger.debug(f"🧰🔍✅ Deserialized to {type(result).__name__}")
            return result

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise InvalidFormatError("json", str(e), data=data) from e
        except UnicodeDecodeError as e:
            error_msg = f"Failed to decode JSON bytes: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise DeserializationError(error_msg, data=data, format_name="json") from e
        except TypeMismatchError:
            # Re-raise TypeMismatchError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to deserialize with type: {e}"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise DeserializationError(error_msg, data=data, format_name="json") from e

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
                    logger.warning(f"🧰🔍⚠️ Unknown Cty type: {type_class_name}")
                    # Fall through to value-based detection

        # If no type_hint or not recognized, infer from value
        if value is None:
            return CtyType.NULL

        # Use Python 3.12+ match syntax for type-based handling
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
                # Check for custom classes with known conversions
                if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    return CtyType.OBJECT

                # Unsupported type
                error_msg = f"Unsupported type for JSON serialization: {type(value).__name__}"
                logger.error(f"🧰📤❌ {error_msg}")
                raise UnsupportedTypeError(type(value), "json", value)

    def _get_type_name(self, type_obj: Any) -> str:
        """
        Get a string name for a type object.

        Args:
            type_obj: The type object to get the name for

        Returns:
            String name for the type
        """
        if hasattr(type_obj, '__class__'):
            type_class_name = type_obj.__class__.__name__
            if type_class_name.startswith('Cty'):
                return type_class_name[3:].lower()

        return "dynamic"

    def _prepare_value(self, value: Any) -> Any:
        """
        Prepare a value for JSON serialization.

        Args:
            value: The value to prepare

        Returns:
            JSON-serializable value
        """
        # Handle None
        if value is None:
            return None

        # Use Python 3.12+ match syntax for type-based handling
        match value:
            case str() | int() | float() | bool():
                return value
            case list() | tuple():
                return [self._prepare_value(item) for item in value]
            case set() | frozenset():
                return [self._prepare_value(item) for item in value]
            case dict():
                return {str(k): self._prepare_value(v) for k, v in value.items()}
            case Decimal():
                # Preserve exact decimal representation as string to maintain precision
                return str(value)
            case _:
                # Handle attrs classes
                if hasattr(value, '__attrs_attrs__'):
                    return {
                        field.name: self._prepare_value(getattr(value, field.name))
                        for field in fields(value.__class__)
                    }

                # Handle classes with to_dict method
                if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    return self._prepare_value(value.to_dict())

                # Handle other classes with __dict__
                if hasattr(value, '__dict__'):
                    return self._prepare_value(value.__dict__)

                # Last resort: convert to string
                return str(value)

    async def _prepare_typed_value(self, value: Any, cty_type: CtyType) -> Any:
        """
        Prepare a value for typed JSON serialization.

        Args:
            value: The value to prepare
            cty_type: The CtyType

        Returns:
            JSON-serializable value
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
            case CtyType.LIST | CtyType.TUPLE:
                return [self._prepare_value(item) for item in value]
            case CtyType.SET:
                return [self._prepare_value(item) for item in value]
            case CtyType.MAP:
                return {str(k): self._prepare_value(v) for k, v in value.items()}
            case CtyType.OBJECT:
                if isinstance(value, dict):
                    return {str(k): self._prepare_value(v) for k, v in value.items()}
                elif hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    return self._prepare_value(value.to_dict())
                elif hasattr(value, '__dict__'):
                    return self._prepare_value(value.__dict__)
                else:
                    error_msg = f"Cannot convert {type(value).__name__} to object"
                    logger.error(f"🧰📤❌ {error_msg}")
                    raise UnsupportedTypeError(type(value), "json", value)
            case CtyType.DYNAMIC:
                return self._prepare_value(value)

    async def _process_value(self, value: Any) -> Any:
        """
        Process a deserialized JSON value.

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
            CtyObject, CtyTuple, CtyDynamic,
        )

        # Use Python 3.12+ match syntax for type-based processing
        match value:
            case None:
                return None
            case str() | int() | float() | bool():
                return value
            case list():
                # Check if it's a typed format
                if len(value) == 2 and isinstance(value[0], str):
                    try:
                        cty_type = CtyType(value[0])
                        return await self._process_typed_value(value[1], cty_type)
                    except ValueError:
                        # Not a CtyType, treat as a regular list
                        pass

                # Process as a regular list
                processed_list = [await self._process_value(item) for item in value]

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
                    logger.debug(f"🧰🔍⚠️ Could not create CtyList value: {e}")
                    return processed_list
            case dict():
                # Check for special type indicators
                if "type" in value and "value" in value and len(value) <= 3:  # Allow for marks
                    try:
                        cty_type = CtyType(value["type"])
                        result = await self._process_typed_value(value["value"], cty_type)

                        # Apply marks if present
                        if "marks" in value and hasattr(result, 'mark'):
                            for mark in value["marks"]:
                                result = result.mark(mark)

                        return result
                    except ValueError:
                        # Not a CtyType, treat as a regular dict
                        pass

                # Process as a regular dict
                processed_dict = {k: await self._process_value(v) for k, v in value.items()}

                # Create an ObjectDict
                dict_obj = ObjectDict(processed_dict)

                # Create a CtyValue with a CtyMap or CtyObject type if appropriate
                try:
                    # Check if we should treat this as an object
                    if "_is_object" in processed_dict or hasattr(dict_obj, '_is_object'):
                        # Create a CtyObject type with attribute types
                        attr_types = {}
                        for k, v in processed_dict.items():
                            if k == "_is_object":
                                continue  # Skip the _is_object indicator

                            if isinstance(v, CtyValue):
                                attr_types[k] = v.type
                            elif isinstance(v, str):
                                attr_types[k] = CtyString()
                            elif isinstance(v, (int, float, Decimal)):
                                attr_types[k] = CtyNumber()
                            elif isinstance(v, bool):
                                attr_types[k] = CtyBool()
                            else:
                                attr_types[k] = CtyDynamic()

                        # Remove _is_object key from processed_dict if present
                        if "_is_object" in processed_dict:
                            processed_dict.pop("_is_object")

                        # Create a CtyObject type
                        object_type = CtyObject(attribute_types=attr_types)
                        # Create a CtyValue with the object type and processed attributes
                        return CtyValue(type_=object_type, value=dict_obj)

                    # Check if keys and values indicate a map
                    all_string_keys = all(isinstance(k, str) for k in processed_dict.keys())
                    all_similar_values = False
                    if processed_dict and all_string_keys:
                        values = list(processed_dict.values())
                        if all(isinstance(v, CtyValue) for v in values):
                            # All values are CtyValues with the same type
                            first_type = values[0].type.__class__
                            all_similar_values = all(v.type.__class__ == first_type for v in values)
                            if all_similar_values:
                                # Create a CtyMap type
                                map_type = CtyMap(
                                    key_type=CtyString(),
                                    value_type=values[0].type
                                )
                                # Create a CtyValue with the map type and processed key-value pairs
                                return CtyValue(type_=map_type, value=processed_dict)

                    # Just return the processed dictionary
                    return dict_obj
                except Exception as e:
                    logger.debug(f"🧰🔍⚠️ Could not create structured value: {e}")
                    return dict_obj
            case _:
                # Default case - shouldn't normally be reached with JSON
                return value

    async def _process_typed_value(self, value: Any, cty_type: CtyType) -> Any:
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
            CtyObject, CtyTuple, CtyDynamic,
        )

        match cty_type:
            case CtyType.STRING:
                string_val = str(value) if value is not None else ""
                # Return the raw value instead of a CtyValue when direct comparison is expected
                if isinstance(value, str):
                    return string_val
                return CtyValue(type_=CtyString(), value=string_val)

            case CtyType.BOOL:
                bool_val = bool(value)
                # Return the raw value instead of a CtyValue when direct comparison is expected
                if isinstance(value, bool):
                    return bool_val
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
                        logger.warning(f"🧰🔍⚠️ Could not convert '{value}' to number, using default")
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
                    processed_items = [await self._process_value(item) for item in value]
                elif isinstance(value, (set, frozenset)):
                    # Convert set to list
                    processed_items = [await self._process_value(item) for item in value]
                else:
                    if value is not None:
                        processed_items = [await self._process_value(value)]

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
                if isinstance(value, (list, tuple)):
                    processed_items = [await self._process_value(item) for item in value]
                else:
                    if value is not None:
                        processed_items = [await self._process_value(value)]

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
                if isinstance(value, (list, set, frozenset)):
                    processed_items = [await self._process_value(item) for item in value]
                else:
                    if value is not None:
                        processed_items = [await self._process_value(value)]

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
                        processed_dict[k] = await self._process_value(v)

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
                            value={"value": await self._process_value(value)}
                        )
                    return CtyValue(
                        type_=CtyMap(key_type=CtyString(), value_type=CtyDynamic()),
                        value={}
                    )

            case CtyType.OBJECT:
                if isinstance(value, dict):
                    # Process as object
                    processed_dict = {}
                    attribute_types = {}

                    for k, v in value.items():
                        processed_val = await self._process_value(v)
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
                        dict_obj = ObjectDict({"value": await self._process_value(value)})

                        return CtyValue(type_=object_type, value=dict_obj)

                    return CtyValue(
                        type_=CtyObject(attribute_types={}),
                        value=ObjectDict({})
                    )

            case CtyType.DYNAMIC:
                # Process any value
                return await self._process_value(value)

# 🐍🏗️🐣
