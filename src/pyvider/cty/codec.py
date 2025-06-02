# src/pyvider/cty/codec.py
# 🐍📦🔒

import json
import msgpack
from decimal import Decimal
from typing import Any, TYPE_CHECKING, cast
from attrs import evolve # Added for with_marks

from pyvider.cty.conversion.format import normalize_type_object

from pyvider.cty.conversion.format import normalize_type_object

if TYPE_CHECKING:
    from .values.base import CtyValue
    from .types.base import CtyType
    # Import CtyType for type hinting only


# Sentinel for cases where direct type check on CtyValue is tricky due to circular imports
# We'll rely on its structure (e.g., presence of .type, .value attributes)
# or pass CtyValue type dynamically if needed.

def _value_to_serializable(cty_value: 'CtyValue') -> dict[str, Any]:
    """
    Converts a CtyValue instance into a dictionary suitable for serialization.
    This leverages and extends the existing to_json_comparable_dict structure.
    """
    from .values.base import CtyValue # Lazy import for CtyValue

    # Start with the JSON-comparable dictionary
    # This already handles is_known, is_null, is_unknown, and value representation for primitives
    data = cty_value.to_json_comparable_dict()

    # Ensure 'type_name' is present for deserialization guidance.
    # to_json_comparable_dict() should already include this.
    if "type_name" not in data:
        # This would be an issue with to_json_comparable_dict(), but let's be safe.
        # For CtyValue, type is an attribute holding a CtyType instance.
        data["type_name"] = str(cty_value.type)


    # Handle marks explicitly if not already part of to_json_comparable_dict's main structure
    # Assuming marks are stringifiable or simple data.
    # If to_json_comparable_dict already includes marks in a serializable way, this might be redundant.
    # Let's assume to_json_comparable_dict handles marks appropriately as per its design for comparison.
    # If marks need special handling for serialization beyond what to_json_comparable_dict does,
    # it would be added here. For now, we trust to_json_comparable_dict.

    # The main difference for Msgpack vs JSON might be Decimal handling.
    # to_json_comparable_dict already converts Decimal to string for JSON.
    # This is also suitable for Msgpack to preserve precision.
    # If specific msgpack encoding for Decimals (e.g. as float) was desired,
    # this is where the value part of 'data' would be further processed.
    # However, string representation is generally safer for cross-system compatibility.

    return data


def _serializable_to_value(data: dict[str, Any], target_type: 'CtyType') -> 'CtyValue':
    """
    Recursively reconstructs a CtyValue from basic Python data and a target CtyType.
    'data' is expected to be a dictionary from _value_to_serializable.
    """
    from .types.base import CtyType
    from .values.base import CtyValue
    from pyvider.cty.types import CtyNumber, CtyString, CtyBool
    from pyvider.cty.types import CtyList, CtyMap, CtySet
    from pyvider.cty.types import CtyObject, CtyTuple, CtyDynamic
    from .marks import CtyMark

    # Basic structural validation for the incoming data dict
    if not isinstance(data, dict) or \
       "type_name" not in data or \
       ("value" not in data and not data.get("is_null", False) and not data.get("is_unknown", False)):
        raise ValueError(
            "Invalid serialized CtyValue format: must be a dict with 'type_name' "
            "and either 'value', 'is_null', or 'is_unknown'."
        )

    # Extract core components from the serialized data
    type_name_from_data = data.get("type_name")
    value_from_data = data.get("value")
    is_unknown = data.get("is_unknown", False)
    is_null = data.get("is_null", False)
    marks_from_data = data.get("marks", []) # Assuming marks are list of strings or dicts

    # Validate type consistency if type_name was in data
    # Use normalize_type_object for a consistent string representation of the target type
    normalized_target_type_str = normalize_type_object(target_type)
    if type_name_from_data and type_name_from_data != normalized_target_type_str:
        raise ValueError(
            f"Type mismatch: Serialized data indicates type '{type_name_from_data}', "
            f"but target type is '{normalized_target_type_str}' (normalized from {str(target_type)})."
        )

    # Handle unknown and null states first
    if is_unknown:
        reconstructed_value = CtyValue.unknown(target_type)
    elif is_null:
        reconstructed_value = CtyValue.null(target_type)
    else:
        # Reconstruct based on the target_type for known, non-null values
        if target_type.is_primitive_type():
            # For primitives, value_from_data should be directly usable by validate()
            # after potential Decimal conversion for numbers.
            current_value_for_validation = value_from_data
            if target_type is CtyNumber and isinstance(value_from_data, str):
                current_value_for_validation = Decimal(value_from_data)
            elif target_type is CtyNumber and not isinstance(value_from_data, Decimal):
                # If it's not a string or Decimal (e.g. int/float from msgpack direct conversion)
                current_value_for_validation = Decimal(str(value_from_data))

            reconstructed_value = target_type.validate(current_value_for_validation)

        elif target_type.is_list_type():
            element_type = target_type.element_type # type: ignore

            if not isinstance(value_from_data, list):
                raise ValueError("List value expected for CtyListType")

            elements = []
            for i, elem_data_item in enumerate(value_from_data):
                # Each item in value_from_data for a list *should* be a dict from _value_to_serializable
                # if we serialize elements as full CtyValues.
                # However, to_json_comparable_dict for list might return a plain list of values.
                # Let's assume value_from_data contains raw values for list elements,
                # and we need to wrap them into the "serializable dict" structure if they aren't already.

                # If elem_data_item is already a dict with "type_name", "value" etc, it's from a nested CtyValue.
                # Otherwise, it's a raw value.
                if isinstance(elem_data_item, dict) and "type_name" in elem_data_item and "value" in elem_data_item:
                    pass # Already in the expected format for _serializable_to_value
                else: # It's a raw value, needs to be wrapped for recursive call
                    elem_data_item = {
                        "type_name": str(element_type), # We know the element type
                        "value": elem_data_item,
                        "is_unknown": False, # Assuming direct values are known and not null
                        "is_null": False,
                        "marks": [] # Assuming no marks on raw elements unless explicitly provided
                    }
                elements.append(_serializable_to_value(elem_data_item, element_type))
            reconstructed_value = CtyValue(target_type, elements)

        elif target_type.is_map_type():
            value_type = target_type.value_type # type: ignore

            if not isinstance(value_from_data, dict):
                raise ValueError("Dict value expected for CtyMapType")

            items = {}
            for k, v_data_item in value_from_data.items():
                if isinstance(v_data_item, dict) and "type_name" in v_data_item and "value" in v_data_item:
                    pass
                else:
                    v_data_item = {
                        "type_name": str(value_type),
                        "value": v_data_item,
                        "is_unknown": False,
                        "is_null": False,
                        "marks": []
                    }
                items[k] = _serializable_to_value(v_data_item, value_type)
            reconstructed_value = CtyValue(target_type, items)

        elif target_type.is_object_type():
            if not isinstance(value_from_data, dict):
                raise ValueError("Dict value expected for CtyObjectType")

            attributes = {}
            for attr_name, attr_type in target_type.attribute_types.items(): # type: ignore
                attr_data_item = value_from_data.get(attr_name)
                if attr_data_item is None:
                    # Assuming to_json_comparable_dict ensures all expected keys are present,
                    # possibly with null/unknown markers if that's the intended serialization.
                    # If an attribute is truly missing from serialized data and is required,
                    # this indicates an issue with serialization or the data itself.
                    # For optional-but-missing, it should have been serialized as null.
                    # This check might be too strict if nulls are omitted from serialization.
                    # However, `_value_to_serializable` via `to_json_comparable_dict`
                    # should represent all attributes.
                    raise ValueError(f"Attribute '{attr_name}' missing in serialized object data for type {target_type}.")

                if isinstance(attr_data_item, dict) and "type_name" in attr_data_item and "value" in attr_data_item:
                    pass
                else:
                    attr_data_item = {
                        "type_name": str(attr_type),
                        "value": attr_data_item,
                        "is_unknown": False,
                        "is_null": False,
                        "marks": []
                    }
                attributes[attr_name] = _serializable_to_value(attr_data_item, attr_type)
            reconstructed_value = CtyValue(target_type, attributes)

        elif target_type.is_tuple_type():
            if not isinstance(value_from_data, list): # Tuples are serialized as JSON lists
                raise ValueError("List value expected for CtyTupleType")

            if len(value_from_data) != len(target_type.element_types): # type: ignore
                raise ValueError("Tuple element count mismatch.")

            elements = []
            for i, elem_type in enumerate(target_type.element_types): # type: ignore
                elem_data_item = value_from_data[i]
                if isinstance(elem_data_item, dict) and "type_name" in elem_data_item and "value" in elem_data_item:
                    pass
                else:
                    elem_data_item = {
                        "type_name": str(elem_type),
                        "value": elem_data_item,
                        "is_unknown": False,
                        "is_null": False,
                        "marks": []
                    }
                elements.append(_serializable_to_value(elem_data_item, elem_type))
            reconstructed_value = CtyValue(target_type, elements)

        # TODO: Add CtySetType handling if/when it's fully implemented and part of CtyValue variations
        # elif target_type.is_set_type():
        #     ...

        else:
            raise TypeError(f"Unsupported CtyType for deserialization: {target_type}")

    # Re-apply marks
    # Assuming marks_from_data is a list of strings or dicts that CtyMark can handle
    if marks_from_data:
        current_marks = set()
        for m_data in marks_from_data:
            if isinstance(m_data, dict) and "name" in m_data:
                # Details can be None, so handle its absence or presence
                details = m_data.get("details")
                current_marks.add(CtyMark(name=m_data["name"], details=details))
            # Add handling for old string format if backward compatibility is needed,
            # otherwise, this will ignore/error on old stringified marks.
            # For now, strictly expect the new dict format.
        # This 'if' block is now correctly aligned with the 'for' loop above
        if current_marks:
            reconstructed_value = evolve(reconstructed_value, marks=frozenset(current_marks))

    return reconstructed_value


def cty_value_to_json_string(value: 'CtyValue') -> str:
    """Serializes a CtyValue to a JSON string."""
    serializable_data = _value_to_serializable(value)
    return json.dumps(serializable_data)

def cty_value_from_json_string(json_str: str, target_type: 'CtyType') -> 'CtyValue':
    """Deserializes a CtyValue from a JSON string, targeting a specific CtyType."""
    data = json.loads(json_str)
    if not isinstance(data, dict):
        raise ValueError("Invalid JSON data: root must be an object.")
    return _serializable_to_value(data, target_type)

def cty_value_to_msgpack_bytes(value: 'CtyValue') -> bytes:
    """Serializes a CtyValue to Msgpack bytes."""
    serializable_data = _value_to_serializable(value)
    # msgpack handles basic Python types (dict, list, str, int, float, bool, None)
    # Decimals converted to strings by _value_to_serializable are fine.
    return msgpack.packb(serializable_data, use_bin_type=True)

def cty_value_from_msgpack_bytes(msgpack_bytes: bytes, target_type: 'CtyType') -> 'CtyValue':
    """Deserializes a CtyValue from Msgpack bytes, targeting a specific CtyType."""
    # By default, msgpack decodes strings to str, which is what we expect.
    # It also decodes map keys as str if they were str when packed.
    data = msgpack.unpackb(msgpack_bytes, raw=False)
    if not isinstance(data, dict):
        raise ValueError("Invalid Msgpack data: root must be a map (dict).")
    return _serializable_to_value(data, target_type)

# 🐍📦🔒
