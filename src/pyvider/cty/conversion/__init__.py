# pyvider-cty/src/pyvider/cty/conversion/__init__.py


from pyvider.telemetry import logger

from pyvider.cty.context import OperationContext, get_current_operation
# Directly import the function from its specific module to avoid ambiguity
from pyvider.cty.context.operation_context import operation_context as operation_context_func
# Make 'operation_context' available for export if it's part of the public API of this module
# and ensure it points to the function.
operation_context = operation_context_func

from pyvider.cty.conversion.wire import WireFormat, WireFormatType, WireFormatRegistry

from pyvider.cty.conversion.schema_type_encoder import encode_type_to_wire # Import the moved function

from pyvider.cty.conversion.format import (
    TypeCategory,
    parse_collection_type,
    classify_type,
    standardize_type_string,
    validate_type_format,
    ensure_quoted_bytes,
)

from pyvider.cty.conversion.formats.base import (
    register_formatter,
)

# Import concrete implementations to register them
import pyvider.cty.conversion.terraform

T = type["T"]

def marshal(value: object, format_kind: WireFormatType, operation: OperationContext | None = None, **options: object) -> bytes:
    op_ctx = operation or get_current_operation()
    formatter = WireFormatRegistry.get_formatter(format_kind)
    with operation_context_func(op_ctx): # Use the directly imported function
        return formatter.marshal(value, operation=op_ctx, **options)

def unmarshal(data: bytes | object, format_kind: WireFormatType, expected_type: T | None = None, operation: OperationContext | None = None, **options: object) -> T:
    op_ctx = operation or get_current_operation()
    formatter = WireFormatRegistry.get_formatter(format_kind)
    with operation_context_func(op_ctx): # Use the directly imported function
        return formatter.unmarshal(data, expected_type=expected_type, operation=op_ctx, **options)

__all__ = [
    "WireFormat", "WireFormatType", "WireFormatRegistry",
    "OperationContext", "get_current_operation", "operation_context", # Exporting the function named 'operation_context'
    "marshal", "unmarshal",
    "encode_type_to_wire",
    "TypeCategory", "parse_collection_type", "classify_type", "standardize_type_string", "register_formatter", "validate_type_format", "ensure_quoted_bytes", "operation_context",
]
logger.debug("🗣️ 🧩🔄🔧 CTY conversion module initialized")
# 🐍🏗️
