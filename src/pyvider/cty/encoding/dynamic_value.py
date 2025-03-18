#!/usr/bin/env python3
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

from pyvider.cty.types import CtyDynamic
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import TransformationError
from pyvider.telemetry import logger
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

        Args:
            value: The value to encode (Python primitive, CtyValue, or CtyDynamic)

        Returns:
            ProtoDynamicValue: A proper DynamicValue protobuf message

        Raises:
            TransformationError: If encoding fails
        """
        logger.debug(f"🧰📝🔄 Encoding value to DynamicValue: {repr(value)[:100]}")

        try:
            # Auto-convert primitive types for convenience
            if isinstance(value, (int, float)):
                from pyvider.cty.types.primitives import CtyNumber
                value = CtyValue(CtyNumber(), value)
            elif isinstance(value, str):
                from pyvider.cty.types.primitives import CtyString
                value = CtyValue(CtyString(), value)
            elif isinstance(value, bool):
                from pyvider.cty.types.primitives import CtyBool
                value = CtyValue(CtyBool(), value)
            elif isinstance(value, list):
                from pyvider.cty.types.collections import CtyList
                value = CtyValue(CtyList(element_type=CtyDynamic()), value)
            elif isinstance(value, dict):
                from pyvider.cty.types.collections import CtyMap
                from pyvider.cty.types.primitives import CtyString
                value = CtyValue(CtyMap(key_type=CtyString(), value_type=CtyDynamic()), value)

            # Get the JSON representation
            if hasattr(value, 'to_dict'):
                # Use to_dict method if available
                value_dict = value.to_dict()
                json_str = json.dumps(value_dict)
            else:
                # Direct JSON encoding for Python primitives
                json_str = json.dumps(value)
                
            # Convert to bytes
            json_bytes = json_str.encode('utf-8')
            
            # Create a proper DynamicValue protobuf message
            dynamic_value = ProtoDynamicValue(json=json_bytes)
            
            logger.debug(f"🧰📝✅ Successfully encoded to DynamicValue protobuf message")
            return dynamic_value
            
        except Exception as e:
            error_msg = f"Failed to encode value to DynamicValue: {e}"
            logger.error(f"🧰📝❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e

    @staticmethod
    def decode(data: Union[ProtoDynamicValue, bytes]) -> Any:
        """
        Decode a Terraform DynamicValue protobuf message into a Python value.

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
            value_dict = json.loads(json_str)
            
            # Try to convert to CtyValue if needed
            if isinstance(value_dict, dict) and 'type' in value_dict:
                try:
                    from pyvider.cty.values import CtyValue
                    decoded_value = CtyValue.from_dict(value_dict)
                    logger.debug(f"🧰🔍✅ Decoded to CtyValue: {repr(decoded_value)[:100]}")
                    return decoded_value
                except Exception as e:
                    # Fallback to raw dict if CtyValue conversion fails
                    logger.warning(f"🧰🔍⚠️ Failed to convert to CtyValue: {e}, using raw dict")
                    return value_dict
            else:
                # Return raw Python value
                logger.debug(f"🧰🔍✅ Decoded to Python value: {repr(value_dict)[:100]}")
                return value_dict
                
        except json.JSONDecodeError as e:
            error_msg = f"Failed to decode JSON: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to decode DynamicValue: {e}"
            logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
            raise TransformationError(error_msg) from e

# 🐍🏗️
