# pyvider/cty/conversion/__init__.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pyvider.cty.conversion.adapter import cty_to_native
from pyvider.cty.conversion.explicit import convert, unify

# pyvider-cty/src/pyvider/cty/conversion/__init__.py
from pyvider.cty.conversion.inference_cache import inference_cache_context, with_inference_cache
from pyvider.cty.conversion.raw_to_cty import infer_cty_type_from_raw
from pyvider.cty.conversion.type_encoder import encode_cty_type_to_wire_json

__all__ = [
    "convert",
    "cty_to_native",
    "encode_cty_type_to_wire_json",
    "infer_cty_type_from_raw",
    "inference_cache_context",
    "unify",
    "with_inference_cache",
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
