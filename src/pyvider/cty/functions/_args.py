#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Argument coercions shared by stdlib functions.

One copy, because the recurring fault in this package has been the same idea
implemented several times with each copy guessing at a slightly different set
of cases.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.values import CtyValue

# go-cty reads a number parameter through `gocty.FromCtyValue` into a Go `int`,
# and names these bounds in the error it raises when the value will not fit.
INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1


def whole_number(value: CtyValue[Any], error: str) -> int:
    """A number argument as a Python `int`, or a refusal.

    Refuses a fraction, as go-cty does, and also infinity, NaN and anything
    outside the int64 range. Those last three are not pedantry: `Decimal`
    arithmetic accepts all of them, `int(Decimal("Infinity"))` raises
    `OverflowError` rather than anything a caller can act on, and a merely
    enormous finite count would be accepted and then used -- long enough for
    `indent(2**70, s)` to try to build a 10^21-character string.

    `error` is a format string taking `{value}`.
    """
    raw = cast(Decimal, value.value)
    if not raw.is_finite() or raw != raw.to_integral_value() or not INT64_MIN <= raw <= INT64_MAX:
        raise CtyFunctionError(error.format(value=raw))
    return int(raw)


# 🌊🪢🔚
