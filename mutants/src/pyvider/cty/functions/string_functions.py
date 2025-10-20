# pyvider/cty/functions/string_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from decimal import Decimal
import re
from typing import Any, cast

from pyvider.cty import CtyList, CtyNumber, CtyString, CtyTuple, CtyValue
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


def x_chomp__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = None
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith(None):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("XX\r\nXX"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(None)  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:+2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-3])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") and s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith(None) or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("XX\nXX") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith(None):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("XX\rXX"):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


def x_chomp__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(None)  # type: ignore
    return input_val


def x_chomp__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:+1])  # type: ignore
    return input_val


def x_chomp__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith("\n") or s.endswith("\r"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    return input_val

x_chomp__mutmut_mutants : ClassVar[MutantDict] = {
'x_chomp__mutmut_1': x_chomp__mutmut_1, 
    'x_chomp__mutmut_2': x_chomp__mutmut_2, 
    'x_chomp__mutmut_3': x_chomp__mutmut_3, 
    'x_chomp__mutmut_4': x_chomp__mutmut_4, 
    'x_chomp__mutmut_5': x_chomp__mutmut_5, 
    'x_chomp__mutmut_6': x_chomp__mutmut_6, 
    'x_chomp__mutmut_7': x_chomp__mutmut_7, 
    'x_chomp__mutmut_8': x_chomp__mutmut_8, 
    'x_chomp__mutmut_9': x_chomp__mutmut_9, 
    'x_chomp__mutmut_10': x_chomp__mutmut_10, 
    'x_chomp__mutmut_11': x_chomp__mutmut_11, 
    'x_chomp__mutmut_12': x_chomp__mutmut_12, 
    'x_chomp__mutmut_13': x_chomp__mutmut_13, 
    'x_chomp__mutmut_14': x_chomp__mutmut_14, 
    'x_chomp__mutmut_15': x_chomp__mutmut_15, 
    'x_chomp__mutmut_16': x_chomp__mutmut_16, 
    'x_chomp__mutmut_17': x_chomp__mutmut_17
}

def chomp(*args, **kwargs):
    result = _mutmut_trampoline(x_chomp__mutmut_orig, x_chomp__mutmut_mutants, args, kwargs)
    return result 

chomp.__signature__ = _mutmut_signature(x_chomp__mutmut_orig)
x_chomp__mutmut_orig.__name__ = 'x_chomp'


def x_strrev__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value[::-1])  # type: ignore


def x_strrev__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value[::-1])  # type: ignore


def x_strrev__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value[::-1])  # type: ignore


def x_strrev__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value[::-1])  # type: ignore


def x_strrev__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(None)  # type: ignore


def x_strrev__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value[::+1])  # type: ignore


def x_strrev__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value[::-2])  # type: ignore

x_strrev__mutmut_mutants : ClassVar[MutantDict] = {
'x_strrev__mutmut_1': x_strrev__mutmut_1, 
    'x_strrev__mutmut_2': x_strrev__mutmut_2, 
    'x_strrev__mutmut_3': x_strrev__mutmut_3, 
    'x_strrev__mutmut_4': x_strrev__mutmut_4, 
    'x_strrev__mutmut_5': x_strrev__mutmut_5, 
    'x_strrev__mutmut_6': x_strrev__mutmut_6
}

def strrev(*args, **kwargs):
    result = _mutmut_trampoline(x_strrev__mutmut_orig, x_strrev__mutmut_mutants, args, kwargs)
    return result 

strrev.__signature__ = _mutmut_signature(x_strrev__mutmut_orig)
x_strrev__mutmut_orig.__name__ = 'x_strrev'


def x_trimspace__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimspace: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value.strip())  # type: ignore


def x_trimspace__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimspace: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value.strip())  # type: ignore


def x_trimspace__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value.strip())  # type: ignore


def x_trimspace__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimspace: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value.strip())  # type: ignore


def x_trimspace__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimspace: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(None)  # type: ignore

x_trimspace__mutmut_mutants : ClassVar[MutantDict] = {
'x_trimspace__mutmut_1': x_trimspace__mutmut_1, 
    'x_trimspace__mutmut_2': x_trimspace__mutmut_2, 
    'x_trimspace__mutmut_3': x_trimspace__mutmut_3, 
    'x_trimspace__mutmut_4': x_trimspace__mutmut_4
}

def trimspace(*args, **kwargs):
    result = _mutmut_trampoline(x_trimspace__mutmut_orig, x_trimspace__mutmut_mutants, args, kwargs)
    return result 

trimspace.__signature__ = _mutmut_signature(x_trimspace__mutmut_orig)
x_trimspace__mutmut_orig.__name__ = 'x_trimspace'


def x_indent__mutmut_orig(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_1(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) and not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_2(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_3(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_4(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_5(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("XXindent: arguments must be stringsXX")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_6(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("INDENT: ARGUMENTS MUST BE STRINGS")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_7(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null and prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_8(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown and prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_9(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null and input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_10(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(None)
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_11(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_12(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(None)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_13(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = None
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_14(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(None).splitlines()]
    return CtyString().validate("\n".join(indented_lines))


def x_indent__mutmut_15(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate(None)


def x_indent__mutmut_16(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("\n".join(None))


def x_indent__mutmut_17(prefix_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(prefix_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError("indent: arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    if not input_val.value:
        return CtyString().validate(prefix_val.value)
    indented_lines = [f"{prefix_val.value}{line}" for line in str(input_val.value).splitlines()]
    return CtyString().validate("XX\nXX".join(indented_lines))

x_indent__mutmut_mutants : ClassVar[MutantDict] = {
'x_indent__mutmut_1': x_indent__mutmut_1, 
    'x_indent__mutmut_2': x_indent__mutmut_2, 
    'x_indent__mutmut_3': x_indent__mutmut_3, 
    'x_indent__mutmut_4': x_indent__mutmut_4, 
    'x_indent__mutmut_5': x_indent__mutmut_5, 
    'x_indent__mutmut_6': x_indent__mutmut_6, 
    'x_indent__mutmut_7': x_indent__mutmut_7, 
    'x_indent__mutmut_8': x_indent__mutmut_8, 
    'x_indent__mutmut_9': x_indent__mutmut_9, 
    'x_indent__mutmut_10': x_indent__mutmut_10, 
    'x_indent__mutmut_11': x_indent__mutmut_11, 
    'x_indent__mutmut_12': x_indent__mutmut_12, 
    'x_indent__mutmut_13': x_indent__mutmut_13, 
    'x_indent__mutmut_14': x_indent__mutmut_14, 
    'x_indent__mutmut_15': x_indent__mutmut_15, 
    'x_indent__mutmut_16': x_indent__mutmut_16, 
    'x_indent__mutmut_17': x_indent__mutmut_17
}

def indent(*args, **kwargs):
    result = _mutmut_trampoline(x_indent__mutmut_orig, x_indent__mutmut_mutants, args, kwargs)
    return result 

indent.__signature__ = _mutmut_signature(x_indent__mutmut_orig)
x_indent__mutmut_orig.__name__ = 'x_indent'


def x_substr__mutmut_orig(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_1(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber) and not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_2(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString) and not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_3(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_4(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_5(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_6(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError(None)
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_7(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("XXsubstr: arguments must be string, number, numberXX")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_8(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("SUBSTR: ARGUMENTS MUST BE STRING, NUMBER, NUMBER")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_9(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null and length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_10(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown and length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_11(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null and offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_12(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown and offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_13(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null and input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_14(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(None)
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_15(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = None
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_16(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(None)
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_17(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(None, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_18(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, None))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_19(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_20(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, ))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_21(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = None
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_22(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(None)
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_23(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(None, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_24(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, None))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_25(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_26(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, ))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_27(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset <= 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_28(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 1:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_29(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError(None)
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_30(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("XXsubstr: offset must be a non-negative integerXX")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_31(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("SUBSTR: OFFSET MUST BE A NON-NEGATIVE INTEGER")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_32(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length <= -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_33(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < +1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_34(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -2:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_35(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError(None)
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_36(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("XXsubstr: length must be non-negative or -1XX")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_37(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("SUBSTR: LENGTH MUST BE NON-NEGATIVE OR -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_38(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = None
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_39(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(None, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_40(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, None)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_41(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_42(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, )
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_43(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length != -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_44(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == +1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_45(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -2:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_46(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(None)
    return CtyString().validate(s[offset : offset + length])


def x_substr__mutmut_47(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(None)


def x_substr__mutmut_48(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset - length])

x_substr__mutmut_mutants : ClassVar[MutantDict] = {
'x_substr__mutmut_1': x_substr__mutmut_1, 
    'x_substr__mutmut_2': x_substr__mutmut_2, 
    'x_substr__mutmut_3': x_substr__mutmut_3, 
    'x_substr__mutmut_4': x_substr__mutmut_4, 
    'x_substr__mutmut_5': x_substr__mutmut_5, 
    'x_substr__mutmut_6': x_substr__mutmut_6, 
    'x_substr__mutmut_7': x_substr__mutmut_7, 
    'x_substr__mutmut_8': x_substr__mutmut_8, 
    'x_substr__mutmut_9': x_substr__mutmut_9, 
    'x_substr__mutmut_10': x_substr__mutmut_10, 
    'x_substr__mutmut_11': x_substr__mutmut_11, 
    'x_substr__mutmut_12': x_substr__mutmut_12, 
    'x_substr__mutmut_13': x_substr__mutmut_13, 
    'x_substr__mutmut_14': x_substr__mutmut_14, 
    'x_substr__mutmut_15': x_substr__mutmut_15, 
    'x_substr__mutmut_16': x_substr__mutmut_16, 
    'x_substr__mutmut_17': x_substr__mutmut_17, 
    'x_substr__mutmut_18': x_substr__mutmut_18, 
    'x_substr__mutmut_19': x_substr__mutmut_19, 
    'x_substr__mutmut_20': x_substr__mutmut_20, 
    'x_substr__mutmut_21': x_substr__mutmut_21, 
    'x_substr__mutmut_22': x_substr__mutmut_22, 
    'x_substr__mutmut_23': x_substr__mutmut_23, 
    'x_substr__mutmut_24': x_substr__mutmut_24, 
    'x_substr__mutmut_25': x_substr__mutmut_25, 
    'x_substr__mutmut_26': x_substr__mutmut_26, 
    'x_substr__mutmut_27': x_substr__mutmut_27, 
    'x_substr__mutmut_28': x_substr__mutmut_28, 
    'x_substr__mutmut_29': x_substr__mutmut_29, 
    'x_substr__mutmut_30': x_substr__mutmut_30, 
    'x_substr__mutmut_31': x_substr__mutmut_31, 
    'x_substr__mutmut_32': x_substr__mutmut_32, 
    'x_substr__mutmut_33': x_substr__mutmut_33, 
    'x_substr__mutmut_34': x_substr__mutmut_34, 
    'x_substr__mutmut_35': x_substr__mutmut_35, 
    'x_substr__mutmut_36': x_substr__mutmut_36, 
    'x_substr__mutmut_37': x_substr__mutmut_37, 
    'x_substr__mutmut_38': x_substr__mutmut_38, 
    'x_substr__mutmut_39': x_substr__mutmut_39, 
    'x_substr__mutmut_40': x_substr__mutmut_40, 
    'x_substr__mutmut_41': x_substr__mutmut_41, 
    'x_substr__mutmut_42': x_substr__mutmut_42, 
    'x_substr__mutmut_43': x_substr__mutmut_43, 
    'x_substr__mutmut_44': x_substr__mutmut_44, 
    'x_substr__mutmut_45': x_substr__mutmut_45, 
    'x_substr__mutmut_46': x_substr__mutmut_46, 
    'x_substr__mutmut_47': x_substr__mutmut_47, 
    'x_substr__mutmut_48': x_substr__mutmut_48
}

def substr(*args, **kwargs):
    result = _mutmut_trampoline(x_substr__mutmut_orig, x_substr__mutmut_mutants, args, kwargs)
    return result 

substr.__signature__ = _mutmut_signature(x_substr__mutmut_orig)
x_substr__mutmut_orig.__name__ = 'x_substr'


def x_trim__mutmut_orig(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_1(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) and not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_2(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_3(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_4(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_5(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("XXtrim: both arguments must be stringsXX")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_6(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("TRIM: BOTH ARGUMENTS MUST BE STRINGS")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_7(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null and cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_8(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown and cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_9(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null and input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_10(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(None)
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_11(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = None
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_12(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(None, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_13(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, None)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_14(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_15(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, )
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_16(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = None
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_17(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(None, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_18(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, None)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_19(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_20(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, )
    return CtyString().validate(input_str.strip(cutset_str))


def x_trim__mutmut_21(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(None)


def x_trim__mutmut_22(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(None))

x_trim__mutmut_mutants : ClassVar[MutantDict] = {
'x_trim__mutmut_1': x_trim__mutmut_1, 
    'x_trim__mutmut_2': x_trim__mutmut_2, 
    'x_trim__mutmut_3': x_trim__mutmut_3, 
    'x_trim__mutmut_4': x_trim__mutmut_4, 
    'x_trim__mutmut_5': x_trim__mutmut_5, 
    'x_trim__mutmut_6': x_trim__mutmut_6, 
    'x_trim__mutmut_7': x_trim__mutmut_7, 
    'x_trim__mutmut_8': x_trim__mutmut_8, 
    'x_trim__mutmut_9': x_trim__mutmut_9, 
    'x_trim__mutmut_10': x_trim__mutmut_10, 
    'x_trim__mutmut_11': x_trim__mutmut_11, 
    'x_trim__mutmut_12': x_trim__mutmut_12, 
    'x_trim__mutmut_13': x_trim__mutmut_13, 
    'x_trim__mutmut_14': x_trim__mutmut_14, 
    'x_trim__mutmut_15': x_trim__mutmut_15, 
    'x_trim__mutmut_16': x_trim__mutmut_16, 
    'x_trim__mutmut_17': x_trim__mutmut_17, 
    'x_trim__mutmut_18': x_trim__mutmut_18, 
    'x_trim__mutmut_19': x_trim__mutmut_19, 
    'x_trim__mutmut_20': x_trim__mutmut_20, 
    'x_trim__mutmut_21': x_trim__mutmut_21, 
    'x_trim__mutmut_22': x_trim__mutmut_22
}

def trim(*args, **kwargs):
    result = _mutmut_trampoline(x_trim__mutmut_orig, x_trim__mutmut_mutants, args, kwargs)
    return result 

trim.__signature__ = _mutmut_signature(x_trim__mutmut_orig)
x_trim__mutmut_orig.__name__ = 'x_trim'


def x_title__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.title())


def x_title__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.title())


def x_title__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.title())


def x_title__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.title())


def x_title__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = None
    return CtyString().validate(input_str.title())


def x_title__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(None, input_val.value)
    return CtyString().validate(input_str.title())


def x_title__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, None)
    return CtyString().validate(input_str.title())


def x_title__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(input_val.value)
    return CtyString().validate(input_str.title())


def x_title__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, )
    return CtyString().validate(input_str.title())


def x_title__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(None)

x_title__mutmut_mutants : ClassVar[MutantDict] = {
'x_title__mutmut_1': x_title__mutmut_1, 
    'x_title__mutmut_2': x_title__mutmut_2, 
    'x_title__mutmut_3': x_title__mutmut_3, 
    'x_title__mutmut_4': x_title__mutmut_4, 
    'x_title__mutmut_5': x_title__mutmut_5, 
    'x_title__mutmut_6': x_title__mutmut_6, 
    'x_title__mutmut_7': x_title__mutmut_7, 
    'x_title__mutmut_8': x_title__mutmut_8, 
    'x_title__mutmut_9': x_title__mutmut_9
}

def title(*args, **kwargs):
    result = _mutmut_trampoline(x_title__mutmut_orig, x_title__mutmut_mutants, args, kwargs)
    return result 

title.__signature__ = _mutmut_signature(x_title__mutmut_orig)
x_title__mutmut_orig.__name__ = 'x_title'


def x_trimprefix__mutmut_orig(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_1(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) and not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_2(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_3(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_4(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_5(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("XXtrimprefix: both arguments must be stringsXX")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_6(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("TRIMPREFIX: BOTH ARGUMENTS MUST BE STRINGS")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_7(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null and prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_8(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown and prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_9(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null and input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_10(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(None)
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_11(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = None
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_12(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(None, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_13(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, None)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_14(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_15(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, )
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_16(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = None
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_17(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(None, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_18(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, None)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_19(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_20(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, )
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_21(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(None):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


def x_trimprefix__mutmut_22(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(None)
    return input_val

x_trimprefix__mutmut_mutants : ClassVar[MutantDict] = {
'x_trimprefix__mutmut_1': x_trimprefix__mutmut_1, 
    'x_trimprefix__mutmut_2': x_trimprefix__mutmut_2, 
    'x_trimprefix__mutmut_3': x_trimprefix__mutmut_3, 
    'x_trimprefix__mutmut_4': x_trimprefix__mutmut_4, 
    'x_trimprefix__mutmut_5': x_trimprefix__mutmut_5, 
    'x_trimprefix__mutmut_6': x_trimprefix__mutmut_6, 
    'x_trimprefix__mutmut_7': x_trimprefix__mutmut_7, 
    'x_trimprefix__mutmut_8': x_trimprefix__mutmut_8, 
    'x_trimprefix__mutmut_9': x_trimprefix__mutmut_9, 
    'x_trimprefix__mutmut_10': x_trimprefix__mutmut_10, 
    'x_trimprefix__mutmut_11': x_trimprefix__mutmut_11, 
    'x_trimprefix__mutmut_12': x_trimprefix__mutmut_12, 
    'x_trimprefix__mutmut_13': x_trimprefix__mutmut_13, 
    'x_trimprefix__mutmut_14': x_trimprefix__mutmut_14, 
    'x_trimprefix__mutmut_15': x_trimprefix__mutmut_15, 
    'x_trimprefix__mutmut_16': x_trimprefix__mutmut_16, 
    'x_trimprefix__mutmut_17': x_trimprefix__mutmut_17, 
    'x_trimprefix__mutmut_18': x_trimprefix__mutmut_18, 
    'x_trimprefix__mutmut_19': x_trimprefix__mutmut_19, 
    'x_trimprefix__mutmut_20': x_trimprefix__mutmut_20, 
    'x_trimprefix__mutmut_21': x_trimprefix__mutmut_21, 
    'x_trimprefix__mutmut_22': x_trimprefix__mutmut_22
}

def trimprefix(*args, **kwargs):
    result = _mutmut_trampoline(x_trimprefix__mutmut_orig, x_trimprefix__mutmut_mutants, args, kwargs)
    return result 

trimprefix.__signature__ = _mutmut_signature(x_trimprefix__mutmut_orig)
x_trimprefix__mutmut_orig.__name__ = 'x_trimprefix'


def x_trimsuffix__mutmut_orig(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_1(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) and not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_2(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_3(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_4(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_5(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("XXtrimsuffix: both arguments must be stringsXX")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_6(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("TRIMSUFFIX: BOTH ARGUMENTS MUST BE STRINGS")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_7(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null and suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_8(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown and suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_9(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null and input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_10(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(None)
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_11(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = None
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_12(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(None, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_13(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, None)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_14(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_15(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, )
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_16(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = None
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_17(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(None, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_18(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, None)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_19(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_20(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, )
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_21(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(None):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def x_trimsuffix__mutmut_22(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(None)
    return input_val


def x_trimsuffix__mutmut_23(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: +len(suffix_str)])
    return input_val

x_trimsuffix__mutmut_mutants : ClassVar[MutantDict] = {
'x_trimsuffix__mutmut_1': x_trimsuffix__mutmut_1, 
    'x_trimsuffix__mutmut_2': x_trimsuffix__mutmut_2, 
    'x_trimsuffix__mutmut_3': x_trimsuffix__mutmut_3, 
    'x_trimsuffix__mutmut_4': x_trimsuffix__mutmut_4, 
    'x_trimsuffix__mutmut_5': x_trimsuffix__mutmut_5, 
    'x_trimsuffix__mutmut_6': x_trimsuffix__mutmut_6, 
    'x_trimsuffix__mutmut_7': x_trimsuffix__mutmut_7, 
    'x_trimsuffix__mutmut_8': x_trimsuffix__mutmut_8, 
    'x_trimsuffix__mutmut_9': x_trimsuffix__mutmut_9, 
    'x_trimsuffix__mutmut_10': x_trimsuffix__mutmut_10, 
    'x_trimsuffix__mutmut_11': x_trimsuffix__mutmut_11, 
    'x_trimsuffix__mutmut_12': x_trimsuffix__mutmut_12, 
    'x_trimsuffix__mutmut_13': x_trimsuffix__mutmut_13, 
    'x_trimsuffix__mutmut_14': x_trimsuffix__mutmut_14, 
    'x_trimsuffix__mutmut_15': x_trimsuffix__mutmut_15, 
    'x_trimsuffix__mutmut_16': x_trimsuffix__mutmut_16, 
    'x_trimsuffix__mutmut_17': x_trimsuffix__mutmut_17, 
    'x_trimsuffix__mutmut_18': x_trimsuffix__mutmut_18, 
    'x_trimsuffix__mutmut_19': x_trimsuffix__mutmut_19, 
    'x_trimsuffix__mutmut_20': x_trimsuffix__mutmut_20, 
    'x_trimsuffix__mutmut_21': x_trimsuffix__mutmut_21, 
    'x_trimsuffix__mutmut_22': x_trimsuffix__mutmut_22, 
    'x_trimsuffix__mutmut_23': x_trimsuffix__mutmut_23
}

def trimsuffix(*args, **kwargs):
    result = _mutmut_trampoline(x_trimsuffix__mutmut_orig, x_trimsuffix__mutmut_mutants, args, kwargs)
    return result 

trimsuffix.__signature__ = _mutmut_signature(x_trimsuffix__mutmut_orig)
x_trimsuffix__mutmut_orig.__name__ = 'x_trimsuffix'


def x_regex__mutmut_orig(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_1(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) and not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_2(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_3(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_4(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_5(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("XXregex: both arguments must be stringsXX")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_6(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("REGEX: BOTH ARGUMENTS MUST BE STRINGS")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_7(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null and pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_8(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown and pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_9(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null and input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_10(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(None)
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_11(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = None
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_12(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(None, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_13(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, None)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_14(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_15(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, )
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_16(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = None
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_17(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(None, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_18(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, None)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_19(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_20(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, )
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_21(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = None
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_22(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(None, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_23(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, None)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_24(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_25(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, )
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_26(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(None)
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_27(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(None) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_28(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(1) if match else "")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_29(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "XXXX")
    except re.error as e:
        raise CtyFunctionError(f"regex: invalid regular expression: {e}") from e


def x_regex__mutmut_30(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regex: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        match = re.search(pattern_str, input_str)
        return CtyString().validate(match.group(0) if match else "")
    except re.error as e:
        raise CtyFunctionError(None) from e

x_regex__mutmut_mutants : ClassVar[MutantDict] = {
'x_regex__mutmut_1': x_regex__mutmut_1, 
    'x_regex__mutmut_2': x_regex__mutmut_2, 
    'x_regex__mutmut_3': x_regex__mutmut_3, 
    'x_regex__mutmut_4': x_regex__mutmut_4, 
    'x_regex__mutmut_5': x_regex__mutmut_5, 
    'x_regex__mutmut_6': x_regex__mutmut_6, 
    'x_regex__mutmut_7': x_regex__mutmut_7, 
    'x_regex__mutmut_8': x_regex__mutmut_8, 
    'x_regex__mutmut_9': x_regex__mutmut_9, 
    'x_regex__mutmut_10': x_regex__mutmut_10, 
    'x_regex__mutmut_11': x_regex__mutmut_11, 
    'x_regex__mutmut_12': x_regex__mutmut_12, 
    'x_regex__mutmut_13': x_regex__mutmut_13, 
    'x_regex__mutmut_14': x_regex__mutmut_14, 
    'x_regex__mutmut_15': x_regex__mutmut_15, 
    'x_regex__mutmut_16': x_regex__mutmut_16, 
    'x_regex__mutmut_17': x_regex__mutmut_17, 
    'x_regex__mutmut_18': x_regex__mutmut_18, 
    'x_regex__mutmut_19': x_regex__mutmut_19, 
    'x_regex__mutmut_20': x_regex__mutmut_20, 
    'x_regex__mutmut_21': x_regex__mutmut_21, 
    'x_regex__mutmut_22': x_regex__mutmut_22, 
    'x_regex__mutmut_23': x_regex__mutmut_23, 
    'x_regex__mutmut_24': x_regex__mutmut_24, 
    'x_regex__mutmut_25': x_regex__mutmut_25, 
    'x_regex__mutmut_26': x_regex__mutmut_26, 
    'x_regex__mutmut_27': x_regex__mutmut_27, 
    'x_regex__mutmut_28': x_regex__mutmut_28, 
    'x_regex__mutmut_29': x_regex__mutmut_29, 
    'x_regex__mutmut_30': x_regex__mutmut_30
}

def regex(*args, **kwargs):
    result = _mutmut_trampoline(x_regex__mutmut_orig, x_regex__mutmut_mutants, args, kwargs)
    return result 

regex.__signature__ = _mutmut_signature(x_regex__mutmut_orig)
x_regex__mutmut_orig.__name__ = 'x_regex'


def x_regexall__mutmut_orig(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_1(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) and not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_2(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_3(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_4(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_5(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("XXregexall: both arguments must be stringsXX")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_6(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("REGEXALL: BOTH ARGUMENTS MUST BE STRINGS")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_7(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null and pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_8(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown and pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_9(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null and input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_10(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(None)
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_11(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=None))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_12(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = None
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_13(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(None, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_14(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, None)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_15(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_16(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, )
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_17(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = None
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_18(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(None, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_19(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, None)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_20(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_21(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, )
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_22(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = None
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_23(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(None, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_24(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, None)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_25(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_26(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, )
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_27(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = None
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_28(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(None)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_29(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=None).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(f"regexall: invalid regular expression: {e}") from e


def x_regexall__mutmut_30(input_val: CtyValue[Any], pattern_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(pattern_val.type, CtyString):
        raise CtyFunctionError("regexall: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    try:
        input_str = cast(str, input_val.value)
        pattern_str = cast(str, pattern_val.value)
        matches = re.findall(pattern_str, input_str)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(matches)
        return result
    except re.error as e:
        raise CtyFunctionError(None) from e

x_regexall__mutmut_mutants : ClassVar[MutantDict] = {
'x_regexall__mutmut_1': x_regexall__mutmut_1, 
    'x_regexall__mutmut_2': x_regexall__mutmut_2, 
    'x_regexall__mutmut_3': x_regexall__mutmut_3, 
    'x_regexall__mutmut_4': x_regexall__mutmut_4, 
    'x_regexall__mutmut_5': x_regexall__mutmut_5, 
    'x_regexall__mutmut_6': x_regexall__mutmut_6, 
    'x_regexall__mutmut_7': x_regexall__mutmut_7, 
    'x_regexall__mutmut_8': x_regexall__mutmut_8, 
    'x_regexall__mutmut_9': x_regexall__mutmut_9, 
    'x_regexall__mutmut_10': x_regexall__mutmut_10, 
    'x_regexall__mutmut_11': x_regexall__mutmut_11, 
    'x_regexall__mutmut_12': x_regexall__mutmut_12, 
    'x_regexall__mutmut_13': x_regexall__mutmut_13, 
    'x_regexall__mutmut_14': x_regexall__mutmut_14, 
    'x_regexall__mutmut_15': x_regexall__mutmut_15, 
    'x_regexall__mutmut_16': x_regexall__mutmut_16, 
    'x_regexall__mutmut_17': x_regexall__mutmut_17, 
    'x_regexall__mutmut_18': x_regexall__mutmut_18, 
    'x_regexall__mutmut_19': x_regexall__mutmut_19, 
    'x_regexall__mutmut_20': x_regexall__mutmut_20, 
    'x_regexall__mutmut_21': x_regexall__mutmut_21, 
    'x_regexall__mutmut_22': x_regexall__mutmut_22, 
    'x_regexall__mutmut_23': x_regexall__mutmut_23, 
    'x_regexall__mutmut_24': x_regexall__mutmut_24, 
    'x_regexall__mutmut_25': x_regexall__mutmut_25, 
    'x_regexall__mutmut_26': x_regexall__mutmut_26, 
    'x_regexall__mutmut_27': x_regexall__mutmut_27, 
    'x_regexall__mutmut_28': x_regexall__mutmut_28, 
    'x_regexall__mutmut_29': x_regexall__mutmut_29, 
    'x_regexall__mutmut_30': x_regexall__mutmut_30
}

def regexall(*args, **kwargs):
    result = _mutmut_trampoline(x_regexall__mutmut_orig, x_regexall__mutmut_mutants, args, kwargs)
    return result 

regexall.__signature__ = _mutmut_signature(x_regexall__mutmut_orig)
x_regexall__mutmut_orig.__name__ = 'x_regexall'


def x_upper__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = None
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(None, input_val.value)
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, None)
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(input_val.value)
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, )
    return CtyString().validate(input_str.upper())


def x_upper__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(None)


def x_upper__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.lower())

x_upper__mutmut_mutants : ClassVar[MutantDict] = {
'x_upper__mutmut_1': x_upper__mutmut_1, 
    'x_upper__mutmut_2': x_upper__mutmut_2, 
    'x_upper__mutmut_3': x_upper__mutmut_3, 
    'x_upper__mutmut_4': x_upper__mutmut_4, 
    'x_upper__mutmut_5': x_upper__mutmut_5, 
    'x_upper__mutmut_6': x_upper__mutmut_6, 
    'x_upper__mutmut_7': x_upper__mutmut_7, 
    'x_upper__mutmut_8': x_upper__mutmut_8, 
    'x_upper__mutmut_9': x_upper__mutmut_9, 
    'x_upper__mutmut_10': x_upper__mutmut_10
}

def upper(*args, **kwargs):
    result = _mutmut_trampoline(x_upper__mutmut_orig, x_upper__mutmut_mutants, args, kwargs)
    return result 

upper.__signature__ = _mutmut_signature(x_upper__mutmut_orig)
x_upper__mutmut_orig.__name__ = 'x_upper'


def x_lower__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = None
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(None, input_val.value)
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, None)
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(input_val.value)
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, )
    return CtyString().validate(input_str.lower())


def x_lower__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(None)


def x_lower__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.upper())

x_lower__mutmut_mutants : ClassVar[MutantDict] = {
'x_lower__mutmut_1': x_lower__mutmut_1, 
    'x_lower__mutmut_2': x_lower__mutmut_2, 
    'x_lower__mutmut_3': x_lower__mutmut_3, 
    'x_lower__mutmut_4': x_lower__mutmut_4, 
    'x_lower__mutmut_5': x_lower__mutmut_5, 
    'x_lower__mutmut_6': x_lower__mutmut_6, 
    'x_lower__mutmut_7': x_lower__mutmut_7, 
    'x_lower__mutmut_8': x_lower__mutmut_8, 
    'x_lower__mutmut_9': x_lower__mutmut_9, 
    'x_lower__mutmut_10': x_lower__mutmut_10
}

def lower(*args, **kwargs):
    result = _mutmut_trampoline(x_lower__mutmut_orig, x_lower__mutmut_mutants, args, kwargs)
    return result 

lower.__signature__ = _mutmut_signature(x_lower__mutmut_orig)
x_lower__mutmut_orig.__name__ = 'x_lower'


def x_join__mutmut_orig(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_1(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) and not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_2(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_3(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_4(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError(None)
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_5(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("XXjoin: arguments must be string and list/tupleXX")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_6(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("JOIN: ARGUMENTS MUST BE STRING AND LIST/TUPLE")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_7(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null and elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_8(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown and elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_9(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null and separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_10(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(None)

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_11(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = None
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_12(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(None, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_13(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, None)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_14(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_15(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, )
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_16(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = None
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_17(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(None, elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_18(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], None)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_19(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_20(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], )
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_21(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] & tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_22(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = None
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_23(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(None) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


def x_join__mutmut_24(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(None)


def x_join__mutmut_25(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(None))

x_join__mutmut_mutants : ClassVar[MutantDict] = {
'x_join__mutmut_1': x_join__mutmut_1, 
    'x_join__mutmut_2': x_join__mutmut_2, 
    'x_join__mutmut_3': x_join__mutmut_3, 
    'x_join__mutmut_4': x_join__mutmut_4, 
    'x_join__mutmut_5': x_join__mutmut_5, 
    'x_join__mutmut_6': x_join__mutmut_6, 
    'x_join__mutmut_7': x_join__mutmut_7, 
    'x_join__mutmut_8': x_join__mutmut_8, 
    'x_join__mutmut_9': x_join__mutmut_9, 
    'x_join__mutmut_10': x_join__mutmut_10, 
    'x_join__mutmut_11': x_join__mutmut_11, 
    'x_join__mutmut_12': x_join__mutmut_12, 
    'x_join__mutmut_13': x_join__mutmut_13, 
    'x_join__mutmut_14': x_join__mutmut_14, 
    'x_join__mutmut_15': x_join__mutmut_15, 
    'x_join__mutmut_16': x_join__mutmut_16, 
    'x_join__mutmut_17': x_join__mutmut_17, 
    'x_join__mutmut_18': x_join__mutmut_18, 
    'x_join__mutmut_19': x_join__mutmut_19, 
    'x_join__mutmut_20': x_join__mutmut_20, 
    'x_join__mutmut_21': x_join__mutmut_21, 
    'x_join__mutmut_22': x_join__mutmut_22, 
    'x_join__mutmut_23': x_join__mutmut_23, 
    'x_join__mutmut_24': x_join__mutmut_24, 
    'x_join__mutmut_25': x_join__mutmut_25
}

def join(*args, **kwargs):
    result = _mutmut_trampoline(x_join__mutmut_orig, x_join__mutmut_mutants, args, kwargs)
    return result 

join.__signature__ = _mutmut_signature(x_join__mutmut_orig)
x_join__mutmut_orig.__name__ = 'x_join'


def x_split__mutmut_orig(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_1(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) and not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_2(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_3(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_4(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError(None)
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_5(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("XXsplit: arguments must be stringsXX")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_6(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("SPLIT: ARGUMENTS MUST BE STRINGS")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_7(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null and text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_8(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown and text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_9(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null and separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_10(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(None)

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_11(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=None))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_12(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = None
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_13(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(None, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_14(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, None)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_15(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_16(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, )
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_17(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = None
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_18(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(None, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_19(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, None)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_20(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_21(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, )
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_22(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = None
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_23(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(None)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


def x_split__mutmut_24(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = None
    return result


def x_split__mutmut_25(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(None)
    return result


def x_split__mutmut_26(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=None).validate(parts)
    return result

x_split__mutmut_mutants : ClassVar[MutantDict] = {
'x_split__mutmut_1': x_split__mutmut_1, 
    'x_split__mutmut_2': x_split__mutmut_2, 
    'x_split__mutmut_3': x_split__mutmut_3, 
    'x_split__mutmut_4': x_split__mutmut_4, 
    'x_split__mutmut_5': x_split__mutmut_5, 
    'x_split__mutmut_6': x_split__mutmut_6, 
    'x_split__mutmut_7': x_split__mutmut_7, 
    'x_split__mutmut_8': x_split__mutmut_8, 
    'x_split__mutmut_9': x_split__mutmut_9, 
    'x_split__mutmut_10': x_split__mutmut_10, 
    'x_split__mutmut_11': x_split__mutmut_11, 
    'x_split__mutmut_12': x_split__mutmut_12, 
    'x_split__mutmut_13': x_split__mutmut_13, 
    'x_split__mutmut_14': x_split__mutmut_14, 
    'x_split__mutmut_15': x_split__mutmut_15, 
    'x_split__mutmut_16': x_split__mutmut_16, 
    'x_split__mutmut_17': x_split__mutmut_17, 
    'x_split__mutmut_18': x_split__mutmut_18, 
    'x_split__mutmut_19': x_split__mutmut_19, 
    'x_split__mutmut_20': x_split__mutmut_20, 
    'x_split__mutmut_21': x_split__mutmut_21, 
    'x_split__mutmut_22': x_split__mutmut_22, 
    'x_split__mutmut_23': x_split__mutmut_23, 
    'x_split__mutmut_24': x_split__mutmut_24, 
    'x_split__mutmut_25': x_split__mutmut_25, 
    'x_split__mutmut_26': x_split__mutmut_26
}

def split(*args, **kwargs):
    result = _mutmut_trampoline(x_split__mutmut_orig, x_split__mutmut_mutants, args, kwargs)
    return result 

split.__signature__ = _mutmut_signature(x_split__mutmut_orig)
x_split__mutmut_orig.__name__ = 'x_split'


def x_replace__mutmut_orig(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_1(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString) and not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_2(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString) and not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_3(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_4(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_5(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_6(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError(None)
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_7(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("XXreplace: all arguments must be stringsXX")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_8(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("REPLACE: ALL ARGUMENTS MUST BE STRINGS")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_9(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null and replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_10(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown and replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_11(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null and substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_12(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown and substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_13(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null and string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_14(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(None)

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_15(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = None
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_16(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(None, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_17(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, None)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_18(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_19(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, )
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_20(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = None
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_21(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(None, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_22(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, None)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_23(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_24(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, )
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_25(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = None
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_26(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(None, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_27(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, None)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_28(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_29(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, )
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_30(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = None
    return CtyString().validate(result)


def x_replace__mutmut_31(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(None, replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_32(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, None)
    return CtyString().validate(result)


def x_replace__mutmut_33(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(replacement_str)
    return CtyString().validate(result)


def x_replace__mutmut_34(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, )
    return CtyString().validate(result)


def x_replace__mutmut_35(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(None)

x_replace__mutmut_mutants : ClassVar[MutantDict] = {
'x_replace__mutmut_1': x_replace__mutmut_1, 
    'x_replace__mutmut_2': x_replace__mutmut_2, 
    'x_replace__mutmut_3': x_replace__mutmut_3, 
    'x_replace__mutmut_4': x_replace__mutmut_4, 
    'x_replace__mutmut_5': x_replace__mutmut_5, 
    'x_replace__mutmut_6': x_replace__mutmut_6, 
    'x_replace__mutmut_7': x_replace__mutmut_7, 
    'x_replace__mutmut_8': x_replace__mutmut_8, 
    'x_replace__mutmut_9': x_replace__mutmut_9, 
    'x_replace__mutmut_10': x_replace__mutmut_10, 
    'x_replace__mutmut_11': x_replace__mutmut_11, 
    'x_replace__mutmut_12': x_replace__mutmut_12, 
    'x_replace__mutmut_13': x_replace__mutmut_13, 
    'x_replace__mutmut_14': x_replace__mutmut_14, 
    'x_replace__mutmut_15': x_replace__mutmut_15, 
    'x_replace__mutmut_16': x_replace__mutmut_16, 
    'x_replace__mutmut_17': x_replace__mutmut_17, 
    'x_replace__mutmut_18': x_replace__mutmut_18, 
    'x_replace__mutmut_19': x_replace__mutmut_19, 
    'x_replace__mutmut_20': x_replace__mutmut_20, 
    'x_replace__mutmut_21': x_replace__mutmut_21, 
    'x_replace__mutmut_22': x_replace__mutmut_22, 
    'x_replace__mutmut_23': x_replace__mutmut_23, 
    'x_replace__mutmut_24': x_replace__mutmut_24, 
    'x_replace__mutmut_25': x_replace__mutmut_25, 
    'x_replace__mutmut_26': x_replace__mutmut_26, 
    'x_replace__mutmut_27': x_replace__mutmut_27, 
    'x_replace__mutmut_28': x_replace__mutmut_28, 
    'x_replace__mutmut_29': x_replace__mutmut_29, 
    'x_replace__mutmut_30': x_replace__mutmut_30, 
    'x_replace__mutmut_31': x_replace__mutmut_31, 
    'x_replace__mutmut_32': x_replace__mutmut_32, 
    'x_replace__mutmut_33': x_replace__mutmut_33, 
    'x_replace__mutmut_34': x_replace__mutmut_34, 
    'x_replace__mutmut_35': x_replace__mutmut_35
}

def replace(*args, **kwargs):
    result = _mutmut_trampoline(x_replace__mutmut_orig, x_replace__mutmut_mutants, args, kwargs)
    return result 

replace.__signature__ = _mutmut_signature(x_replace__mutmut_orig)
x_replace__mutmut_orig.__name__ = 'x_replace'


def x_regexreplace__mutmut_orig(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_1(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString) and not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_2(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString) and not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_3(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_4(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_5(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_6(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError(None)
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_7(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("XXregexreplace: all arguments must be stringsXX")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_8(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("REGEXREPLACE: ALL ARGUMENTS MUST BE STRINGS")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_9(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null and replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_10(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown and replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_11(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null and pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_12(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown and pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_13(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null and string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_14(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(None)

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_15(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = None
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_16(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(None, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_17(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, None)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_18(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_19(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, )
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_20(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = None
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_21(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(None, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_22(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, None)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_23(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_24(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, )
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_25(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = None
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_26(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(None, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_27(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, None)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_28(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_29(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, )
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_30(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = None
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_31(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(None, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_32(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, None, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_33(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, None)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_34(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_35(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_36(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, )
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_37(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(None)
    except re.error as e:
        raise CtyFunctionError(f"regexreplace: invalid regular expression: {e}") from e


def x_regexreplace__mutmut_38(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("regexreplace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    try:
        string_str = cast(str, string.value)
        pattern_str = cast(str, pattern.value)
        replacement_str = cast(str, replacement.value)
        result = re.sub(pattern_str, replacement_str, string_str)
        return CtyString().validate(result)
    except re.error as e:
        raise CtyFunctionError(None) from e

x_regexreplace__mutmut_mutants : ClassVar[MutantDict] = {
'x_regexreplace__mutmut_1': x_regexreplace__mutmut_1, 
    'x_regexreplace__mutmut_2': x_regexreplace__mutmut_2, 
    'x_regexreplace__mutmut_3': x_regexreplace__mutmut_3, 
    'x_regexreplace__mutmut_4': x_regexreplace__mutmut_4, 
    'x_regexreplace__mutmut_5': x_regexreplace__mutmut_5, 
    'x_regexreplace__mutmut_6': x_regexreplace__mutmut_6, 
    'x_regexreplace__mutmut_7': x_regexreplace__mutmut_7, 
    'x_regexreplace__mutmut_8': x_regexreplace__mutmut_8, 
    'x_regexreplace__mutmut_9': x_regexreplace__mutmut_9, 
    'x_regexreplace__mutmut_10': x_regexreplace__mutmut_10, 
    'x_regexreplace__mutmut_11': x_regexreplace__mutmut_11, 
    'x_regexreplace__mutmut_12': x_regexreplace__mutmut_12, 
    'x_regexreplace__mutmut_13': x_regexreplace__mutmut_13, 
    'x_regexreplace__mutmut_14': x_regexreplace__mutmut_14, 
    'x_regexreplace__mutmut_15': x_regexreplace__mutmut_15, 
    'x_regexreplace__mutmut_16': x_regexreplace__mutmut_16, 
    'x_regexreplace__mutmut_17': x_regexreplace__mutmut_17, 
    'x_regexreplace__mutmut_18': x_regexreplace__mutmut_18, 
    'x_regexreplace__mutmut_19': x_regexreplace__mutmut_19, 
    'x_regexreplace__mutmut_20': x_regexreplace__mutmut_20, 
    'x_regexreplace__mutmut_21': x_regexreplace__mutmut_21, 
    'x_regexreplace__mutmut_22': x_regexreplace__mutmut_22, 
    'x_regexreplace__mutmut_23': x_regexreplace__mutmut_23, 
    'x_regexreplace__mutmut_24': x_regexreplace__mutmut_24, 
    'x_regexreplace__mutmut_25': x_regexreplace__mutmut_25, 
    'x_regexreplace__mutmut_26': x_regexreplace__mutmut_26, 
    'x_regexreplace__mutmut_27': x_regexreplace__mutmut_27, 
    'x_regexreplace__mutmut_28': x_regexreplace__mutmut_28, 
    'x_regexreplace__mutmut_29': x_regexreplace__mutmut_29, 
    'x_regexreplace__mutmut_30': x_regexreplace__mutmut_30, 
    'x_regexreplace__mutmut_31': x_regexreplace__mutmut_31, 
    'x_regexreplace__mutmut_32': x_regexreplace__mutmut_32, 
    'x_regexreplace__mutmut_33': x_regexreplace__mutmut_33, 
    'x_regexreplace__mutmut_34': x_regexreplace__mutmut_34, 
    'x_regexreplace__mutmut_35': x_regexreplace__mutmut_35, 
    'x_regexreplace__mutmut_36': x_regexreplace__mutmut_36, 
    'x_regexreplace__mutmut_37': x_regexreplace__mutmut_37, 
    'x_regexreplace__mutmut_38': x_regexreplace__mutmut_38
}

def regexreplace(*args, **kwargs):
    result = _mutmut_trampoline(x_regexreplace__mutmut_orig, x_regexreplace__mutmut_mutants, args, kwargs)
    return result 

regexreplace.__signature__ = _mutmut_signature(x_regexreplace__mutmut_orig)
x_regexreplace__mutmut_orig.__name__ = 'x_regexreplace'


# 🌊🪢🔣🪄
