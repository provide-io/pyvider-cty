# pyvider/cty/types/primitives/bool.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from attrs import define

from pyvider.cty.exceptions import CtyBoolValidationError
from pyvider.cty.types.base import CtyType

if TYPE_CHECKING:
    from pyvider.cty.values import CtyValue
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


@define(frozen=True, slots=True)
class CtyBool(CtyType[bool]):
    ctype: ClassVar[str] = "bool"
    _type_order: ClassVar[int] = 2  # Correct go-cty order

    def validate(self, value: object) -> CtyValue[bool]:  # noqa: C901
        from pyvider.cty.values import CtyValue, UnknownValue

        if isinstance(value, UnknownValue):
            return CtyValue.unknown(self)

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            raw_value = value.value
        else:
            raw_value = value

        if raw_value is None:
            return CtyValue.null(self)

        if isinstance(raw_value, bool):
            return CtyValue(vtype=self, value=raw_value)
        if isinstance(raw_value, str):
            if raw_value.lower() == "true":
                return CtyValue(vtype=self, value=True)
            if raw_value.lower() == "false":
                return CtyValue(vtype=self, value=False)
        if isinstance(raw_value, int | float):
            if raw_value == 1:
                return CtyValue(vtype=self, value=True)
            if raw_value == 0:
                return CtyValue(vtype=self, value=False)

        raise CtyBoolValidationError(f"Cannot convert {type(raw_value).__name__} to bool.")

    def equal(self, other: CtyType[Any]) -> bool:
        return isinstance(other, CtyBool)

    def usable_as(self, other: CtyType[Any]) -> bool:
        from pyvider.cty.types.structural import CtyDynamic

        return isinstance(other, CtyBool | CtyDynamic)

    def _to_wire_json(self) -> Any:
        return self.ctype

    def __str__(self) -> str:
        return "bool"

    def is_primitive_type(self) -> bool:
        return True


# 🌊🪢🧱🪄
