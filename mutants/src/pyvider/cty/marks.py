# pyvider/cty/marks.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from attrs import define, field
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


def x__convert_details__mutmut_orig(value: Any) -> frozenset[Any] | None:
    """Converter to ensure the 'details' field is always hashable."""
    if value is None:
        return None
    if isinstance(value, dict):
        return frozenset(value.items())
    if isinstance(value, list | set | tuple):
        return frozenset(value)
    return frozenset([value])


def x__convert_details__mutmut_1(value: Any) -> frozenset[Any] | None:
    """Converter to ensure the 'details' field is always hashable."""
    if value is not None:
        return None
    if isinstance(value, dict):
        return frozenset(value.items())
    if isinstance(value, list | set | tuple):
        return frozenset(value)
    return frozenset([value])


def x__convert_details__mutmut_2(value: Any) -> frozenset[Any] | None:
    """Converter to ensure the 'details' field is always hashable."""
    if value is None:
        return None
    if isinstance(value, dict):
        return frozenset(None)
    if isinstance(value, list | set | tuple):
        return frozenset(value)
    return frozenset([value])


def x__convert_details__mutmut_3(value: Any) -> frozenset[Any] | None:
    """Converter to ensure the 'details' field is always hashable."""
    if value is None:
        return None
    if isinstance(value, dict):
        return frozenset(value.items())
    if isinstance(value, list | set | tuple):
        return frozenset(None)
    return frozenset([value])


def x__convert_details__mutmut_4(value: Any) -> frozenset[Any] | None:
    """Converter to ensure the 'details' field is always hashable."""
    if value is None:
        return None
    if isinstance(value, dict):
        return frozenset(value.items())
    if isinstance(value, list | set | tuple):
        return frozenset(value)
    return frozenset(None)

x__convert_details__mutmut_mutants : ClassVar[MutantDict] = {
'x__convert_details__mutmut_1': x__convert_details__mutmut_1, 
    'x__convert_details__mutmut_2': x__convert_details__mutmut_2, 
    'x__convert_details__mutmut_3': x__convert_details__mutmut_3, 
    'x__convert_details__mutmut_4': x__convert_details__mutmut_4
}

def _convert_details(*args, **kwargs):
    result = _mutmut_trampoline(x__convert_details__mutmut_orig, x__convert_details__mutmut_mutants, args, kwargs)
    return result 

_convert_details.__signature__ = _mutmut_signature(x__convert_details__mutmut_orig)
x__convert_details__mutmut_orig.__name__ = 'x__convert_details'


@define(frozen=True, slots=True)
class CtyMark:
    """
    Represents a mark that can be applied to a cty.Value.
    The 'details' attribute is automatically converted to a hashable frozenset.
    """

    name: str = field()
    details: frozenset[Any] | None = field(default=None, converter=_convert_details)

    def __repr__(self) -> str:
        if self.details is not None:
            return f"CtyMark({self.name!r}, {dict(self.details)!r})"
        return f"CtyMark({self.name!r})"

    def __str__(self) -> str:
        return self.name


# 🌊🪢🏷️🪄
