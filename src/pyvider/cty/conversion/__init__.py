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
    normalize_type_object, # Added normalize_type_object
)

# Re-export type marshaling utilities
from pyvider.cty.conversion.marshal import (
    marshal_type,
    unmarshal_type,
    marshal_json,
    unmarshal_json,
)

# Re-export JSON conversion utilities
# from pyvider.cty.conversion.formats.json import JsonEncoder # Imported below
# from pyvider.cty.conversion.formats.msgpack import MsgPackEncoder # Imported below

# Re-export wire format implementation
from pyvider.cty.conversion.wire import CtyWireFormat # Imports the CTY-specific wire format

# Export format-specific utilities
from pyvider.cty.conversion.formats import (
    FormatEncoder,
    register_formatter,
    get_formatter,
    list_formatters,
    JSON,
    MSGPACK,
)

# --- FIX: Explicitly import implementation modules to trigger registration ---
# This ensures @register_formatter runs for JsonEncoder and MsgPackEncoder
# Also ensures CtyWireFormat registration runs via its module import.
from pyvider.cty.conversion.formats import json as _json_fmt
from pyvider.cty.conversion.formats import msgpack as _msgpack_fmt
from pyvider.cty.conversion import wire as _cty_wire_fmt # Ensure CtyWireFormat registers
# --- END FIX ---

# Re-export format types from core
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
    "normalize_type_object", # Added

    # Type marshaling
    "marshal_type",
    "unmarshal_type",

    "marshal_json",
    "unmarshal_json",

    # Wire format
    "CtyWireFormat", # Export the CTY wire format implementation
    "WireFormatType", # Re-export from core

    # Format-specific utilities
    "FormatEncoder",
    "register_formatter",
    "get_formatter",
    "list_formatters",
    "JSON",
    "MSGPACK",

    # Format implementations (can be accessed via get_formatter)
    # "JsonEncoder",
    # "MsgPackEncoder",
]

# 🐍🏗️🐣
