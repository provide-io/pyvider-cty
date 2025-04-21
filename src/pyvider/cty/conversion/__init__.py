#!/usr/bin/env python3
# pyvider/cty/conversion/__init__.py

"""
Conversion package for Pyvider CTY.

This package provides comprehensive utilities for converting between CTY types/values
and various serialization formats. It includes format standardization, type marshaling,
value serialization, and specialized encoders for different wire formats.

The conversion system follows a layered approach:
1. Format standardization (type strings, collection types)
2. Type marshaling (CTY types <-> wire formats)
3. Value serialization (CTY values <-> wire formats)
4. Format-specific encoding (JSON, MessagePack)

All conversion operations maintain type safety, provide comprehensive error handling,
and support various serialization options.
"""

from pyvider.telemetry import logger

# Re-export format standardization utilities
from pyvider.cty.conversion.format import (
    TypeCategory,
    parse_collection_type,
    classify_type,
    validate_type_format,
    standardize_type_string,
    ensure_quoted_bytes,
)

# Re-export type marshaling utilities
from pyvider.cty.conversion.marshal import (
    marshal_type,
    unmarshal_type,
    marshal_json,
    unmarshal_json,
)

# Re-export JSON conversion utilities
from pyvider.cty.conversion.formats.json import JsonEncoder
from pyvider.cty.conversion.formats.msgpack import MsgPackEncoder

# Re-export wire format implementation
from pyvider.cty.conversion.wire import CtyWireFormat

# Export format-specific utilities
from pyvider.cty.conversion.formats import (
    FormatEncoder,
    register_formatter,
    get_formatter,
    list_formatters,
    JSON,
    MSGPACK,
)

# Re-export format types
from pyvider.core.conversion.wire_format import WireFormatType

# Register wire format (ensures CtyWireFormat registration happens)
logger.debug("🧩🔄🔧 Initializing CTY conversion module")

__all__ = [
    # Format standardization
    "TypeCategory",
    "parse_collection_type",
    "classify_type",
    "validate_type_format",
    "standardize_type_string",
    "ensure_quoted_bytes",

    # Type marshaling
    "marshal_type",
    "unmarshal_type",

    "marshal_json",
    "unmarshal_json",

    # Wire format
    "CtyWireFormat",
    "WireFormatType",
    
    # Format-specific utilities
    "FormatEncoder",
    "register_formatter",
    "get_formatter",
    "list_formatters",
    "JSON",
    "MSGPACK",

    # Format implementations
    "JsonEncoder",
    "MsgPackEncoder",
]

# 🐍🏗️🐣
