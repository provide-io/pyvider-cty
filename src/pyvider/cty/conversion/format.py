#
# pyvider/cty/conversion/format.py
#

"""
Type format standardization for Pyvider conversion system.

This module provides a comprehensive set of utilities for standardizing
type string formats across the Pyvider codebase. It serves as the single
source of truth for how type strings should be formatted, ensuring consistency
when encoding types for Terraform protocol communication.

Features:
    - Type string normalization
    - Quote handling
    - Collection type formatting
    - Recursive type handling
    - Format validation

Usage:
    from pyvider.cty.conversion.format import standardize_type_string, ensure_quoted_bytes

    # Normalize a type string
    normalized = standardize_type_string("list(string)")

    # Convert to properly quoted bytes
    type_bytes = ensure_quoted_bytes(normalized)
"""

import re
from enum import StrEnum, auto
from typing import Any, Optional, TypeAlias, Union, Pattern, Literal
from functools import cache

from pyvider.telemetry import logger

# Type aliases for clarity
TypeString: TypeAlias = str
TypeBytes: TypeAlias = bytes

class TypeCategory(StrEnum):
    """Enumeration of type categories for classification."""
    PRIMITIVE = auto()
    COLLECTION = auto()
    STRUCTURED = auto()
    UNKNOWN = auto()

# Define constants for primitive types
PRIMITIVE_TYPES = frozenset(["string", "number", "bool", "dynamic", "null"])
COLLECTION_TYPES = frozenset(["list", "map", "set"])

@cache
def _get_collection_pattern() -> Pattern[str]:
    """
    Get cached regex pattern for matching collection types.
    
    Returns:
        Compiled regex pattern for collection types
    """
    # Matches patterns like: list(string), map(number), set(bool)
    return re.compile(r'^([a-z]+)\(([^()]*(?:\([^()]*\)[^()]*)*)\)$')

def classify_type(type_str: TypeString) -> TypeCategory:
    """
    Classify a type string into its category.
    
    Args:
        type_str: The type string to classify
        
    Returns:
        TypeCategory enum indicating the category
    """
    logger.debug(f"🧰🔄📊 Classifying type: {type_str!r}")
    
    # Check for primitive types
    if type_str in PRIMITIVE_TYPES:
        return TypeCategory.PRIMITIVE
        
    # Check for collection types
    match = _get_collection_pattern().match(type_str)
    if match and match.group(1) in COLLECTION_TYPES:
        return TypeCategory.COLLECTION
        
    # For now, anything else is unknown
    # Could add STRUCTURED for object types later
    return TypeCategory.UNKNOWN

def standardize_type_string(type_str: Optional[TypeString]) -> TypeString:
    """
    Standardize type string format by removing outer quotes and normalizing inner types.

    Args:
        type_str: The type string to standardize

    Returns:
        Normalized type string
    """
    logger.debug(f"🧰🔄📊 Standardizing type string: {type_str!r}")

    if not type_str:
        logger.debug("🧰🔄📊 Empty type string, defaulting to 'dynamic'")
        return "dynamic"

    # Remove outer quotes
    normalized = type_str.strip('"')

    # Handle collection types using match/case
    match = _get_collection_pattern().match(normalized)
    if match:
        collection_type, element_type = match.groups()
        if collection_type in COLLECTION_TYPES:
            # Recursively normalize element type
            normalized_element = standardize_type_string(element_type)
            result = f"{collection_type}({normalized_element})"
            logger.debug(f"🧰🔄📊 Normalized collection type to: {result!r}")
            return result

    logger.debug(f"🧰🔄📊 Normalized type string: {normalized!r}")
    return normalized

def ensure_quoted_bytes(type_str: Optional[TypeString]) -> TypeBytes:
    """
    Convert a type string to properly quoted bytes format for Terraform protocol.

    Args:
        type_str: The type string to convert

    Returns:
        Type string as properly quoted bytes
    """
    if not type_str:
        logger.debug("🧰🔄📊 Empty type string, defaulting to b'\"dynamic\"'")
        return b'"dynamic"'  # Default for None/empty

    # Standardize then quote
    normalized = standardize_type_string(type_str)
    result = f'"{normalized}"'.encode('utf-8')
    logger.debug(f"🧰🔄📊 Converted to quoted bytes: {result!r}")
    return result

# Improved implementation with nested support
def Xparse_collection_type(type_str: str) -> tuple[str, str]:
    logger.debug("!!!! PARSING COLLECTION.")
    """Parse collection type with support for nested types."""
    if not type_str or '(' not in type_str or not type_str.endswith(')'):
        raise ValueError(f"Invalid collection type format: {type_str}")
        
    # Extract base type and potentially nested content
    base_type, rest = type_str.split('(', 1)
    content = rest[:-1]  # Remove trailing ')'
    
    # Validate balanced parentheses for nested types
    if content.count('(') != content.count(')'):
        raise ValueError(f"Unbalanced parentheses in type: {type_str}")
        
    return base_type.strip(), content.strip()

def parse_collection_type(type_str: TypeString) -> tuple[str, str]:
    """
    Parse a collection type string into collection type and element type.

    Args:
        type_str: The collection type string (e.g., "list(string)")

    Returns:
        Tuple of (collection_type, element_type)

    Raises:
        ValueError: If the input is not a valid collection type
    """
    logger.debug(f"🧰🔄📊 Parsing collection type: {type_str!r}")

    match = _get_collection_pattern().match(type_str)
    if not match or match.group(1) not in COLLECTION_TYPES:
        error_msg = f"Invalid collection type format: {type_str!r}"
        logger.error(f"🧰🔄❌ {error_msg}")
        raise ValueError(error_msg)

    collection_type, element_type = match.groups()
    logger.debug(f"🧰🔄📊 Parsed collection: {collection_type}({element_type})")
    return collection_type, element_type

def validate_type_format(type_value: Union[TypeString, TypeBytes]) -> list[str]:
    """
    Validate a type string or bytes has proper format and return any errors.

    Args:
        type_value: Type string or bytes to validate

    Returns:
        List of error messages (empty if valid)
    """
    logger.debug(f"🧰🔄🔍 Validating type format: {type_value!r}")
    errors: list[str] = []

    # Convert bytes to string if needed
    if isinstance(type_value, bytes):
        try:
            type_str = type_value.decode('utf-8')
        except UnicodeDecodeError:
            errors.append(f"Invalid UTF-8 encoding: {type_value!r}")
            return errors
    else:
        type_str = type_value

    # Check for quotes if it's meant to be quoted
    if not type_str.startswith('"') or not type_str.endswith('"'):
        errors.append(f"Type string not properly quoted: {type_str!r}")

    # Extract the inner type string
    inner_type = type_str.strip('"')

    # Empty type is invalid
    if not inner_type:
        errors.append("Empty type string")
        return errors

    # Validate collection types recursively
    match _get_collection_pattern().match(inner_type):
        case re.Match() as m if m.group(1) in COLLECTION_TYPES:
            collection_type, element_type = m.groups()

            # Check if element type is empty
            if not element_type:
                errors.append(f"Collection type '{collection_type}' missing element type")

            # Recursively validate element type
            element_errors = validate_type_format(element_type)
            if element_errors:
                # Prefix with collection context
                prefixed_errors = [f"In {collection_type}(): {err}" for err in element_errors]
                errors.extend(prefixed_errors)

        # Check if it's a bare collection type
        case None if inner_type in COLLECTION_TYPES:
            errors.append(f"Bare collection type: {inner_type!r} needs element type")

    # Log validation result
    if errors:
        logger.debug(f"🧰🔄⚠️ Type format validation failed with {len(errors)} errors")
    else:
        logger.debug("🧰🔄✅ Type format validation passed")

    return errors

def normalize_type_object(type_obj: Any) -> TypeString:
    """
    Extract and normalize a type string from various type objects.

    This is a high-level utility that can handle various type representations
    and convert them to a standard type string format.

    Args:
        type_obj: The type object to normalize

    Returns:
        Normalized type string
    """
    logger.debug(f"🧰🔄📊 Normalizing type object: {type(type_obj).__name__}")

    # Handle different type representations using match/case
    match type_obj:
        case str() as s:
            return standardize_type_string(s)

        case bytes() as b:
            try:
                decoded = b.decode('utf-8')
                return standardize_type_string(decoded)
            except UnicodeDecodeError:
                logger.error(f"🧰🔄❌ Cannot decode type bytes: {b!r}")
                return "dynamic"

        case _ if hasattr(type_obj, "type_name"):
            # Handle PvsAttributeType
            type_name = getattr(type_obj, "type_name")
            element_type = getattr(type_obj, "element_type", None)

            base_type = normalize_type_object(type_name)

            # Handle collection with element type
            if element_type and base_type in COLLECTION_TYPES:
                element_type_str = normalize_type_object(element_type)
                return f"{base_type}({element_type_str})"

            return base_type

        case _ if hasattr(type_obj, "__class__") and type_obj.__class__.__name__.startswith("Cty"):
            # Handle CtyType objects based on class name
            class_name = type_obj.__class__.__name__

            # Extract base type from class name
            if class_name == "CtyString":
                return "string"
            elif class_name == "CtyNumber":
                return "number"
            elif class_name == "CtyBool":
                return "bool"
            elif class_name == "CtyDynamic":
                return "dynamic"
            elif class_name == "CtyList" and hasattr(type_obj, "element_type"):
                element_type_str = normalize_type_object(type_obj.element_type)
                return f"list({element_type_str})"
            elif class_name == "CtyMap" and hasattr(type_obj, "value_type"):
                value_type_str = normalize_type_object(type_obj.value_type)
                return f"map({value_type_str})"
            elif class_name == "CtySet" and hasattr(type_obj, "element_type"):
                element_type_str = normalize_type_object(type_obj.element_type)
                return f"set({element_type_str})"

        case _:
            # For unknown type objects, log and return dynamic
            logger.warning(f"🧰🔄⚠️ Unknown type object: {type_obj!r}, defaulting to dynamic")
            return "dynamic"

# 🐍🏗️🐣
