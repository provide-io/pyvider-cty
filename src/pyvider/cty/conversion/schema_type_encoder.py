# pyvider/schema/conversion/wire_type_encoder.py
import json
import re
from typing import cast

from pyvider.telemetry import logger
from pyvider.cty.conversion.format import standardize_type_string, classify_type, parse_collection_type, TypeCategory

def _parse_comma_separated_elements(elements_str: str, is_object_attrs: bool) -> list[tuple[str, str]] | list[str]:
    elements = []

    # Handles "" (empty string) and "  " (whitespace only string)
    if not elements_str.strip():
        if not is_object_attrs and elements_str: # Input was "  " (whitespace only for tuple) -> one dynamic element
            return [""]
        return [] # Empty string for object_attrs, or truly empty string for tuple -> no elements/attributes

    current_pos = 0
    element_start = 0
    nesting_level = 0

    while current_pos < len(elements_str):
        char = elements_str[current_pos]
        if char == '(':
            nesting_level += 1
        elif char == ')':
            nesting_level -= 1
        elif char == ',' and nesting_level == 0:
            part = elements_str[element_start:current_pos].strip()
            elements.append(part)
            element_start = current_pos + 1
        current_pos += 1

    # Always append the last part after stripping, crucial for trailing commas or single element
    elements.append(elements_str[element_start:].strip())

    if is_object_attrs:
        parsed_attrs = []
        for attr_pair_str in elements:
            if not attr_pair_str: # Skip if an element itself is empty (e.g. from "name=type,,other=type")
                # This can happen if input was like "a=string,,b=number"
                # The middle empty part should be skipped for objects.
                continue
            if "=" not in attr_pair_str:
                logger.error(f"Invalid object attribute format: \"{attr_pair_str}\" in \"{elements_str}\"")
                # Skipping malformed attribute definitions
                continue
            name, type_val_str = attr_pair_str.split("=", 1)
            parsed_attrs.append((name.strip(), type_val_str.strip()))
        return parsed_attrs
    else:
        # For tuples, all parts (including empty strings from commas) are preserved.
        return elements

def _encode_wire_element(element_type_str: str) -> object:
    std_element_type = standardize_type_string(element_type_str)
    category = classify_type(std_element_type)
    if category == TypeCategory.PRIMITIVE: return std_element_type
    elif category == TypeCategory.COLLECTION:
        collection_kind, inner_element_type_str = parse_collection_type(std_element_type)
        inner_content = _encode_wire_element(inner_element_type_str)
        return [collection_kind, inner_content]
    elif std_element_type.startswith("object("):
        match = re.match(r"object\((.*)\)$", std_element_type)
        if not match: logger.error(f"Invalid object type string format for wire encoding: {std_element_type}"); return "dynamic"
        attrs_str = match.group(1)
        if not attrs_str: return ["object", {}]
        parsed_attrs = _parse_comma_separated_elements(attrs_str, is_object_attrs=True)
        attrs_dict_encoded = {name: _encode_wire_element(type_str) for name, type_str in cast(list[tuple[str,str]], parsed_attrs)}
        return ["object", attrs_dict_encoded]
    elif std_element_type.startswith("tuple("):
        match = re.match(r"tuple\((.*)\)$", std_element_type)
        if not match: logger.error(f"Invalid tuple type string format for wire encoding: {std_element_type}"); return "dynamic"
        elements_str = match.group(1)
        if not elements_str: return ["tuple", []]
        parsed_elements = _parse_comma_separated_elements(elements_str, is_object_attrs=False)
        elements_list_encoded = [_encode_wire_element(type_str) for type_str in cast(list[str], parsed_elements)]
        return ["tuple", elements_list_encoded]
    logger.warning(f"Unhandled type string in _encode_wire_element: \"{std_element_type}\", defaulting to dynamic.")
    return "dynamic"

def encode_type_to_wire(type_repr_str: str) -> bytes:
    logger.debug(f"🧰🔄📑 Encoding schema type string \"{type_repr_str}\" to wire format bytes")
    standardized_type = standardize_type_string(type_repr_str)
    encoded_content = _encode_wire_element(standardized_type)
    try:
        final_json_string = json.dumps(encoded_content)
        result_bytes = final_json_string.encode("utf-8")
        logger.debug(f"🧰🔄✅ Encoded \"{type_repr_str}\" (std: \"{standardized_type}\") to wire: {result_bytes!r}")
        return result_bytes
    except Exception as e:
        logger.error(f"Error JSON dumping encoded content for \"{type_repr_str}\": {e}. Content: {encoded_content!r}")
        return f"\"error_encoding_{standardized_type}\"".encode("utf-8")

__all__ = ["encode_type_to_wire"]
