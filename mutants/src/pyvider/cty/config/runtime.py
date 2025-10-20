# pyvider/cty/config/runtime.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Self

from attrs import define
from provide.foundation.config import RuntimeConfig, env_field

from pyvider.cty.config.defaults import ENABLE_TYPE_INFERENCE_CACHE

"""Runtime configuration for pyvider-cty using Foundation config patterns."""
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


@define
class CtyConfig(RuntimeConfig):
    """Runtime configuration for pyvider-cty.

    Uses Foundation's RuntimeConfig for consistent environment variable loading
    and validation patterns.
    """

    enable_type_inference_cache: bool = env_field(
        env_var="PYVIDER_CTY_ENABLE_TYPE_INFERENCE_CACHE",
        default=ENABLE_TYPE_INFERENCE_CACHE,
    )

    @classmethod
    def get_current(cls) -> Self:
        """Get current configuration from environment variables.

        Returns:
            Current CtyConfig instance loaded from environment
        """
        return cls.from_env(prefix="PYVIDER_CTY")


# 🌊🪢⚙️🪄
