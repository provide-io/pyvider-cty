#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/set.go`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, cast

from pyvider.cty import CtyDynamic, CtySet, CtyType, CtyValue
from pyvider.cty.config.defaults import (
    ERR_SET_OP_ARG_MUST_BE_SET,
    ERR_SET_OP_INCOMPATIBLE_ELEMENTS,
    ERR_SET_OP_REQUIRES_ONE_SET,
)
from pyvider.cty.conversion import convert, unify
from pyvider.cty.exceptions import CtyConversionError, CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function


def _set_arg(value: CtyValue[Any], func: str) -> CtyValue[Any]:
    inner = value
    while isinstance(inner.type, CtyDynamic) and isinstance(inner.value, CtyValue):
        inner = inner.value
    if not isinstance(inner.type, CtySet):
        raise CtyFunctionError(ERR_SET_OP_ARG_MUST_BE_SET.format(func=func, type=inner.type.ctype))
    return inner


def _result_element_type(args: list[CtyValue[Any]], func: str) -> CtyType[Any]:
    """go-cty's `setOperationReturnType`, minus its return-type wrapper."""
    element_types: list[CtyType[Any]] = []
    for arg in args:
        element_type = cast(CtySet[Any], arg.type).element_type
        # An empty set of dynamic converts to any concrete set type, so letting
        # it into unification would drag every result down to dynamic.
        if not arg.is_unknown and not arg.is_null and not arg.value and isinstance(element_type, CtyDynamic):
            continue
        element_types.append(element_type)

    if not element_types:
        return CtyDynamic()
    if all(element_type.equal(element_types[0]) for element_type in element_types):
        return element_types[0]

    # go-cty unifies with `convert.UnifyUnsafe`, which widens a mixture of
    # primitives to string. This package's `unify` has no such rule and answers
    # dynamic instead, so a mixed-element result is a set of dynamic here and a
    # set of string there. Recorded as a divergence and pinned in the sweep,
    # rather than fixed by changing `unify` under everything else that calls it.
    return unify(element_types)


def _as_set_of(value: CtyValue[Any], element_type: CtyType[Any], func: str) -> frozenset[CtyValue[Any]]:
    """The argument's elements, converted to the result's element type."""
    elements = cast(Iterable[CtyValue[Any]], value.value or ())
    if cast(CtySet[Any], value.type).element_type.equal(element_type):
        return frozenset(elements)
    try:
        return frozenset(convert(element, element_type) for element in elements)
    except CtyConversionError as e:
        raise CtyFunctionError(ERR_SET_OP_INCOMPATIBLE_ELEMENTS.format(func=func)) from e


def _set_operation(
    func: str,
    combine: Callable[[frozenset[CtyValue[Any]], frozenset[CtyValue[Any]]], frozenset[CtyValue[Any]]],
    args: tuple[CtyValue[Any], ...],
    *,
    allow_unknowns: bool,
) -> CtyValue[Any]:
    """go-cty's `setOperationImpl`.

    `allow_unknowns` is true only for union. Everywhere else an unknown element
    makes the answer unknowable rather than merely imprecise: learning what it
    is can remove elements from the result, or change the result's length, so
    no partial answer is safe to give.
    """
    if not args:
        raise CtyFunctionError(ERR_SET_OP_REQUIRES_ONE_SET.format(func=func))

    sets = [_set_arg(arg, func) for arg in args]
    element_type = _result_element_type(sets, func)
    result_type = CtySet(element_type=element_type)

    if not allow_unknowns and not all(arg.is_wholly_known() for arg in sets):
        return CtyValue.unknown(result_type)

    combined = _as_set_of(sets[0], element_type, func)
    for arg in sets[1:]:
        combined = combine(combined, _as_set_of(arg, element_type, func))
    return cast(CtyValue[Any], result_type.validate(list(combined)))


@stdlib_function("setunion")
def setunion(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SetUnionFunc`."""
    return _set_operation("setunion", lambda a, b: a | b, args, allow_unknowns=True)


@stdlib_function("setintersection")
def setintersection(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SetIntersectionFunc`."""
    return _set_operation("setintersection", lambda a, b: a & b, args, allow_unknowns=False)


@stdlib_function("setsubtract")
def setsubtract(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SetSubtractFunc`. Takes exactly two sets."""
    return _set_operation("setsubtract", lambda a, b: a - b, args, allow_unknowns=False)


@stdlib_function("setsymmetricdifference")
def setsymmetricdifference(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SetSymmetricDifferenceFunc`."""
    return _set_operation("setsymmetricdifference", lambda a, b: a ^ b, args, allow_unknowns=False)


@stdlib_function("sethaselement")
def sethaselement(collection: CtyValue[Any], element: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SetHasElementFunc`.

    Routed through `contains`, which already carries the three-valued answer an
    unknown element demands.
    """
    from pyvider.cty.functions.collection_functions import contains

    _set_arg(collection, "sethaselement")
    return contains(collection, element)


# 🌊🪢🔚
