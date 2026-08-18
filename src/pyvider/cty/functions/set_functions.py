#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/set.go`."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any, cast

from pyvider.cty import CtyBool, CtyDynamic, CtySet, CtyType, CtyValue
from pyvider.cty.config.defaults import (
    ERR_SET_OP_ARG_MUST_BE_SET,
    ERR_SET_OP_INCOMPATIBLE_ELEMENTS,
)
from pyvider.cty.conversion import convert, unify
from pyvider.cty.exceptions import CtyConversionError, CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, TypeFunc, refine_not_null

# go-cty's `cty.Set(cty.DynamicPseudoType)`, the declared type of every set
# parameter in `set.go`. Built once: a parameter's type is read on every call.
_SET_OF_ANY = CtySet(element_type=CtyDynamic())


def _set_operation_return_type(func: str) -> TypeFunc:
    """go-cty's `setOperationReturnType` (`stdlib/set.go:173`), named per function.

    go-cty shares one callback between the four operations and so its error
    carries no function name; the constant here takes one, because every other
    message this package raises does.
    """

    def type_func(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
        element_types: list[CtyType[Any]] = []
        for arg in args:
            if not isinstance(arg.type, CtySet):
                # Only `cty.DynamicVal` reaches here, because every parameter
                # declares `AllowDynamicType` and so a value of undecided type
                # passes the conformance check. go-cty then calls
                # `Type.ElementType()` on `DynamicPseudoType`, which panics, and
                # its framework recovers that into an ordinary error
                # (`function.go:226`): the oracle answers `panic in function
                # implementation: not a collection type`. Refused here in the
                # words this package already uses for the same refusal.
                raise CtyFunctionError(ERR_SET_OP_ARG_MUST_BE_SET.format(func=func, type=arg.type.ctype))

            element_type = arg.type.element_type
            # An empty set of dynamic converts to any concrete set type, so
            # letting it into unification would drag every result down to
            # dynamic. Unknown-ness is checked first because `arg` may be
            # unknown here even though no parameter allows it -- a return type
            # has to be computable before the values are.
            if not arg.is_unknown and not arg.value and isinstance(element_type, CtyDynamic):
                continue
            element_types.append(element_type)

        # Every element type was skipped, so the result is a set of dynamic too.
        if not element_types:
            return _SET_OF_ANY

        # go-cty's `UnifyUnsafe` refuses the call when the element types have
        # nothing in common -- `setunion(set(number), set(bool))` is an error
        # there. It used to be a `set(dynamic)` here, because `unify` answered
        # dynamic both for "these unify to dynamic" and for "these do not unify".
        unified = unify(element_types)
        if unified is None:
            raise CtyFunctionError(ERR_SET_OP_INCOMPATIBLE_ELEMENTS.format(func=func))
        return CtySet(element_type=unified)

    return type_func


def _as_set_of(value: CtyValue[Any], element_type: CtyType[Any], func: str) -> frozenset[CtyValue[Any]]:
    """The argument's elements, converted to the result's element type.

    go-cty converts the whole argument to the result *set* type in one step
    (`stdlib/set.go:203`); element-wise is the same conversion, and it is the
    one this package's `convert` is shaped for.
    """
    elements = cast(Iterable[CtyValue[Any]], value.value or ())
    if cast(CtySet[Any], value.type).element_type.equal(element_type):
        return frozenset(elements)
    try:
        return frozenset(convert(element, element_type) for element in elements)
    except CtyConversionError as e:
        raise CtyFunctionError(ERR_SET_OP_INCOMPATIBLE_ELEMENTS.format(func=func)) from e


def _ordered_elements(value: CtyValue[Any], element_type: CtyType[Any], func: str) -> list[CtyValue[Any]]:
    """`_as_set_of` without the frozenset, so element order is the caller's.

    The set semantics are applied by CtySet.validate, which is the only place
    that knows two unknowns are not interchangeable.
    """
    elements = cast(Iterable[CtyValue[Any]], value.value or ())
    if cast(CtySet[Any], value.type).element_type.equal(element_type):
        return list(elements)
    try:
        return [convert(element, element_type) for element in elements]
    except CtyConversionError as e:
        raise CtyFunctionError(ERR_SET_OP_INCOMPATIBLE_ELEMENTS.format(func=func)) from e


def _set_operation(
    func: str,
    combine: Callable[[frozenset[CtyValue[Any]], frozenset[CtyValue[Any]]], frozenset[CtyValue[Any]]],
    args: Sequence[CtyValue[Any]],
    return_type: CtyType[Any],
    *,
    allow_unknowns: bool,
) -> CtyValue[Any]:
    """go-cty's `setOperationImpl` (`stdlib/set.go:200`).

    `allow_unknowns` is true only for union. Everywhere else an unknown element
    makes the answer unknowable rather than merely imprecise: learning what it
    is can remove elements from the result, or change the result's length, so
    no partial answer is safe to give.
    """
    element_type = cast(CtySet[Any], return_type).element_type

    if not allow_unknowns and not all(arg.is_wholly_known() for arg in args):
        return CtyValue.unknown(return_type)

    if allow_unknowns:
        # Union is the only operation that admits unknown elements, and a Python
        # frozenset is the wrong container for them twice over.
        #
        # It de-duplicates through CtyValue.__eq__/__hash__, under which any two
        # unknowns of a type are the same object -- so `setunion` collapsed
        # distinct unknowns that CtySet.validate deliberately keeps apart, and a
        # for_each derived from a union came out short. go-cty keeps them: a set
        # built from ["a", unknown, unknown] encodes three elements.
        #
        # It also iterates in an order derived from PYTHONHASHSEED, and because
        # every unknown ties at rank 1 in the canonical sort, that order survived
        # into the element tuple and out onto the wire. Six single-element sets
        # unioned under four seeds produced four different msgpack payloads,
        # where go-cty is deterministic run to run -- a plan diff that reappears
        # in a new shape after every provider restart.
        #
        # Concatenating in argument order and letting validate do the work is
        # both correct and deterministic: it de-duplicates knowns by canonical
        # key and preserves every unknown in the order supplied.
        merged: list[CtyValue[Any]] = []
        for arg in args:
            merged.extend(_ordered_elements(arg, element_type, func))
        return return_type.validate(merged)

    combined = _as_set_of(args[0], element_type, func)
    for arg in args[1:]:
        combined = combine(combined, _as_set_of(arg, element_type, func))
    return return_type.validate(list(combined))


@stdlib_function(
    "setunion",
    params=[CtyParameter("first_set", _SET_OF_ANY, allow_dynamic_type=True)],
    var_param=CtyParameter("other_sets", _SET_OF_ANY, allow_dynamic_type=True),
    type_func=_set_operation_return_type("setunion"),
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Returns the union of all given sets.",
)
def setunion(*args: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `SetUnionFunc` (`stdlib/set.go:33`)."""
    return _set_operation("setunion", lambda a, b: a | b, args, return_type, allow_unknowns=True)


@stdlib_function(
    "setintersection",
    params=[CtyParameter("first_set", _SET_OF_ANY, allow_dynamic_type=True)],
    var_param=CtyParameter("other_sets", _SET_OF_ANY, allow_dynamic_type=True),
    type_func=_set_operation_return_type("setintersection"),
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Returns the intersection of all given sets.",
)
def setintersection(*args: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `SetIntersectionFunc` (`stdlib/set.go:54`)."""
    return _set_operation("setintersection", lambda a, b: a & b, args, return_type, allow_unknowns=False)


@stdlib_function(
    "setsubtract",
    params=[
        CtyParameter("a", _SET_OF_ANY, allow_dynamic_type=True),
        CtyParameter("b", _SET_OF_ANY, allow_dynamic_type=True),
    ],
    type_func=_set_operation_return_type("setsubtract"),
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Returns the relative complement of the two given sets.",
)
def setsubtract(a: CtyValue[Any], b: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `SetSubtractFunc` (`stdlib/set.go:75`).

    The only one of the four that is not variadic: `set.go` gives it two fixed
    parameters and no `VarParam`, so a third argument is an arity error rather
    than a third set to subtract.
    """
    return _set_operation("setsubtract", lambda x, y: x - y, (a, b), return_type, allow_unknowns=False)


@stdlib_function(
    "setsymmetricdifference",
    params=[CtyParameter("first_set", _SET_OF_ANY, allow_dynamic_type=True)],
    var_param=CtyParameter("other_sets", _SET_OF_ANY, allow_dynamic_type=True),
    type_func=_set_operation_return_type("setsymmetricdifference"),
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Returns the symmetric difference of the two given sets.",
)
def setsymmetricdifference(*args: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `SetSymmetricDifferenceFunc` (`stdlib/set.go:96`)."""
    return _set_operation(
        "setsymmetricdifference", lambda a, b: a ^ b, args, return_type, allow_unknowns=False
    )


@stdlib_function(
    "sethaselement",
    params=[
        CtyParameter("set", _SET_OF_ANY, allow_dynamic_type=True),
        CtyParameter("elem", CtyDynamic(), allow_dynamic_type=True),
    ],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Returns true if the given set contains the given element, or false otherwise.",
)
def sethaselement(collection: CtyValue[Any], element: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SetHasElementFunc` (`stdlib/set.go:12`).

    Its whole body is `args[0].HasElement(args[1])` (`value_ops.go:1050`), which
    is transcribed here rather than routed through `contains`: the two answer
    different questions. `contains` is `ContainsFunc` and accepts a list or a
    tuple as well; this one accepts only a set, and settles a mismatched element
    type as a definite *absence* rather than an error, because a set cannot hold
    an element of any type but its own (`value_ops.go:1088`).
    """
    element_type = cast(CtySet[Any], collection.type).element_type
    if not element_type.equal(element.type):
        return cast(CtyValue[Any], CtyBool().validate(False))

    if element in cast(Iterable[CtyValue[Any]], collection.value or ()):
        # A hit cannot be un-hit by whatever any unknown element turns out to be.
        return cast(CtyValue[Any], CtyBool().validate(True))
    if not collection.is_wholly_known():
        # A miss against a set holding an unknown is undecided rather than
        # false: the unknown could still turn out to be the element asked about.
        return CtyValue.unknown(CtyBool())
    return cast(CtyValue[Any], CtyBool().validate(False))


# 🌊🪢🔚
