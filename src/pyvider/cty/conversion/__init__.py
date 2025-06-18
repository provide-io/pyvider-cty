# pyvider-cty/src/pyvider/cty/conversion/__init__.py
"""
Core CTY conversion functionalities.

This package provides the main entry points for marshalling and unmarshalling
CTY values to/from various wire formats (like JSON, MessagePack), and includes
utilities for type classification, standardization, and validation.
"""
# Ensure WireFormatRegistry is defined before formatters try to register.
from pyvider.cty.conversion.wire import WireFormat, WireFormatRegistry, WireFormatType

# Import concrete formatter modules to ensure their @register_formatter decorators run.
# These imports are primarily for their side effects (registration).
import pyvider.cty.conversion.formats.json
import pyvider.cty.conversion.formats.msgpack
import pyvider.cty.conversion.terraform  # F401 in original, but import for registration side-effect

from pyvider.cty.context import (
    OperationContext,
    get_current_operation,
    operation_context,
)
from pyvider.cty.conversion.format import (
    TypeCategory,
    classify_type,
    ensure_quoted_bytes,
    parse_collection_type,
    standardize_type_string,
    validate_type_format,
)
from pyvider.cty.conversion.schema_type_encoder import (
    encode_type_to_wire,  # Import the moved function
)
from pyvider.telemetry import logger
from typing import TypeVar

T = TypeVar("T")


def marshal(
    value: object,
    format_kind: WireFormatType,
    operation: OperationContext | None = None,
    **options: object,
) -> bytes:
    """
    Marshals a given value into bytes using the specified wire format.

    Args:
        value: The value to marshal.
        format_kind: The target wire format (e.g., JSON, MSGPACK).
        operation: The operational context, influencing serialization.
        **options: Additional options specific to the chosen formatter.

    Returns:
        The marshalled value as bytes.

    Raises:
        WireFormatError: If no formatter is registered for the format_kind
                         or if marshalling fails.
    """
    op_ctx = operation or get_current_operation()
    formatter = WireFormatRegistry.get_formatter(format_kind)
    with operation_context(op_ctx):
        return formatter.marshal(value, operation=op_ctx, **options)


def unmarshal(
    data: bytes | object,
    format_kind: WireFormatType,
    expected_type: T | None = None,
    operation: OperationContext | None = None,
    **options: object,
) -> T:
    """
    Unmarshals data from bytes into a Python object, potentially a CtyValue,
    using the specified wire format and expected type.

    Args:
        data: The bytes or pre-parsed object to unmarshal.
        format_kind: The wire format of the data (e.g., JSON, MSGPACK).
        expected_type: The expected Python type or CtyType of the result.
        operation: The operational context, influencing deserialization.
        **options: Additional options specific to the chosen formatter.

    Returns:
        The unmarshalled Python object, cast to type T if expected_type is provided.

    Raises:
        WireFormatError: If no formatter is registered for the format_kind
                         or if unmarshalling fails.
    """
    op_ctx = operation or get_current_operation()
    formatter = WireFormatRegistry.get_formatter(format_kind)
    with operation_context(op_ctx):
        return formatter.unmarshal(
            data, expected_type=expected_type, operation=op_ctx, **options
        )


__all__ = [
    "OperationContext",
    "TypeCategory",
    "WireFormat",
    "WireFormatRegistry",
    "WireFormatType",
    "classify_type",
    "encode_type_to_wire",
    "ensure_quoted_bytes",
    "get_current_operation",
    "marshal",
    "operation_context",
    "parse_collection_type",
    "standardize_type_string",
    "unmarshal",
    "validate_type_format",
]
# logger.debug("🗣️ 🧩🔄🔧 CTY conversion module initialized") # Removed by AI Agent

# 🐍🏗️
