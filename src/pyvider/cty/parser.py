#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

import reprlib
from typing import Any

from pyvider.cty.config.defaults import (
    MAX_STRING_LENGTH_DISPLAY,
    MAX_TYPE_NESTING_DEPTH,
    TYPE_KIND_LIST,
    TYPE_KIND_MAP,
    TYPE_KIND_OBJECT,
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


# A type description arrives from a peer, so the diagnostic built from it is
# built from attacker-controlled data and has to be bounded before it is
# rendered. `reprlib` stops descending at `maxlevel` rather than rendering the
# whole tree and trimming afterwards, which is the difference between a bounded
# diagnostic and a linear one that is then thrown away.
_DIAGNOSTIC = reprlib.Repr()
_DIAGNOSTIC.maxlevel = 6
_DIAGNOSTIC.maxlist = 4
_DIAGNOSTIC.maxdict = 4
_DIAGNOSTIC.maxtuple = 4
_DIAGNOSTIC.maxstring = MAX_STRING_LENGTH_DISPLAY
_DIAGNOSTIC.maxother = MAX_STRING_LENGTH_DISPLAY


def parse_tf_type_to_ctytype(tf_type: Any) -> CtyType[Any]:
    """
    Parses a Terraform type constraint, represented as a raw Python object
    (typically from JSON), into a CtyType instance.
    """
    # No `error_boundary` here, and its absence is the fix rather than an
    # oversight. It wrapped the *recursive* function, so a description nested N
    # deep built N diagnostic contexts and each stringified the whole remaining
    # subtree -- quadratic, and paid on the way in, before anything was
    # validated: 1600 levels cost seventeen seconds.
    #
    # Hoisting it to a single entry here fixed that and left a worse problem.
    # The boundary logs with `exc_info=True`, and rendering that traceback walks
    # the frame locals -- which hold `tf_type` itself. On a 2000-level
    # description the render ran the interpreter out of stack and raised
    # `RecursionError`, replacing the `CtyValidationError` the depth budget had
    # correctly raised. A boundary that converts an in-taxonomy refusal into an
    # out-of-taxonomy crash, on exactly the input the budget exists to refuse,
    # is not a diagnostic worth keeping. Every failure below is already a
    # `CtyValidationError` carrying a bounded message.
    return _parse(tf_type, 0)


def _parse(tf_type: Any, depth: int) -> CtyType[Any]:  # noqa: C901
    """One level of the descent, counting how far down it has gone."""
    if depth > MAX_TYPE_NESTING_DEPTH:
        # A `CtyValidationError`, so a caller catching `CtyError` around its
        # decoding catches this too. Unbounded, the descent ran the interpreter
        # out of stack instead and raised a bare `RecursionError`.
        raise CtyValidationError(
            f"Type description nests deeper than {MAX_TYPE_NESTING_DEPTH} levels: {_DIAGNOSTIC.repr(tf_type)}"
        )
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
                # Bounded like the rest: the name is attacker-controlled text and
                # nothing caps its length before it reaches here.
                raise CtyValidationError(f"Unknown primitive type name: {_DIAGNOSTIC.repr(tf_type)}")

    # An object type may carry a third element: the names that may be omitted.
    # Accepting only the 2-element form rejects every type terraform sends back
    # for a schema that declares optional object attributes.
    if isinstance(tf_type, list) and len(tf_type) in (2, 3):
        type_kind, type_spec = tf_type[0], tf_type[1]
        # go-cty writes the third element for object types only. Before the
        # kind dispatch this check refused `["list", "string", "junk"]` with a
        # message about *object* optional names and let `["list", "string",
        # ["a"]]` through with the extra element silently dropped.
        if len(tf_type) == 3 and type_kind != TYPE_KIND_OBJECT:
            raise CtyValidationError(
                f"Type {type_kind!r} has a third element; only an object type carries a third element"
            )

        # Handle collection types where the spec is a single type
        if type_kind in (TYPE_KIND_LIST, TYPE_KIND_SET, TYPE_KIND_MAP):
            element_type = _parse(type_spec, depth + 1)
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
                optional_names = tf_type[2] if len(tf_type) == 3 else ()
                # go-cty decodes this element as `[]string`. Fed straight to
                # `frozenset`, the string "ab" became the two optional names a and b.
                if not isinstance(optional_names, list | tuple) or not all(
                    isinstance(n, str) for n in optional_names
                ):
                    raise CtyValidationError(
                        "Object optional attribute names must be a list of strings, got "
                        f"{_DIAGNOSTIC.repr(optional_names)}"
                    )
                attr_types = {name: _parse(spec, depth + 1) for name, spec in type_spec.items()}
                return CtyObject(
                    attribute_types=attr_types,
                    optional_attributes=frozenset(optional_names),
                )
            case "tuple":
                if not isinstance(type_spec, list):
                    raise CtyValidationError(f"Tuple type spec must be a list, got {type(type_spec).__name__}")
                elem_types = tuple(_parse(spec, depth + 1) for spec in type_spec)
                return CtyTuple(element_types=elem_types)

    raise CtyValidationError(f"Invalid Terraform type specification: {_DIAGNOSTIC.repr(tf_type)}")


# Alias for backward compatibility if needed, though direct use is preferred.
parse_type_string_to_ctytype = parse_tf_type_to_ctytype

# 🌊🪢🔚
