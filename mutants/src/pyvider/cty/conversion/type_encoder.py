# pyvider/cty/conversion/type_encoder.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# pyvider-cty/src/pyvider/cty/conversion/type_encoder.py
from typing import Any

from pyvider.cty.config.defaults import ERR_EXPECTED_CTYTYPE
from pyvider.cty.types import CtyType
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


def x_encode_cty_type_to_wire_json__mutmut_orig(cty_type: CtyType[Any]) -> Any:
    """
    Encodes a CtyType into a JSON-serializable structure for the wire format
    by delegating to the type's own `_to_wire_json` method.
    """
    if not isinstance(cty_type, CtyType):
        error_message = ERR_EXPECTED_CTYTYPE.format(type_name=type(cty_type).__name__)
        raise TypeError(error_message)
    return cty_type._to_wire_json()


def x_encode_cty_type_to_wire_json__mutmut_1(cty_type: CtyType[Any]) -> Any:
    """
    Encodes a CtyType into a JSON-serializable structure for the wire format
    by delegating to the type's own `_to_wire_json` method.
    """
    if isinstance(cty_type, CtyType):
        error_message = ERR_EXPECTED_CTYTYPE.format(type_name=type(cty_type).__name__)
        raise TypeError(error_message)
    return cty_type._to_wire_json()


def x_encode_cty_type_to_wire_json__mutmut_2(cty_type: CtyType[Any]) -> Any:
    """
    Encodes a CtyType into a JSON-serializable structure for the wire format
    by delegating to the type's own `_to_wire_json` method.
    """
    if not isinstance(cty_type, CtyType):
        error_message = None
        raise TypeError(error_message)
    return cty_type._to_wire_json()


def x_encode_cty_type_to_wire_json__mutmut_3(cty_type: CtyType[Any]) -> Any:
    """
    Encodes a CtyType into a JSON-serializable structure for the wire format
    by delegating to the type's own `_to_wire_json` method.
    """
    if not isinstance(cty_type, CtyType):
        error_message = ERR_EXPECTED_CTYTYPE.format(type_name=None)
        raise TypeError(error_message)
    return cty_type._to_wire_json()


def x_encode_cty_type_to_wire_json__mutmut_4(cty_type: CtyType[Any]) -> Any:
    """
    Encodes a CtyType into a JSON-serializable structure for the wire format
    by delegating to the type's own `_to_wire_json` method.
    """
    if not isinstance(cty_type, CtyType):
        error_message = ERR_EXPECTED_CTYTYPE.format(type_name=type(None).__name__)
        raise TypeError(error_message)
    return cty_type._to_wire_json()


def x_encode_cty_type_to_wire_json__mutmut_5(cty_type: CtyType[Any]) -> Any:
    """
    Encodes a CtyType into a JSON-serializable structure for the wire format
    by delegating to the type's own `_to_wire_json` method.
    """
    if not isinstance(cty_type, CtyType):
        error_message = ERR_EXPECTED_CTYTYPE.format(type_name=type(cty_type).__name__)
        raise TypeError(None)
    return cty_type._to_wire_json()

x_encode_cty_type_to_wire_json__mutmut_mutants : ClassVar[MutantDict] = {
'x_encode_cty_type_to_wire_json__mutmut_1': x_encode_cty_type_to_wire_json__mutmut_1, 
    'x_encode_cty_type_to_wire_json__mutmut_2': x_encode_cty_type_to_wire_json__mutmut_2, 
    'x_encode_cty_type_to_wire_json__mutmut_3': x_encode_cty_type_to_wire_json__mutmut_3, 
    'x_encode_cty_type_to_wire_json__mutmut_4': x_encode_cty_type_to_wire_json__mutmut_4, 
    'x_encode_cty_type_to_wire_json__mutmut_5': x_encode_cty_type_to_wire_json__mutmut_5
}

def encode_cty_type_to_wire_json(*args, **kwargs):
    result = _mutmut_trampoline(x_encode_cty_type_to_wire_json__mutmut_orig, x_encode_cty_type_to_wire_json__mutmut_mutants, args, kwargs)
    return result 

encode_cty_type_to_wire_json.__signature__ = _mutmut_signature(x_encode_cty_type_to_wire_json__mutmut_orig)
x_encode_cty_type_to_wire_json__mutmut_orig.__name__ = 'x_encode_cty_type_to_wire_json'


# 🌊🪢🧱🪄
