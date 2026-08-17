#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/conversion.go`."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pyvider.cty import CtyBool, CtyDynamic, CtyNumber, CtyString, CtyType, CtyValue
from pyvider.cty.config.defaults import ERR_CANNOT_CONVERT_TO_TYPE
from pyvider.cty.conversion import can_convert_unsafe, convert
from pyvider.cty.exceptions import CtyConversionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import (
    CtyArgumentError,
    CtyParameter,
    TypeFunc,
    refine_not_null,
)


def _value_param() -> CtyParameter:
    """`MakeToFunc`'s single parameter, the same for every target type.

    Declared `dynamic` rather than as the target type on purpose, and go-cty
    says why at `stdlib/conversion.go:26`: every value must reach the function
    verbatim so the refusal can be worded for an *explicit* conversion instead
    of borrowing the function framework's wording for an implicit one. Deciding
    whether the conversion exists therefore moves into `Type`, below.

    `AllowNull` is local to this factory rather than a framework-wide decision:
    a null converts, and converting it is the point -- `tostring(null)` is still
    nothing, now typed as a string. `AllowUnknown` is absent, so an unknown
    short-circuits to an unknown of the target type without reaching `convert`.
    """
    return CtyParameter("v", CtyDynamic(), allow_null=True, allow_dynamic_type=True)


def _target_type(target: CtyType[Any], func: str) -> TypeFunc:
    """`MakeToFunc`'s `Type` callback, bound to one target type.

    This is what makes `MakeToFunc` a factory: the return type *and* the
    admissibility check both depend on `wantTy`, so go-cty closes over it rather
    than declaring three near-identical specs (`stdlib/conversion.go:38`).

    The question asked is the *unsafe* one, so a conversion admitted here can
    still fail on the value: `tonumber("abc")` type-checks as a number and is
    then refused by `convert`, which is the behaviour go-cty documents at
    `:63`.
    """

    def type_func(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
        got = args[0].type
        if not got.equal(target) and not can_convert_unsafe(got, target):
            raise CtyArgumentError(
                0,
                ERR_CANNOT_CONVERT_TO_TYPE.format(func=func, type=got.ctype, target=target.ctype),
            )
        return target

    return type_func


def _to(value: CtyValue[Any], target: CtyType[Any], func: str) -> CtyValue[Any]:
    """`MakeToFunc`'s `Impl`, which is one call to `convert` and a refusal.

    The conversion is `convert`'s, not a hand-rolled one. `tostring` used to end
    in `str(input_val.value)` for anything it did not recognise, and the payload
    of a collection is its internal tuple of CtyValues, so `tostring(["a"])`
    returned the text of a repr -- a plausible string headed for state. The rule
    for what converts to what belongs in one place, and that place is `convert`.
    """
    try:
        return convert(value, target)
    except CtyConversionError as e:
        raise CtyArgumentError(
            0,
            ERR_CANNOT_CONVERT_TO_TYPE.format(func=func, type=value.type.ctype, target=target.ctype),
        ) from e


@stdlib_function(
    "tostring",
    params=[_value_param()],
    type_func=_target_type(CtyString(), "tostring"),
    description="Converts the given value to string, or raises an error if that conversion is impossible.",
)
def to_string(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MakeToFunc(cty.String)` (`stdlib/conversion.go:20`)."""
    return _to(input_val, CtyString(), "tostring")


@stdlib_function(
    "tonumber",
    params=[_value_param()],
    type_func=_target_type(CtyNumber(), "tonumber"),
    description="Converts the given value to number, or raises an error if that conversion is impossible.",
)
def to_number(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MakeToFunc(cty.Number)` (`stdlib/conversion.go:20`)."""
    return _to(input_val, CtyNumber(), "tonumber")


@stdlib_function(
    "tobool",
    params=[_value_param()],
    type_func=_target_type(CtyBool(), "tobool"),
    description="Converts the given value to bool, or raises an error if that conversion is impossible.",
)
def to_bool(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MakeToFunc(cty.Bool)` (`stdlib/conversion.go:20`)."""
    return _to(input_val, CtyBool(), "tobool")


def _same_type(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
    """go-cty's `AssertNotNullFunc.Type`: whatever came in (`conversion.go:110`)."""
    return args[0].type


@stdlib_function(
    "assertnotnull",
    params=[CtyParameter("v", CtyDynamic())],
    type_func=_same_type,
    refine_result=refine_not_null,
    description="Returns the given value varbatim if it is non-null, or raises an error if it's null.",
)
def assertnotnull(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """Return the value unchanged, having established that it is not null.

    The body is the whole implementation in go-cty too (`conversion.go:114`).
    Its parameter deliberately sets *none* of the permissive flags, and go-cty's
    own comment at `:105` says why for the first of them: the framework rejects
    a null before `Impl` is ever reached, so the check is the declaration rather
    than code.

    Withholding `AllowUnknown` is what the function is *for*. An unknown
    argument short-circuits to an unknown of the same type carrying
    `RefineResult`'s not-null claim, which is the whole point: a downstream
    comparison against null can then answer definitely even though the value
    itself is still undecided. This package returned the argument untouched, so
    the refinement -- the only observable effect the function has on an unknown
    -- was missing.

    The typo in the description is go-cty's, copied verbatim.
    """
    return input_val


# 🌊🪢🔚
