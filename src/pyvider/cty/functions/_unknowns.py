#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""What a stdlib function returns when it declines to answer.

go-cty's stdlib almost never returns a bare `cty.UnknownVal` from a function
body. It returns `cty.UnknownVal(retType).RefineNotNull()`, because declining to
compute a result is not the same as admitting the result might be absent: a
`join` whose list holds an unknown element still definitely produces a string,
and Terraform can plan on that even while the characters are undecided.

One copy, for the same reason `_args.py` is one copy: the shape below appeared
in several function bodies as `CtyValue.unknown(t)`, and every one of them threw
away a promise go-cty makes.
"""

from __future__ import annotations

from typing import Any

from pyvider.cty.refinement import refine
from pyvider.cty.types import CtyType
from pyvider.cty.values import CtyValue


def unknown_not_null(vtype: CtyType[Any]) -> CtyValue[Any]:
    """An unknown of `vtype`, refined to say it will not turn out to be null.

    go-cty's `Value.RefineNotNull()`.
    """
    return refine(CtyValue.unknown(vtype)).not_null().new_value()


# 🌊🪢🔚
