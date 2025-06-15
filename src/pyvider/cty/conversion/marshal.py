# pyvider/cty/conversion/marshal.py

from typing import cast, Type
from pyvider.telemetry import logger
from enum import Enum, auto

from pyvider.cty.types import (
    CtyType, CtyString, CtyNumber, CtyBool, CtyDynamic,
    CtyList, CtyMap, CtySet, CtyObject, CtyTuple
)
from pyvider.cty.exceptions import CtyConversionError, CtyTypeConversionError


class TypeCategory(Enum):
    PRIMITIVE = auto()
    LIST = auto()
    MAP = auto()
    SET = auto()
    OBJECT = auto() # Not directly used by marshal/unmarshal string format yet
    TUPLE = auto()  # Not directly used by marshal/unmarshal string format yet
    UNKNOWN = auto()


def _standardize_type_string(type_str: str) -> str:
    """
    Normalize a type string by stripping quotes and whitespace,
    and ensuring consistent formatting for collections.
    """
    logger.debug(f"🧰🔄📊 Standardizing type string: {type_str!r}")

    original_type_str = type_str # For logging original if it gets changed to dynamic

    type_str = type_str.strip()
    if type_str.startswith('"') and type_str.endswith('"'):
        type_str = type_str[1:-1].strip()

    if not type_str: # Handles empty string or quoted empty string
        logger.debug(f"🧰🔄📊 Empty type string, defaulting to 'dynamic'")
        return "dynamic"

    # Normalize list(), map(), set() to list(dynamic), map(dynamic), set(dynamic)
    # This helps simplify parsing later if the element type is omitted.
    if type_str.lower() == "list()":
        type_str = "list(dynamic)"
        logger.debug(f"🧰🔄📊 Normalized collection type to: {type_str!r}")
    elif type_str.lower() == "map()":
        type_str = "map(dynamic)"
        logger.debug(f"🧰🔄📊 Normalized collection type to: {type_str!r}")
    elif type_str.lower() == "set()":
        type_str = "set(dynamic)"
        logger.debug(f"🧰🔄📊 Normalized collection type to: {type_str!r}")
    # Recursively standardize inner types for collections
    elif type_str.lower().startswith(("list(", "map(", "set(")) and type_str.endswith(")"):
        base_type, inner_content = "", ""
        if type_str.lower().startswith("list("):
            base_type = "list"
            inner_content = type_str[len("list("):-1].strip()
        elif type_str.lower().startswith("map("):
            base_type = "map"
            inner_content = type_str[len("map("):-1].strip()
        elif type_str.lower().startswith("set("):
            base_type = "set"
            inner_content = type_str[len("set("):-1].strip()

        if inner_content:
            standardized_inner = _standardize_type_string(inner_content)
            type_str = f"{base_type}({standardized_inner})"
            logger.debug(f"🧰🔄📊 Normalized collection type to: {type_str!r}")
        # If inner_content was empty after strip, it means something like "list( )"
        # which was already handled by "list()" -> "list(dynamic)" if it was truly empty.
        # If it's not empty but standardize_type_string makes it dynamic (e.g. "list(unknown)"),
        # that's also fine.

    logger.debug(f"🧰🔄📊 Normalized type string: {type_str!r}")
    return type_str


def marshal_type(type_obj: CtyType | str) -> bytes:
    """
    Convert a CTY type object or string representation to Terraform protocol type bytes.

    Args:
        type_obj: The CTY type object or its string representation

    Returns:
        bytes: The Terraform protocol type bytes

    Raises:
        CtyTypeConversionError: If conversion fails
    """
    logger.debug(f"🧰🔄📊 Converting {type(type_obj).__name__} to type bytes")
    try:
        normalized_str = _normalize_type_object(type_obj)
        standardized_str = _standardize_type_string(normalized_str)
        # Ensure the final string is quoted for the wire format
        quoted_str = f'"{standardized_str}"'
        logger.debug(f"🧰🔄📊 Converted to quoted bytes: {quoted_str.encode('utf-8')!r}")
        return quoted_str.encode("utf-8")
    except Exception as e:
        if isinstance(e, CtyConversionError): # Already a specific error we want to propagate
            raise
        # Wrap other unexpected errors for consistent error handling
        raise CtyTypeConversionError(f"Unexpected error marshalling type: {e}", source_value=type_obj) from e


def unmarshal_type(type_bytes: bytes, options: dict[str, object] | None = None) -> CtyType:
    """
    Convert Terraform protocol type bytes to a CTY type.

    Args:
        type_bytes: The type bytes to convert
        options: Optional conversion options

    Returns:
        CtyType: The corresponding CTY type

    Raises:
        CtyConversionError: If conversion fails
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
            type_str = _standardize_type_string(decoded_str)
            logger.debug(f"🧰🔍📊 Standardized type string: {type_str!r}")
        except UnicodeDecodeError:
            raise CtyTypeConversionError(f"Type bytes are not valid UTF-8: {type_bytes!r}") # Fixed exception type
        except Exception as e: # Catch other errors during standardization
            raise CtyTypeConversionError(f"Unexpected error standardizing type string: {e}", source_value=type_bytes) from e


        category = _classify_type(type_str)

        if category == TypeCategory.PRIMITIVE:
            return _parse_primitive_type(type_str)
        elif category in (TypeCategory.LIST, TypeCategory.MAP, TypeCategory.SET):
            return _parse_collection_type(type_str, category)
        elif category == TypeCategory.UNKNOWN: # Should catch malformed like "list(string"
             raise CtyTypeConversionError(f"Unknown or malformed CTY type string format: {type_str}")
        else: # Should not happen if _classify_type is comprehensive
            raise CtyTypeConversionError(f"Unsupported type category for type string: {type_str}")

    except Exception as e:
        if isinstance(e, CtyConversionError): # Re-raise our specific errors
            raise
        # Wrap other unexpected errors
        raise CtyTypeConversionError(f"Unexpected error classifying type string: {e}", source_value=type_bytes) from e


def _classify_type(type_str: str) -> TypeCategory:
    """Classify a type string into a category."""
    logger.debug(f"🧰🔄📊 Classifying type: {type_str!r}")
    type_str_lower = type_str.lower()

    if type_str_lower in ("string", "number", "bool", "dynamic", "null"):
        return TypeCategory.PRIMITIVE
    if type_str_lower.startswith("list(") and type_str_lower.endswith(")"):
        if not type_str_lower[len("list("):-1].strip(): # e.g. list() or list( )
            logger.warning(f"🧰🔍⚠️ Malformed list type (empty element): {type_str}, defaulting to dynamic list element")
            # This will be standardized to list(dynamic) by _standardize_type_string if called before,
            # but _classify_type itself should still recognize the structure.
        return TypeCategory.LIST
    if type_str_lower.startswith("map(") and type_str_lower.endswith(")"):
        if not type_str_lower[len("map("):-1].strip():
             logger.warning(f"🧰🔍⚠️ Malformed map type (empty element): {type_str}, defaulting to dynamic map value")
        return TypeCategory.MAP
    if type_str_lower.startswith("set(") and type_str_lower.endswith(")"):
        if not type_str_lower[len("set("):-1].strip():
             logger.warning(f"🧰🔍⚠️ Malformed set type (empty element): {type_str}, defaulting to dynamic set element")
        return TypeCategory.SET

    logger.warning(f"🧰🔍⚠️ Unknown type format: {type_str}, defaulting to dynamic")
    return TypeCategory.UNKNOWN


def _parse_primitive_type(type_str: str) -> CtyType:
    """Parse a primitive type string to a CtyType object."""
    match type_str.lower():
        case "string": return CtyString()
        case "number": return CtyNumber()
        case "bool": return CtyBool()
        case "dynamic" | "null" | "": return CtyDynamic() # Treat "null" type string as dynamic for now
        case _:
            # This case should ideally not be reached if _classify_type and _standardize_type_string are robust
            # and unmarshal_type handles UNKNOWN category by raising error.
            logger.warning(f"🧰🔍⚠️ Unrecognized primitive type string '{type_str}', defaulting to CtyDynamic.")
            return CtyDynamic()


def _parse_collection_type(type_str: str, category: TypeCategory) -> CtyType:
    """Parse a collection type string to a CtyType object."""
    logger.debug(f"🧰🔄📊 Parsing collection type: {type_str!r}")

    base_type_str = ""
    element_type_str = ""

    if category == TypeCategory.LIST:
        base_type_str = "list"
        element_type_str = type_str[len("list("):-1].strip()
    elif category == TypeCategory.MAP:
        base_type_str = "map"
        element_type_str = type_str[len("map("):-1].strip() # This is the value type
    elif category == TypeCategory.SET:
        base_type_str = "set"
        element_type_str = type_str[len("set("):-1].strip()
    else: # Should not happen based on call sites
        raise CtyTypeConversionError(f"Internal error: _parse_collection_type called with invalid category {category}")

    if not element_type_str: # e.g. "list()" after stripping, which means "list( )" originally
        raise ValueError(f"Invalid collection type string: {base_type_str}() has no element type")
    if not type_str.lower().startswith(f"{base_type_str}(") or not type_str.endswith(")"): # Defensive
         raise ValueError(f"Invalid collection type string: {type_str} does not end with ')' or start correctly")


    logger.debug(f"🧰🔄📊 Parsed collection: {base_type_str}({element_type_str})")

    # Recursively unmarshal the element type
    # We need to pass the element type string as bytes and quoted, as unmarshal_type expects.
    element_type_bytes = f'"{element_type_str}"'.encode("utf-8")
    logger.debug(f"🧰🔍📊 Recursively unmarshaling element type: {element_type_bytes!r}")
    element_cty_type = unmarshal_type(element_type_bytes)

    if category == TypeCategory.LIST:
        return CtyList(element_type=element_cty_type)
    elif category == TypeCategory.MAP:
        # Terraform's string format `map(T)` implies string keys.
        return CtyMap(key_type=CtyString(), value_type=element_cty_type)
    elif category == TypeCategory.SET:
        return CtySet(element_type=element_cty_type)

    # Should be unreachable due to earlier checks
    raise CtyTypeConversionError(f"Internal error: Unhandled category in _parse_collection_type: {category}")


def _normalize_type_object(type_obj: CtyType | str) -> str:
    """
    Normalize a CtyType instance or a type string into a canonical string form.
    Handles CtyObject and CtyTuple by converting them to "dynamic" as per current
    Terraform wire protocol behavior for these complex types when simplified.
    """
    logger.debug(f"🧰🔄📊 Normalizing type object: {type(type_obj).__name__}")
    if isinstance(type_obj, str):
        return type_obj # Already a string, assume it's in a somewhat standard form

    if isinstance(type_obj, CtyString): return "string"
    if isinstance(type_obj, CtyNumber): return "number"
    if isinstance(type_obj, CtyBool): return "bool"
    if isinstance(type_obj, CtyDynamic): return "dynamic"

    if isinstance(type_obj, CtyList):
        element_str = _normalize_type_object(type_obj.element_type)
        return f"list({element_str})"
    if isinstance(type_obj, CtyMap):
        # Ensure key is primitive for wire format
        if not isinstance(type_obj.key_type, (CtyString, CtyNumber, CtyBool, CtyDynamic)):
            raise CtyConversionError(f"Map key type must be a primitive type, got {type_obj.key_type.__class__.__name__}")
        # Wire format for map(T) implies string keys, value type T
        value_str = _normalize_type_object(type_obj.value_type)
        return f"map({value_str})"
    if isinstance(type_obj, CtySet):
        element_str = _normalize_type_object(type_obj.element_type)
        return f"set({element_str})"

    # For CtyObject and CtyTuple, Terraform's type bytes often simplify to "dynamic"
    # or a more complex JSON structure not representable by the simple "type(element)" strings.
    # The current marshal_type aims to produce the simple quoted string format.
    if isinstance(type_obj, CtyObject):
        attrs_parts = []
        for name, attr_type in sorted(type_obj.attribute_types.items()): # Sort for consistent output
            attrs_parts.append(f"{name}={_normalize_type_object(attr_type)}")
        return f"object({{{', '.join(attrs_parts)}}})"

    if isinstance(type_obj, CtyTuple):
        elems_parts = [_normalize_type_object(et) for et in type_obj.element_types]
        return f"tuple([{', '.join(elems_parts)}])"

    logger.warning(f"🧰🔄⚠️ Unknown type object: {type(type_obj).__name__}, defaulting to dynamic")
    raise CtyConversionError(f"Unhandled CTY type class: {type_obj.__class__.__name__}")
