# src/pyvider/cty/codec.py
# 🐍📦🔒

from decimal import Decimal
import json
import re  # For more robust parsing
from typing import TYPE_CHECKING, cast

from attrs import evolve  # Added for with_marks
import msgpack
from msgpack import ExtType

from pyvider.cty.conversion.format import normalize_type_object

from .types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
)
# CtyType is imported below under TYPE_CHECKING to resolve forward ref if needed,
# but it's also directly used, so ensure it's available for runtime.
from .types.base import CtyType as CtyTypeDefinition

if TYPE_CHECKING:
    from .values.base import CtyValue
    from .types.base import CtyType # Ensure CtyType is available for type hints


# Custom exception for parsing errors
class CtyTypeParseError(ValueError):
    """Raised when a CTY type string cannot be parsed."""

    pass


# Sentinel for cases where direct type check on CtyValue is tricky due to circular imports
# We'll rely on its structure (e.g., presence of .type, .value attributes)
# or pass CtyValue type dynamically if needed.


def _value_to_serializable(cty_value: CtyValue) -> dict[str, object]:
    """
    Converts a CtyValue instance into a dictionary suitable for serialization.
    This leverages and extends the existing to_json_comparable_dict structure.
    """

    data = cty_value.to_json_comparable_dict()
    if "type_name" not in data:
        data["type_name"] = str(cty_value.type)
    return data


def _serializable_to_value(
    data: dict[str, object], target_type: CtyType
) -> CtyValue:
    """
    Recursively reconstructs a CtyValue from basic Python data and a target CtyType.
    'data' is expected to be a dictionary from _value_to_serializable.
    """
    from .marks import CtyMark
    from .values.base import CtyValue

    if (
        not isinstance(data, dict)
        or "type_name" not in data
        or (
            "value" not in data
            and not data.get("is_null", False)
            and not data.get("is_unknown", False)
        )
    ):
        raise ValueError(
            "Invalid serialized CtyValue format: must be a dict with 'type_name' "
            "and either 'value', 'is_null', or 'is_unknown'."
        )

    type_name_from_data = data.get("type_name")
    value_from_data = data.get("value")
    is_unknown = data.get("is_unknown", False)
    is_null = data.get("is_null", False)
    marks_from_data = data.get("marks", [])

    normalized_target_type_str = normalize_type_object(target_type)
    if type_name_from_data and type_name_from_data != normalized_target_type_str:
        raise ValueError(
            f"Type mismatch: Serialized data indicates type '{type_name_from_data}', "
            f"but target type is '{normalized_target_type_str}' (normalized from {target_type!s})."
        )

    if (
        isinstance(target_type, CtyDynamic)
        and isinstance(value_from_data, dict)
        and "type" in value_from_data
        and "value" in value_from_data
        and not is_unknown
        and not is_null
    ):
        embedded_type_name_str = cast(str, value_from_data["type"])
        embedded_value_payload = value_from_data["value"]

        try:
            actual_embedded_cty_type = parse_type_string_to_ctytype(
                embedded_type_name_str
            )
        except CtyTypeParseError as e:
            raise ValueError(
                f"Failed to parse embedded type string '{embedded_type_name_str}': {e}"
            ) from e

        if actual_embedded_cty_type:
            recursive_data = {
                "type_name": embedded_type_name_str,  # Use the parsed name
                "value": embedded_value_payload,
                "is_unknown": False,
                "is_null": False,
                "marks": [],
            }
            inner_value_instance = _serializable_to_value(
                recursive_data, actual_embedded_cty_type
            )
            reconstructed_value = CtyValue(target_type, inner_value_instance)
        else:  # Should not happen if parse_type_string_to_ctytype errors or returns valid
            reconstructed_value = target_type.validate(value_from_data)
    elif is_unknown:
        reconstructed_value = CtyValue.unknown(target_type)
    elif is_null:
        reconstructed_value = CtyValue.null(target_type)
    else:
        if target_type.is_primitive_type():
            current_value_for_validation = value_from_data
            if target_type is CtyNumber and isinstance(value_from_data, str):
                current_value_for_validation = Decimal(value_from_data)
            elif target_type is CtyNumber and not isinstance(value_from_data, Decimal):
                current_value_for_validation = Decimal(str(value_from_data))
            reconstructed_value = target_type.validate(current_value_for_validation)
        elif target_type.is_list_type():
            element_type = target_type.element_type  # type: ignore
            if not isinstance(value_from_data, list):
                raise ValueError("List value expected for CtyListType")
            elements = []
            for i, elem_data_item in enumerate(value_from_data):
                if (
                    isinstance(elem_data_item, dict)
                    and "type_name" in elem_data_item
                    and "value" in elem_data_item
                ):
                    pass
                else:
                    elem_data_item = {
                        "type_name": str(element_type),
                        "value": elem_data_item,
                        "is_unknown": False,
                        "is_null": False,
                        "marks": [],
                    }
                elements.append(_serializable_to_value(elem_data_item, element_type))
            reconstructed_value = CtyValue(target_type, elements)
        elif target_type.is_map_type():
            value_type = target_type.value_type  # type: ignore
            if not isinstance(value_from_data, dict):
                raise ValueError("Dict value expected for CtyMapType")
            items = {}
            for k, v_data_item in value_from_data.items():
                if (
                    isinstance(v_data_item, dict)
                    and "type_name" in v_data_item
                    and "value" in v_data_item
                ):
                    pass
                else:
                    v_data_item = {
                        "type_name": str(value_type),
                        "value": v_data_item,
                        "is_unknown": False,
                        "is_null": False,
                        "marks": [],
                    }
                items[k] = _serializable_to_value(v_data_item, value_type)
            reconstructed_value = CtyValue(target_type, items)
        elif target_type.is_object_type():
            if not isinstance(value_from_data, dict):
                raise ValueError("Dict value expected for CtyObjectType")
            attributes = {}
            for attr_name, attr_type in target_type.attribute_types.items():  # type: ignore
                attr_data_item = value_from_data.get(attr_name)
                if attr_data_item is None:
                    raise ValueError(
                        f"Attribute '{attr_name}' missing in serialized object data for type {target_type}."
                    )
                if (
                    isinstance(attr_data_item, dict)
                    and "type_name" in attr_data_item
                    and "value" in attr_data_item
                ):
                    pass
                else:
                    attr_data_item = {
                        "type_name": str(attr_type),
                        "value": attr_data_item,
                        "is_unknown": False,
                        "is_null": False,
                        "marks": [],
                    }
                attributes[attr_name] = _serializable_to_value(
                    attr_data_item, attr_type
                )
            reconstructed_value = CtyValue(target_type, attributes)
        elif target_type.is_tuple_type():
            if value_from_data is None and not target_type.element_types:  # type: ignore
                reconstructed_internal_value = tuple()
            elif not isinstance(value_from_data, list):
                raise ValueError(
                    f"List value expected for CtyTupleType, got {type(value_from_data).__name__} for type {target_type}"
                )
            elif len(value_from_data) != len(target_type.element_types):  # type: ignore
                raise ValueError(
                    f"Tuple element count mismatch for type {target_type}. Expected {len(target_type.element_types)}, got {len(value_from_data)}"
                )  # type: ignore
            else:
                processed_elements = []
                for i, elem_type in enumerate(target_type.element_types):  # type: ignore
                    elem_data_item = value_from_data[i]
                    if not (
                        isinstance(elem_data_item, dict)
                        and "type_name" in elem_data_item
                    ):
                        elem_data_item = {
                            "type_name": normalize_type_object(elem_type),
                            "value": elem_data_item,
                            "is_unknown": False,
                            "is_null": False,
                            "marks": [],
                        }
                    processed_elements.append(
                        _serializable_to_value(elem_data_item, elem_type)
                    )
                reconstructed_internal_value = tuple(processed_elements)
            reconstructed_value = CtyValue(target_type, reconstructed_internal_value)
        else:
            raise TypeError(f"Unsupported CtyType for deserialization: {target_type}")

    if marks_from_data:
        current_marks = set()
        for m_data in marks_from_data:
            if isinstance(m_data, dict) and "name" in m_data:
                details = m_data.get("details")
                current_marks.add(CtyMark(name=m_data["name"], details=details))
        if current_marks:
            reconstructed_value = evolve(
                reconstructed_value, marks=frozenset(current_marks)
            )
    return reconstructed_value


def cty_value_to_json_string(value: CtyValue) -> str:
    serializable_data = _value_to_serializable(value)
    return json.dumps(serializable_data)


def cty_value_from_json_string(json_str: str, target_type: CtyType) -> CtyValue:
    data = json.loads(json_str)
    if not isinstance(data, dict):
        raise ValueError("Invalid JSON data: root must be an object.")
    return _serializable_to_value(data, target_type)


def cty_value_to_msgpack_bytes(value: CtyValue) -> bytes:
    if value.is_unknown:
        return msgpack.packb(ExtType(0, b""), use_bin_type=True)
    serializable_data = _value_to_serializable(value)
    return msgpack.packb(serializable_data, use_bin_type=True)


__PYVIDER_CTY_UNKNOWN_SENTINEL__ = "__PYVIDER_CTY_UNKNOWN_SENTINEL__"


def cty_msgpack_ext_hook(code, data):
    if code == 0:
        return __PYVIDER_CTY_UNKNOWN_SENTINEL__
    raise ValueError(f"Unknown msgpack extension type code: {code}")


def cty_value_from_msgpack_bytes(
    msgpack_bytes: bytes, target_type: CtyType
) -> CtyValue:
    from .values.base import CtyValue

    data = msgpack.unpackb(msgpack_bytes, ext_hook=cty_msgpack_ext_hook, raw=False)
    if data == __PYVIDER_CTY_UNKNOWN_SENTINEL__:
        return CtyValue.unknown(target_type)
    if not isinstance(data, dict):
        raise ValueError(
            "Invalid Msgpack data: root must be a map (dict) or known Cty extension type."
        )
    return _serializable_to_value(data, target_type)


def _split_by_delimiter_respecting_nesting(text: str, delimiter: str) -> list[str]:
    if not text:
        return []
    parts = []
    balance_paren = 0
    balance_bracket = 0
    balance_brace = 0
    current_part_start = 0
    for i, char in enumerate(text):
        if char == "(":
            balance_paren += 1
        elif char == ")":
            balance_paren -= 1
        elif char == "[":
            balance_bracket += 1
        elif char == "]":
            balance_bracket -= 1
        elif char == "{":
            balance_brace += 1
        elif char == "}":
            balance_brace -= 1
        elif (
            char == delimiter
            and balance_paren == 0
            and balance_bracket == 0
            and balance_brace == 0
        ):
            parts.append(text[current_part_start:i].strip())
            current_part_start = i + 1
    parts.append(text[current_part_start:].strip())
    return parts  # Do not filter empty strings here; let caller decide


def parse_type_string_to_ctytype(type_str: str) -> CtyType:
    type_str = type_str.strip()

    if type_str.lower() == "string":
        return CtyString()
    if type_str.lower() == "number":
        return CtyNumber()
    if type_str.lower() == "bool":
        return CtyBool()
    if type_str.lower() == "dynamic":
        return CtyDynamic()

    m = re.match(r"^\s*(list|set|map)\s*\((.*)\)\s*$", type_str, re.IGNORECASE)
    if m:
        keyword = m.group(1).lower()
        content = m.group(2).strip()
        if not content:
            raise CtyTypeParseError(f"Missing content for {keyword} type: '{type_str}'")

        element_type = parse_type_string_to_ctytype(content)
        if keyword == "list":
            return CtyList(element_type=element_type)
        if keyword == "set":
            return CtySet(element_type=element_type)
        if keyword == "map":  # Default key_type is CtyString
            return CtyMap(key_type=CtyString(), value_type=element_type)

    m_obj = re.match(r"^\s*object\s*\(\s*\{(.*)\}\s*\)\s*$", type_str, re.IGNORECASE)
    if m_obj:
        attrs_str = m_obj.group(1).strip()
        if not attrs_str:
            return CtyObject({})
        attributes = {}
        attr_pairs = _split_by_delimiter_respecting_nesting(attrs_str, ",")

        for pair_str in attr_pairs:
            pair = pair_str.strip()
            if not pair:  # Skip empty parts that might result from trailing commas
                continue
            if "=" not in pair:
                raise CtyTypeParseError(
                    f"Invalid attribute format in object string: '{pair}' in '{attrs_str}'"
                )
            name, attr_type_str = pair.split("=", 1)
            name = name.strip()
            if not name:
                raise CtyTypeParseError(
                    f"Empty attribute name in object string: '{attrs_str}'"
                )
            if not attr_type_str.strip():
                raise CtyTypeParseError(
                    f"Empty attribute type string for attribute '{name}' in '{attrs_str}'"
                )
            attributes[name] = parse_type_string_to_ctytype(attr_type_str.strip())
        return CtyObject(attributes)

    m_tuple = re.match(r"^\s*tuple\s*\(\s*\[(.*)\]\s*\)\s*$", type_str, re.IGNORECASE)
    if m_tuple:
        elems_str = m_tuple.group(1).strip()
        if not elems_str:
            return CtyTuple(element_types=tuple())
        element_types_str = _split_by_delimiter_respecting_nesting(elems_str, ",")

        element_types = []
        for s_raw in element_types_str:
            s_stripped = s_raw.strip()
            if not s_stripped:
                # If original elems_str was "string," -> split gives ['string', ''] -> s_stripped becomes '' -> error
                # If original elems_str was "string, , number" -> split gives ['string', '', 'number'] -> error on ''
                raise CtyTypeParseError(
                    f"Empty type string found in tuple elements: '{elems_str}'"
                )
            element_types.append(parse_type_string_to_ctytype(s_stripped))

        if (
            not element_types and elems_str
        ):  # Handles cases like "tuple([,])" which results in only empty strings
            raise CtyTypeParseError(
                f"Tuple definition contains only empty elements: '{elems_str}'"
            )

        return CtyTuple(element_types=tuple(element_types))

    raise CtyTypeParseError(f"Unknown or invalid CTY type string: {type_str}")


# 🐍📦🔒
