# pyvider/cty/functions/conversion_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from pyvider.cty import CtyBool, CtyNumber, CtyString, CtyValue
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


def x_to_string__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null and input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(None)
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate(None)
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("XXtrueXX" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("TRUE" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "XXfalseXX")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "FALSE")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(None)
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(None))
    return CtyString().validate(str(input_val.value))


def x_to_string__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(None)


def x_to_string__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if isinstance(input_val.type, CtyBool):
        return CtyString().validate("true" if input_val.value else "false")
    if isinstance(input_val.type, CtyNumber):
        return CtyString().validate(str(input_val.value))
    return CtyString().validate(str(None))

x_to_string__mutmut_mutants : ClassVar[MutantDict] = {
'x_to_string__mutmut_1': x_to_string__mutmut_1, 
    'x_to_string__mutmut_2': x_to_string__mutmut_2, 
    'x_to_string__mutmut_3': x_to_string__mutmut_3, 
    'x_to_string__mutmut_4': x_to_string__mutmut_4, 
    'x_to_string__mutmut_5': x_to_string__mutmut_5, 
    'x_to_string__mutmut_6': x_to_string__mutmut_6, 
    'x_to_string__mutmut_7': x_to_string__mutmut_7, 
    'x_to_string__mutmut_8': x_to_string__mutmut_8, 
    'x_to_string__mutmut_9': x_to_string__mutmut_9, 
    'x_to_string__mutmut_10': x_to_string__mutmut_10, 
    'x_to_string__mutmut_11': x_to_string__mutmut_11
}

def to_string(*args, **kwargs):
    result = _mutmut_trampoline(x_to_string__mutmut_orig, x_to_string__mutmut_mutants, args, kwargs)
    return result 

to_string.__signature__ = _mutmut_signature(x_to_string__mutmut_orig)
x_to_string__mutmut_orig.__name__ = 'x_to_string'


def x_to_number__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        return CtyNumber().validate(input_val.value)
    except Exception as e:
        raise CtyFunctionError(f"tostring: cannot convert {input_val.type.ctype} to number") from e


def x_to_number__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null and input_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        return CtyNumber().validate(input_val.value)
    except Exception as e:
        raise CtyFunctionError(f"tostring: cannot convert {input_val.type.ctype} to number") from e


def x_to_number__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(None)
    try:
        return CtyNumber().validate(input_val.value)
    except Exception as e:
        raise CtyFunctionError(f"tostring: cannot convert {input_val.type.ctype} to number") from e


def x_to_number__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        return CtyNumber().validate(None)
    except Exception as e:
        raise CtyFunctionError(f"tostring: cannot convert {input_val.type.ctype} to number") from e


def x_to_number__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        return CtyNumber().validate(input_val.value)
    except Exception as e:
        raise CtyFunctionError(None) from e

x_to_number__mutmut_mutants : ClassVar[MutantDict] = {
'x_to_number__mutmut_1': x_to_number__mutmut_1, 
    'x_to_number__mutmut_2': x_to_number__mutmut_2, 
    'x_to_number__mutmut_3': x_to_number__mutmut_3, 
    'x_to_number__mutmut_4': x_to_number__mutmut_4
}

def to_number(*args, **kwargs):
    result = _mutmut_trampoline(x_to_number__mutmut_orig, x_to_number__mutmut_mutants, args, kwargs)
    return result 

to_number.__signature__ = _mutmut_signature(x_to_number__mutmut_orig)
x_to_number__mutmut_orig.__name__ = 'x_to_number'


def x_to_bool__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyBool())
    try:
        return CtyBool().validate(input_val.value)
    except Exception as e:
        raise CtyFunctionError(f"tobool: cannot convert {input_val.type.ctype} to bool") from e


def x_to_bool__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null and input_val.is_unknown:
        return CtyValue.unknown(CtyBool())
    try:
        return CtyBool().validate(input_val.value)
    except Exception as e:
        raise CtyFunctionError(f"tobool: cannot convert {input_val.type.ctype} to bool") from e


def x_to_bool__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(None)
    try:
        return CtyBool().validate(input_val.value)
    except Exception as e:
        raise CtyFunctionError(f"tobool: cannot convert {input_val.type.ctype} to bool") from e


def x_to_bool__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyBool())
    try:
        return CtyBool().validate(None)
    except Exception as e:
        raise CtyFunctionError(f"tobool: cannot convert {input_val.type.ctype} to bool") from e


def x_to_bool__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyBool())
    try:
        return CtyBool().validate(input_val.value)
    except Exception as e:
        raise CtyFunctionError(None) from e

x_to_bool__mutmut_mutants : ClassVar[MutantDict] = {
'x_to_bool__mutmut_1': x_to_bool__mutmut_1, 
    'x_to_bool__mutmut_2': x_to_bool__mutmut_2, 
    'x_to_bool__mutmut_3': x_to_bool__mutmut_3, 
    'x_to_bool__mutmut_4': x_to_bool__mutmut_4
}

def to_bool(*args, **kwargs):
    result = _mutmut_trampoline(x_to_bool__mutmut_orig, x_to_bool__mutmut_mutants, args, kwargs)
    return result 

to_bool.__signature__ = _mutmut_signature(x_to_bool__mutmut_orig)
x_to_bool__mutmut_orig.__name__ = 'x_to_bool'


# 🌊🪢🔣🪄
