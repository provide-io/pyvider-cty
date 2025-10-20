# pyvider/cty/functions/bytes_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from pyvider.cty import CtyNumber, CtyValue
from pyvider.cty.config.defaults import (
    ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE,
    ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.types import BytesCapsule
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


def x_byteslen__mutmut_orig(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(BytesCapsule):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=buffer.type.ctype)
        raise CtyFunctionError(error_message)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


def x_byteslen__mutmut_1(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if buffer.type.equal(BytesCapsule):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=buffer.type.ctype)
        raise CtyFunctionError(error_message)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


def x_byteslen__mutmut_2(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(None):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=buffer.type.ctype)
        raise CtyFunctionError(error_message)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


def x_byteslen__mutmut_3(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(BytesCapsule):
        error_message = None
        raise CtyFunctionError(error_message)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


def x_byteslen__mutmut_4(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(BytesCapsule):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=None)
        raise CtyFunctionError(error_message)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


def x_byteslen__mutmut_5(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(BytesCapsule):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=buffer.type.ctype)
        raise CtyFunctionError(None)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


def x_byteslen__mutmut_6(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(BytesCapsule):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=buffer.type.ctype)
        raise CtyFunctionError(error_message)
    if buffer.is_unknown and buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


def x_byteslen__mutmut_7(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(BytesCapsule):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=buffer.type.ctype)
        raise CtyFunctionError(error_message)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(None)
    return CtyNumber().validate(len(buffer.value))  # type: ignore[arg-type]


def x_byteslen__mutmut_8(buffer: CtyValue[Any]) -> CtyValue[Any]:
    if not buffer.type.equal(BytesCapsule):
        error_message = ERR_BYTESLEN_ARG_MUST_BE_BYTES_CAPSULE.format(type=buffer.type.ctype)
        raise CtyFunctionError(error_message)
    if buffer.is_unknown or buffer.is_null:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(None)  # type: ignore[arg-type]

x_byteslen__mutmut_mutants : ClassVar[MutantDict] = {
'x_byteslen__mutmut_1': x_byteslen__mutmut_1, 
    'x_byteslen__mutmut_2': x_byteslen__mutmut_2, 
    'x_byteslen__mutmut_3': x_byteslen__mutmut_3, 
    'x_byteslen__mutmut_4': x_byteslen__mutmut_4, 
    'x_byteslen__mutmut_5': x_byteslen__mutmut_5, 
    'x_byteslen__mutmut_6': x_byteslen__mutmut_6, 
    'x_byteslen__mutmut_7': x_byteslen__mutmut_7, 
    'x_byteslen__mutmut_8': x_byteslen__mutmut_8
}

def byteslen(*args, **kwargs):
    result = _mutmut_trampoline(x_byteslen__mutmut_orig, x_byteslen__mutmut_mutants, args, kwargs)
    return result 

byteslen.__signature__ = _mutmut_signature(x_byteslen__mutmut_orig)
x_byteslen__mutmut_orig.__name__ = 'x_byteslen'


def x_bytesslice__mutmut_orig(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_1(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber) and not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_2(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule) and not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_3(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_4(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(None)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_5(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_6(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_7(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = None
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_8(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(None)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_9(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown and end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_10(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null and end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_11(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown and start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_12(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null and start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_13(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown and buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_14(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(None)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_15(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = None  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_16(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(None), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_17(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(None)  # type: ignore[call-overload]
    return BytesCapsule.validate(buffer.value[start_idx:end_idx])  # type: ignore[index]


def x_bytesslice__mutmut_18(buffer: CtyValue[Any], start: CtyValue[Any], end: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not buffer.type.equal(BytesCapsule)
        or not isinstance(start.type, CtyNumber)
        or not isinstance(end.type, CtyNumber)
    ):
        error_message = ERR_BYTESSLICE_ARGS_MUST_BE_BYTES_NUMBER_NUMBER
        raise CtyFunctionError(error_message)
    if (
        buffer.is_unknown
        or buffer.is_null
        or start.is_unknown
        or start.is_null
        or end.is_unknown
        or end.is_null
    ):
        return CtyValue.unknown(BytesCapsule)

    start_idx, end_idx = int(start.value), int(end.value)  # type: ignore[call-overload]
    return BytesCapsule.validate(None)  # type: ignore[index]

x_bytesslice__mutmut_mutants : ClassVar[MutantDict] = {
'x_bytesslice__mutmut_1': x_bytesslice__mutmut_1, 
    'x_bytesslice__mutmut_2': x_bytesslice__mutmut_2, 
    'x_bytesslice__mutmut_3': x_bytesslice__mutmut_3, 
    'x_bytesslice__mutmut_4': x_bytesslice__mutmut_4, 
    'x_bytesslice__mutmut_5': x_bytesslice__mutmut_5, 
    'x_bytesslice__mutmut_6': x_bytesslice__mutmut_6, 
    'x_bytesslice__mutmut_7': x_bytesslice__mutmut_7, 
    'x_bytesslice__mutmut_8': x_bytesslice__mutmut_8, 
    'x_bytesslice__mutmut_9': x_bytesslice__mutmut_9, 
    'x_bytesslice__mutmut_10': x_bytesslice__mutmut_10, 
    'x_bytesslice__mutmut_11': x_bytesslice__mutmut_11, 
    'x_bytesslice__mutmut_12': x_bytesslice__mutmut_12, 
    'x_bytesslice__mutmut_13': x_bytesslice__mutmut_13, 
    'x_bytesslice__mutmut_14': x_bytesslice__mutmut_14, 
    'x_bytesslice__mutmut_15': x_bytesslice__mutmut_15, 
    'x_bytesslice__mutmut_16': x_bytesslice__mutmut_16, 
    'x_bytesslice__mutmut_17': x_bytesslice__mutmut_17, 
    'x_bytesslice__mutmut_18': x_bytesslice__mutmut_18
}

def bytesslice(*args, **kwargs):
    result = _mutmut_trampoline(x_bytesslice__mutmut_orig, x_bytesslice__mutmut_mutants, args, kwargs)
    return result 

bytesslice.__signature__ = _mutmut_signature(x_bytesslice__mutmut_orig)
x_bytesslice__mutmut_orig.__name__ = 'x_bytesslice'


# 🌊🪢🔣🪄
