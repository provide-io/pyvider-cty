# pyvider-cty/src/pyvider/cty/codec.py
"""
Provides functionality for encoding and decoding CTY types and values.
This includes the critical function for parsing CTY type strings.
"""
import re
from typing import Any

from .exceptions import CtyTypeParseError
from .types import (
    CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber,
    CtyObject, CtySet, CtyString, CtyTuple, CtyType
)

# Regex to capture the outer type and its inner content.
# e.g., for "list(string)", it captures "list" and "string".
# For "object({name=string})", it captures "object" and "{name=string}".
_type_pattern = re.compile(r"\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)\s*$", re.DOTALL)

def _split_arguments(arg_string: str) -> list[str]:
    """
    Splits a string of arguments by top-level commas, correctly handling nested structures.
    Example: "arg1, list(string), object({a=b,c=d})" -> ["arg1", "list(string)", "object({a=b,c=d})"]
    """
    if not arg_string:
        return []

    parts = []
    balance = 0
    current_part_start = 0
    for i, char in enumerate(arg_string):
        if char in '({[':
            balance += 1
        elif char in ')}]':
            balance -= 1
        elif char == ',' and balance == 0:
            parts.append(arg_string[current_part_start:i].strip())
            current_part_start = i + 1

    # Add the last part
    parts.append(arg_string[current_part_start:].strip())
    return parts

def parse_type_string_to_ctytype(type_str: str) -> CtyType:
    """
    Parses a CTY type string representation into a CtyType object.
    Handles primitives, collections, objects, and tuples, including nesting.
    Also supports shorthand for objects and tuples (e.g., "{...}" and "[...]").

    Args:
        type_str: The string representation of the CTY type.

    Returns:
        A CtyType instance corresponding to the string.

    Raises:
        CtyTypeParseError: If the string is invalid or cannot be parsed.
    """
    type_str = type_str.strip()

    # Handle primitive types
    primitives: dict[str, CtyType] = {
        "string": CtyString(),
        "number": CtyNumber(),
        "bool": CtyBool(),
        "dynamic": CtyDynamic(),
        "any": CtyDynamic(),
    }
    if type_str.lower() in primitives:
        return primitives[type_str.lower()]

    # Handle collection, object, and tuple types
    match = _type_pattern.match(type_str)
    
    type_keyword: str
    inner_content: str

    if match:
        # Matched canonical format like "list(string)"
        type_keyword, inner_content = match.groups()
        type_keyword = type_keyword.lower()
        inner_content = inner_content.strip()
    elif type_str.startswith("{") and type_str.endswith("}"):
        # Handle shorthand object format "{...}"
        type_keyword = "object"
        inner_content = type_str
    elif type_str.startswith("[") and type_str.endswith("]"):
        # Handle shorthand tuple format "[...]"
        type_keyword = "tuple"
        inner_content = type_str
    else:
        raise CtyTypeParseError("Invalid type format", type_str)

    try:
        if type_keyword in ("list", "set", "map"):
            element_type = parse_type_string_to_ctytype(inner_content)
            if type_keyword == "list":
                return CtyList(element_type=element_type)
            if type_keyword == "set":
                return CtySet(element_type=element_type)
            # For map, key is always string, value is the element type
            return CtyMap(key_type=CtyString(), value_type=element_type)

        if type_keyword == "object":
            if not inner_content.startswith("{") or not inner_content.endswith("}"):
                raise CtyTypeParseError("Object type definition must be enclosed in braces {}", type_str)
            attr_content = inner_content[1:-1].strip()
            if not attr_content:
                return CtyObject(attribute_types={})

            attribute_types = {}
            parts = _split_arguments(attr_content)
            for part in parts:
                if "=" not in part:
                    raise CtyTypeParseError(f"Invalid attribute format in object: '{part}' (missing '=')", type_str)
                name, attr_type_str = part.split("=", 1)
                name_stripped = name.strip()
                if not name_stripped:
                    raise CtyTypeParseError(f"Invalid attribute format in object: attribute name cannot be empty in '{part}'", type_str)
                attribute_types[name_stripped] = parse_type_string_to_ctytype(attr_type_str.strip())
            return CtyObject(attribute_types=attribute_types)

        if type_keyword == "tuple":
            if not inner_content.startswith("[") or not inner_content.endswith("]"):
                raise CtyTypeParseError("Tuple type definition must be enclosed in brackets []", type_str)
            elem_content = inner_content[1:-1].strip()
            if not elem_content:
                return CtyTuple(element_types=())

            element_types = [parse_type_string_to_ctytype(part.strip()) for part in _split_arguments(elem_content)]
            return CtyTuple(element_types=tuple(element_types))

    except CtyTypeParseError as e:
        # Re-raise nested parsing errors to provide full context
        raise CtyTypeParseError(f"Failed to parse inner content of '{type_keyword}': {e.message}", type_str) from e
    except Exception as e:
        # Catch other unexpected errors during parsing
        raise CtyTypeParseError(f"An unexpected error occurred while parsing '{type_keyword}': {e}", type_str) from e

    raise CtyTypeParseError(f"Unknown type keyword '{type_keyword}'", type_str)
