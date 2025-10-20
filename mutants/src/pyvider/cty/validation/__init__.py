# pyvider/cty/validation/__init__.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from pyvider.cty.validation.recursion import (
    RecursionContext,
    RecursionDetector,
    clear_recursion_context,
    get_recursion_context,
    with_recursion_detection,
)

"""
Advanced validation utilities for CTY.

This module provides sophisticated validation capabilities designed for
production IaC requirements including advanced recursion detection,
performance monitoring, and comprehensive diagnostics.
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


# Define validate_config here to avoid circular imports
def x_validate_config__mutmut_orig(schema: Any, config: Any) -> None:
    """
    Validates a configuration against a CtyType schema.

    This function serves as the primary entry point for validation,
    delegating to the `validate` method of the provided schema. It allows
    the CtyValidationError to propagate, which is the expected contract
    for testing and low-level framework integration.

    Args:
        schema: The CtyType object to validate against.
        config: The raw Python data to validate.

    Raises:
        CtyValidationError: If the configuration does not conform to the schema.
    """
    # The schema (a CtyType instance) has the validation logic.
    # We simply call it and let it raise its exception on failure.
    schema.validate(config)


# Define validate_config here to avoid circular imports
def x_validate_config__mutmut_1(schema: Any, config: Any) -> None:
    """
    Validates a configuration against a CtyType schema.

    This function serves as the primary entry point for validation,
    delegating to the `validate` method of the provided schema. It allows
    the CtyValidationError to propagate, which is the expected contract
    for testing and low-level framework integration.

    Args:
        schema: The CtyType object to validate against.
        config: The raw Python data to validate.

    Raises:
        CtyValidationError: If the configuration does not conform to the schema.
    """
    # The schema (a CtyType instance) has the validation logic.
    # We simply call it and let it raise its exception on failure.
    schema.validate(None)

x_validate_config__mutmut_mutants : ClassVar[MutantDict] = {
'x_validate_config__mutmut_1': x_validate_config__mutmut_1
}

def validate_config(*args, **kwargs):
    result = _mutmut_trampoline(x_validate_config__mutmut_orig, x_validate_config__mutmut_mutants, args, kwargs)
    return result 

validate_config.__signature__ = _mutmut_signature(x_validate_config__mutmut_orig)
x_validate_config__mutmut_orig.__name__ = 'x_validate_config'


__all__ = [
    "RecursionContext",
    "RecursionDetector",
    "clear_recursion_context",
    "get_recursion_context",
    "validate_config",
    "with_recursion_detection",
]
# 🌊🪢📦🪄
