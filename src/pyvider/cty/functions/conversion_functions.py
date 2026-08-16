#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/conversion.go`."""

from __future__ import annotations

from typing import Any

from pyvider.cty import CtyBool, CtyNumber, CtyString, CtyType, CtyValue
from pyvider.cty.config.defaults import ERR_CANNOT_CONVERT_TO_TYPE
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import CtyConversionError, CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function


def _to(value: CtyValue[Any], target_type: CtyType[Any], func: str) -> CtyValue[Any]:
    """go-cty's `MakeToFunc`, which builds all three of these from one body.

    Two things follow from being one body rather than three.

    The conversion is `convert`'s, not a hand-rolled one. `tostring` used to end
    in `str(input_val.value)` for anything it did not recognise, and the payload
    of a collection is its internal tuple of CtyValues, so `tostring(["a"])`
    returned the text of a repr -- a plausible string headed for state. The rule
    for what converts to what belongs in one place, and that place is `convert`.

    A null converts; it does not become unknown. go-cty's parameter sets
    `AllowNull: true` (`stdlib/conversion.go:33`) precisely so that
    `convert.Convert` can carry a null through to a null of the target type,
    which is what `tostring(null)` means: still nothing, now typed as a string.
    These three returned unknown instead, which claims the value might yet turn
    out to be something.
    """
    if value.is_unknown:
        return CtyValue.unknown(target_type)
    try:
        return convert(value, target_type)
    except CtyConversionError as e:
        error_message = ERR_CANNOT_CONVERT_TO_TYPE.format(
            func=func, type=value.type.ctype, target=target_type.ctype
        )
        raise CtyFunctionError(error_message) from e


@stdlib_function("tostring")
def to_string(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MakeToFunc(cty.String)`."""
    return _to(input_val, CtyString(), "tostring")


@stdlib_function("tonumber")
def to_number(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MakeToFunc(cty.Number)`."""
    return _to(input_val, CtyNumber(), "tonumber")


@stdlib_function("tobool")
def to_bool(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `MakeToFunc(cty.Bool)`."""
    return _to(input_val, CtyBool(), "tobool")


# 🌊🪢🔚
