# pyvider-cty/src/pyvider/cty/parser.py
"""
Contains logic for parsing Terraform's JSON-based type constraint strings
into the framework's internal CtyType objects.
"""

from typing import Any

from .exceptions import CtyValidationError
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
    CtyType,
)


def parse_tf_type_to_ctytype(tf_type: Any) -> "CtyType[Any]":  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    if isinstance(tf_type, str):
        match tf_type:
            case "string":
                return CtyString()
            case "number":
                return CtyNumber()
            case "bool":
                return CtyBool()
            case "dynamic":
                return CtyDynamic()
            case _:
                raise CtyValidationError(f"Unknown primitive type name: '{tf_type}'")

    if isinstance(tf_type, list) and len(tf_type) == 2:
        type_kind, type_spec = tf_type

        # Handle collection types where the spec is a single type
        if type_kind in ("list", "set", "map"):
            element_type = parse_tf_type_to_ctytype(type_spec)
            if type_kind == "list":
                return CtyList(element_type=element_type)
            if type_kind == "set":
                return CtySet(element_type=element_type)
            if type_kind == "map":
                return CtyMap(element_type=element_type)

        # Handle structural types where the spec is a container
        if type_kind == "object":
            if not isinstance(type_spec, dict):
                raise CtyValidationError(
                    f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                )
            attr_types = {
                name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()
            }
            return CtyObject(attribute_types=attr_types)

        if type_kind == "tuple":
            if not isinstance(type_spec, list):
                raise CtyValidationError(
                    f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                )
            elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
            return CtyTuple(element_types=elem_types)

    raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


# Alias for backward compatibility if needed, though direct use is preferred.
parse_type_string_to_ctytype = parse_tf_type_to_ctytype
