# pyvider/cty/context/validation_context.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# In a new file: pyvider/cty/context/validation_context.py
from collections.abc import Generator
from contextlib import contextmanager
import contextvars

MAX_VALIDATION_DEPTH = 500  # Configurable

_validation_depth = contextvars.ContextVar("validation_depth", default=0)
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


@contextmanager
def deeper_validation() -> Generator[None]:
    """A context manager to safely increment and decrement validation depth."""
    token = _validation_depth.set(_validation_depth.get() + 1)
    try:
        yield
    finally:
        _validation_depth.reset(token)


def get_validation_depth() -> int:
    """Returns the current validation depth."""
    return _validation_depth.get()


# 🌊🪢✅🪄
