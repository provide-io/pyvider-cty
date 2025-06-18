# pyvider/cty/conversion/formats/base.py
"""
Base definitions for CTY format encoders and their registry.

This module provides the `FormatEncoder` interface that all specific
format encoders (like JSON, MessagePack) must implement. It also includes
a registry mechanism (`register_formatter`, `get_formatter`, `list_formatters`)
for managing these encoder implementations.
"""
from collections.abc import Callable  # Moved Callable import
from typing import TypeVar

from pyvider.cty.conversion.wire import WireFormatType, WireFormat # Import WireFormat

T = TypeVar("T")
JSON = WireFormatType.JSON
MSGPACK = WireFormatType.MSGPACK


class FormatEncoder(WireFormat): # Inherit from WireFormat
    """
    Abstract base class for CTY format encoders.

    Defines the interface that all format-specific encoders must implement
    to provide encoding (to bytes) and decoding (from bytes) capabilities.
    """
    @classmethod
    def format_type(cls) -> WireFormatType:
        """Returns the specific WireFormatType this encoder handles."""
        raise NotImplementedError(f"{cls.__name__}.format_type() must be implemented")

    @classmethod
    def encode(cls, value: object, **options: object) -> bytes:
        """
        Encodes the given Python object (typically a CtyValue) into bytes.

        Args:
            value: The value to encode.
            **options: Formatter-specific encoding options.

        Returns:
            The encoded value as bytes.
        """
        raise NotImplementedError(f"{cls.__name__}.encode() must be implemented")

    @classmethod
    def decode(cls, data: bytes, **options: object) -> object:
        """
        Decodes bytes into a Python object (potentially a CtyValue).

        Args:
            data: The bytes to decode.
            **options: Formatter-specific decoding options.

        Returns:
            The decoded Python object.
        """
        raise NotImplementedError(f"{cls.__name__}.decode() must be implemented")

# Old registry system removed as WireFormatRegistry is now used.

# 🐍🏗️
