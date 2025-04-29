#
# pyvider/cty/conversion/__init__.py
#

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

# Import core wire format system
from pyvider.core.conversion.wire_format import WireFormatType

# --- Ensure implementation modules are imported for registration ---
import pyvider.cty.conversion.formats.json
import pyvider.cty.conversion.formats.msgpack
import pyvider.cty.conversion.wire

# Re-export format-specific utilities
from pyvider.cty.conversion.formats.base import (
    FormatEncoder,
    register_formatter,
    get_formatter,
    list_formatters,
)

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
    "WireFormatType",

    # Format-specific utilities
    "FormatEncoder",
    "register_formatter",
    "get_formatter",
    "list_formatters",
]

logger.debug("🧩🔄🔧 CTY conversion module initialized")

# 🐍🏗️🐣
