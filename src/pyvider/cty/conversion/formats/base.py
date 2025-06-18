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

from pyvider.cty.conversion.wire import WireFormatType

T = TypeVar("T")
JSON = WireFormatType.JSON
MSGPACK = WireFormatType.MSGPACK


class FormatEncoder:
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


_ENCODERS: dict[WireFormatType, type[FormatEncoder]] = {}


def register_formatter(
    format_type: WireFormatType,
) -> Callable[[type[FormatEncoder]], type[FormatEncoder]]:
    """
    Decorator to register a FormatEncoder implementation for a specific WireFormatType.

    Args:
        format_type: The WireFormatType that the decorated class handles.

    Returns:
        A decorator function that registers the class.
    """
    def decorator(encoder_class: type[FormatEncoder]) -> type[FormatEncoder]:
        if not issubclass(encoder_class, FormatEncoder):
            raise TypeError(
                f"Format encoder {encoder_class.__name__} must extend FormatEncoder"
            )
        _ENCODERS[format_type] = encoder_class
        return encoder_class

    return decorator


def get_formatter(format_type: WireFormatType) -> type[FormatEncoder] | None:
    """
    Retrieves the registered FormatEncoder class for a given WireFormatType.

    Args:
        format_type: The WireFormatType to look up.

    Returns:
        The registered FormatEncoder class, or None if not found.
    """
    return _ENCODERS.get(format_type)


def list_formatters() -> dict[WireFormatType, str]:
    """
    Lists all registered format encoders.

    Returns:
        A dictionary mapping WireFormatType to the name of the registered encoder class.
    """
    return {fmt: encoder.__name__ for fmt, encoder in _ENCODERS.items()}


# 🐍🏗️
