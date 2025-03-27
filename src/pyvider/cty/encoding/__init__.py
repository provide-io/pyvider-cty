#!/usr/bin/env python3
# pyvider/cty/encoding/__init__.py

"""
Serialization package for Cty values.

This package provides a comprehensive set of tools for serializing and
deserializing Cty values to various formats, including JSON and MessagePack.
It includes support for preserving type information, handling unknown and
null values, and format auto-detection.
"""

# Import and expose the common utilities
from pyvider.cty.encoding.utils import (
    serialize,
    deserialize,
    serialize_with_type,
    deserialize_with_type,
    get_available_formats,
    is_format_available,
    detect_format,
)

# Import and expose protocol interfaces
from pyvider.cty.encoding.protocols import (
    SerializerProtocol,
    TypedSerializerProtocol,
)

# Import and expose exceptions
from pyvider.cty.encoding.exceptions import (
    SerializationError,
    DeserializationError,
    UnsupportedTypeError,
    TypeMismatchError,
    InvalidFormatError,
    NoSuitableSerializerError,
)

# Import and expose registry functions
from pyvider.cty.encoding.registry import (
    registry,
    register_serializer,
    get_serializer,
    create_serializer,
)

# Import serializers
from pyvider.cty.encoding.json_serializer import JsonSerializer
from pyvider.cty.encoding.msgpack_serializer import (
    MsgpackSerializer,
    marshal,
    unmarshal,
)

# Define the public API
# src/pyvider/cty/encoding/__init__.py
# Add marshal and unmarshal to __all__

# Define the public API
__all__ = [
    # Common utilities
    "serialize",
    "deserialize",
    "serialize_with_type",
    "deserialize_with_type",
    "get_available_formats",
    "is_format_available",
    "detect_format",
    
    # Protocol interfaces
    "SerializerProtocol",
    "TypedSerializerProtocol",
    
    # Exceptions
    "SerializationError",
    "DeserializationError",
    "UnsupportedTypeError",
    "TypeMismatchError",
    "InvalidFormatError",
    "NoSuitableSerializerError",
    
    # Registry functions
    "registry",
    "register_serializer",
    "get_serializer",
    "create_serializer",
    
    # Serializers
    "JsonSerializer",
    "MsgpackSerializer",
    
    # MessagePack-specific functions
    "marshal",
    "unmarshal",
]
