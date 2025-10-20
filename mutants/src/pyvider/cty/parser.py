# pyvider/cty/parser.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from provide.foundation.errors import error_boundary

from pyvider.cty.config.defaults import (
    TYPE_KIND_LIST,
    TYPE_KIND_MAP,
    TYPE_KIND_SET,
)
from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types import (
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

# pyvider-cty/src/pyvider/cty/parser.py
"""
Contains logic for parsing Terraform's JSON-based type constraint strings
into the framework's internal CtyType objects.
"""
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_parse_tf_type_to_ctytype__mutmut_orig(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_1(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context=None
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_2(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "XXoperationXX": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_3(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "OPERATION": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_4(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "XXterraform_type_parsingXX",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_5(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "TERRAFORM_TYPE_PARSING",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_6(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "XXtf_typeXX": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_7(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "TF_TYPE": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_8(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(None),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_9(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "XXtf_type_python_typeXX": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_10(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "TF_TYPE_PYTHON_TYPE": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_11(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(None).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_12(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_13(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "bool":
                    return CtyBool()
                case "dynamic":
                    return CtyDynamic()
                case _:
                    raise CtyValidationError(f"Unknown primitive type name: '{tf_type}'")

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_14(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "number":
                    return CtyNumber()
                case "dynamic":
                    return CtyDynamic()
                case _:
                    raise CtyValidationError(f"Unknown primitive type name: '{tf_type}'")

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_15(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "number":
                    return CtyNumber()
                case "bool":
                    return CtyBool()
                case _:
                    raise CtyValidationError(f"Unknown primitive type name: '{tf_type}'")

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_16(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_17(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "XXstringXX":
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_18(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "STRING":
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_19(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "XXnumberXX":
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_20(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "NUMBER":
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_21(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "number":
                    return CtyNumber()
                case "XXboolXX":
                    return CtyBool()
                case "dynamic":
                    return CtyDynamic()
                case _:
                    raise CtyValidationError(f"Unknown primitive type name: '{tf_type}'")

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_22(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "number":
                    return CtyNumber()
                case "BOOL":
                    return CtyBool()
                case "dynamic":
                    return CtyDynamic()
                case _:
                    raise CtyValidationError(f"Unknown primitive type name: '{tf_type}'")

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_23(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "number":
                    return CtyNumber()
                case "bool":
                    return CtyBool()
                case "XXdynamicXX":
                    return CtyDynamic()
                case _:
                    raise CtyValidationError(f"Unknown primitive type name: '{tf_type}'")

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_24(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
        if isinstance(tf_type, str):
            match tf_type:
                case "string":
                    return CtyString()
                case "number":
                    return CtyNumber()
                case "bool":
                    return CtyBool()
                case "DYNAMIC":
                    return CtyDynamic()
                case _:
                    raise CtyValidationError(f"Unknown primitive type name: '{tf_type}'")

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_25(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
                    raise CtyValidationError(None)

        if isinstance(tf_type, list) and len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_26(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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

        if isinstance(tf_type, list) or len(tf_type) == 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_27(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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

        if isinstance(tf_type, list) and len(tf_type) != 2:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_28(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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

        if isinstance(tf_type, list) and len(tf_type) == 3:
            type_kind, type_spec = tf_type

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_29(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            type_kind, type_spec = None

            # Handle collection types where the spec is a single type
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_30(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind not in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_31(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = None
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_32(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(None)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_33(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_34(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_35(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_36(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "XXlistXX":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_37(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "LIST":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_38(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=None)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_39(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "XXsetXX":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_40(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "SET":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_41(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=None)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_42(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "XXmapXX":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_43(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "MAP":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_44(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=None)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_45(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_46(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_47(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "XXobjectXX":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_48(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "OBJECT":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_49(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_50(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            None
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_51(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(None).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_52(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = None
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_53(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(None) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_54(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=None)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_55(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "XXtupleXX":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_56(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "TUPLE":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_57(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_58(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            None
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_59(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(None).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_60(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = None
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_61(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(None)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_62(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(None) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_63(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=None)

        raise CtyValidationError(f"Invalid Terraform type specification: {tf_type}")


def x_parse_tf_type_to_ctytype__mutmut_64(tf_type: Any) -> CtyType[Any]:  # noqa: C901
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    with error_boundary(
        context={
            "operation": "terraform_type_parsing",
            "tf_type": str(tf_type),
            "tf_type_python_type": type(tf_type).__name__,
        }
    ):
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
            if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
                element_type = parse_tf_type_to_ctytype(type_spec)
                match type_kind:
                    case "list":
                        return CtyList(element_type=element_type)
                    case "set":
                        return CtySet(element_type=element_type)
                    case "map":
                        return CtyMap(element_type=element_type)

            # Handle structural types where the spec is a container
            match type_kind:
                case "object":
                    if not isinstance(type_spec, dict):
                        raise CtyValidationError(
                            f"Object type spec must be a dictionary, got {type(type_spec).__name__}"
                        )
                    attr_types = {name: parse_tf_type_to_ctytype(spec) for name, spec in type_spec.items()}
                    return CtyObject(attribute_types=attr_types)
                case "tuple":
                    if not isinstance(type_spec, list):
                        raise CtyValidationError(
                            f"Tuple type spec must be a list, got {type(type_spec).__name__}"
                        )
                    elem_types = tuple(parse_tf_type_to_ctytype(spec) for spec in type_spec)
                    return CtyTuple(element_types=elem_types)

        raise CtyValidationError(None)

x_parse_tf_type_to_ctytype__mutmut_mutants : ClassVar[MutantDict] = {
'x_parse_tf_type_to_ctytype__mutmut_1': x_parse_tf_type_to_ctytype__mutmut_1, 
    'x_parse_tf_type_to_ctytype__mutmut_2': x_parse_tf_type_to_ctytype__mutmut_2, 
    'x_parse_tf_type_to_ctytype__mutmut_3': x_parse_tf_type_to_ctytype__mutmut_3, 
    'x_parse_tf_type_to_ctytype__mutmut_4': x_parse_tf_type_to_ctytype__mutmut_4, 
    'x_parse_tf_type_to_ctytype__mutmut_5': x_parse_tf_type_to_ctytype__mutmut_5, 
    'x_parse_tf_type_to_ctytype__mutmut_6': x_parse_tf_type_to_ctytype__mutmut_6, 
    'x_parse_tf_type_to_ctytype__mutmut_7': x_parse_tf_type_to_ctytype__mutmut_7, 
    'x_parse_tf_type_to_ctytype__mutmut_8': x_parse_tf_type_to_ctytype__mutmut_8, 
    'x_parse_tf_type_to_ctytype__mutmut_9': x_parse_tf_type_to_ctytype__mutmut_9, 
    'x_parse_tf_type_to_ctytype__mutmut_10': x_parse_tf_type_to_ctytype__mutmut_10, 
    'x_parse_tf_type_to_ctytype__mutmut_11': x_parse_tf_type_to_ctytype__mutmut_11, 
    'x_parse_tf_type_to_ctytype__mutmut_12': x_parse_tf_type_to_ctytype__mutmut_12, 
    'x_parse_tf_type_to_ctytype__mutmut_13': x_parse_tf_type_to_ctytype__mutmut_13, 
    'x_parse_tf_type_to_ctytype__mutmut_14': x_parse_tf_type_to_ctytype__mutmut_14, 
    'x_parse_tf_type_to_ctytype__mutmut_15': x_parse_tf_type_to_ctytype__mutmut_15, 
    'x_parse_tf_type_to_ctytype__mutmut_16': x_parse_tf_type_to_ctytype__mutmut_16, 
    'x_parse_tf_type_to_ctytype__mutmut_17': x_parse_tf_type_to_ctytype__mutmut_17, 
    'x_parse_tf_type_to_ctytype__mutmut_18': x_parse_tf_type_to_ctytype__mutmut_18, 
    'x_parse_tf_type_to_ctytype__mutmut_19': x_parse_tf_type_to_ctytype__mutmut_19, 
    'x_parse_tf_type_to_ctytype__mutmut_20': x_parse_tf_type_to_ctytype__mutmut_20, 
    'x_parse_tf_type_to_ctytype__mutmut_21': x_parse_tf_type_to_ctytype__mutmut_21, 
    'x_parse_tf_type_to_ctytype__mutmut_22': x_parse_tf_type_to_ctytype__mutmut_22, 
    'x_parse_tf_type_to_ctytype__mutmut_23': x_parse_tf_type_to_ctytype__mutmut_23, 
    'x_parse_tf_type_to_ctytype__mutmut_24': x_parse_tf_type_to_ctytype__mutmut_24, 
    'x_parse_tf_type_to_ctytype__mutmut_25': x_parse_tf_type_to_ctytype__mutmut_25, 
    'x_parse_tf_type_to_ctytype__mutmut_26': x_parse_tf_type_to_ctytype__mutmut_26, 
    'x_parse_tf_type_to_ctytype__mutmut_27': x_parse_tf_type_to_ctytype__mutmut_27, 
    'x_parse_tf_type_to_ctytype__mutmut_28': x_parse_tf_type_to_ctytype__mutmut_28, 
    'x_parse_tf_type_to_ctytype__mutmut_29': x_parse_tf_type_to_ctytype__mutmut_29, 
    'x_parse_tf_type_to_ctytype__mutmut_30': x_parse_tf_type_to_ctytype__mutmut_30, 
    'x_parse_tf_type_to_ctytype__mutmut_31': x_parse_tf_type_to_ctytype__mutmut_31, 
    'x_parse_tf_type_to_ctytype__mutmut_32': x_parse_tf_type_to_ctytype__mutmut_32, 
    'x_parse_tf_type_to_ctytype__mutmut_33': x_parse_tf_type_to_ctytype__mutmut_33, 
    'x_parse_tf_type_to_ctytype__mutmut_34': x_parse_tf_type_to_ctytype__mutmut_34, 
    'x_parse_tf_type_to_ctytype__mutmut_35': x_parse_tf_type_to_ctytype__mutmut_35, 
    'x_parse_tf_type_to_ctytype__mutmut_36': x_parse_tf_type_to_ctytype__mutmut_36, 
    'x_parse_tf_type_to_ctytype__mutmut_37': x_parse_tf_type_to_ctytype__mutmut_37, 
    'x_parse_tf_type_to_ctytype__mutmut_38': x_parse_tf_type_to_ctytype__mutmut_38, 
    'x_parse_tf_type_to_ctytype__mutmut_39': x_parse_tf_type_to_ctytype__mutmut_39, 
    'x_parse_tf_type_to_ctytype__mutmut_40': x_parse_tf_type_to_ctytype__mutmut_40, 
    'x_parse_tf_type_to_ctytype__mutmut_41': x_parse_tf_type_to_ctytype__mutmut_41, 
    'x_parse_tf_type_to_ctytype__mutmut_42': x_parse_tf_type_to_ctytype__mutmut_42, 
    'x_parse_tf_type_to_ctytype__mutmut_43': x_parse_tf_type_to_ctytype__mutmut_43, 
    'x_parse_tf_type_to_ctytype__mutmut_44': x_parse_tf_type_to_ctytype__mutmut_44, 
    'x_parse_tf_type_to_ctytype__mutmut_45': x_parse_tf_type_to_ctytype__mutmut_45, 
    'x_parse_tf_type_to_ctytype__mutmut_46': x_parse_tf_type_to_ctytype__mutmut_46, 
    'x_parse_tf_type_to_ctytype__mutmut_47': x_parse_tf_type_to_ctytype__mutmut_47, 
    'x_parse_tf_type_to_ctytype__mutmut_48': x_parse_tf_type_to_ctytype__mutmut_48, 
    'x_parse_tf_type_to_ctytype__mutmut_49': x_parse_tf_type_to_ctytype__mutmut_49, 
    'x_parse_tf_type_to_ctytype__mutmut_50': x_parse_tf_type_to_ctytype__mutmut_50, 
    'x_parse_tf_type_to_ctytype__mutmut_51': x_parse_tf_type_to_ctytype__mutmut_51, 
    'x_parse_tf_type_to_ctytype__mutmut_52': x_parse_tf_type_to_ctytype__mutmut_52, 
    'x_parse_tf_type_to_ctytype__mutmut_53': x_parse_tf_type_to_ctytype__mutmut_53, 
    'x_parse_tf_type_to_ctytype__mutmut_54': x_parse_tf_type_to_ctytype__mutmut_54, 
    'x_parse_tf_type_to_ctytype__mutmut_55': x_parse_tf_type_to_ctytype__mutmut_55, 
    'x_parse_tf_type_to_ctytype__mutmut_56': x_parse_tf_type_to_ctytype__mutmut_56, 
    'x_parse_tf_type_to_ctytype__mutmut_57': x_parse_tf_type_to_ctytype__mutmut_57, 
    'x_parse_tf_type_to_ctytype__mutmut_58': x_parse_tf_type_to_ctytype__mutmut_58, 
    'x_parse_tf_type_to_ctytype__mutmut_59': x_parse_tf_type_to_ctytype__mutmut_59, 
    'x_parse_tf_type_to_ctytype__mutmut_60': x_parse_tf_type_to_ctytype__mutmut_60, 
    'x_parse_tf_type_to_ctytype__mutmut_61': x_parse_tf_type_to_ctytype__mutmut_61, 
    'x_parse_tf_type_to_ctytype__mutmut_62': x_parse_tf_type_to_ctytype__mutmut_62, 
    'x_parse_tf_type_to_ctytype__mutmut_63': x_parse_tf_type_to_ctytype__mutmut_63, 
    'x_parse_tf_type_to_ctytype__mutmut_64': x_parse_tf_type_to_ctytype__mutmut_64
}

def parse_tf_type_to_ctytype(*args, **kwargs):
    result = _mutmut_trampoline(x_parse_tf_type_to_ctytype__mutmut_orig, x_parse_tf_type_to_ctytype__mutmut_mutants, args, kwargs)
    return result 

parse_tf_type_to_ctytype.__signature__ = _mutmut_signature(x_parse_tf_type_to_ctytype__mutmut_orig)
x_parse_tf_type_to_ctytype__mutmut_orig.__name__ = 'x_parse_tf_type_to_ctytype'


# Alias for backward compatibility if needed, though direct use is preferred.
parse_type_string_to_ctytype = parse_tf_type_to_ctytype
# 🌊🪢🧩🪄
