# pyvider/schema/conversion/wire_type_encoder.py
"""
Encodes CTY type schema representations into a JSON-based wire format.

This module is responsible for taking a string representation of a CTY type
(e.g., "list(string)", "object({name=string,age=number})") and converting it
into a structured JSON format suitable for wire transmission or storage.
This is different from serializing CtyValue instances; this serializes the
type *schema* itself.
"""
import json
import re
from typing import cast

from pyvider.cty.conversion.format import (
    TypeCategory,
    classify_type,
    parse_collection_type,
    standardize_type_string,
)
from pyvider.telemetry import logger


def _parse_comma_separated_elements(
    elements_str_input: str, is_object_attrs: bool
) -> list[tuple[str, str]] | list[str]:
    """
    Parses a string of comma-separated elements, respecting nested structures.

    This function is used to break down the content within object attribute
    definitions (e.g., "name=string,age=number") and tuple element type
    definitions (e.g., "string,number,list(string)").

    Args:
        elements_str_input: The raw string content to parse.
        is_object_attrs: Boolean flag indicating if the string represents
                         object attributes (which are key-value pairs) or
                         tuple elements (which are just type strings).

    Returns:
        If is_object_attrs is True, returns a list of (name, type_str) tuples.
        If is_object_attrs is False, returns a list of type_str strings.
        Returns an empty list if the input string is empty or represents
        an empty structure (e.g., "{}" for objects, "[]" for tuples).
    """
    elements = []
    # Use a different variable for the string to be parsed by the loop
    # This ensures that modifications for object attributes (like stripping braces)
    # are applied to the content being iterated over for comma splitting.
    parsable_content = elements_str_input.strip()

    # Handles "" (empty string) and "  " (whitespace only string)
    if not parsable_content:
        # For tuples, if original input was just whitespace (e.g. "  ") but not empty,
        # it implies an intent for a single element that should be treated as dynamic or similar.
        # Returning [""] allows _encode_wire_element to process it (likely becoming "dynamic").
        if (
            not is_object_attrs and elements_str_input
        ):  # Original input was not empty but parsable_content is
            return [""]
        return []  # Empty string for object_attrs, or truly empty string for tuple -> no elements/attributes

    # Handle specific tuple case: an explicit "[]" content for a tuple means zero elements.
    if not is_object_attrs and parsable_content == "[]":
        return []

    if is_object_attrs:
        # Object attributes string from regex (attrs_str) can be:
        # 1. {{attr1=type1,...}} (if standardize_type_string results in this for multiple attributes)
        # 2. {attr1=type1} (if standardize_type_string results in this for single attribute)
        # 3. {} (for empty object from {{}})
        # 4. "" (for empty object from {})
        # We need to strip down to the actual "attr1=type1,..." part or "" for the loop.

        if parsable_content.startswith("{{") and parsable_content.endswith("}}"):
            # Handles case 1: {{attr1=type1,...}} -> {attr1=type1,...}
            # Also handles case 3: {{}} -> {}
            parsable_content = parsable_content[1:-1].strip()

        if parsable_content.startswith("{") and parsable_content.endswith("}"):
            # Handles case 2: {attr1=type1} -> attr1=type1
            # Also handles result from case 1: {attr1=type1,...} -> attr1=type1,...
            # Also handles result from case 3: {} -> ""
            parsable_content = parsable_content[1:-1].strip()

        # After stripping, if parsable_content is empty, it means an empty object definition.
        if not parsable_content:
            return []  # Represents an empty list of attributes

    current_pos = 0
    element_start = 0
    nesting_level = 0

    # The loop should iterate over `parsable_content`
    while current_pos < len(parsable_content):
        char = parsable_content[current_pos]
        if char == "(":
            nesting_level += 1
        elif char == ")":
            nesting_level -= 1
        elif char == "," and nesting_level == 0:
            part = parsable_content[element_start:current_pos].strip()
            elements.append(part)
            element_start = current_pos + 1
        current_pos += 1

    # Always append the last part of `parsable_content`
    elements.append(parsable_content[element_start:].strip())

    if is_object_attrs:
        parsed_attrs = []
        for attr_pair_str in elements:
            if (
                not attr_pair_str
            ):  # Skip if an element itself is empty (e.g. from "name=type,,other=type")
                # This can happen if input was like "a=string,,b=number"
                # The middle empty part should be skipped for objects.
                continue
            if "=" not in attr_pair_str:
                logger.error(
                    f'Invalid object attribute format: "{attr_pair_str}" in "{elements_str_input}"'
                )
                # Skipping malformed attribute definitions
                continue
            name, type_val_str = attr_pair_str.split("=", 1)
            parsed_attrs.append((name.strip(), type_val_str.strip()))
        return parsed_attrs
    else:
        # For tuples, all parts (including empty strings from commas) are preserved.
        return elements


def _encode_wire_element(element_type_str: str) -> object:
    """
    Recursively encodes a standardized CTY type string into a JSON-serializable structure.

    Primitives are returned as strings. Collections and structural types are
    returned as lists or lists of lists/dictionaries representing their structure
    and element/attribute types. For example:
    - "string" -> "string"
    - "list(number)" -> ["list", "number"]
    - "object({name=string})" -> ["object", {"name": "string"}]
    - "tuple([bool,string])" -> ["tuple", ["bool", "string"]]

    Args:
        element_type_str: A standardized CTY type string.

    Returns:
        A JSON-serializable representation of the type schema.
    """
    std_element_type = standardize_type_string(element_type_str)
    category = classify_type(std_element_type)
    if category == TypeCategory.PRIMITIVE:
        return std_element_type
    elif category == TypeCategory.COLLECTION:
        collection_kind, inner_element_type_str = parse_collection_type(
            std_element_type
        )
        inner_content = _encode_wire_element(inner_element_type_str)
        return [collection_kind, inner_content]
    elif std_element_type.startswith("object("):
        match = re.match(r"object\((.*)\)$", std_element_type)
        if not match:
            logger.error(
                f"Invalid object type string format for wire encoding: {std_element_type}"
            )
            return "dynamic"
        attrs_str = match.group(1)
        if not attrs_str:
            return ["object", {}]
        parsed_attrs = _parse_comma_separated_elements(attrs_str, is_object_attrs=True)
        attrs_dict_encoded = {
            name: _encode_wire_element(type_str)
            for name, type_str in cast(list[tuple[str, str]], parsed_attrs)
        }
        return ["object", attrs_dict_encoded]
    elif std_element_type.startswith("tuple("):
        match = re.match(r"tuple\((.*)\)$", std_element_type)
        if not match:
            logger.error(
                f"Invalid tuple type string format for wire encoding: {std_element_type}"
            )
            return "dynamic"
        elements_str = match.group(1)
        if not elements_str:
            return ["tuple", []]
        parsed_elements = _parse_comma_separated_elements(
            elements_str, is_object_attrs=False
        )
        elements_list_encoded = [
            _encode_wire_element(type_str)
            for type_str in cast(list[str], parsed_elements)
        ]
        return ["tuple", elements_list_encoded]
    # The handling of unstandardized list/object-like strings that might appear as tuple elements
    # (previously attempted here) is removed. The responsibility for recognizing these forms
    # correctly lies with format.py's standardize_type_string and classify_type, or the
    # specific tests need to align with the fact that _encode_wire_element expects
    # its input type strings to be in a recognizable, standard format.
    logger.warning(
        f'Unhandled type string in _encode_wire_element: "{std_element_type}", defaulting to dynamic.'
    )
    return "dynamic"


def encode_type_to_wire(type_repr_str: str) -> bytes:
    """
    Encodes a CTY type representation string into a JSON-based wire format bytes.

    The input string is first standardized, then recursively encoded into a
    structured list/dictionary format, which is finally dumped as a JSON
    string and encoded to UTF-8 bytes.

    Example:
        "list(object({id=string}))" ->
        b'["list", ["object", {"id": "string"}]]'

    Args:
        type_repr_str: The CTY type representation string.

    Returns:
        Bytes representing the JSON-encoded type schema.
        Returns a fallback error string encoded to bytes if encoding fails.
    """
    logger.debug(
        f'🧰🔄📑 Encoding schema type string "{type_repr_str}" to wire format bytes'
    )
    standardized_type = standardize_type_string(type_repr_str)
    encoded_content = _encode_wire_element(standardized_type)
    try:
        final_json_string = json.dumps(encoded_content)
        result_bytes = final_json_string.encode("utf-8")
        logger.debug(
            f'🧰🔄✅ Encoded "{type_repr_str}" (std: "{standardized_type}") to wire: {result_bytes!r}'
        )
        return result_bytes
    except Exception as e:
        logger.error(
            f'Error JSON dumping encoded content for "{type_repr_str}": {e}. Content: {encoded_content!r}'
        )
        return f'"error_encoding_{standardized_type}"'.encode()


__all__ = ["encode_type_to_wire"]
