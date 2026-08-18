#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from decimal import Decimal
from typing import Any

from pyvider.cty.config.defaults import (
    ERR_CANNOT_INFER_FROM_CTY_TYPE,
    ERR_CANNOT_INFER_FROM_CTY_VALUE,
)

# pyvider-cty/src/pyvider/cty/conversion/_utils.py
"""Internal conversion utilities to avoid circular dependencies."""


def non_finite_text(number: Any) -> str | None:
    """Go's spelling of a non-finite number, or `None` if it is finite.

    `big.Float.Text` writes `+Inf` and `-Inf`, with the sign always present --
    including on the positive one -- and Go's `strconv` writes `NaN` unsigned.
    `str(Decimal)` says `Infinity`, `-Infinity` and `NaN`, so every place that
    spells a number for go-cty parity has to translate: the string conversion
    (`f.Text('f', -1)`, `convert/conversion_primitive.go:16`), `%v`
    (`bf.Text('g', -1)`, `stdlib/format.go:377`) and the float verbs, which
    delegate to Go's own `fmt`.

    go-cty cannot hold a NaN at all -- `big.Float.SetFloat64` panics on one --
    so the `NaN` spelling is Go's rather than go-cty's. A `Decimal` NaN reaches
    this package from arithmetic go-cty performs in `float64`, so it needs *an*
    answer, and Go's is the only one with a claim on being right.
    """
    if not isinstance(number, Decimal) or number.is_finite():
        return None
    if number.is_nan():
        return "NaN"
    return "-Inf" if number < 0 else "+Inf"


def canonical_sort_key(member: Any) -> Any:
    """The order a set's elements are put in, for a member that may not be one.

    `CtyValue._canonical_sort_key` is total and never raises, so the fallback
    here is only for a member of a *hand-built* value -- `validate` normalises
    every member into a `CtyValue`. Shared rather than restated: this rule
    decides de-duplication, hashing, and the byte order of every serialized set,
    so two callers sorting a set two ways is a diff Terraform sees.

    Asked of the member rather than checked with `isinstance`, because importing
    `CtyValue` here is a cycle -- `types.structural.object` imports this module --
    and doing it inside the function would put an import on a path that runs once
    per element of every set this package converts or serializes.
    """
    key = getattr(member, "_canonical_sort_key", None)
    return key() if key is not None else (0, str(member))


def _attrs_to_dict_safe(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


# 🌊🪢🔚
