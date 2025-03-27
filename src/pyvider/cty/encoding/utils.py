
# pyvider/cty/encoding/utils.py

"""
Utilities for Cty serialization.

This module provides convenience functions and tools for working with
Cty serialization, including format detection, auto-serialization,
and registry management.
"""

from typing import Any, Dict, List, Optional, Type, Union

from pyvider.cty.logger import logger
from pyvider.cty.encoding.protocols import SerializerProtocol
from pyvider.cty.encoding.exceptions import (
    DeserializationError,
    NoSuitableSerializerError
)
from pyvider.cty.encoding.registry import registry, get_serializer


def serialize(value: Any, format_name: str = "json") -> bytes:
    """
    Serialize a value to the specified format.
    
    This is a convenience function that automatically selects the
    appropriate serializer for the given format.
    
    Args:
        value: The value to serialize
        format_name: The name of the format to use (default: "json")
        
    Returns:
        Serialized bytes
        
    Raises:
        NoSuitableSerializerError: If no serializer is found for the format
    """
    logger.debug(f"🧰📤🔄 Serializing with format: {format_name}")
    
    try:
        # Make sure the serializer is registered
        if not is_format_available(format_name):
            error_msg = f"Format {format_name} is not available"
            logger.error(f"🧰📤❌ {error_msg}")
            raise NoSuitableSerializerError(format_name=format_name)
            
        # Get a serializer for the format
        serializer_class = get_serializer(format_name=format_name)
        serializer = serializer_class()
        
        # Serialize the value
        result = serializer.serialize(value)
        logger.debug(f"🧰📤✅ Serialized {len(result)} bytes")
        return result
    except Exception as e:
        logger.error(f"🧰📤❌ Serialization error: {e}")
        raise
    

def deserialize(data: bytes, format_name: Optional[str] = None) -> Any:
    """
    Deserialize bytes to a value.
    
    This is a convenience function that automatically detects the
    format if not specified and selects the appropriate serializer.
    
    Args:
        data: The bytes to deserialize
        format_name: The name of the format to use, or None to auto-detect
        
    Returns:
        Deserialized value
        
    Raises:
        NoSuitableSerializerError: If no serializer is found for the format
        DeserializationError: If deserialization fails
    """
    logger.debug(f"🧰📥🔄 Deserializing {len(data)} bytes")
    
    try:
        if format_name is not None:
            # Make sure the serializer is registered
            if not is_format_available(format_name):
                error_msg = f"Format {format_name} is not available"
                logger.error(f"🧰📥❌ {error_msg}")
                raise NoSuitableSerializerError(format_name=format_name)
                
            # Get a serializer for the format
            serializer_class = get_serializer(format_name=format_name)
        else:
            # Try to auto-detect the format
            detected_format = detect_format(data)
            if detected_format is None:
                error_msg = "Could not auto-detect serialization format"
                logger.error(f"🧰📥❌ {error_msg}")
                raise NoSuitableSerializerError()
                
            # Get a serializer for the detected format
            serializer_class = get_serializer(format_name=detected_format)
        
        # Create and use the serializer
        serializer = serializer_class()
        result = serializer.deserialize(data)
        logger.debug(f"🧰📥✅ Deserialized to {type(result).__name__}")
        return result
    except Exception as e:
        logger.error(f"🧰📥❌ Deserialization error: {e}")
        raise


def serialize_with_type(value: Any, type_hint: Any = None, format_name: str = "json") -> bytes:
    """
    Serialize a value with type information.
    
    This is a convenience function for serializing values with explicit
    type information, which is useful for preserving type information
    across serialization/deserialization boundaries.
    
    Args:
        value: The value to serialize
        type_hint: Optional type hint to guide serialization
        format_name: The name of the format to use (default: "json")
        
    Returns:
        Serialized bytes with type information
        
    Raises:
        NoSuitableSerializerError: If no serializer is found for the format
    """
    logger.debug(f"🧰📤🔄 Serializing with type and format: {format_name}")
    
    try:
        # Make sure the serializer is registered
        if not is_format_available(format_name):
            error_msg = f"Format {format_name} is not available"
            logger.error(f"🧰📤❌ {error_msg}")
            raise NoSuitableSerializerError(format_name=format_name)
            
        # Get a serializer for the format
        serializer_class = get_serializer(format_name=format_name)
        
        # Check if it supports typed serialization
        if not hasattr(serializer_class, 'serialize_with_type'):
            error_msg = f"Format {format_name} does not support typed serialization"
            logger.error(f"🧰📤❌ {error_msg}")
            raise NoSuitableSerializerError(
                format_name=format_name, 
                value_type=type(value) if value is not None else None
            )
        
        serializer = serializer_class()
        
        # Serialize the value with type information
        result = serializer.serialize_with_type(value, type_hint)
        logger.debug(f"🧰📤✅ Serialized with type {len(result)} bytes")
        return result
    except Exception as e:
        logger.error(f"🧰📤❌ Typed serialization error: {e}")
        raise


def deserialize_with_type(data: bytes, type_hint: Any = None, format_name: Optional[str] = None) -> Any:
    """
    Deserialize bytes with type information.
    
    This is a convenience function for deserializing values with explicit
    type information, which is useful for preserving type information
    across serialization/deserialization boundaries.
    
    Args:
        data: The bytes to deserialize
        type_hint: Optional type hint to guide deserialization
        format_name: The name of the format to use, or None to auto-detect
        
    Returns:
        Deserialized value with preserved type information
        
    Raises:
        NoSuitableSerializerError: If no serializer is found for the format
        DeserializationError: If deserialization fails
    """
    logger.debug(f"🧰📥🔄 Deserializing with type {len(data)} bytes")
    
    try:
        if format_name is not None:
            # Make sure the serializer is registered
            if not is_format_available(format_name):
                error_msg = f"Format {format_name} is not available"
                logger.error(f"🧰📥❌ {error_msg}")
                raise NoSuitableSerializerError(format_name=format_name)
                
            # Get a serializer for the format
            serializer_class = get_serializer(format_name=format_name)
        else:
            # Try to auto-detect the format
            detected_format = detect_format(data)
            if detected_format is None:
                error_msg = "Could not auto-detect serialization format"
                logger.error(f"🧰📥❌ {error_msg}")
                raise NoSuitableSerializerError()
                
            # Get a serializer for the detected format
            serializer_class = get_serializer(format_name=detected_format)
        
        # Check if it supports typed deserialization
        if not hasattr(serializer_class, 'deserialize_with_type'):
            error_msg = f"Format {detected_format} does not support typed deserialization"
            logger.error(f"🧰📥❌ {error_msg}")
            raise NoSuitableSerializerError(
                format_name=detected_format,
                value_type=type(type_hint) if type_hint is not None else None
            )
        
        # Create and use the serializer
        serializer = serializer_class()
        result = serializer.deserialize_with_type(data, type_hint)
        logger.debug(f"🧰📥✅ Deserialized with type to {type(result).__name__}")
        return result
    except Exception as e:
        logger.error(f"🧰📥❌ Typed deserialization error: {e}")
        raise


def get_available_formats() -> List[str]:
    """
    Get a list of all available serialization formats.
    
    Returns:
        List of format names
    """
    return registry.list_formats()


def is_format_available(format_name: str) -> bool:
    """
    Check if a serialization format is available.
    
    Args:
        format_name: The name of the format to check
        
    Returns:
        True if the format is available, False otherwise
    """
    return format_name in get_available_formats()


def detect_format(data: bytes) -> Optional[str]:
    """
    Detect the serialization format of the given bytes.
    
    This function tries each registered serializer to find one that
    can handle the given data.
    
    Args:
        data: The bytes to check
        
    Returns:
        The name of the detected format, or None if no format was detected
    """
    try:
        # Try to get a serializer for the data
        serializer_class = registry.get_serializer_for_data(data)
        return serializer_class.format_name
    except NoSuitableSerializerError:
        return None
