# pyvider/cty/__init__.py
"""
Pyvider CTY (Compatible Type System) Package.

This package provides a type system inspired by HashiCorp's CTY, designed for
handling complex data structures with type safety, validation, and conversion
capabilities, particularly for infrastructure-as-code applications.
"""
from pyvider.cty.conversion import (
    TypeCategory,
    classify_type,
    ensure_quoted_bytes,
    parse_collection_type,
    standardize_type_string,
    validate_type_format,
    encode_type_to_wire as marshal_type,
)
from pyvider.cty.codec import cty_value_to_json_string as marshal_json
from pyvider.cty.codec import cty_value_from_json_string as unmarshal_json
from pyvider.cty.codec import parse_type_string_to_ctytype as unmarshal_type
from pyvider.cty.marks import CtyMark
from pyvider.cty.path import CtyPath
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.cty.values import CtyValue

# pyvider.core.conversion.wire_format.WireFormatType is imported in pyvider.cty.conversion
# to avoid direct dependency from cty.__init__ to core.

__all__ = [
    "CtyBool",
    "CtyDynamic",
    "CtyList",
    "CtyMap",
    "CtyMark",
    "CtyNumber",
    "CtyObject",
    "CtyPath",
    "CtySet",
    "CtyString",
    "CtyTuple",
    "CtyType",
    "CtyValue",
    "TypeCategory",
    "classify_type",
    "ensure_quoted_bytes",
    "marshal_json",
    "marshal_type",
    "parse_collection_type",
    "standardize_type_string",
    "unmarshal_json",
    "unmarshal_type",
    "validate_type_format",
]
