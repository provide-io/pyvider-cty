# pyvider/cty/functions/datetime_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Any, cast

from pyvider.cty import CtyString, CtyValue
from pyvider.cty.config.defaults import (
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    SECONDS_PER_SECOND,
)
from pyvider.cty.exceptions import CtyFunctionError

# A simplified mapping from Go's time layout to Python's strftime format.
# This is not exhaustive but covers common cases.
GO_TO_PYTHON_FORMAT_MAP = {
    "2006": "%Y",
    "06": "%y",
    "01": "%m",
    "Jan": "%b",
    "January": "%B",
    "02": "%d",
    "_2": "%e",
    "15": "%H",
    "03": "%I",
    "04": "%M",
    "05": "%S",
    "PM": "%p",
    "MST": "%Z",
    "Z07:00": "%z",
}
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


def x__translate_go_format__mutmut_orig(go_fmt: str) -> str:
    py_fmt = go_fmt
    for go, py in GO_TO_PYTHON_FORMAT_MAP.items():
        py_fmt = py_fmt.replace(go, py)
    return py_fmt


def x__translate_go_format__mutmut_1(go_fmt: str) -> str:
    py_fmt = None
    for go, py in GO_TO_PYTHON_FORMAT_MAP.items():
        py_fmt = py_fmt.replace(go, py)
    return py_fmt


def x__translate_go_format__mutmut_2(go_fmt: str) -> str:
    py_fmt = go_fmt
    for go, py in GO_TO_PYTHON_FORMAT_MAP.items():
        py_fmt = None
    return py_fmt


def x__translate_go_format__mutmut_3(go_fmt: str) -> str:
    py_fmt = go_fmt
    for go, py in GO_TO_PYTHON_FORMAT_MAP.items():
        py_fmt = py_fmt.replace(None, py)
    return py_fmt


def x__translate_go_format__mutmut_4(go_fmt: str) -> str:
    py_fmt = go_fmt
    for go, py in GO_TO_PYTHON_FORMAT_MAP.items():
        py_fmt = py_fmt.replace(go, None)
    return py_fmt


def x__translate_go_format__mutmut_5(go_fmt: str) -> str:
    py_fmt = go_fmt
    for go, py in GO_TO_PYTHON_FORMAT_MAP.items():
        py_fmt = py_fmt.replace(py)
    return py_fmt


def x__translate_go_format__mutmut_6(go_fmt: str) -> str:
    py_fmt = go_fmt
    for go, py in GO_TO_PYTHON_FORMAT_MAP.items():
        py_fmt = py_fmt.replace(go, )
    return py_fmt

x__translate_go_format__mutmut_mutants : ClassVar[MutantDict] = {
'x__translate_go_format__mutmut_1': x__translate_go_format__mutmut_1, 
    'x__translate_go_format__mutmut_2': x__translate_go_format__mutmut_2, 
    'x__translate_go_format__mutmut_3': x__translate_go_format__mutmut_3, 
    'x__translate_go_format__mutmut_4': x__translate_go_format__mutmut_4, 
    'x__translate_go_format__mutmut_5': x__translate_go_format__mutmut_5, 
    'x__translate_go_format__mutmut_6': x__translate_go_format__mutmut_6
}

def _translate_go_format(*args, **kwargs):
    result = _mutmut_trampoline(x__translate_go_format__mutmut_orig, x__translate_go_format__mutmut_mutants, args, kwargs)
    return result 

_translate_go_format.__signature__ = _mutmut_signature(x__translate_go_format__mutmut_orig)
x__translate_go_format__mutmut_orig.__name__ = 'x__translate_go_format'


def x_formatdate__mutmut_orig(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_1(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) and not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_2(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_3(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_4(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError(None)
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_5(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("XXformatdate: arguments must be stringsXX")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_6(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("FORMATDATE: ARGUMENTS MUST BE STRINGS")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_7(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown and timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_8(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null and timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_9(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown and spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_10(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(None)
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_11(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = None
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_12(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(None, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_13(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, None)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_14(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_15(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, )
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_16(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = None
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_17(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(None, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_18(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, None)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_19(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_20(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, )
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_21(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = None
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_22(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(None)
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_23(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace(None, "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_24(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", None))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_25(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_26(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", ))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_27(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("XXZXX", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_28(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_29(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "XX+00:00XX"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_30(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = None
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_31(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(None)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_32(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(None)
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_33(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(None))
    except ValueError as e:
        raise CtyFunctionError(f"formatdate: invalid timestamp format: {e}") from e


def x_formatdate__mutmut_34(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(spec.type, CtyString) or not isinstance(timestamp.type, CtyString):
        raise CtyFunctionError("formatdate: arguments must be strings")
    if spec.is_unknown or spec.is_null or timestamp.is_unknown or timestamp.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        spec_str = cast(str, spec.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        py_format_spec = _translate_go_format(spec_str)
        return CtyString().validate(dt.strftime(py_format_spec))
    except ValueError as e:
        raise CtyFunctionError(None) from e

x_formatdate__mutmut_mutants : ClassVar[MutantDict] = {
'x_formatdate__mutmut_1': x_formatdate__mutmut_1, 
    'x_formatdate__mutmut_2': x_formatdate__mutmut_2, 
    'x_formatdate__mutmut_3': x_formatdate__mutmut_3, 
    'x_formatdate__mutmut_4': x_formatdate__mutmut_4, 
    'x_formatdate__mutmut_5': x_formatdate__mutmut_5, 
    'x_formatdate__mutmut_6': x_formatdate__mutmut_6, 
    'x_formatdate__mutmut_7': x_formatdate__mutmut_7, 
    'x_formatdate__mutmut_8': x_formatdate__mutmut_8, 
    'x_formatdate__mutmut_9': x_formatdate__mutmut_9, 
    'x_formatdate__mutmut_10': x_formatdate__mutmut_10, 
    'x_formatdate__mutmut_11': x_formatdate__mutmut_11, 
    'x_formatdate__mutmut_12': x_formatdate__mutmut_12, 
    'x_formatdate__mutmut_13': x_formatdate__mutmut_13, 
    'x_formatdate__mutmut_14': x_formatdate__mutmut_14, 
    'x_formatdate__mutmut_15': x_formatdate__mutmut_15, 
    'x_formatdate__mutmut_16': x_formatdate__mutmut_16, 
    'x_formatdate__mutmut_17': x_formatdate__mutmut_17, 
    'x_formatdate__mutmut_18': x_formatdate__mutmut_18, 
    'x_formatdate__mutmut_19': x_formatdate__mutmut_19, 
    'x_formatdate__mutmut_20': x_formatdate__mutmut_20, 
    'x_formatdate__mutmut_21': x_formatdate__mutmut_21, 
    'x_formatdate__mutmut_22': x_formatdate__mutmut_22, 
    'x_formatdate__mutmut_23': x_formatdate__mutmut_23, 
    'x_formatdate__mutmut_24': x_formatdate__mutmut_24, 
    'x_formatdate__mutmut_25': x_formatdate__mutmut_25, 
    'x_formatdate__mutmut_26': x_formatdate__mutmut_26, 
    'x_formatdate__mutmut_27': x_formatdate__mutmut_27, 
    'x_formatdate__mutmut_28': x_formatdate__mutmut_28, 
    'x_formatdate__mutmut_29': x_formatdate__mutmut_29, 
    'x_formatdate__mutmut_30': x_formatdate__mutmut_30, 
    'x_formatdate__mutmut_31': x_formatdate__mutmut_31, 
    'x_formatdate__mutmut_32': x_formatdate__mutmut_32, 
    'x_formatdate__mutmut_33': x_formatdate__mutmut_33, 
    'x_formatdate__mutmut_34': x_formatdate__mutmut_34
}

def formatdate(*args, **kwargs):
    result = _mutmut_trampoline(x_formatdate__mutmut_orig, x_formatdate__mutmut_mutants, args, kwargs)
    return result 

formatdate.__signature__ = _mutmut_signature(x_formatdate__mutmut_orig)
x_formatdate__mutmut_orig.__name__ = 'x_formatdate'


def x__parse_duration__mutmut_orig(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_1(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_2(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(None, duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_3(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", None):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_4(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_5(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", ):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_6(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"XX(\d+\.?\d*[hms])+XX", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_7(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_8(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[HMS])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_9(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(None)

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_10(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = None
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_11(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(None, duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_12(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", None)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_13(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_14(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", )
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_15(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"XX(\d+\.?\d*)([hms])XX", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_16(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_17(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([HMS])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_18(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = None
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_19(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 1.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_20(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = None
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_21(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(None)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_22(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_23(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_24(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_25(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "XXhXX":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_26(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "H":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_27(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds = val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_28(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds -= val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_29(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val / SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_30(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "XXmXX":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_31(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "M":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_32(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds = val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_33(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds -= val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_34(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val / SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_35(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "XXsXX":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_36(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "S":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_37(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds = val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_38(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds -= val * SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_39(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val / SECONDS_PER_SECOND
    return timedelta(seconds=total_seconds)


def x__parse_duration__mutmut_40(duration_str: str) -> timedelta:
    # This regex now ensures the entire string consists only of valid duration parts.
    if not re.fullmatch(r"(\d+\.?\d*[hms])+", duration_str):
        raise ValueError(f"Invalid duration string format: '{duration_str}'")

    parts = re.findall(r"(\d+\.?\d*)([hms])", duration_str)
    total_seconds: float = 0.0
    for value, unit in parts:
        val = float(value)
        match unit:
            case "h":
                total_seconds += val * SECONDS_PER_HOUR
            case "m":
                total_seconds += val * SECONDS_PER_MINUTE
            case "s":
                total_seconds += val * SECONDS_PER_SECOND
    return timedelta(seconds=None)

x__parse_duration__mutmut_mutants : ClassVar[MutantDict] = {
'x__parse_duration__mutmut_1': x__parse_duration__mutmut_1, 
    'x__parse_duration__mutmut_2': x__parse_duration__mutmut_2, 
    'x__parse_duration__mutmut_3': x__parse_duration__mutmut_3, 
    'x__parse_duration__mutmut_4': x__parse_duration__mutmut_4, 
    'x__parse_duration__mutmut_5': x__parse_duration__mutmut_5, 
    'x__parse_duration__mutmut_6': x__parse_duration__mutmut_6, 
    'x__parse_duration__mutmut_7': x__parse_duration__mutmut_7, 
    'x__parse_duration__mutmut_8': x__parse_duration__mutmut_8, 
    'x__parse_duration__mutmut_9': x__parse_duration__mutmut_9, 
    'x__parse_duration__mutmut_10': x__parse_duration__mutmut_10, 
    'x__parse_duration__mutmut_11': x__parse_duration__mutmut_11, 
    'x__parse_duration__mutmut_12': x__parse_duration__mutmut_12, 
    'x__parse_duration__mutmut_13': x__parse_duration__mutmut_13, 
    'x__parse_duration__mutmut_14': x__parse_duration__mutmut_14, 
    'x__parse_duration__mutmut_15': x__parse_duration__mutmut_15, 
    'x__parse_duration__mutmut_16': x__parse_duration__mutmut_16, 
    'x__parse_duration__mutmut_17': x__parse_duration__mutmut_17, 
    'x__parse_duration__mutmut_18': x__parse_duration__mutmut_18, 
    'x__parse_duration__mutmut_19': x__parse_duration__mutmut_19, 
    'x__parse_duration__mutmut_20': x__parse_duration__mutmut_20, 
    'x__parse_duration__mutmut_21': x__parse_duration__mutmut_21, 
    'x__parse_duration__mutmut_22': x__parse_duration__mutmut_22, 
    'x__parse_duration__mutmut_23': x__parse_duration__mutmut_23, 
    'x__parse_duration__mutmut_24': x__parse_duration__mutmut_24, 
    'x__parse_duration__mutmut_25': x__parse_duration__mutmut_25, 
    'x__parse_duration__mutmut_26': x__parse_duration__mutmut_26, 
    'x__parse_duration__mutmut_27': x__parse_duration__mutmut_27, 
    'x__parse_duration__mutmut_28': x__parse_duration__mutmut_28, 
    'x__parse_duration__mutmut_29': x__parse_duration__mutmut_29, 
    'x__parse_duration__mutmut_30': x__parse_duration__mutmut_30, 
    'x__parse_duration__mutmut_31': x__parse_duration__mutmut_31, 
    'x__parse_duration__mutmut_32': x__parse_duration__mutmut_32, 
    'x__parse_duration__mutmut_33': x__parse_duration__mutmut_33, 
    'x__parse_duration__mutmut_34': x__parse_duration__mutmut_34, 
    'x__parse_duration__mutmut_35': x__parse_duration__mutmut_35, 
    'x__parse_duration__mutmut_36': x__parse_duration__mutmut_36, 
    'x__parse_duration__mutmut_37': x__parse_duration__mutmut_37, 
    'x__parse_duration__mutmut_38': x__parse_duration__mutmut_38, 
    'x__parse_duration__mutmut_39': x__parse_duration__mutmut_39, 
    'x__parse_duration__mutmut_40': x__parse_duration__mutmut_40
}

def _parse_duration(*args, **kwargs):
    result = _mutmut_trampoline(x__parse_duration__mutmut_orig, x__parse_duration__mutmut_mutants, args, kwargs)
    return result 

_parse_duration.__signature__ = _mutmut_signature(x__parse_duration__mutmut_orig)
x__parse_duration__mutmut_orig.__name__ = 'x__parse_duration'


def x_timeadd__mutmut_orig(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_1(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) and not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_2(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_3(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_4(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError(None)
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_5(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("XXtimeadd: arguments must be stringsXX")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_6(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("TIMEADD: ARGUMENTS MUST BE STRINGS")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_7(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown and duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_8(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null and duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_9(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown and timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_10(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(None)
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_11(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = None
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_12(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(None, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_13(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, None)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_14(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_15(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, )
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_16(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = None
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_17(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(None, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_18(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, None)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_19(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_20(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, )
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_21(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = None
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_22(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(None)
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_23(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace(None, "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_24(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", None))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_25(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_26(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", ))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_27(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("XXZXX", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_28(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_29(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "XX+00:00XX"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_30(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = None
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_31(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(None)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_32(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = None
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_33(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt - td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_34(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(None)
    except ValueError as e:
        raise CtyFunctionError(f"timeadd: invalid argument format: {e}") from e


def x_timeadd__mutmut_35(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(timestamp.type, CtyString) or not isinstance(duration.type, CtyString):
        raise CtyFunctionError("timeadd: arguments must be strings")
    if timestamp.is_unknown or timestamp.is_null or duration.is_unknown or duration.is_null:
        return CtyValue.unknown(CtyString())
    try:
        timestamp_str = cast(str, timestamp.value)
        duration_str = cast(str, duration.value)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        td = _parse_duration(duration_str)
        new_dt = dt + td
        return CtyString().validate(new_dt.isoformat())
    except ValueError as e:
        raise CtyFunctionError(None) from e

x_timeadd__mutmut_mutants : ClassVar[MutantDict] = {
'x_timeadd__mutmut_1': x_timeadd__mutmut_1, 
    'x_timeadd__mutmut_2': x_timeadd__mutmut_2, 
    'x_timeadd__mutmut_3': x_timeadd__mutmut_3, 
    'x_timeadd__mutmut_4': x_timeadd__mutmut_4, 
    'x_timeadd__mutmut_5': x_timeadd__mutmut_5, 
    'x_timeadd__mutmut_6': x_timeadd__mutmut_6, 
    'x_timeadd__mutmut_7': x_timeadd__mutmut_7, 
    'x_timeadd__mutmut_8': x_timeadd__mutmut_8, 
    'x_timeadd__mutmut_9': x_timeadd__mutmut_9, 
    'x_timeadd__mutmut_10': x_timeadd__mutmut_10, 
    'x_timeadd__mutmut_11': x_timeadd__mutmut_11, 
    'x_timeadd__mutmut_12': x_timeadd__mutmut_12, 
    'x_timeadd__mutmut_13': x_timeadd__mutmut_13, 
    'x_timeadd__mutmut_14': x_timeadd__mutmut_14, 
    'x_timeadd__mutmut_15': x_timeadd__mutmut_15, 
    'x_timeadd__mutmut_16': x_timeadd__mutmut_16, 
    'x_timeadd__mutmut_17': x_timeadd__mutmut_17, 
    'x_timeadd__mutmut_18': x_timeadd__mutmut_18, 
    'x_timeadd__mutmut_19': x_timeadd__mutmut_19, 
    'x_timeadd__mutmut_20': x_timeadd__mutmut_20, 
    'x_timeadd__mutmut_21': x_timeadd__mutmut_21, 
    'x_timeadd__mutmut_22': x_timeadd__mutmut_22, 
    'x_timeadd__mutmut_23': x_timeadd__mutmut_23, 
    'x_timeadd__mutmut_24': x_timeadd__mutmut_24, 
    'x_timeadd__mutmut_25': x_timeadd__mutmut_25, 
    'x_timeadd__mutmut_26': x_timeadd__mutmut_26, 
    'x_timeadd__mutmut_27': x_timeadd__mutmut_27, 
    'x_timeadd__mutmut_28': x_timeadd__mutmut_28, 
    'x_timeadd__mutmut_29': x_timeadd__mutmut_29, 
    'x_timeadd__mutmut_30': x_timeadd__mutmut_30, 
    'x_timeadd__mutmut_31': x_timeadd__mutmut_31, 
    'x_timeadd__mutmut_32': x_timeadd__mutmut_32, 
    'x_timeadd__mutmut_33': x_timeadd__mutmut_33, 
    'x_timeadd__mutmut_34': x_timeadd__mutmut_34, 
    'x_timeadd__mutmut_35': x_timeadd__mutmut_35
}

def timeadd(*args, **kwargs):
    result = _mutmut_trampoline(x_timeadd__mutmut_orig, x_timeadd__mutmut_mutants, args, kwargs)
    return result 

timeadd.__signature__ = _mutmut_signature(x_timeadd__mutmut_orig)
x_timeadd__mutmut_orig.__name__ = 'x_timeadd'


# 🌊🪢🔣🪄
