#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The seam every stdlib function is declared through.

It registers the function under go-cty's own name for it, applies the mark
policy, and enforces the null-argument policy. All three are properties of
*being* a stdlib function, so they are declared once at the function rather than
re-derived inside 79 function bodies -- which is how the mark bugs, and most of
the argument-handling divergences found since, came about.

On nulls specifically. go-cty's `cty/function` framework refuses a null argument
before the implementation runs unless the parameter sets `AllowNull`
(`function.go:169`). This package hand-rolled that check 144 times, and the
shape it reached for -- `if x.is_null or x.is_unknown: return unknown` -- treats
a null as an unknown, which they are not: an unknown is a value nobody knows
yet, a null is a value that is definitely absent.

Measured against the oracle by nulling each argument of every sweep case in
turn: **109 of 138 argument positions disagreed**, every one of them go-cty
raising where this package did something else -- unknown in 69, a *computed
result* in 21 (`lookup` on a null map returned its default; `max(null, 5)`
returned 5), and a null in 19. The allow-list below is derived from that run
rather than from reading go-cty's parameter specs.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from pyvider.cty.config.defaults import ERR_ARGUMENT_MUST_NOT_BE_NULL, ERR_STDLIB_DUPLICATE_NAME
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._marks import preserve_marks
from pyvider.cty.values import CtyValue

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

# Which parameters accept a null, per function. `True` means every parameter --
# the right answer for a variadic whose whole job involves nulls.
AllowNull = bool | Sequence[int]


def _refuses_null(allow_null: AllowNull, position: int) -> bool:
    """Whether this position rejects a null. `allow_null=True` never reaches here."""
    if allow_null is False:
        return True
    return position not in cast(Sequence[int], allow_null)


def _check_nulls(name: str, allow_null: AllowNull, args: tuple[Any, ...]) -> None:
    for position, argument in enumerate(args):
        if isinstance(argument, CtyValue) and argument.is_null and _refuses_null(allow_null, position):
            raise CtyFunctionError(ERR_ARGUMENT_MUST_NOT_BE_NULL.format(func=name, position=position))


def stdlib_function(name: str, *, allow_null: AllowNull = False) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Declare a go-cty stdlib function under the name go-cty gives it.

    The name lives at the function so that it cannot drift from it. A mapping
    maintained separately is exactly what the compatibility sweep used to
    carry, and it silently skipped fourteen functions while reporting them as
    covered.

    `allow_null` mirrors go-cty's per-parameter `AllowNull`, defaulting to
    refusing -- which is go-cty's default too. Pass `True` for a variadic that
    takes nulls throughout, or the positions that accept one.
    """

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        marked = preserve_marks(fn)

        @wraps(fn)
        def guarded(*args: P.args, **kwargs: P.kwargs) -> R:
            _check_nulls(name, allow_null, args)
            return marked(*args, **kwargs)

        # A function that accepts a null everywhere needs no guard at all, so
        # it keeps the bare marked wrapper rather than paying for a scan.
        wrapped = marked if allow_null is True else guarded
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
