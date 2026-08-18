#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The seam every stdlib function is declared through.

It registers the function under go-cty's own name for it and builds the real
`CtyFunction` from `_function.py`, so every call goes through go-cty's `Call`
algorithm: arity, per-parameter type conformance, the null policy, mark
stripping, the unknown short-circuit typed by the return type, the result
conformance check and `refine_result`. These are properties of *being* a stdlib
function, so they are declared once at the function rather than re-derived
inside 83 function bodies -- which is how the mark bugs, and most of the
argument-handling divergences found since, came about.

There used to be a pre-framework path here that knew only about marks and a
whole-function null policy. All 83 functions migrated on 2026-08-17 and it was
deleted the same day; `tests/functions/test_stdlib_registry.py` asserts the
registry and the signature table stay the same size so a declaration cannot
quietly fall back to nothing.

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
returned 5), and a null in 19. `CtyParameter.allow_null` now carries that
policy per parameter, transcribed from go-cty's specs.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, Literal, ParamSpec, TypeVar, cast, overload

from pyvider.cty.config.defaults import ERR_STDLIB_DUPLICATE_NAME
from pyvider.cty.functions._function import (
    CtyFunction,
    CtyFunctionSpec,
    CtyParameter,
    RefineResult,
    TypeFunc,
    bind_positionally,
    positional_impl,
    static_return_type,
)
from pyvider.cty.types import CtyType
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

# The declared signature behind each name. This is what makes return-type
# prediction possible: `SIGNATURES["upper"].return_type` answers without a value
# in sight. Keyed the same way as `STDLIB`, and always the same size -- a test
# asserts it, so a function cannot be registered without saying what it accepts.
SIGNATURES: dict[str, CtyFunction] = {}


def unmigrated() -> list[str]:
    """Stdlib names with no declared signature. Empty since 2026-08-17.

    Kept because a guard test asserts it *stays* empty -- and because this list
    alone cannot prove completeness: a module that fails to import registers
    nothing, so the test pairs it with a count of `STDLIB` itself.
    """
    return [name for name in STDLIB if name not in SIGNATURES]


def _register(name: str, fn: Callable[..., Any], wrapped: Callable[..., Any]) -> None:
    """Claim `name` for `fn`, refusing to let two functions claim one name."""
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


def _coerce(
    args: tuple[Any, ...], params: tuple[CtyParameter, ...], var_param: CtyParameter | None
) -> tuple[CtyValue[Any], ...]:
    """Every argument as a `CtyValue`, validating a raw Python one on the way in.

    go-cty's `Call` takes `[]cty.Value` and nothing else, because Go has no
    untyped literal to accept. Callers of this package have always been able to
    pass `length([1, 2, 3])`, and the parameter now says what type that should
    become -- so the coercion has a declared answer instead of each function
    guessing at one.

    A raw Python argument is a convenience this package offers and go-cty has no
    counterpart for, so its semantics are `validate`'s, conversions included --
    a raw `"7"` into a number parameter is `7`, where a `CtyString` *value*
    holding `"7"` is refused by conformance. Callers who want go-cty's exact
    strictness pass `CtyValue`s.
    """
    if var_param is None and len(args) > len(params):
        # Too many arguments, and no parameter to coerce the extras against.
        # `CtyFunction.call` refuses this in go-cty's words; coercing first would
        # raise a validation error about an argument that should not exist.
        return cast("tuple[CtyValue[Any], ...]", args)

    coerced: list[CtyValue[Any]] = []
    for index, arg in enumerate(args):
        if isinstance(arg, CtyValue):
            coerced.append(arg)
            continue
        param = params[index] if index < len(params) else var_param
        assert param is not None
        coerced.append(param.type.validate(arg))
    return tuple(coerced)


@overload
def stdlib_function(
    name: str,
    *,
    params: Sequence[CtyParameter] = ...,
    var_param: CtyParameter | None = ...,
    returns: CtyType[Any] | None = ...,
    type_func: TypeFunc | None = ...,
    refine_result: RefineResult | None = ...,
    wants_return_type: Literal[True],
    description: str = ...,
) -> Callable[[Callable[..., R]], Callable[..., R]]: ...


@overload
def stdlib_function(
    name: str,
    *,
    params: Sequence[CtyParameter] = ...,
    var_param: CtyParameter | None = ...,
    returns: CtyType[Any] | None = ...,
    type_func: TypeFunc | None = ...,
    refine_result: RefineResult | None = ...,
    wants_return_type: Literal[False] = ...,
    description: str = ...,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def stdlib_function(
    name: str,
    *,
    params: Sequence[CtyParameter] = (),
    var_param: CtyParameter | None = None,
    returns: CtyType[Any] | None = None,
    type_func: TypeFunc | None = None,
    refine_result: RefineResult | None = None,
    wants_return_type: bool = False,
    description: str = "",
) -> Callable[[Callable[P, R]], Callable[P, R]] | Callable[[Callable[..., R]], Callable[..., R]]:
    """Declare a go-cty stdlib function under the name go-cty gives it.

    The name lives at the function so that it cannot drift from it. A mapping
    maintained separately is exactly what the compatibility sweep used to
    carry, and it silently skipped fourteen functions while reporting them as
    covered.

    `params` and `var_param` are go-cty's `Spec.Params`/`Spec.VarParam`; at
    least one parameter must be declared. Exactly one of `returns` and
    `type_func` says what comes back: `returns` for a fixed return type,
    `type_func` for one computed from the arguments. `refine_result` is go-cty's
    `Spec.RefineResult` -- what stays true of the answer even when the answer is
    unknown.

    Overloaded on `wants_return_type` because the decorator is not an identity
    when it is set. The framework supplies `return_type` itself, so the callable
    it returns takes the implementation's parameters *minus* that one -- a
    subtraction Python's type system cannot express. Typed as an identity, the
    injected keyword leaked into every caller's view: `flatten(x)` and `sort(x)`
    were type errors demanding an argument nobody is allowed to pass, on
    thirteen public functions. `...` is the accurate statement instead -- these
    arguments are not statically checkable -- and it costs argument checking
    only for those thirteen, where the alternative was a false error on every
    call.
    """
    if not params and var_param is None:
        raise ValueError(f"{name}: a stdlib function declares its parameters")
    if (returns is None) == (type_func is None):
        raise ValueError(f"{name}: declare exactly one of `returns` and `type_func`")

    fixed = tuple(params)
    resolved_type_func = static_return_type(returns) if returns is not None else type_func
    assert resolved_type_func is not None

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        function = CtyFunction(
            CtyFunctionSpec(
                name=name,
                params=fixed,
                var_param=var_param,
                type_func=resolved_type_func,
                impl=positional_impl(fn, wants_return_type=wants_return_type),
                description=description,
                refine_result=refine_result,
            )
        )

        @wraps(fn)
        def called(*args: P.args, **kwargs: P.kwargs) -> R:
            positional = bind_positionally(fn, args, kwargs)
            return cast("R", function.call(_coerce(positional, fixed, var_param)))

        # The declared signature is reachable from the function as well as from
        # the registry, so a caller holding only the callable can still ask what
        # it returns.
        called.cty_function = function  # type: ignore[attr-defined]
        _register(name, fn, called)
        SIGNATURES[name] = function
        return called

    return decorate


# 🌊🪢🔚
