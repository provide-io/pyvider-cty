# pyvider/cty/__init__.py

"""
Pyvider CTY Type System

A Python implementation of the go-cty type system providing strongly-typed
value representations with validation, serialization, and path-based access.
This package enables precise data modeling with comprehensive type safety
for infrastructure-as-code and configuration applications.

Key concepts:

Types - Represent data formats and constraints:
  - Primitive types: String, Number, Bool
  - Collection types: List, Map, Set
  - Structural types: Object, Tuple, Dynamic

Values - Combine data with type information:
  - Known values: Regular values with their associated type
  - Unknown values: Values with a known type but unknown content
  - Null values: Type-aware representation of absent values
  - Marked values: Values with metadata annotations

Usage:
    from pyvider.cty import CtyString, CtyValue

    # Create a type
    string_type = CtyString()

    # Validate and create a value
    string_value = string_type.validate("hello")

    # Use factory methods
    number_value = CtyValue.number(42)

The type system provides consistent behavior with immutable values,
comprehensive validation, and path-based traversal capabilities.
"""

# Import primitive types
from pyvider.cty.types import (
    CtyType,  # Base type class

    # Primitive types
    CtyBool,
    CtyNumber,
    CtyString,

    # Collection types
    CtyList,
    CtyMap,
    CtySet,

    # Structural types
    CtyDynamic,
    CtyObject,
    CtyTuple,
)

from pyvider.cty.conversion import (
    TypeCategory,
    classify_type,
    validate_type_format,
    ensure_quoted_bytes,
    marshal_type,
    unmarshal_type,
    marshal_json,
    unmarshal_json,
)

# Import value and path classes
from pyvider.cty.values import CtyValue
from pyvider.cty.path import CtyPath

# Define public API
__all__ = [
    # Core concepts
    "CtyType",   # Base type class for all type implementations
    "CtyValue",  # Value representation with type information
    "CtyPath",   # Path-based access to structured values

    # Primitive types
    "CtyBool",   # Boolean true/false values
    "CtyNumber", # Numeric values (int, float, decimal)
    "CtyString", # Text string values

    # Collection types (homogeneous element types)
    "CtyList",   # Ordered sequences with numeric indices
    "CtyMap",    # Key-value collections with string keys
    "CtySet",    # Unordered collections of unique values

    # Structural types
    "CtyObject", # Named attributes with potentially different types
    "CtyTuple",  # Fixed-length sequences with position-specific types
    "CtyDynamic", # Type-unknown placeholder for dynamic values

    "TypeCategory",
    "classify_type",
    "validate_type_format",
    "ensure_quoted_bytes",

    "marshal_type",
    "unmarshal_type",

    "marshal_json",
    "unmarshal_json",

]

# 🐍🏗️🐣
