# pyvider-cty/src/pyvider/cty/conversion/__init__.py

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
from pyvider.cty.conversion.formats.base import (
    register_formatter,
)
from pyvider.cty.conversion.schema_type_encoder import (
    encode_type_to_wire,  # Import the moved function
)

# Import concrete implementations to register them
import pyvider.cty.conversion.terraform
from pyvider.cty.conversion.wire import WireFormat, WireFormatRegistry, WireFormatType
from pyvider.telemetry import logger

T = type["T"]

def marshal(value: object, format_kind: WireFormatType, operation: OperationContext | None = None, **options: object) -> bytes:
    op_ctx = operation or get_current_operation()
    formatter = WireFormatRegistry.get_formatter(format_kind)
    with operation_context(op_ctx):
        return formatter.marshal(value, operation=op_ctx, **options)

def unmarshal(data: bytes | object, format_kind: WireFormatType, expected_type: T | None = None, operation: OperationContext | None = None, **options: object) -> T:
    op_ctx = operation or get_current_operation()
    formatter = WireFormatRegistry.get_formatter(format_kind)
    with operation_context(op_ctx):
        return formatter.unmarshal(data, expected_type=expected_type, operation=op_ctx, **options)

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
    "register_formatter",
    "standardize_type_string",
    "unmarshal",
    "validate_type_format",
]
logger.debug("🗣️ 🧩🔄🔧 CTY conversion module initialized")

# 🐍🏗️
