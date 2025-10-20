# pyvider/cty/functions/encoding_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import csv
import io
import json
from typing import Any, cast

from pyvider.cty import CtyDynamic, CtyList, CtyObject, CtyString, CtyValue
from pyvider.cty.conversion import cty_to_native
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


def x_jsonencode__mutmut_orig(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        native_val = cty_to_native(val)
        return CtyString().validate(json.dumps(native_val))
    except Exception as e:
        raise CtyFunctionError(f"jsonencode: failed to encode value: {e}") from e


def x_jsonencode__mutmut_1(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(None)
    try:
        native_val = cty_to_native(val)
        return CtyString().validate(json.dumps(native_val))
    except Exception as e:
        raise CtyFunctionError(f"jsonencode: failed to encode value: {e}") from e


def x_jsonencode__mutmut_2(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        native_val = None
        return CtyString().validate(json.dumps(native_val))
    except Exception as e:
        raise CtyFunctionError(f"jsonencode: failed to encode value: {e}") from e


def x_jsonencode__mutmut_3(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        native_val = cty_to_native(None)
        return CtyString().validate(json.dumps(native_val))
    except Exception as e:
        raise CtyFunctionError(f"jsonencode: failed to encode value: {e}") from e


def x_jsonencode__mutmut_4(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        native_val = cty_to_native(val)
        return CtyString().validate(None)
    except Exception as e:
        raise CtyFunctionError(f"jsonencode: failed to encode value: {e}") from e


def x_jsonencode__mutmut_5(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        native_val = cty_to_native(val)
        return CtyString().validate(json.dumps(None))
    except Exception as e:
        raise CtyFunctionError(f"jsonencode: failed to encode value: {e}") from e


def x_jsonencode__mutmut_6(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(CtyString())
    try:
        native_val = cty_to_native(val)
        return CtyString().validate(json.dumps(native_val))
    except Exception as e:
        raise CtyFunctionError(None) from e

x_jsonencode__mutmut_mutants : ClassVar[MutantDict] = {
'x_jsonencode__mutmut_1': x_jsonencode__mutmut_1, 
    'x_jsonencode__mutmut_2': x_jsonencode__mutmut_2, 
    'x_jsonencode__mutmut_3': x_jsonencode__mutmut_3, 
    'x_jsonencode__mutmut_4': x_jsonencode__mutmut_4, 
    'x_jsonencode__mutmut_5': x_jsonencode__mutmut_5, 
    'x_jsonencode__mutmut_6': x_jsonencode__mutmut_6
}

def jsonencode(*args, **kwargs):
    result = _mutmut_trampoline(x_jsonencode__mutmut_orig, x_jsonencode__mutmut_mutants, args, kwargs)
    return result 

jsonencode.__signature__ = _mutmut_signature(x_jsonencode__mutmut_orig)
x_jsonencode__mutmut_orig.__name__ = 'x_jsonencode'


def x_jsondecode__mutmut_orig(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_1(val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_2(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(None)
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_3(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown and val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_4(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(None)
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_5(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = None
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_6(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(None, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_7(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, None)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_8(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_9(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, )
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_10(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = None
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_11(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(None)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_12(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = None
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_13(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(None)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(f"jsondecode: failed to decode JSON: {e}") from e


def x_jsondecode__mutmut_14(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"jsondecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        val_str = cast(str, val.value)
        native_val = json.loads(val_str)
        result: CtyValue[Any] = CtyDynamic().validate(native_val)
        return result
    except json.JSONDecodeError as e:
        raise CtyFunctionError(None) from e

x_jsondecode__mutmut_mutants : ClassVar[MutantDict] = {
'x_jsondecode__mutmut_1': x_jsondecode__mutmut_1, 
    'x_jsondecode__mutmut_2': x_jsondecode__mutmut_2, 
    'x_jsondecode__mutmut_3': x_jsondecode__mutmut_3, 
    'x_jsondecode__mutmut_4': x_jsondecode__mutmut_4, 
    'x_jsondecode__mutmut_5': x_jsondecode__mutmut_5, 
    'x_jsondecode__mutmut_6': x_jsondecode__mutmut_6, 
    'x_jsondecode__mutmut_7': x_jsondecode__mutmut_7, 
    'x_jsondecode__mutmut_8': x_jsondecode__mutmut_8, 
    'x_jsondecode__mutmut_9': x_jsondecode__mutmut_9, 
    'x_jsondecode__mutmut_10': x_jsondecode__mutmut_10, 
    'x_jsondecode__mutmut_11': x_jsondecode__mutmut_11, 
    'x_jsondecode__mutmut_12': x_jsondecode__mutmut_12, 
    'x_jsondecode__mutmut_13': x_jsondecode__mutmut_13, 
    'x_jsondecode__mutmut_14': x_jsondecode__mutmut_14
}

def jsondecode(*args, **kwargs):
    result = _mutmut_trampoline(x_jsondecode__mutmut_orig, x_jsondecode__mutmut_mutants, args, kwargs)
    return result 

jsondecode.__signature__ = _mutmut_signature(x_jsondecode__mutmut_orig)
x_jsondecode__mutmut_orig.__name__ = 'x_jsondecode'


def x_csvdecode__mutmut_orig(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_1(val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_2(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(None)
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_3(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown and val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_4(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(None)

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_5(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=None))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_6(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject(None)))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_7(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = None
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_8(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(None, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_9(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, None)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_10(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_11(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, )
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_12(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = None
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_13(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(None)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_14(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = None
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_15(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(None)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_16(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = None
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_17(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(None)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_18(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = None
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_19(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(None)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_20(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=None).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(f"csvdecode: failed to decode CSV: {e}") from e


def x_csvdecode__mutmut_21(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(f"csvdecode: argument must be a string, got {val.type.ctype}")
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyList(element_type=CtyObject({})))

    val_str = cast(str, val.value)
    f = io.StringIO(val_str)
    try:
        # The csv module can raise csv.Error for malformed data
        reader = csv.DictReader(f)
        rows = list(reader)
        result: CtyValue[Any] = CtyList(element_type=CtyDynamic()).validate(rows)
        return result
    except Exception as e:
        raise CtyFunctionError(None) from e

x_csvdecode__mutmut_mutants : ClassVar[MutantDict] = {
'x_csvdecode__mutmut_1': x_csvdecode__mutmut_1, 
    'x_csvdecode__mutmut_2': x_csvdecode__mutmut_2, 
    'x_csvdecode__mutmut_3': x_csvdecode__mutmut_3, 
    'x_csvdecode__mutmut_4': x_csvdecode__mutmut_4, 
    'x_csvdecode__mutmut_5': x_csvdecode__mutmut_5, 
    'x_csvdecode__mutmut_6': x_csvdecode__mutmut_6, 
    'x_csvdecode__mutmut_7': x_csvdecode__mutmut_7, 
    'x_csvdecode__mutmut_8': x_csvdecode__mutmut_8, 
    'x_csvdecode__mutmut_9': x_csvdecode__mutmut_9, 
    'x_csvdecode__mutmut_10': x_csvdecode__mutmut_10, 
    'x_csvdecode__mutmut_11': x_csvdecode__mutmut_11, 
    'x_csvdecode__mutmut_12': x_csvdecode__mutmut_12, 
    'x_csvdecode__mutmut_13': x_csvdecode__mutmut_13, 
    'x_csvdecode__mutmut_14': x_csvdecode__mutmut_14, 
    'x_csvdecode__mutmut_15': x_csvdecode__mutmut_15, 
    'x_csvdecode__mutmut_16': x_csvdecode__mutmut_16, 
    'x_csvdecode__mutmut_17': x_csvdecode__mutmut_17, 
    'x_csvdecode__mutmut_18': x_csvdecode__mutmut_18, 
    'x_csvdecode__mutmut_19': x_csvdecode__mutmut_19, 
    'x_csvdecode__mutmut_20': x_csvdecode__mutmut_20, 
    'x_csvdecode__mutmut_21': x_csvdecode__mutmut_21
}

def csvdecode(*args, **kwargs):
    result = _mutmut_trampoline(x_csvdecode__mutmut_orig, x_csvdecode__mutmut_mutants, args, kwargs)
    return result 

csvdecode.__signature__ = _mutmut_signature(x_csvdecode__mutmut_orig)
x_csvdecode__mutmut_orig.__name__ = 'x_csvdecode'


# 🌊🪢🔣🪄
