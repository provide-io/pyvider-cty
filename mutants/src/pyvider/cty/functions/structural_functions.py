# pyvider/cty/functions/structural_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from pyvider.cty import CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_coalesce__mutmut_orig(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("coalesce must have at least one argument")

    for arg in args:
        if not arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(args[-1].type)


def x_coalesce__mutmut_1(*args: CtyValue[Any]) -> CtyValue[Any]:
    if args:
        raise CtyFunctionError("coalesce must have at least one argument")

    for arg in args:
        if not arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(args[-1].type)


def x_coalesce__mutmut_2(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError(None)

    for arg in args:
        if not arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(args[-1].type)


def x_coalesce__mutmut_3(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("XXcoalesce must have at least one argumentXX")

    for arg in args:
        if not arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(args[-1].type)


def x_coalesce__mutmut_4(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("COALESCE MUST HAVE AT LEAST ONE ARGUMENT")

    for arg in args:
        if not arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(args[-1].type)


def x_coalesce__mutmut_5(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("coalesce must have at least one argument")

    for arg in args:
        if not arg.is_null or not arg.is_unknown:
            return arg

    return CtyValue.null(args[-1].type)


def x_coalesce__mutmut_6(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("coalesce must have at least one argument")

    for arg in args:
        if arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(args[-1].type)


def x_coalesce__mutmut_7(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("coalesce must have at least one argument")

    for arg in args:
        if not arg.is_null and arg.is_unknown:
            return arg

    return CtyValue.null(args[-1].type)


def x_coalesce__mutmut_8(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("coalesce must have at least one argument")

    for arg in args:
        if not arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(None)


def x_coalesce__mutmut_9(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("coalesce must have at least one argument")

    for arg in args:
        if not arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(args[+1].type)


def x_coalesce__mutmut_10(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not args:
        raise CtyFunctionError("coalesce must have at least one argument")

    for arg in args:
        if not arg.is_null and not arg.is_unknown:
            return arg

    return CtyValue.null(args[-2].type)

x_coalesce__mutmut_mutants : ClassVar[MutantDict] = {
'x_coalesce__mutmut_1': x_coalesce__mutmut_1, 
    'x_coalesce__mutmut_2': x_coalesce__mutmut_2, 
    'x_coalesce__mutmut_3': x_coalesce__mutmut_3, 
    'x_coalesce__mutmut_4': x_coalesce__mutmut_4, 
    'x_coalesce__mutmut_5': x_coalesce__mutmut_5, 
    'x_coalesce__mutmut_6': x_coalesce__mutmut_6, 
    'x_coalesce__mutmut_7': x_coalesce__mutmut_7, 
    'x_coalesce__mutmut_8': x_coalesce__mutmut_8, 
    'x_coalesce__mutmut_9': x_coalesce__mutmut_9, 
    'x_coalesce__mutmut_10': x_coalesce__mutmut_10
}

def coalesce(*args, **kwargs):
    result = _mutmut_trampoline(x_coalesce__mutmut_orig, x_coalesce__mutmut_mutants, args, kwargs)
    return result 

coalesce.__signature__ = _mutmut_signature(x_coalesce__mutmut_orig)
x_coalesce__mutmut_orig.__name__ = 'x_coalesce'


# 🌊🪢🔣🪄
