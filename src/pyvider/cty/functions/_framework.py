#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The seam every stdlib function is declared through.

Today it does two things: it registers the function under go-cty's own name for
it, and it applies the mark policy. Both are properties of *being* a stdlib
function, so they are declared in one place at the function rather than
re-derived inside 79 function bodies -- which is how the mark bugs, and most of
the argument-handling divergences found since, came about.

It is deliberately shaped to take more later. go-cty's `cty/function` framework
declares each parameter's type and whether it accepts null, unknown or marked
values, and enforces that before the implementation runs. This package still
hand-rolls those checks (146 of them at last count, no two quite alike). When
that policy moves here it goes behind this decorator, and the function bodies
do not change.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from pyvider.cty.config.defaults import ERR_STDLIB_DUPLICATE_NAME
from pyvider.cty.functions._marks import preserve_marks

P = ParamSpec("P")
R = TypeVar("R")

# go-cty's name for a function, mapped to this package's implementation of it.
#
# Keyed by name rather than reached by attribute because the two vocabularies
# cannot be made to coincide: `and`, `or` and `not` are Python keywords, so no
# Python function can ever carry those names, and six more would shadow
# builtins that the surrounding modules actually call. A dict key has no such
# problem, so the Python identifier stays Python-shaped and this is the surface
# that speaks Terraform.
STDLIB: dict[str, Callable[..., Any]] = {}


def stdlib_function(name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Declare a go-cty stdlib function under the name go-cty gives it.

    The name lives at the function so that it cannot drift from it. A mapping
    maintained separately is exactly what the compatibility sweep used to
    carry, and it silently skipped fourteen functions while reporting them as
    covered.
    """

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        wrapped = preserve_marks(fn)
        existing = STDLIB.get(name)
        # Re-importing a module re-runs its decorators, which is not a clash.
        # Two different functions claiming one name is.
        if existing is not None and (
            existing.__module__,
            existing.__qualname__,
        ) != (fn.__module__, fn.__qualname__):
            raise ValueError(
                ERR_STDLIB_DUPLICATE_NAME.format(
                    name=name,
                    first=f"{existing.__module__}.{existing.__qualname__}",
                    second=f"{fn.__module__}.{fn.__qualname__}",
                )
            )
        STDLIB[name] = wrapped
        return wrapped

    return decorate


# 🌊🪢🔚
