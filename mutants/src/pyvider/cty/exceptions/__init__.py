# pyvider/cty/exceptions/__init__.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pyvider.cty.exceptions.base import CtyError, CtyFunctionError
from pyvider.cty.exceptions.conversion import (
    CtyConversionError,
    CtyTypeConversionError,
    CtyTypeParseError,
)
from pyvider.cty.exceptions.encoding import (
    AttributePathError,
    DeserializationError,
    DynamicValueError,
    EncodingError,
    InvalidTypeError,
    JsonEncodingError,
    MsgPackEncodingError,
    SerializationError,
    TransformationError,
    WireFormatError,
)
from pyvider.cty.exceptions.validation import (
    CtyAttributeValidationError,
    CtyBoolValidationError,
    CtyCollectionValidationError,
    CtyListValidationError,
    CtyMapValidationError,
    CtyNumberValidationError,
    CtySetValidationError,
    CtyStringValidationError,
    CtyTupleValidationError,
    CtyTypeMismatchError,
    CtyTypeValidationError,
    CtyValidationError,
)

"""
Exception hierarchy for the pyvider.cty type system.
"""

__all__ = [
    "AttributePathError",
    "CtyAttributeValidationError",
    "CtyBoolValidationError",
    "CtyCollectionValidationError",
    "CtyConversionError",
    "CtyError",
    "CtyFunctionError",
    "CtyListValidationError",
    "CtyMapValidationError",
    "CtyNumberValidationError",
    "CtySetValidationError",
    "CtyStringValidationError",
    "CtyTupleValidationError",
    "CtyTypeConversionError",
    "CtyTypeMismatchError",
    "CtyTypeParseError",
    "CtyTypeValidationError",
    "CtyValidationError",
    "DeserializationError",
    "DynamicValueError",
    "EncodingError",
    "InvalidTypeError",
    "JsonEncodingError",
    "MsgPackEncodingError",
    "SerializationError",
    "TransformationError",
    "WireFormatError",
]
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
# 🌊🪢📦🪄
