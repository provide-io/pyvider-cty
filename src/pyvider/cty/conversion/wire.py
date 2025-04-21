#
# pyvider/cty/conversion/wire.py
#

"""
Wire format implementation for CTY values.

This module provides a comprehensive implementation of the WireFormat interface
for CTY values, enabling serialization and deserialization between CTY values
and wire format representations. It supports standard serialization formats
including JSON and MessagePack, with rigorous validation and error handling.

The implementation follows the Factory + Strategy pattern defined in the
core conversion system, ensuring extensibility and format selection at runtime.
"""

from typing import Any, ClassVar, Dict, Optional, Type, TypeVar, cast, final

from attrs import define, field

from pyvider.telemetry import logger
from pyvider.core.conversion.wire_format import (
    WireFormat,
    WireFormatType,
    WireFormatRegistry,
    WireFormatError
)

from pyvider.cty.exceptions import EncodingError
from pyvider.cty.types import CtyType
from pyvider.cty.values import CtyValue

T = TypeVar('T')

@WireFormatRegistry.register(WireFormatType.STANDARD)
class CtyWireFormat(WireFormat):
    """
    Pyvider's standard wire format implementation for CTY values.

    This class implements the WireFormat protocol for serializing and
    deserializing CTY values using a standardized, self-describing format.
    The format preserves type information, state (known/unknown/null),
    and other metadata associated with CTY values.

    The implementation supports delegation to format-specific encoders
    like JSON and MessagePack based on configuration options.
    """

    DEFAULT_FORMAT: ClassVar[WireFormatType] = WireFormatType.JSON

    @classmethod
    def marshal(
        cls,
        value: Any,
        *,
        operation: Optional[str] = None,
        **options
    ) -> bytes:
        """
        Marshal a CTY value to wire format bytes.

        This method converts a CTY value (or raw Python value that can be
        converted to a CTY value) into bytes using the specified or default
        format. It preserves type information, state, and marks.

        Args:
            value: The value to marshal (CtyValue or compatible Python value)
            operation: Optional operation context (default: None)
            **options: Format-specific options including:
                - format_type: The specific format to use (JSON, MSGPACK)
                - preserve_type: Whether to include type information (default: True)
                - include_marks: Whether to include marks (default: True)

        Returns:
            Marshaled value as bytes

        Raises:
            WireFormatError: If marshaling fails
            TypeError: If the value cannot be converted to a CtyValue
        """
        logger.debug(f"🧩🔄📤 Marshaling value to CTY wire format: {type(value).__name__}")

        # Determine format type to use
        format_type = options.get('format_type', cls.DEFAULT_FORMAT)
        logger.debug(f"🧩🔄📤 Using format: {format_type.name}")

        try:
            # Ensure we have a CtyValue
            cty_value = cls._ensure_cty_value(value)

            # Get the appropriate format encoder
            from pyvider.cty.conversion.formats import get_formatter
            formatter = get_formatter(format_type)
            if formatter is None:
                error_msg = f"No formatter available for format: {format_type.name}"
                logger.error(f"🧩🔄❌ {error_msg}")
                raise WireFormatError(error_msg, format_type=format_type)

            # Convert to wire format
            result = formatter.encode(cty_value, **options)
            logger.debug(f"🧩🔄✅ Successfully marshaled to {len(result)} bytes")
            return result

        except Exception as e:
            if isinstance(e, WireFormatError):
                raise

            error_msg = f"Failed to marshal to CTY wire format: {e}"
            logger.error(f"🧩🔄❌ {error_msg}", exc_info=True)
            raise WireFormatError(
                error_msg,
                format_type=WireFormatType.STANDARD,
                operation="marshal",
                source_value=value
            ) from e

    @classmethod
    def unmarshal(
        cls,
        data: bytes,
        expected_type: Optional[Type[T]] = None,
        *,
        operation: Optional[str] = None,
        **options
    ) -> Any:
        """
        Unmarshal wire format bytes to a CTY value.

        Converts bytes in the CTY wire format back into a CTY value,
        with optional validation against an expected type.

        Args:
            data: The bytes to unmarshal
            expected_type: Optional type to validate against
            operation: Optional operation context (default: None)
            **options: Format-specific options including:
                - format_type: The specific format to use (auto-detected if not specified)
                - validate: Whether to validate against expected_type (default: True)

        Returns:
            The unmarshaled CTY value

        Raises:
            WireFormatError: If unmarshaling fails
            ValidationError: If validation against expected_type fails
        """
        logger.debug(f"🧩🔍📥 Unmarshaling from CTY wire format: {len(data)} bytes")

        try:
            # Auto-detect format if not specified
            format_type = options.get('format_type')
            if format_type is None:
                format_type = cls._detect_format(data)
                logger.debug(f"🧩🔍📥 Auto-detected format: {format_type.name}")

            # Get the appropriate format decoder
            from pyvider.cty.conversion.formats import get_formatter
            formatter = get_formatter(format_type)
            if formatter is None:
                error_msg = f"No formatter available for format: {format_type.name}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise WireFormatError(error_msg, format_type=format_type)

            # Decode from wire format
            result = formatter.decode(data, **options)

            # Validate against expected type if provided
            if expected_type is not None and options.get('validate', True):
                result = cls._validate_result(result, expected_type)

            logger.debug(f"🧩🔍✅ Successfully unmarshaled to {type(result).__name__}")
            return result

        except Exception as e:
            if isinstance(e, WireFormatError):
                raise

            error_msg = f"Failed to unmarshal from CTY wire format: {e}"
            logger.error(f"🧩🔍❌ {error_msg}", exc_info=True)
            raise WireFormatError(
                error_msg,
                format_type=WireFormatType.STANDARD,
                operation="unmarshal",
                target_type=expected_type
            ) from e

    @classmethod
    def _ensure_cty_value(cls, value: Any) -> CtyValue:
        """
        Ensure that a value is a CtyValue.

        If the value is already a CtyValue, return it directly.
        Otherwise, attempt to convert it to a CtyValue using appropriate type inference.

        Args:
            value: The value to ensure is a CtyValue

        Returns:
            The value as a CtyValue

        Raises:
            TypeError: If the value cannot be converted to a CtyValue
        """
        logger.debug(f"🧩🔄🔍 Ensuring value is CtyValue: {type(value).__name__}")

        # Already a CtyValue
        if isinstance(value, CtyValue):
            return value

        # Handle None
        if value is None:
            logger.debug("🧩🔄🔍 Converting None to null CtyValue")
            from pyvider.cty.types import CtyDynamic
            return CtyValue.null(CtyDynamic())

        # Convert based on type using match/case
        match value:
            case bool():
                logger.debug("🧩🔄🔍 Converting bool to CtyValue")
                return CtyValue.bool(value)
            case int() | float():
                logger.debug("🧩🔄🔍 Converting number to CtyValue")
                return CtyValue.number(value)
            case str():
                logger.debug("🧩🔄🔍 Converting string to CtyValue")
                return CtyValue.string(value)
            case list():
                logger.debug("🧩🔄🔍 Converting list to CtyValue")
                # Use dynamic for element type inference
                from pyvider.cty.types import CtyDynamic
                return CtyValue.list(CtyDynamic(), value)
            case dict():
                logger.debug("🧩🔄🔍 Converting dict to CtyValue")
                # Use dynamic for key/value type inference
                from pyvider.cty.types import CtyDynamic, CtyString
                return CtyValue.map(CtyString(), CtyDynamic(), value)
            case _:
                error_msg = f"Cannot convert {type(value).__name__} to CtyValue"
                logger.error(f"🧩🔄❌ {error_msg}")
                raise TypeError(error_msg)

    @classmethod
    def _validate_result(cls, result: Any, expected_type: Type[T]) -> T:
        """
        Validate a result against an expected type.

        Args:
            result: The result to validate
            expected_type: The expected type

        Returns:
            The validated result

        Raises:
            ValidationError: If validation fails
        """
        logger.debug(f"🧩🔍🔄 Validating result against {expected_type.__name__}")

        # Check if already valid
        if isinstance(result, expected_type):
            return cast(T, result)

        # Handle CtyValue with expected CtyType
        if isinstance(result, CtyValue) and issubclass(expected_type, CtyType):
            if isinstance(result.type, expected_type):
                return cast(T, result.type)
            else:
                error_msg = f"Expected CtyType {expected_type.__name__}, got {result.type.__class__.__name__}"
                logger.error(f"🧩🔍❌ {error_msg}")
                raise EncodingError(error_msg)

        # Attempt conversion
        try:
            converted = expected_type(result)
            logger.debug(f"🧩🔍✅ Successfully converted to {expected_type.__name__}")
            return converted
        except Exception as e:
            error_msg = f"Failed to convert {type(result).__name__} to {expected_type.__name__}: {e}"
            logger.error(f"🧩🔍❌ {error_msg}")
            raise EncodingError(error_msg) from e

    @classmethod
    def _detect_format(cls, data: bytes) -> WireFormatType:
        """
        Detect the format of the given bytes.

        This method attempts to determine the wire format by examining the
        content of the bytes. It looks for format-specific markers.

        Args:
            data: The bytes to detect format for

        Returns:
            The detected WireFormatType

        Raises:
            WireFormatError: If format cannot be reliably detected
        """
        logger.debug(f"🧩🔍🔄 Detecting format for {len(data)} bytes")

        # Check if it looks like JSON (starts with { or [)
        if data and data[0] in (b'{'[0], b'['[0]):
            logger.debug("🧩🔍✅ Detected JSON format")
            return WireFormatType.JSON

        # Check if it looks like MsgPack (various markers)
        if data and data[0] in (0x80, 0x81, 0x82, 0x90, 0x91, 0x92):
            logger.debug("🧩🔍✅ Detected MsgPack format")
            return WireFormatType.MSGPACK

        # Default to JSON as fallback
        logger.warning("🧩🔍⚠️ Could not reliably detect format, defaulting to JSON")
        return WireFormatType.JSON

# 🐍🏗️🐣
