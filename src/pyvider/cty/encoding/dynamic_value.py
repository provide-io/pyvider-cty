
# pyvider/cty/encoding/dynamic_value.py

"""
Terraform-compatible dynamic value transformation.

This module provides the core transformation between Cty values and
Terraform-compatible data structures for serialization.
"""

import json
from decimal import Decimal
from typing import Any, Dict, List, TypeVar, Union

from pyvider.cty.logger import logger
from pyvider.cty.exceptions import TransformationError

T = TypeVar('T')


# Define value types as strings instead of using enum
class ValueTypes:
    """Terraform value type identifiers."""
    STRING = "string"
    NUMBER = "number"
    BOOL = "bool" 
    NULL = "null"
    TUPLE = "tuple"
    LIST = "list"
    SET = "set"
    MAP = "map"
    OBJECT = "object"
    DYNAMIC = "dynamic"


class CtyDynamicValue:
    """
    Transforms between Cty values and Terraform-compatible representations.
    
    This class serves as the primary integration point between the Cty type
    system and serialization formats, particularly Terraform's wire format.
    """
    
    @staticmethod
    def encode(value: Any) -> Any:
        """
        Convert a Cty value to a Terraform-compatible structure.
        
        Args:
            value: The value to encode (Python primitive or Cty)
            
        Returns:
            A structure ready for serialization
            
        Raises:
            TransformationError: If encoding fails
        """
        logger.debug(f"🧰📝🔄 Encoding value to CtyDynamicValue: {repr(value)[:100]}")

        try:
            # Handle None/null values
            if value is None:
                return None
                
            # Extract the value if it's a Cty-like value
            if hasattr(value, "is_known") and hasattr(value, "value"):
                # Handle unknown values
                if not getattr(value, "is_known", True):
                    logger.debug("🧰📝🔄 Encoding unknown value")
                    return {"__unknown__": True}
                    
                # Handle null values    
                if getattr(value, "is_null", False):
                    logger.debug("🧰📝🔄 Encoding null value")
                    return None
                    
                # Extract actual value
                actual_value = value.value
                logger.debug(f"🧰📝🔄 Extracted value from Cty-like object: {repr(actual_value)[:100]}")
            else:
                actual_value = value
            
            # Determine type and encode accordingly
            return CtyDynamicValue._encode_value(actual_value)
            
        except Exception as e:
            error_msg = f"Failed to encode value to CtyDynamicValue: {e}"
            logger.error(f"🧰📝❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
    
    @staticmethod
    def _encode_value(value: Any) -> Any:
        """
        Encode a specific value based on its type.
        
        Args:
            value: The value to encode
            
        Returns:
            Encoded value structure
        """
        # Handle primitive types
        if value is None:
            return None
        elif isinstance(value, str):
            logger.debug(f"🧰📝🔄 Encoding string: {value[:50]}")
            return [ValueTypes.STRING, value]
        elif isinstance(value, bool):
            logger.debug(f"🧰📝🔄 Encoding bool: {value}")
            return [ValueTypes.BOOL, value]
        elif isinstance(value, (int, float, Decimal)):
            logger.debug(f"🧰📝🔄 Encoding number: {value}")
            # Convert Decimal to float for JSON compatibility
            numeric_value = float(value) if isinstance(value, Decimal) else value
            return [ValueTypes.NUMBER, numeric_value]
        elif isinstance(value, list):
            logger.debug(f"🧰📝🔄 Encoding list with {len(value)} items")
            encoded_items = [CtyDynamicValue._encode_value(item) for item in value]
            return [ValueTypes.TUPLE, encoded_items]
        elif isinstance(value, tuple):
            logger.debug(f"🧰📝🔄 Encoding tuple with {len(value)} items")
            encoded_items = [CtyDynamicValue._encode_value(item) for item in value]
            return [ValueTypes.TUPLE, encoded_items]
        elif isinstance(value, (set, frozenset)):
            logger.debug(f"🧰📝🔄 Encoding set with {len(value)} items")
            encoded_items = [CtyDynamicValue._encode_value(item) for item in value]
            return [ValueTypes.SET, encoded_items]
        elif isinstance(value, dict):
            logger.debug(f"🧰📝🔄 Encoding dict with {len(value)} keys")
            # Ensure all keys are strings for Terraform compatibility
            encoded_dict = {}
            for k, v in value.items():
                str_key = str(k)
                encoded_dict[str_key] = CtyDynamicValue._encode_value(v)
            return [ValueTypes.OBJECT, encoded_dict]
        else:
            # Try object with to_dict method
            if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                logger.debug(f"🧰📝🔄 Encoding object with to_dict method: {type(value).__name__}")
                dict_value = value.to_dict()
                return CtyDynamicValue._encode_value(dict_value)
                
            # Try object with __dict__ attribute
            if hasattr(value, '__dict__'):
                logger.debug(f"🧰📝🔄 Encoding object using __dict__: {type(value).__name__}")
                return CtyDynamicValue._encode_value(value.__dict__)
                
            # Last resort - convert to string
            logger.debug(f"🧰📝🔄 Encoding as string (fallback): {type(value).__name__}")
            return [ValueTypes.STRING, str(value)]
    
    @staticmethod
    def decode(data: Union[Dict, List, str, bytes, None]) -> Any:
        """
        Convert a Terraform-compatible structure to a Cty value.
        
        Args:
            data: The structure or bytes to decode
            
        Returns:
            The corresponding value
            
        Raises:
            TransformationError: If decoding fails
        """
        logger.debug("🧰🔍🔄 Decoding CtyDynamicValue")

        try:
            # Handle None/null
            if data is None:
                logger.debug("🧰🔍🔄 Decoded null value")
                return None
                
            # Handle bytes by parsing as JSON
            if isinstance(data, bytes):
                logger.debug(f"🧰🔍🔄 Parsing {len(data)} bytes as JSON")
                data = json.loads(data.decode('utf-8'))
                
            # Handle string by parsing if it looks like JSON
            if isinstance(data, str):
                if data.startswith('{') or data.startswith('['):
                    logger.debug(f"🧰🔍🔄 Parsing string as JSON: {data[:50]}")
                    data = json.loads(data)
                else:
                    logger.debug(f"🧰🔍🔄 Using string as-is: {data[:50]}")
                    return data
            
            # Handle special marker for unknown values
            if isinstance(data, dict) and data.get("__unknown__", False):
                logger.debug("🧰🔍🔄 Decoded unknown value")
                return None  # Or return a proper unknown value if available
            
            # Decode the value
            result = CtyDynamicValue._decode_value(data)
            logger.debug(f"🧰🔍✅ Decoded to: {repr(result)[:100]}")
            return result
                
        except json.JSONDecodeError as e:
            error_msg = f"Failed to decode JSON: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to decode CtyDynamicValue: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
    
    @staticmethod
    def _decode_value(value: Any) -> Any:
        """
        Decode a specific value based on its structure.
        
        Args:
            value: The value to decode
            
        Returns:
            Decoded value
        """
        # Handle Terraform typed values [type, value]
        if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
            type_name, actual_value = value
            
            logger.debug(f"🧰🔍🔄 Decoding typed value: {type_name}")
            
            # Handle by value type
            if type_name == ValueTypes.STRING:
                return str(actual_value)
            elif type_name == ValueTypes.NUMBER:
                # Try to preserve integer vs float
                if isinstance(actual_value, int):
                    return actual_value
                if isinstance(actual_value, float) and actual_value.is_integer():
                    return int(actual_value)
                return actual_value
            elif type_name == ValueTypes.BOOL:
                return bool(actual_value)
            elif type_name == ValueTypes.NULL:
                return None
            elif type_name in (ValueTypes.TUPLE, ValueTypes.LIST):
                # Recursively decode each element
                return [CtyDynamicValue._decode_value(item) for item in actual_value]
            elif type_name == ValueTypes.SET:
                # Convert to a set after decoding elements
                return {CtyDynamicValue._decode_value(item) for item in actual_value}
            elif type_name in (ValueTypes.MAP, ValueTypes.OBJECT):
                # Recursively decode each value
                return {k: CtyDynamicValue._decode_value(v) for k, v in actual_value.items()}
            else:
                # Unknown type, return as is
                logger.warning(f"🧰🔍⚠️ Unknown value type: {type_name}, returning raw value")
                return actual_value
        
        # Handle raw values (not wrapped in type)
        if value is None:
            return None
        elif isinstance(value, (bool, int, float, str)):
            # Return primitive types as is
            return value
        elif isinstance(value, list):
            # Recursively decode elements
            return [CtyDynamicValue._decode_value(item) for item in value]
        elif isinstance(value, dict):
            # Recursively decode values
            return {k: CtyDynamicValue._decode_value(v) for k, v in value.items()}
        else:
            # Return anything else as is
            return value
    
    @classmethod
    def to_json(cls, value: Any) -> bytes:
        """
        Convert a value to JSON bytes in Terraform format.
        
        Args:
            value: The value to serialize
            
        Returns:
            JSON bytes
            
        Raises:
            TransformationError: If serialization fails
        """
        try:
            logger.debug(f"🧰📝🔄 Serializing to JSON: {repr(value)[:100]}")
            structure = cls.encode(value)
            json_str = json.dumps(structure)
            result = json_str.encode('utf-8')
            logger.debug(f"🧰📝✅ Serialized to {len(result)} bytes of JSON")
            return result
        except Exception as e:
            error_msg = f"Failed to serialize to JSON: {e}"
            logger.error(f"🧰📝❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
    
    @classmethod
    def from_json(cls, data: bytes) -> Any:
        """
        Convert JSON bytes in Terraform format to a value.
        
        Args:
            data: The JSON bytes to deserialize
            
        Returns:
            The corresponding value
            
        Raises:
            TransformationError: If deserialization fails
        """
        try:
            logger.debug(f"🧰🔍🔄 Deserializing from {len(data)} bytes of JSON")
            return cls.decode(data)
        except Exception as e:
            error_msg = f"Failed to deserialize from JSON: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
    
    @classmethod
    def to_msgpack(cls, value: Any) -> bytes:
        """
        Convert a value to msgpack bytes in Terraform format.
        
        Args:
            value: The value to serialize
            
        Returns:
            msgpack bytes
            
        Raises:
            TransformationError: If serialization fails
        """
        try:
            import msgpack
            logger.debug(f"🧰📝🔄 Serializing to msgpack: {repr(value)[:100]}")
            structure = cls.encode(value)
            result = msgpack.packb(structure)
            logger.debug(f"🧰📝✅ Serialized to {len(result)} bytes of msgpack")
            return result
        except ImportError:
            error_msg = "msgpack library not installed"
            logger.error(f"🧰📝❌ {error_msg}")
            raise TransformationError(error_msg)
        except Exception as e:
            error_msg = f"Failed to serialize to msgpack: {e}"
            logger.error(f"🧰📝❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
    
    @classmethod
    def from_msgpack(cls, data: bytes) -> Any:
        """
        Convert msgpack bytes in Terraform format to a value.
        
        Args:
            data: The msgpack bytes to deserialize
            
        Returns:
            The corresponding value
            
        Raises:
            TransformationError: If deserialization fails
        """
        try:
            import msgpack
            logger.debug(f"🧰🔍🔄 Deserializing from {len(data)} bytes of msgpack")
            structure = msgpack.unpackb(data)
            return cls.decode(structure)
        except ImportError:
            error_msg = "msgpack library not installed"
            logger.error(f"🧰🔍❌ {error_msg}")
            raise TransformationError(error_msg)
        except Exception as e:
            error_msg = f"Failed to deserialize from msgpack: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
    
    @staticmethod
    def is_terraform_value(data: Any) -> bool:
        """
        Check if the data appears to be in Terraform value format.
        
        Args:
            data: The data to check
            
        Returns:
            True if it looks like a Terraform value, False otherwise
        """
        # Check for [type, value] structure
        if isinstance(value := data, list) and len(value) == 2 and isinstance(value[0], str):
            type_name = value[0]
            # Check if type name is one of the known Terraform types
            valid_types = [
                ValueTypes.STRING,
                ValueTypes.NUMBER, 
                ValueTypes.BOOL,
                ValueTypes.NULL,
                ValueTypes.TUPLE,
                ValueTypes.LIST,
                ValueTypes.SET,
                ValueTypes.MAP,
                ValueTypes.OBJECT,
                ValueTypes.DYNAMIC
            ]
            return type_name in valid_types
        return False


if __name__ == "__main__":
    print("Testing DynamicValue encoding/decoding...")
    
    # Simple test
    test_values = [
        "Hello, world!",
        42,
        3.14,
        True,
        None,
        [1, 2, 3],
        {"name": "John", "age": 30},
        {"items": [1, 2, {"key": "value"}]}
    ]
    
    for value in test_values:
        encoded = CtyDynamicValue.encode(value)
        print(f"Encoded: {encoded}")
        
        decoded = CtyDynamicValue.decode(encoded)
        print(f"Decoded: {decoded}")
        
        assert decoded == value, f"Roundtrip failed for {value}"
        
    print("All tests passed!")

# 🐍🏗️
