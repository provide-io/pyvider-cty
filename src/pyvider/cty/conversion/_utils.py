#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from decimal import Decimal, localcontext
from typing import Any

from pyvider.cty.config.defaults import (
    ERR_CANNOT_INFER_FROM_CTY_TYPE,
    ERR_CANNOT_INFER_FROM_CTY_VALUE,
)

# pyvider-cty/src/pyvider/cty/conversion/_utils.py
"""Internal conversion utilities to avoid circular dependencies."""


def exact_normalize(number: Decimal) -> Decimal:
    """`Decimal.normalize()` without the ambient context deciding how much to keep.

    `normalize` strips trailing zeros, and it honours the active context while
    doing it -- whose default precision is 28 -- so it silently rounds anything
    wider. Every renderer that reaches for it has to widen the context to the
    number's own digit count first, which can never be too few: stripping zeros
    needs no more digits than it was given.

    Three renderers did not, and all three under-reported the same value:
    `format("%v", 10**28 + 1)` came back `1e+28` where go-cty writes
    `1.0000000000000000000000000001e+28`, and `%g` and `%#v` with it. The string
    conversion had the same bug and was fixed on 2026-08-19; this is that fix
    made shared, after the stdlib fuzz found the copies that had not had it.
    """
    if not number.is_finite():
        return number
    with localcontext() as ctx:
        ctx.prec = max(len(number.as_tuple().digits), 1)
        return number.normalize()


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

    A member that cannot produce a key is handed to `_member_key`, which is the
    same fallback hashing and de-duplication use. It has to be the same one: its
    key is `(0, -1, repr(member))` and a real value's is `(0, <rank>, ...)`, so
    the two are comparable only because the raw one keeps the arity and puts an
    int where an int is expected. The `(0, str(member))` this used to return was
    a two-tuple whose second element is a string, and sorting a set holding both
    kinds compared an int against a str and raised a bare `TypeError` -- from
    inside `cty_to_native`, and outside the error taxonomy. That import is on the
    rare path: only a hand-built value can hold a member `validate` did not
    normalise.
    """
    key = getattr(member, "_canonical_sort_key", None)
    if key is not None:
        return key()
    from pyvider.cty.values.base import _member_key

    return _member_key(member)


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
