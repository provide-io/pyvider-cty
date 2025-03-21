
# pyvider/cty/encoding/json_serializer.py

"""
JSON serializer implementation.

This module provides a JSON-based serializer that handles both standard
Python types and Cty types with type information preservation.
"""

import json
from decimal import Decimal
from enum import Enum
from typing import Any, List, TypedDict

import attrs

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


class TerraformType(str, Enum):
    """Enumeration of Terraform type names."""
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


@register_serializer
class JsonSerializer(TypedSerializerProtocol):
    """
    JSON serializer implementation.
    
    This serializer uses JSON as the underlying format and preserves
    type information using a ["type", value] structure compatible
    with Terraform's DynamicValue format.
    """
    
    format_name: str = "json"
    
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
        if data[0:1] in (b'{', b'[', b'"', b'n', b't', b'f', b'-', b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9'):
            try:
                # Try to parse the first few bytes to confirm it's JSON
                test_data = data[:min(20, len(data))]
                # This will raise an exception if not valid JSON start
                json.loads(test_data + b'}' if test_data.startswith(b'{') else
                           test_data + b']' if test_data.startswith(b'[') else
                           test_data + b'"' if test_data.startswith(b'"') else
                           test_data)
                return True
            except Exception:
                # Not valid JSON
                return False
        return False
    
    @classmethod
    def format_priority(cls) -> int:
        """
        Return the priority of this serializer for format auto-detection.
        
        JSON is a common format but can sometimes be confused with other formats,
        so we give it a moderate priority.
        
        Returns:
            Priority value
        """
        return 5
    
    def serialize(self, value: Any) -> bytes:
        """
        Serialize a value to JSON bytes.
        
        This method handles automatic type inference and conversion.
        
        Args:
            value: The value to serialize
            
        Returns:
            JSON bytes
            
        Raises:
            SerializationError: If serialization fails
        """
        logger.debug(f"🧰📝🔄 Serializing to JSON: {type(value).__name__}")
        
        try:
            # Check if it's a Cty value
            if hasattr(value, 'type') and hasattr(value, 'value'):
                logger.debug("🧰📝🔄 Unwrapping Cty value")
                cty_type = value.type
                actual_value = value.value
                return self.serialize_with_type(actual_value, cty_type)
            
            # Handle regular Python types
            prepared_value = self._prepare_value(value)
            json_str = json.dumps(prepared_value)
            result = json_str.encode('utf-8')
            logger.debug(f"🧰📝✅ Serialized {len(result)} bytes")
            return result
            
        except TypeError as e:
            error_msg = f"Type error during JSON serialization: {e}"
            logger.error(f"🧰📝❌ {error_msg}")
            raise SerializationError(error_msg, value) from e
        except Exception as e:
            error_msg = f"Failed to serialize to JSON: {e}"
            logger.error(f"🧰📝❌ {error_msg}")
            raise SerializationError(error_msg, value) from e
    
    def deserialize(self, data: bytes) -> Any:
        """
        Deserialize JSON bytes to a Python value.
        
        This method automatically handles typed values.
        
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
            result = self._process_value(raw_value)
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
    
    def serialize_with_type(self, value: Any, type_hint: Any = None) -> bytes:
        """
        Serialize a value with explicit type information.
        
        This method encodes type information alongside the value,
        using the Terraform-compatible ["type", value] structure.
        
        Args:
            value: The value to serialize
            type_hint: Optional type hint to guide serialization
            
        Returns:
            JSON bytes with type information
            
        Raises:
            SerializationError: If serialization fails
            UnsupportedTypeError: If the type is not supported
        """
        logger.debug(f"🧰📝🔄 Serializing with type: {value}, hint: {type_hint}")
        
        try:
            # Determine the Terraform type
            tf_type = self._get_terraform_type(value, type_hint)
            
            # Prepare the value based on its type
            prepared_value = self._prepare_typed_value(value, tf_type)
            
            # Create the typed value structure
            typed_value: List[Any] = [tf_type.value, prepared_value]
            
            # Serialize to JSON
            json_str = json.dumps(typed_value)
            result = json_str.encode('utf-8')
            logger.debug(f"🧰📝✅ Serialized {len(result)} bytes with type {tf_type.value}")
            return result
            
        except TypeError as e:
            error_msg = f"Type error during typed serialization: {e}"
            logger.error(f"🧰📝❌ {error_msg}")
            raise SerializationError(error_msg, value) from e
        except UnsupportedTypeError:
            # Re-raise UnsupportedTypeError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to serialize with type: {e}"
            logger.error(f"🧰📝❌ {error_msg}")
            raise SerializationError(error_msg, value) from e
    
    def deserialize_with_type(self, data: bytes, type_hint: Any = None) -> Any:
        """
        Deserialize JSON bytes with type information.
        
        This method handles typed values, either in the Terraform-compatible
        ["type", value] structure or using the type_hint parameter.
        
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
            
            # Check if the value is in the Terraform typed format
            if isinstance(raw_value, list) and len(raw_value) == 2 and isinstance(raw_value[0], str):
                # Extract type and value
                type_str, value = raw_value
                
                # If we have a type_hint, verify type compatibility
                if type_hint is not None:
                    expected_type = self._get_terraform_type(None, type_hint)
                    actual_type = TerraformType(type_str)
                    
                    if expected_type != actual_type:
                        error_msg = f"Expected {expected_type.value}, found {actual_type.value}"
                        logger.error(f"🧰🔍❌ {error_msg}")
                        raise TypeMismatchError(expected_type, actual_type, data=data, format_name="json")
                
                # Process the value with the specified type
                try:
                    tf_type = TerraformType(type_str)
                    result = self._process_typed_value(value, tf_type)
                    logger.debug(f"🧰🔍✅ Deserialized to {type(result).__name__} with type {tf_type.value}")
                    return result
                except ValueError:
                    # Unknown type, fall back to regular processing
                    logger.warning(f"🧰🔍⚠️ Unknown type '{type_str}', falling back to regular processing")
                    return self._process_value(value)
            
            # If not a typed value or type_hint is provided, use type_hint for processing
            if type_hint is not None:
                tf_type = self._get_terraform_type(None, type_hint)
                result = self._process_typed_value(raw_value, tf_type)
                logger.debug(f"🧰🔍✅ Deserialized to {type(result).__name__} with type hint")
                return result
            
            # Otherwise, process as regular value
            result = self._process_value(raw_value)
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
    
    def _get_terraform_type(self, value: Any, type_hint: Any = None) -> TerraformType:
        """
        Determine the Terraform type for a value.
        
        Args:
            value: The value to get the type for
            type_hint: Optional type hint
            
        Returns:
            Terraform type
            
        Raises:
            UnsupportedTypeError: If the type is not supported
        """
        # If type_hint is a TerraformType enum, use it directly
        if isinstance(type_hint, TerraformType):
            return type_hint
            
        # If type_hint is a Cty type, extract the Terraform type from it
        if type_hint is not None and hasattr(type_hint, '__class__'):
            # Check for Cty type naming conventions (CtyString, CtyNumber, etc.)
            type_class_name = type_hint.__class__.__name__
            if type_class_name.startswith('Cty'):
                tf_type_name = type_class_name[3:].upper()
                try:
                    return TerraformType[tf_type_name]
                except KeyError:
                    logger.warning(f"🧰🔍⚠️ Unknown Cty type: {type_class_name}")
                    # Fall through to value-based detection
        
        # If no type_hint or not recognized, infer from value
        if value is None:
            return TerraformType.NULL
        
        # Map Python types to Terraform types
        match value:
            case str():
                return TerraformType.STRING
            case bool():
                return TerraformType.BOOL
            case int() | float() | Decimal():
                return TerraformType.NUMBER
            case list() | tuple():
                # Check if it's a tuple (fixed structure) or list (homogeneous)
                if isinstance(value, tuple) or (hasattr(value, '_is_tuple') and value._is_tuple):
                    return TerraformType.TUPLE
                return TerraformType.LIST
            case set() | frozenset():
                return TerraformType.SET
            case dict():
                # Check if it's an object (structured) or map (key-value)
                if hasattr(value, '_is_object') and value._is_object:
                    return TerraformType.OBJECT
                return TerraformType.MAP
            case _:
                # Check for custom classes with known conversions
                if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    return TerraformType.OBJECT
                
                # Unsupported type
                error_msg = f"Unsupported type for JSON serialization: {type(value).__name__}"
                logger.error(f"🧰📝❌ {error_msg}")
                raise UnsupportedTypeError(type(value), "json", value)
    
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
            
        # Handle primitive types
        if isinstance(value, (str, int, float, bool)):
            return value
            
        # Handle collections recursively
        if isinstance(value, (list, tuple)):
            return [self._prepare_value(item) for item in value]
            
        if isinstance(value, (set, frozenset)):
            return [self._prepare_value(item) for item in value]
            
        if isinstance(value, dict):
            return {str(k): self._prepare_value(v) for k, v in value.items()}
            
        # Handle Decimal
        if isinstance(value, Decimal):
            # Convert to float with minimal precision loss
            return float(value)
            
        # Handle attrs classes
        if hasattr(value, '__attrs_attrs__'):
            # Convert attrs class to dict
            return {
                field.name: self._prepare_value(getattr(value, field.name))
                for field in attrs.fields(value.__class__)
            }
            
        # Handle classes with to_dict method
        if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
            return self._prepare_value(value.to_dict())
            
        # Handle other classes with __dict__
        if hasattr(value, '__dict__'):
            return self._prepare_value(value.__dict__)
            
        # Last resort: convert to string
        return str(value)
    
    def _prepare_typed_value(self, value: Any, tf_type: TerraformType) -> Any:
        """
        Prepare a value for typed JSON serialization.
        
        Args:
            value: The value to prepare
            tf_type: The Terraform type
            
        Returns:
            JSON-serializable value
        """
        match tf_type:
            case TerraformType.NULL:
                return None
                
            case TerraformType.STRING:
                return str(value)
                
            case TerraformType.BOOL:
                return bool(value)
                
            case TerraformType.NUMBER:
                if isinstance(value, Decimal):
                    return float(value)
                return value
                
            case TerraformType.LIST | TerraformType.TUPLE:
                return [self._prepare_value(item) for item in value]
                
            case TerraformType.SET:
                # Convert set to list
                return [self._prepare_value(item) for item in value]
                
            case TerraformType.MAP:
                # Ensure keys are strings
                return {str(k): self._prepare_value(v) for k, v in value.items()}
                
            case TerraformType.OBJECT:
                # Handle object (structured map)
                if isinstance(value, dict):
                    return {str(k): self._prepare_value(v) for k, v in value.items()}
                elif hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    return self._prepare_value(value.to_dict())
                elif hasattr(value, '__dict__'):
                    return self._prepare_value(value.__dict__)
                else:
                    error_msg = f"Cannot convert {type(value).__name__} to object"
                    logger.error(f"🧰📝❌ {error_msg}")
                    raise UnsupportedTypeError(type(value), "json", value)
                    
            case TerraformType.DYNAMIC:
                # Handle dynamic type (any value)
                return self._prepare_value(value)
    
    def _process_value(self, value: Any) -> Any:
        """
        Process a deserialized JSON value.
        
        Args:
            value: The raw deserialized value
            
        Returns:
            Processed value
        """
        # Handle None
        if value is None:
            return None
            
        # Handle primitive types
        if isinstance(value, (str, int, float, bool)):
            return value
            
        # Handle collections recursively
        if isinstance(value, list):
            return [self._process_value(item) for item in value]
            
        if isinstance(value, dict):
            return {k: self._process_value(v) for k, v in value.items()}
            
        # Handle typed values
        if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
            try:
                # Check if it's in the ["type", value] format
                tf_type = TerraformType(value[0])
                return self._process_typed_value(value[1], tf_type)
            except ValueError:
                # Not a recognized type, treat as a regular list
                return [self._process_value(item) for item in value]
        
        # Default: return as is
        return value
    
    def _process_typed_value(self, value: Any, tf_type: TerraformType) -> Any:
        """
        Process a deserialized value with type information.
        
        Args:
            value: The raw deserialized value
            tf_type: The Terraform type
            
        Returns:
            Processed value
        """
        match tf_type:
            case TerraformType.NULL:
                return None
                
            case TerraformType.STRING:
                return str(value) if value is not None else ""
                
            case TerraformType.BOOL:
                return bool(value)
                
            case TerraformType.NUMBER:
                if isinstance(value, str):
                    # Try to convert string to number
                    try:
                        if '.' in value:
                            return float(value)
                        else:
                            return int(value)
                    except ValueError:
                        logger.warning(f"🧰🔍⚠️ Could not convert '{value}' to number, keeping as string")
                        return value
                return value
                
            case TerraformType.LIST:
                # Process list elements recursively
                if isinstance(value, list):
                    return [self._process_value(item) for item in value]
                else:
                    logger.warning(f"🧰🔍⚠️ Expected list, got {type(value).__name__}, converting")
                    return [value] if value is not None else []
                    
            case TerraformType.TUPLE:
                # Process tuple elements recursively
                if isinstance(value, list):
                    result = [self._process_value(item) for item in value]
                    # Mark as tuple
                    result._is_tuple = True  # type: ignore
                    return result
                else:
                    logger.warning(f"🧰🔍⚠️ Expected tuple, got {type(value).__name__}, converting")
                    result = [value] if value is not None else []
                    result._is_tuple = True  # type: ignore
                    return result
                    
            case TerraformType.SET:
                # Process set elements recursively
                if isinstance(value, list):
                    # Convert to set (this loses order but enforces uniqueness)
                    result = {self._process_value(item) for item in value}
                    return result
                else:
                    logger.warning(f"🧰🔍⚠️ Expected set, got {type(value).__name__}, converting")
                    return {value} if value is not None else set()
                    
            case TerraformType.MAP:
                # Process map key/values recursively
                if isinstance(value, dict):
                    return {k: self._process_value(v) for k, v in value.items()}
                else:
                    logger.warning(f"🧰🔍⚠️ Expected map, got {type(value).__name__}, converting")
                    return {"value": value} if value is not None else {}
                    
            case TerraformType.OBJECT:
                # Process object (structured map)
                if isinstance(value, dict):
                    result = {k: self._process_value(v) for k, v in value.items()}
                    # Mark as object
                    result._is_object = True  # type: ignore
                    return result
                else:
                    logger.warning(f"🧰🔍⚠️ Expected object, got {type(value).__name__}, converting")
                    result = {"value": value} if value is not None else {}
                    result._is_object = True  # type: ignore
                    return result
                    
            case TerraformType.DYNAMIC:
                # Process any value
                return self._process_value(value)