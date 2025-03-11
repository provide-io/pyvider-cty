
# pyvider/cty/encoding/protobuf.py

"""
Protobuf encoding for CTY types and values.

This module provides bidirectional conversion between Pyvider's CTY type system
and Terraform's protobuf representations. It enables serialization of CTY values
to protobuf DynamicValue messages and deserialization back to CTY values.

Key functions:
- encode_value: Convert CTY value to protobuf DynamicValue
- decode_value: Convert protobuf DynamicValue to CTY value
- get_proto_type: Convert CTY type to protobuf schema type bytes
- get_cty_type: Convert protobuf schema type bytes to CTY type
"""

import json
import asyncio
from typing import Any, Dict, Optional, Type, TypeVar, Union, cast

from pyvider.telemetry import logger
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.primitives import CtyString, CtyNumber, CtyBool
from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
from pyvider.cty.types.structural import CtyObject, CtyDynamic, CtyTuple

# Import the protocol types for serialization
from pyvider.protocols.tfprotov6.protobuf import DynamicValue

# Type variable for generic functions
T = TypeVar('T')

# Mapping from CTY type classes to protobuf schema type bytes
_CTY_TYPE_TO_PROTO: Dict[Type[CtyType], bytes] = {
    CtyString: b'"string"',
    CtyNumber: b'"number"',
    CtyBool: b'"bool"',
    CtyList: b'"list"',
    CtyMap: b'"map"',
    CtySet: b'"set"',
    CtyObject: b'"object"',
    CtyDynamic: b'"dynamic"',
    CtyTuple: b'"tuple"',
}

# Mapping from protobuf schema type bytes to CTY type classes
_PROTO_TO_CTY_TYPE: Dict[bytes, Type[CtyType]] = {
    b'"string"': CtyString,
    b'"number"': CtyNumber,
    b'"bool"': CtyBool,
    b'"list"': CtyList,
    b'"map"': CtyMap,
    b'"set"': CtySet,
    b'"object"': CtyObject,
    b'"dynamic"': CtyDynamic,
    b'"tuple"': CtyTuple,
}

async def get_proto_type(cty_type: Union[CtyType, Type[CtyType]]) -> bytes:
    """
    Convert a CTY type to its protobuf schema type representation.
    
    Args:
        cty_type: A CTY type instance or class
        
    Returns:
        bytes: The protobuf schema type bytes
        
    Raises:
        ValueError: If the type cannot be converted
    """
    logger.debug(f"🧰📤🔄 Converting CTY type to protobuf: {cty_type!r}")
    
    # Handle instance vs class
    actual_type = type(cty_type) if isinstance(cty_type, CtyType) else cty_type
    
    # Look up in mapping
    if actual_type in _CTY_TYPE_TO_PROTO:
        proto_type = _CTY_TYPE_TO_PROTO[actual_type]
        logger.debug(f"🧰📤✅ Converted to protobuf type: {proto_type!r}")
        return proto_type
    
    # Fallback to dynamic type
    logger.warning(f"🧰📤⚠️ Unknown CTY type {cty_type!r}, using dynamic")
    return _CTY_TYPE_TO_PROTO[CtyDynamic]

async def get_cty_type(proto_type: bytes) -> Type[CtyType]:
    """
    Convert a protobuf schema type to its corresponding CTY type class.
    
    Args:
        proto_type: The protobuf schema type bytes
        
    Returns:
        Type[CtyType]: The corresponding CTY type class
        
    Raises:
        ValueError: If the type cannot be converted
    """
    logger.debug(f"🧰📥🔄 Converting protobuf type to CTY: {proto_type!r}")
    
    # Look up in mapping
    if proto_type in _PROTO_TO_CTY_TYPE:
        cty_type = _PROTO_TO_CTY_TYPE[proto_type]
        logger.debug(f"🧰📥✅ Converted to CTY type: {cty_type.__name__}")
        return cty_type
    
    # Fallback to dynamic type
    logger.warning(f"🧰📥⚠️ Unknown protobuf type {proto_type!r}, using dynamic")
    return CtyDynamic

async def encode_value(value: Any, cty_type: Optional[Union[CtyType, Type[CtyType]]] = None) -> DynamicValue:
    """
    Encode a Python value to a protobuf DynamicValue using the specified CTY type.
    
    Args:
        value: The Python value to encode
        cty_type: Optional CTY type to use for encoding (inferred if not provided)
        
    Returns:
        DynamicValue: Protobuf DynamicValue message
        
    Raises:
        ValueError: If the value cannot be encoded
    """
    logger.debug(f"🧰📤🔄 Encoding value to DynamicValue: {value!r}")
    
    # Handle None value
    if value is None:
        logger.debug("🧰📤🔄 Encoding None value as null")
        return DynamicValue(json=b"null")
    
    # Infer type if not provided
    if cty_type is None:
        cty_type = _infer_cty_type(value)
        logger.debug(f"🧰📤🔄 Inferred CTY type: {cty_type.__name__}")
    
    # Convert to canonical form based on type
    try:
        # Get the type as a class
        type_class = type(cty_type) if isinstance(cty_type, CtyType) else cty_type
        
        # Convert based on type
        if type_class == CtyString:
            native_val = str(value)
        elif type_class == CtyNumber:
            native_val = float(value)
        elif type_class == CtyBool:
            native_val = bool(value)
        elif type_class == CtyList:
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"Expected list, got {type(value).__name__}")
            native_val = list(value)
        elif type_class == CtyMap or type_class == CtyObject:
            if not isinstance(value, dict):
                raise ValueError(f"Expected dict, got {type(value).__name__}")
            native_val = dict(value)
        elif type_class == CtySet:
            if not isinstance(value, (set, frozenset, list, tuple)):
                raise ValueError(f"Expected set or list, got {type(value).__name__}")
            native_val = list(value)  # JSON doesn't support sets
        else:
            # Use string representation for unknown types
            native_val = str(value)
        
        # Convert to JSON
        json_str = json.dumps(native_val)
        json_bytes = json_str.encode('utf-8')
        
        # Create DynamicValue
        dynamic_value = DynamicValue(json=json_bytes)
        logger.debug(f"🧰📤✅ Encoded to DynamicValue: {json_str[:100]}{'...' if len(json_str) > 100 else ''}")
        return dynamic_value
        
    except Exception as e:
        logger.error(f"🧰📤❌ Error encoding value: {e}")
        raise ValueError(f"Failed to encode value to DynamicValue: {e}")

async def decode_value(dynamic_value: DynamicValue, cty_type: Union[CtyType, Type[CtyType]]) -> Any:
    """
    Decode a protobuf DynamicValue to a Python value using the specified CTY type.
    
    Args:
        dynamic_value: The protobuf DynamicValue message
        cty_type: CTY type to use for decoding
        
    Returns:
        Any: The decoded Python value
        
    Raises:
        ValueError: If the value cannot be decoded
    """
    logger.debug(f"🧰📥🔄 Decoding DynamicValue to Python value")
    
    # Handle empty dynamic value
    if not dynamic_value or (not dynamic_value.json and not dynamic_value.msgpack):
        logger.debug("🧰📥🔄 Empty DynamicValue, returning None")
        return None
    
    try:
        # Parse JSON or msgpack
        if dynamic_value.json:
            json_str = dynamic_value.json.decode('utf-8')
            logger.debug(f"🧰📥🔄 Decoding JSON: {json_str[:100]}{'...' if len(json_str) > 100 else ''}")
            parsed = json.loads(json_str)
        elif dynamic_value.msgpack:
            logger.warning("🧰📥⚠️ msgpack decoding not fully implemented")
            # For msgpack, we'd need to import and use the msgpack module
            # parsed = msgpack.unpackb(dynamic_value.msgpack)
            raise ValueError("msgpack decoding not implemented")
        else:
            logger.error("🧰📥❌ DynamicValue has no json or msgpack content")
            raise ValueError("DynamicValue has no content to decode")
        
        # Handle null value
        if parsed is None:
            logger.debug("🧰📥✅ Decoded null value")
            return None
        
        # Get the type as a class
        type_class = type(cty_type) if isinstance(cty_type, CtyType) else cty_type
        
        # Convert based on type
        if type_class == CtyString:
            if not isinstance(parsed, str):
                logger.warning(f"🧰📥⚠️ Expected string, got {type(parsed).__name__}, converting")
                result = str(parsed)
            else:
                result = parsed
        elif type_class == CtyNumber:
            if not isinstance(parsed, (int, float)):
                logger.warning(f"🧰📥⚠️ Expected number, got {type(parsed).__name__}, converting")
                result = float(parsed)
            else:
                result = parsed
        elif type_class == CtyBool:
            if not isinstance(parsed, bool):
                logger.warning(f"🧰📥⚠️ Expected boolean, got {type(parsed).__name__}, converting")
                result = bool(parsed)
            else:
                result = parsed
        elif type_class == CtyList:
            if not isinstance(parsed, list):
                logger.warning(f"🧰📥⚠️ Expected list, got {type(parsed).__name__}, converting")
                result = list(parsed) if hasattr(parsed, '__iter__') else [parsed]
            else:
                result = parsed
        elif type_class == CtyMap or type_class == CtyObject:
            if not isinstance(parsed, dict):
                logger.warning(f"🧰📥⚠️ Expected dict, got {type(parsed).__name__}, cannot convert")
                raise ValueError(f"Cannot convert {type(parsed).__name__} to dict")
            result = parsed
        elif type_class == CtySet:
            if not isinstance(parsed, list):
                logger.warning(f"🧰📥⚠️ Expected list for set, got {type(parsed).__name__}, converting")
                result = set(parsed) if hasattr(parsed, '__iter__') else {parsed}
            else:
                result = set(parsed)
        else:
            # Return as-is for unknown types
            result = parsed
        
        logger.debug(f"🧰📥✅ Decoded value: {result!r}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"🧰📥❌ JSON decode error: {e}")
        raise ValueError(f"Failed to decode JSON: {e}")
    except Exception as e:
        logger.error(f"🧰📥❌ Error decoding value: {e}")
        raise ValueError(f"Failed to decode DynamicValue: {e}")

def _infer_cty_type(value: Any) -> Type[CtyType]:
    """
    Infer the CTY type from a Python value.
    
    Args:
        value: The Python value
        
    Returns:
        Type[CtyType]: The inferred CTY type class
    """
    if isinstance(value, str):
        return CtyString
    elif isinstance(value, bool):
        return CtyBool
    elif isinstance(value, (int, float)):
        return CtyNumber
    elif isinstance(value, (list, tuple)):
        return CtyList
    elif isinstance(value, dict):
        return CtyMap
    elif isinstance(value, (set, frozenset)):
        return CtySet
    else:
        # Default to string for unknown types
        return CtyString

async def encode_schema_value(value: Any, schema_type: bytes) -> DynamicValue:
    """
    Encode a Python value to a protobuf DynamicValue using a schema type.
    
    This is a convenience function that combines get_cty_type and encode_value.
    
    Args:
        value: The Python value to encode
        schema_type: The schema type bytes (e.g., b'"string"')
        
    Returns:
        DynamicValue: Protobuf DynamicValue message
    """
    logger.debug(f"🧰📤🔄 Encoding value with schema type: {schema_type!r}")
    
    # Convert schema type to CTY type
    cty_type = await get_cty_type(schema_type)
    
    # Encode value
    return await encode_value(value, cty_type)

async def decode_schema_value(dynamic_value: DynamicValue, schema_type: bytes) -> Any:
    """
    Decode a protobuf DynamicValue to a Python value using a schema type.
    
    This is a convenience function that combines get_cty_type and decode_value.
    
    Args:
        dynamic_value: The protobuf DynamicValue message
        schema_type: The schema type bytes (e.g., b'"string"')
        
    Returns:
        Any: The decoded Python value
    """
    logger.debug(f"🧰📥🔄 Decoding value with schema type: {schema_type!r}")
    
    # Convert schema type to CTY type
    cty_type = await get_cty_type(schema_type)
    
    # Decode value
    return await decode_value(dynamic_value, cty_type)