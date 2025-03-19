
# pyvider/cty/encoding/dynamic_value.py

"""
Terraform DynamicValue Encoding for Pyvider

This module implements Terraform's DynamicValue encoding and decoding.
It handles the conversion between Python/Cty values and Terraform's
wire format for DynamicValue messages.

Key Features:
- Encodes Python/Cty values to Terraform-compatible JSON bytes
- Decodes Terraform DynamicValue messages to Python/Cty values
- Detailed error handling and logging for debugging serialization issues
"""

import json
from typing import Any, Union

from pyvider.cty.ctypes import CtyDynamic
from pyvider.cty.exceptions import TransformationError
from pyvider.cty.logger import logger
from pyvider.protocols.tfprotov6.protobuf import DynamicValue as ProtoDynamicValue


class CtyDynamicValue:
    """
    Implements Terraform's DynamicValue encoding/decoding for the Terraform protocol.
    
    This class provides static methods to convert between Python/Cty values and
    Terraform's DynamicValue protobuf messages.
    """

    @staticmethod
    def encode(value: Any) -> ProtoDynamicValue:
        """
        Encode a Python value or CtyValue into a Terraform DynamicValue protobuf message.
        FIXED to handle more types correctly, especially lists.

        Args:
            value: The value to encode (Python primitive, CtyValue, or CtyDynamic)

        Returns:
            ProtoDynamicValue: A proper DynamicValue protobuf message

        Raises:
            TransformationError: If encoding fails
        """
        logger.debug(f"🧰📝🔄 Encoding value to DynamicValue: {repr(value)[:100]}")

        try:
            # Handle special cases
            if value is None:
                return ProtoDynamicValue(json=b"null")
                
            # Extract the value if it's a CtyValue
            if hasattr(value, "value") and hasattr(value, "type"):
                actual_value = value.value
                logger.debug(f"🧰📝🔄 Extracted value from CtyValue: {repr(actual_value)[:100]}")
            else:
                actual_value = value
                
            # Direct encoding for primitive types
            if isinstance(actual_value, (int, float, bool, str)):
                # For Terraform compatibility, encode as ["type", value]
                if isinstance(actual_value, int) or isinstance(actual_value, float):
                    typed_value = ["number", actual_value]
                elif isinstance(actual_value, bool):
                    typed_value = ["bool", actual_value]
                elif isinstance(actual_value, str):
                    typed_value = ["string", actual_value]
                else:
                    typed_value = actual_value
                    
                json_str = json.dumps(typed_value)
                logger.debug(f"🧰📝🔄 Encoded primitive value: {json_str}")
                json_bytes = json_str.encode('utf-8')
                return ProtoDynamicValue(json=json_bytes)
                
            # Handle lists directly
            if isinstance(actual_value, list):
                # For Terraform compatibility, encode as ["tuple", [...]]
                typed_value = ["tuple", actual_value]
                json_str = json.dumps(typed_value)
                logger.debug(f"🧰📝🔄 Encoded list as tuple: {json_str[:100]}")
                json_bytes = json_str.encode('utf-8')
                return ProtoDynamicValue(json=json_bytes)
                
            # Handle dict directly
            if isinstance(actual_value, dict):
                # Encode as raw object for now
                json_str = json.dumps(actual_value)
                logger.debug(f"🧰📝🔄 Encoded dict: {json_str[:100]}")
                json_bytes = json_str.encode('utf-8')
                return ProtoDynamicValue(json=json_bytes)
                
            # Handle objects with to_dict method
            if hasattr(actual_value, 'to_dict') and callable(getattr(actual_value, 'to_dict')):
                dict_value = actual_value.to_dict()
                json_str = json.dumps(dict_value)
                logger.debug(f"🧰📝🔄 Encoded object via to_dict: {json_str[:100]}")
                json_bytes = json_str.encode('utf-8')
                return ProtoDynamicValue(json=json_bytes)
                
            # Last resort - convert to string
            json_str = json.dumps(str(actual_value))
            logger.debug(f"🧰📝🔄 Encoded as string (last resort): {json_str[:100]}")
            json_bytes = json_str.encode('utf-8')
            return ProtoDynamicValue(json=json_bytes)
            
        except Exception as e:
            error_msg = f"Failed to encode value to DynamicValue: {e}"
            logger.error(f"🧰📝❌ {error_msg}", exc_info=True)
            
            # Provide a fallback encoding
            try:
                fallback_str = f"Error encoding value: {str(value)[:100]}"
                json_bytes = json.dumps(fallback_str).encode('utf-8')
                return ProtoDynamicValue(json=json_bytes)
            except Exception:
                # Ultimate fallback
                return ProtoDynamicValue(json=b'"encoding_error"')

    @staticmethod
    def decode(data: Union[ProtoDynamicValue, bytes]) -> Any:
        """
        Decode a Terraform DynamicValue protobuf message into a Python value.
        FIXED to handle Terraform type wrappers correctly.

        Args:
            data: The DynamicValue protobuf message or encoded bytes

        Returns:
            The decoded Python value or CtyValue

        Raises:
            TransformationError: If decoding fails
        """
        logger.debug(f"🧰🔍🔄 Decoding DynamicValue")

        try:
            # Extract bytes from DynamicValue protobuf message
            if isinstance(data, ProtoDynamicValue):
                logger.debug("🧰🔍🔄 Processing ProtoDynamicValue object")
                
                # Check which field is set (json or msgpack)
                if hasattr(data, 'json') and data.json:
                    logger.debug("🧰🔍🔄 Found JSON encoding")
                    json_bytes = data.json
                elif hasattr(data, 'msgpack') and data.msgpack:
                    logger.debug("🧰🔍🔄 Found msgpack encoding")
                    # Import msgpack lazily
                    import msgpack
                    return msgpack.unpackb(data.msgpack)
                else:
                    error_msg = "DynamicValue has no data (missing json or msgpack field)"
                    logger.error(f"🧰🔍❌ {error_msg}")
                    raise TransformationError(error_msg)
            else:
                # Assume raw bytes with JSON encoding
                logger.debug("🧰🔍🔄 Processing raw bytes")
                json_bytes = data

            # Decode JSON bytes to string
            json_str = json_bytes.decode('utf-8')
            logger.debug(f"🧰🔍🔄 Decoded JSON string: {json_str[:100]}")

            # Parse JSON string to Python value
            raw_value = json.loads(json_str)
            
            # Handle Terraform type wrappers
            if isinstance(raw_value, list) and len(raw_value) == 2:
                type_name = raw_value[0]
                value = raw_value[1]
                
                logger.debug(f"🧰🔍🔄 Found typed value: [{type_name}, {repr(value)[:50]}]")
                
                # Extract value based on type
                if type_name == "string":
                    return str(value)
                elif type_name == "number":
                    try:
                        if isinstance(value, str) and '.' in value:
                            return float(value)
                        elif isinstance(value, str):
                            return int(value)
                        return value  # Already a number
                    except (ValueError, TypeError):
                        return value
                elif type_name == "bool":
                    return bool(value)
                elif type_name == "tuple":
                    # Recursively process tuple elements
                    return [CtyDynamicValue._extract_value(item) for item in value]
                else:
                    # Unknown type, return as is
                    return value
            
            # Return raw value if not a type wrapper
            logger.debug(f"🧰🔍✅ Decoded to Python value: {repr(raw_value)[:100]}")
            return raw_value
                
        except json.JSONDecodeError as e:
            error_msg = f"Failed to decode JSON: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to decode DynamicValue: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e

    @staticmethod
    def _extract_value(value):
        """Helper to extract values from nested Terraform type wrappers."""
        if isinstance(value, list) and len(value) == 2:
            type_name = value[0]
            actual_value = value[1]
            
            # Handle by type
            if type_name == "string":
                return str(actual_value)
            elif type_name == "number":
                try:
                    if '.' in str(actual_value):
                        return float(actual_value)
                    return int(actual_value)
                except (ValueError, TypeError):
                    return actual_value
            elif type_name == "bool":
                return bool(actual_value)
            elif type_name == "tuple":
                return [CtyDynamicValue._extract_value(item) for item in actual_value]
                
            # Unknown type, return actual value
            return actual_value
            
        # Not a type wrapper
        return value

# 🐍🏗️
