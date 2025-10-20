# pyvider/cty/values/markers.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from decimal import Decimal

from attrs import define

# pyvider/cty/values/markers.py
"""
This module contains simple marker classes to break import cycles.
"""
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


class UnknownValue:
    """A base marker class for all unknown value types."""

    pass


class UnrefinedUnknownValue(UnknownValue):
    """A marker class for a simple, unrefined unknown value."""

    def xǁUnrefinedUnknownValueǁ__repr____mutmut_orig(self) -> str:
        return "UNREFINED_UNKNOWN"

    def xǁUnrefinedUnknownValueǁ__repr____mutmut_1(self) -> str:
        return "XXUNREFINED_UNKNOWNXX"

    def xǁUnrefinedUnknownValueǁ__repr____mutmut_2(self) -> str:
        return "unrefined_unknown"
    
    xǁUnrefinedUnknownValueǁ__repr____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁUnrefinedUnknownValueǁ__repr____mutmut_1': xǁUnrefinedUnknownValueǁ__repr____mutmut_1, 
        'xǁUnrefinedUnknownValueǁ__repr____mutmut_2': xǁUnrefinedUnknownValueǁ__repr____mutmut_2
    }
    
    def __repr__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁUnrefinedUnknownValueǁ__repr____mutmut_orig"), object.__getattribute__(self, "xǁUnrefinedUnknownValueǁ__repr____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __repr__.__signature__ = _mutmut_signature(xǁUnrefinedUnknownValueǁ__repr____mutmut_orig)
    xǁUnrefinedUnknownValueǁ__repr____mutmut_orig.__name__ = 'xǁUnrefinedUnknownValueǁ__repr__'


@define(frozen=True, slots=True, auto_attribs=True, match_args=True)
class RefinedUnknownValue(UnknownValue):
    """Represents an unknown value with additional constraints."""

    is_known_null: bool | None = None
    string_prefix: str | None = None
    number_lower_bound: tuple[Decimal, bool] | None = None
    number_upper_bound: tuple[Decimal, bool] | None = None
    collection_length_lower_bound: int | None = None
    collection_length_upper_bound: int | None = None


# This singleton represents an unknown value with no refinements.
UNREFINED_UNKNOWN = UnrefinedUnknownValue()
# 🌊🪢🏷️🪄
