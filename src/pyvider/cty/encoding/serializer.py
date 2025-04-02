# pyvider/cty/encoding/serializer.py

"""
Low-level serialization utilities for Cty values.

This module provides the core serialization capabilities for converting Cty values
to and from various binary formats. It implements direct serialization functions
without protocol-specific handling or type information preservation, serving as
the foundation layer for the higher-level serialization system.

The ValueSerializer class provides static methods for common serialization formats
including JSON and MessagePack, handling the raw conversion between Python values
and their binary representations.
"""

from typing import Any, Dict, List, Optional, Union

from attrs import define

@define(frozen=True, slots=True)
class ValueSerializer:
    """
    Core value serialization handler for Cty values.

    This class provides low-level serialization capabilities for converting between
    Cty/Python values and their binary representations. It operates without protocol
    awareness or type information, focusing solely on the transformation of values
    to and from bytes.

    The class is immutable and provides only static methods, acting as a namespace
    for serialization functions rather than maintaining any state. Each method handles
    a specific serialization format with consistent interfaces for serialization
    and deserialization.

    This class is typically not used directly by client code; instead, the higher-level
    serialization functions in the encoding package provide a more convenient API
    with type preservation and format detection.

    Example:
        >>> from pyvider.cty.encoding.serializer import ValueSerializer
        >>> data = {"name": "example", "value": 42}
        >>> binary = ValueSerializer.to_json_bytes(data)
        >>> restored = ValueSerializer.from_json_bytes(binary)
        >>> assert data == restored
    """

    @staticmethod
    def to_json_bytes(value: Any) -> bytes:
        """
        Serialize a Python/Cty value to JSON bytes.

        Converts the given value to a JSON string and then encodes it as UTF-8 bytes.
        This method handles basic Python data types including dictionaries, lists,
        strings, numbers, booleans, and None, but does not preserve Cty type information.

        Args:
            value: The Python/Cty value to serialize. Must be JSON-serializable.

        Returns:
            bytes: UTF-8 encoded JSON representation of the value

        Raises:
            TypeError: If the value contains types that cannot be serialized to JSON
            ValueError: If the value structure cannot be serialized

        Example:
            >>> ValueSerializer.to_json_bytes({"name": "example"})
            b'{"name":"example"}'
        """
        # Implementation using standard json module
        import json
        return json.dumps(value).encode('utf-8')

    @staticmethod
    def from_json_bytes(json_bytes: bytes) -> Any:
        """
        Deserialize JSON bytes to a Python value.

        Decodes the given bytes as UTF-8 and parses the resulting JSON string.
        This method produces standard Python data types (dict, list, str, int,
        float, bool, None) without any Cty type information.

        Args:
            json_bytes: UTF-8 encoded JSON bytes to deserialize

        Returns:
            Any: The deserialized Python value

        Raises:
            UnicodeDecodeError: If the bytes cannot be decoded as UTF-8
            json.JSONDecodeError: If the decoded string is not valid JSON

        Example:
            >>> ValueSerializer.from_json_bytes(b'{"name":"example"}')
            {'name': 'example'}
        """
        import json
        return json.loads(json_bytes.decode('utf-8'))

    @staticmethod
    def to_msgpack_bytes(value: Any) -> bytes:
        """
        Serialize a Python/Cty value to MessagePack bytes.

        Converts the given value to the MessagePack binary format, which is more
        compact and often faster than JSON. This method handles a wide range of
        Python data types including bytes and custom types with __dict__ attributes,
        but does not preserve Cty type information.

        Args:
            value: The Python/Cty value to serialize. Must be compatible with MessagePack.

        Returns:
            bytes: MessagePack binary representation of the value

        Raises:
            TypeError: If the value contains types that cannot be packed
            OverflowError: If a numeric value is out of range
            ValueError: If the value structure cannot be serialized

        Example:
            >>> ValueSerializer.to_msgpack_bytes({"compact": True})
            b'\x81\xa7compact\xc3'  # Example binary output
        """
        import msgpack
        return msgpack.packb(value)

    @staticmethod
    def from_msgpack_bytes(msgpack_bytes: bytes) -> Any:
        """
        Deserialize MessagePack bytes to a Python value.

        Unpacks the given MessagePack binary data into standard Python data types.
        This method produces Python objects without any Cty type information.

        Args:
            msgpack_bytes: MessagePack binary data to deserialize

        Returns:
            Any: The deserialized Python value

        Raises:
            ValueError: If the bytes are not valid MessagePack data
            TypeError: If the MessagePack data contains unsupported types

        Example:
            >>> # Assuming msgpack_bytes contains valid MessagePack data
            >>> ValueSerializer.from_msgpack_bytes(msgpack_bytes)
            {'compact': True}
        """
        import msgpack
        return msgpack.unpackb(msgpack_bytes)

# 🐍🏗️🐣
