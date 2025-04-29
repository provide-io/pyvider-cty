#
# pyvider/cty/conversion/formats/base.py
#

"""
Format-specific encoders for CTY wire format.

This module provides a registry of format-specific encoders for
the CTY wire format system. Each encoder handles serialization and
deserialization for a specific format like JSON or MessagePack.

The registry follows the same Factory + Strategy pattern as the
main wire format system, ensuring extensibility and runtime format
selection.
"""

from enum import Enum, auto
from typing import ClassVar, Dict, Optional, Type, TypeVar, Any, Final

from pyvider.telemetry import logger
from pyvider.core.conversion.wire_format import WireFormatType

T = TypeVar('T')

# Wire format constants
JSON = WireFormatType.JSON
MSGPACK = WireFormatType.MSGPACK

class FormatEncoder:
    """
    Base class for format-specific encoders.

    Format encoders handle the actual serialization and deserialization
    for specific wire formats like JSON or MessagePack. They convert
    between CTY values and bytes according to format-specific rules.
    """

    @classmethod
    def format_type(cls) -> WireFormatType:
        """
        Get the wire format type this encoder handles.

        Returns:
            WireFormatType: The wire format type
        """
        raise NotImplementedError(f"{cls.__name__}.format_type() must be implemented")

    @classmethod
    def encode(cls, value: Any, **options) -> bytes:
        """
        Encode a value to bytes.

        Args:
            value: The value to encode
            **options: Format-specific options

        Returns:
            The encoded bytes

        Raises:
            EncodingError: If encoding fails
        """
        raise NotImplementedError(f"{cls.__name__}.encode() must be implemented")

    @classmethod
    def decode(cls, data: bytes, **options) -> Any:
        """
        Decode bytes to a value.

        Args:
            data: The bytes to decode
            **options: Format-specific options

        Returns:
            The decoded value

        Raises:
            EncodingError: If decoding fails
        """
        raise NotImplementedError(f"{cls.__name__}.decode() must be implemented")

# Global registry of format encoders
_ENCODERS: Dict[WireFormatType, Type[FormatEncoder]] = {}

def register_formatter(format_type: WireFormatType):
    """
    Decorator to register a format encoder.

    Args:
        format_type: The wire format type to register for

    Returns:
        Decorator function

    Example:
        ```python
        @register_formatter(WireFormatType.JSON)
        class JsonEncoder(FormatEncoder):
            # Implementation...
        ```
    """
    logger.debug(f"🧩🔄🔧 Preparing registration for format encoder: {format_type.name}")

    def decorator(encoder_class: Type[FormatEncoder]):
        """Register a format encoder class."""
        if not issubclass(encoder_class, FormatEncoder):
            error_msg = f"Format encoder {encoder_class.__name__} must extend FormatEncoder"
            logger.error(f"🧩🔄❌ {error_msg}")
            raise TypeError(error_msg)

        # Register the encoder
        _ENCODERS[format_type] = encoder_class
        logger.debug(f"🧩🔄✅ Registered format encoder for {format_type.name}: {encoder_class.__name__}")
        return encoder_class

    return decorator

def get_formatter(format_type: WireFormatType) -> Optional[Type[FormatEncoder]]:
    """
    Get the format encoder for the specified format.

    Args:
        format_type: The wire format type to get encoder for

    Returns:
        The format encoder class, or None if not found
    """
    logger.debug(f"🧩🔄🔍 Getting format encoder for {format_type.name}")

    encoder = _ENCODERS.get(format_type)
    if encoder:
        logger.debug(f"🧩🔄✅ Found encoder: {encoder.__name__}")
    else:
        logger.debug(f"🧩🔄⚠️ No encoder found for {format_type.name}")

    return encoder

def list_formatters() -> Dict[WireFormatType, str]:
    """
    Get a dictionary of all registered format encoders.

    Returns:
        Dictionary mapping format types to encoder class names
    """
    return {fmt: encoder.__name__ for fmt, encoder in _ENCODERS.items()}

# 🐍🏗️🐣
