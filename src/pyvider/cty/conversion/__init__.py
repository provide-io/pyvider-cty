# pyvider/cty/conversion/__init__.py

from pyvider.telemetry import logger
from pyvider.cty.conversion.format import (
    TypeCategory, parse_collection_type, classify_type,
    validate_type_format, standardize_type_string, ensure_quoted_bytes,
)
from pyvider.cty.conversion.marshal import (
    marshal_type, unmarshal_type, marshal_json, unmarshal_json,
)
# Import WireFormatType from core, as cty.conversion needs to know about it for formatters
from pyvider.core.conversion.wire_format import WireFormatType

import pyvider.cty.conversion.formats.json
import pyvider.cty.conversion.formats.msgpack
# pyvider.cty.conversion.wire is where CtyWireFormat is defined, which depends on core.
# This import is fine as it's within the cty package structure.
import pyvider.cty.conversion.wire

from pyvider.cty.conversion.formats.base import (
    FormatEncoder, register_formatter, get_formatter, list_formatters,
)

__all__ = [
    "TypeCategory", "parse_collection_type", "classify_type",
    "validate_type_format", "standardize_type_string", "ensure_quoted_bytes",
    "marshal_type", "unmarshal_type", "marshal_json", "unmarshal_json",
    "WireFormatType", # Re-export for convenience if needed by cty users
    "FormatEncoder", "register_formatter", "get_formatter", "list_formatters",
]
logger.debug("🗣️ 🧩🔄🔧 CTY conversion module initialized")
