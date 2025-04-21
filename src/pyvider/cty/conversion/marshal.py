#
# pyvider/cty/conversion/marshal.py
#

"""
Type conversion utilities for Pyvider.

This module provides comprehensive utilities for handling type conversion
between various representations used in Terraform provider development.
It supports validation, extraction, categorization, and manipulation of
type definitions with full support for nested and collection types.
"""

import re
from typing import Any, Optional, Type, TypeVar, Union, cast, Literal, TypeGuard

from pyvider.telemetry import logger

from pyvider.core.exceptions import ConversionError, TypeConversionError
from pyvider.cty import (
    CtyType, CtyString, CtyNumber, CtyBool,
    CtyList, CtyMap, CtySet, CtyTuple, CtyObject, CtyDynamic,
)
from pyvider.cty.conversion.format import (
    TypeCategory,
    standardize_type_string,
    ensure_quoted_bytes,
    parse_collection_type,
    classify_type,
    normalize_type_object,
)

# Type variables for generic conversions
T = TypeVar('T')
TypeString = str
TypeBytes = bytes

def marshal_type(type_obj: Any) -> bytes:
    """
    Convert a type object to standard bytes representation.

    Args:
        type_obj: The type object to convert (CtyType, PvsAttributeType, etc.)

    Returns:
        bytes: The type as properly formatted bytes for Terraform protocol

    Raises:
        ConversionError: If encoding fails
    """
    logger.debug(f"🧰🔄📊 Converting {type(type_obj).__name__} to type bytes")

    try:
        # Use centralized type normalization from format module
        type_str = normalize_type_object(type_obj)

        # Convert to standardized bytes format
        return ensure_quoted_bytes(type_str)
    except Exception as e:
        error_msg = f"Failed to encode type {type_obj!r}: {e}"
        logger.error(f"🧰🔄❌ {error_msg}", exc_info=True)
        raise ConversionError(error_msg) from e

def unmarshal_type(type_bytes: bytes, options: Optional[dict[str, Any]] = None) -> CtyType:
    """
    Convert Terraform protocol type bytes to a CTY type.

    Args:
        type_bytes: The type bytes to convert
        options: Optional conversion options

    Returns:
        CtyType: The corresponding CTY type

    Raises:
        ConversionError: If conversion fails
    """
    logger.debug(f"🧰🔍📊 Converting type bytes to CTY type: {type_bytes!r}")

    options = options or {}

    try:
        # Handle None case
        if not type_bytes:
            return CtyDynamic()

        # Parse type string using format module
        try:
            decoded_str = type_bytes.decode("utf-8")
            # Remove quotes if present
            if decoded_str.startswith('"') and decoded_str.endswith('"'):
                decoded_str = decoded_str[1:-1]
            type_str = standardize_type_string(decoded_str)
            logger.debug(f"🧰🔍📊 Standardized type string: {type_str!r}")
        except UnicodeDecodeError:
            raise ConversionError(f"Invalid type bytes: {type_bytes}")

        # Use match/case for type categorization
        match classify_type(type_str):
            case TypeCategory.PRIMITIVE:
                # Handle primitive types with match/case
                match type_str:
                    case "string":
                        return CtyString()
                    case "number":
                        return CtyNumber()
                    case "bool":
                        return CtyBool()
                    case "dynamic" | "null":
                        return CtyDynamic()
                    case _:
                        logger.warning(f"🧰🔍⚠️ Unknown primitive type: {type_str}")
                        return CtyDynamic()

            case TypeCategory.COLLECTION:
                # Handle collection types properly
                try:
                    collection_type, element_type_str = parse_collection_type(type_str)

                    # Recursively convert element type
                    element_type_bytes = ensure_quoted_bytes(element_type_str)
                    logger.debug(f"🧰🔍📊 Recursively unmarshaling element type: {element_type_bytes!r}")
                    element_type = unmarshal_type(element_type_bytes, options)

                    # Create the appropriate collection type
                    match collection_type:
                        case "list":
                            return CtyList(element_type=element_type)
                        case "map":
                            return CtyMap(key_type=CtyString(), value_type=element_type)
                        case "set":
                            return CtySet(element_type=element_type)
                        case _:
                            logger.warning(f"🧰🔍⚠️ Unsupported collection type: {collection_type}")
                            return CtyDynamic()
                except ValueError as e:
                    logger.error(f"🧰🔍❌ Failed to parse collection type: {e}")
                    raise ConversionError(f"Invalid collection type format: {type_str}") from e

            case _:
                # Handle unknown or structured types
                logger.warning(f"🧰🔍⚠️ Unknown type format: {type_str}, defaulting to dynamic")
                return CtyDynamic()

    except Exception as e:
        if isinstance(e, ConversionError):
            raise
        error_msg = f"Failed to decode type: {e}"
        logger.error(f"🧰🔍❌ {error_msg}", exc_info=True)
        raise ConversionError(error_msg) from e

def validate_collection_type(type_str: str) -> bool:
    """
    Validate that a collection type string has proper format.

    This function checks if a type string is a valid collection type format,
    ensuring it has the correct syntax: collection_type(element_type).

    Args:
        type_str: The type string to validate

    Returns:
        bool: True if the type string is a valid collection type format
    """
    logger.debug(f"🧰🔄🔍 Validating collection type format: {type_str!r}")

    try:
        # Normalize the type string first
        normalized = standardize_type_string(type_str)

        # Check if it matches collection pattern
        category = classify_type(normalized)
        if category != TypeCategory.COLLECTION:
            logger.debug(f"🧰🔄⚠️ Not a collection type: {normalized} (category: {category.name})")
            return False

        # Parse to ensure element type is valid
        collection_type, element_type = parse_collection_type(normalized)

        # Check if collection type is supported
        if collection_type not in ("list", "map", "set"):
            logger.debug(f"🧰🔄⚠️ Unsupported collection type: {collection_type}")
            return False

        logger.debug(f"🧰🔄✅ Valid collection type: {normalized}")
        return True

    except Exception as e:
        logger.debug(f"🧰🔄❌ Invalid collection type format: {e}")
        return False

def extract_element_type(type_str: str) -> str:
    """
    Extract element type from a collection type string.

    This function parses a collection type string and returns only the
    element type portion, handling nested collections recursively.

    Args:
        type_str: The collection type string to extract from

    Returns:
        str: The extracted element type string

    Raises:
        TypeConversionError: If the input is not a valid collection type
    """
    logger.debug(f"🧰🔄🔍 Extracting element type from: {type_str!r}")

    try:
        # Normalize the type string first
        normalized = standardize_type_string(type_str)

        # Check if it's a collection type
        if not validate_collection_type(normalized):
            raise TypeConversionError(f"Not a valid collection type: {normalized}")

        # Parse the collection type
        _, element_type = parse_collection_type(normalized)

        logger.debug(f"🧰🔄✅ Extracted element type: {element_type}")
        return element_type

    except Exception as e:
        if isinstance(e, TypeConversionError):
            raise
        error_msg = f"Failed to extract element type: {e}"
        logger.error(f"🧰🔄❌ {error_msg}", exc_info=True)
        raise TypeConversionError(error_msg) from e

def get_type_category(type_obj: Any) -> TypeCategory:
    """
    Get the category of a type object.

    This function determines the category of a type object, classifying it
    as primitive, collection, or structured type.

    Args:
        type_obj: The type object to categorize (string, CtyType, etc.)

    Returns:
        TypeCategory: The category of the type
    """
    logger.debug(f"🧰🔄🔍 Getting type category for: {type_obj!r}")

    try:
        # Normalize to type string first
        type_str = normalize_type_object(type_obj)

        # Classify the normalized type string
        category = classify_type(type_str)

        logger.debug(f"🧰🔄✅ Type category for {type_str}: {category.name}")
        return category

    except Exception as e:
        logger.error(f"🧰🔄❌ Failed to determine type category: {e}", exc_info=True)
        return TypeCategory.UNKNOWN

def is_primitive_type(type_obj: Any) -> bool:
    """
    Check if a type object represents a primitive type.

    Primitive types include: string, number, bool, and dynamic.

    Args:
        type_obj: The type object to check

    Returns:
        bool: True if the type is a primitive type
    """
    logger.debug(f"🧰🔄🔍 Checking if {type_obj!r} is a primitive type")

    try:
        return get_type_category(type_obj) == TypeCategory.PRIMITIVE
    except Exception:
        return False

def is_collection_type(type_obj: Any) -> bool:
    """
    Check if a type object represents a collection type.

    Collection types include: list, map, and set.

    Args:
        type_obj: The type object to check

    Returns:
        bool: True if the type is a collection type
    """
    logger.debug(f"🧰🔄🔍 Checking if {type_obj!r} is a collection type")

    try:
        return get_type_category(type_obj) == TypeCategory.COLLECTION
    except Exception:
        return False

def is_structured_type(type_obj: Any) -> bool:
    """
    Check if a type object represents a structured type.

    Structured types include: object and tuple.

    Args:
        type_obj: The type object to check

    Returns:
        bool: True if the type is a structured type
    """
    logger.debug(f"🧰🔄🔍 Checking if {type_obj!r} is a structured type")

    try:
        return get_type_category(type_obj) == TypeCategory.STRUCTURED
    except Exception:
        return False

def sanitize_type_representation(type_obj: Any) -> str:
    """
    Create a clean, standardized string representation of a type.

    This function normalizes type objects into a consistent string format,
    useful for display, logging, and serialization.

    Args:
        type_obj: The type object to sanitize

    Returns:
        str: A sanitized string representation of the type
    """
    logger.debug(f"🧰🔄🔧 Sanitizing type representation: {type_obj!r}")

    try:
        # Normalize to type string
        type_str = normalize_type_object(type_obj)

        # Ensure standard format
        sanitized = standardize_type_string(type_str)

        logger.debug(f"🧰🔄✅ Sanitized type: {sanitized}")
        return sanitized

    except Exception as e:
        # For display purposes, fallback gracefully on error
        logger.warning(f"🧰🔄⚠️ Failed to sanitize type: {e}")
        return str(type_obj)

def marshal_json(value: Any, options: Optional[dict[str, Any]] = None) -> bytes:
    """
    Marshal a value to JSON format bytes.

    This high-level function converts any value to JSON-encoded bytes,
    maintaining type information and metadata.

    Args:
        value: The value to marshal (typically a CtyValue)
        options: Optional JSON-specific encoding options

    Returns:
        JSON-encoded bytes

    Raises:
        EncodingError: If JSON encoding fails
    """
    logger.debug(f"🧩📝🔄 Marshaling value to JSON: {type(value).__name__}")
    from pyvider.cty.conversion.formats.json import JsonEncoder
    return JsonEncoder.encode(value, **(options or {}))

def unmarshal_json(marshaled: Union[bytes, str],
                  expected_type: Optional[CtyType] = None,
                  options: Optional[dict[str, Any]] = None) -> Any:
    """
    Unmarshal JSON bytes to a value.

    This high-level function converts JSON-encoded bytes back into a value,
    restoring type information and metadata.

    Args:
        marshaled: The JSON bytes or string to unmarshal
        expected_type: Optional type to validate against
        options: Optional JSON-specific decoding options

    Returns:
        The unmarshaled value (typically a CtyValue)

    Raises:
        EncodingError: If JSON decoding fails
    """
    logger.debug(f"🧩🔍🔄 Unmarshaling from JSON")

    # Convert string to bytes if needed
    if isinstance(marshaled, str):
        marshaled = marshaled.encode('utf-8')

    from pyvider.cty.conversion.formats.json import JsonEncoder
    return JsonEncoder.decode(marshaled, **(options or {}))

# 🐍🏗️🐣
