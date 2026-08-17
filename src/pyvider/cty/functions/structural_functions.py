#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `CoalesceFunc` (`cty/function/stdlib/general.go:61`)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pyvider.cty import CtyDynamic, CtyType, CtyValue
from pyvider.cty.conversion import convert, unify
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null


def _unified_type(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
    """The one type every argument can convert to. go-cty's `CoalesceFunc.Type`.

    `UnifyUnsafe` over the argument types, and a refusal when they have no
    common type (`stdlib/general.go:71`). This is also the answer for no
    arguments at all: `unify` of nothing is nothing, so `coalesce()` is refused
    here rather than by an arity check, which is why go-cty's message for it
    talks about types.
    """
    unified = unify([arg.type for arg in args])
    if unified is None:
        raise CtyFunctionError("all arguments must have the same type")
    return unified


@stdlib_function(
    "coalesce",
    var_param=CtyParameter(
        "vals",
        CtyDynamic(),
        allow_null=True,
        allow_unknown=True,
        allow_dynamic_type=True,
    ),
    type_func=_unified_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Returns the first of the given arguments that isn't null, or raises an "
        "error if there are no non-null arguments."
    ),
)
def coalesce(*args: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `CoalesceFunc` (`stdlib/general.go:83`).

    Three details this package had wrong, all of them in the four lines go-cty
    spends on the loop:

    - An **unknown stops the search**. It could still turn out to be non-null,
      so nothing after it can be claimed as the answer. This package skipped
      unknowns as though they were nulls, and `coalesce(unknown, "b")` returned
      `"b"` -- a definite answer that the first argument may yet contradict.
    - The answer is **converted to the unified return type**. Returning the
      argument as it stands means `coalesce(1, "b")` answers with a number where
      the declared return type is string, which is the inconsistency the
      framework now panics on.
    - **All-null is an error**, not a null. `refineNonNull` says the result is
      never null, and go-cty raises rather than break that promise.
    """
    for arg in args:
        if arg.is_unknown:
            return CtyValue.unknown(return_type)
        if arg.is_null:
            continue
        return convert(arg, return_type)
    raise CtyFunctionError("no non-null arguments")


# 🌊🪢🔚
