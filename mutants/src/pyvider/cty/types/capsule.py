# pyvider/cty/types/capsule.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Callable
import inspect
from typing import Any, ClassVar

from pyvider.cty.exceptions import CtyValidationError
from pyvider.cty.types.base import CtyType
from pyvider.cty.types.structural import CtyDynamic
from pyvider.cty.values import CtyValue

# pyvider/cty/types/capsule.py
"""
Defines the CtyCapsule type for encapsulating opaque Python objects
within the CTY type system.
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


class CtyCapsule(CtyType[Any]):
    """
    Represents a capsule type in the Cty type system.
    Capsule types are opaque types that can be used to wrap arbitrary Python objects.
    """

    _type_order: ClassVar[int] = 8

    def xǁCtyCapsuleǁ__init____mutmut_orig(self, capsule_name: str, py_type: type) -> None:
        super().__init__()
        self.name = capsule_name
        self._py_type = py_type

    def xǁCtyCapsuleǁ__init____mutmut_1(self, capsule_name: str, py_type: type) -> None:
        super().__init__()
        self.name = None
        self._py_type = py_type

    def xǁCtyCapsuleǁ__init____mutmut_2(self, capsule_name: str, py_type: type) -> None:
        super().__init__()
        self.name = capsule_name
        self._py_type = None
    
    xǁCtyCapsuleǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleǁ__init____mutmut_1': xǁCtyCapsuleǁ__init____mutmut_1, 
        'xǁCtyCapsuleǁ__init____mutmut_2': xǁCtyCapsuleǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyCapsuleǁ__init____mutmut_orig)
    xǁCtyCapsuleǁ__init____mutmut_orig.__name__ = 'xǁCtyCapsuleǁ__init__'

    @property
    def py_type(self) -> type:
        return self._py_type

    def xǁCtyCapsuleǁvalidate__mutmut_orig(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_1(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = None

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_2(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(None)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_3(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(None)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_4(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = None
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_5(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = None
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_6(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = None

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_7(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is not None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_8(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(None)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_9(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_10(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                None
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_11(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(None).__name__}."
            )
        return CtyValue(self, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_12(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(None, val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_13(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, None, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_14(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, marks=None)

    def xǁCtyCapsuleǁvalidate__mutmut_15(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(val_to_check, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_16(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, marks=original_marks)

    def xǁCtyCapsuleǁvalidate__mutmut_17(self, value: object) -> CtyValue[Any]:
        val_to_check: object | None
        original_marks: frozenset[Any] = frozenset()

        if isinstance(value, CtyValue):
            if value.is_null:
                return CtyValue.null(self)
            if value.is_unknown:
                return CtyValue.unknown(self)
            val_to_check = value.value
            original_marks = value.marks
        else:
            val_to_check = value

        if val_to_check is None:
            return CtyValue.null(self)

        if not isinstance(val_to_check, self._py_type):
            raise CtyValidationError(
                f"Value is not an instance of {self._py_type.__name__}. Got {type(val_to_check).__name__}."
            )
        return CtyValue(self, val_to_check, )
    
    xǁCtyCapsuleǁvalidate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleǁvalidate__mutmut_1': xǁCtyCapsuleǁvalidate__mutmut_1, 
        'xǁCtyCapsuleǁvalidate__mutmut_2': xǁCtyCapsuleǁvalidate__mutmut_2, 
        'xǁCtyCapsuleǁvalidate__mutmut_3': xǁCtyCapsuleǁvalidate__mutmut_3, 
        'xǁCtyCapsuleǁvalidate__mutmut_4': xǁCtyCapsuleǁvalidate__mutmut_4, 
        'xǁCtyCapsuleǁvalidate__mutmut_5': xǁCtyCapsuleǁvalidate__mutmut_5, 
        'xǁCtyCapsuleǁvalidate__mutmut_6': xǁCtyCapsuleǁvalidate__mutmut_6, 
        'xǁCtyCapsuleǁvalidate__mutmut_7': xǁCtyCapsuleǁvalidate__mutmut_7, 
        'xǁCtyCapsuleǁvalidate__mutmut_8': xǁCtyCapsuleǁvalidate__mutmut_8, 
        'xǁCtyCapsuleǁvalidate__mutmut_9': xǁCtyCapsuleǁvalidate__mutmut_9, 
        'xǁCtyCapsuleǁvalidate__mutmut_10': xǁCtyCapsuleǁvalidate__mutmut_10, 
        'xǁCtyCapsuleǁvalidate__mutmut_11': xǁCtyCapsuleǁvalidate__mutmut_11, 
        'xǁCtyCapsuleǁvalidate__mutmut_12': xǁCtyCapsuleǁvalidate__mutmut_12, 
        'xǁCtyCapsuleǁvalidate__mutmut_13': xǁCtyCapsuleǁvalidate__mutmut_13, 
        'xǁCtyCapsuleǁvalidate__mutmut_14': xǁCtyCapsuleǁvalidate__mutmut_14, 
        'xǁCtyCapsuleǁvalidate__mutmut_15': xǁCtyCapsuleǁvalidate__mutmut_15, 
        'xǁCtyCapsuleǁvalidate__mutmut_16': xǁCtyCapsuleǁvalidate__mutmut_16, 
        'xǁCtyCapsuleǁvalidate__mutmut_17': xǁCtyCapsuleǁvalidate__mutmut_17
    }
    
    def validate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleǁvalidate__mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleǁvalidate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    validate.__signature__ = _mutmut_signature(xǁCtyCapsuleǁvalidate__mutmut_orig)
    xǁCtyCapsuleǁvalidate__mutmut_orig.__name__ = 'xǁCtyCapsuleǁvalidate'

    def xǁCtyCapsuleǁequal__mutmut_orig(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsule) or isinstance(other, CtyCapsuleWithOps):
            return False
        return self.name == other.name and self._py_type == other._py_type

    def xǁCtyCapsuleǁequal__mutmut_1(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsule) and isinstance(other, CtyCapsuleWithOps):
            return False
        return self.name == other.name and self._py_type == other._py_type

    def xǁCtyCapsuleǁequal__mutmut_2(self, other: CtyType[Any]) -> bool:
        if isinstance(other, CtyCapsule) or isinstance(other, CtyCapsuleWithOps):
            return False
        return self.name == other.name and self._py_type == other._py_type

    def xǁCtyCapsuleǁequal__mutmut_3(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsule) or isinstance(other, CtyCapsuleWithOps):
            return True
        return self.name == other.name and self._py_type == other._py_type

    def xǁCtyCapsuleǁequal__mutmut_4(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsule) or isinstance(other, CtyCapsuleWithOps):
            return False
        return self.name == other.name or self._py_type == other._py_type

    def xǁCtyCapsuleǁequal__mutmut_5(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsule) or isinstance(other, CtyCapsuleWithOps):
            return False
        return self.name != other.name and self._py_type == other._py_type

    def xǁCtyCapsuleǁequal__mutmut_6(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsule) or isinstance(other, CtyCapsuleWithOps):
            return False
        return self.name == other.name and self._py_type != other._py_type
    
    xǁCtyCapsuleǁequal__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleǁequal__mutmut_1': xǁCtyCapsuleǁequal__mutmut_1, 
        'xǁCtyCapsuleǁequal__mutmut_2': xǁCtyCapsuleǁequal__mutmut_2, 
        'xǁCtyCapsuleǁequal__mutmut_3': xǁCtyCapsuleǁequal__mutmut_3, 
        'xǁCtyCapsuleǁequal__mutmut_4': xǁCtyCapsuleǁequal__mutmut_4, 
        'xǁCtyCapsuleǁequal__mutmut_5': xǁCtyCapsuleǁequal__mutmut_5, 
        'xǁCtyCapsuleǁequal__mutmut_6': xǁCtyCapsuleǁequal__mutmut_6
    }
    
    def equal(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleǁequal__mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleǁequal__mutmut_mutants"), args, kwargs, self)
        return result 
    
    equal.__signature__ = _mutmut_signature(xǁCtyCapsuleǁequal__mutmut_orig)
    xǁCtyCapsuleǁequal__mutmut_orig.__name__ = 'xǁCtyCapsuleǁequal'

    def xǁCtyCapsuleǁusable_as__mutmut_orig(self, other: CtyType[Any]) -> bool:
        if isinstance(other, CtyDynamic):
            return True
        return self.equal(other)

    def xǁCtyCapsuleǁusable_as__mutmut_1(self, other: CtyType[Any]) -> bool:
        if isinstance(other, CtyDynamic):
            return False
        return self.equal(other)

    def xǁCtyCapsuleǁusable_as__mutmut_2(self, other: CtyType[Any]) -> bool:
        if isinstance(other, CtyDynamic):
            return True
        return self.equal(None)
    
    xǁCtyCapsuleǁusable_as__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleǁusable_as__mutmut_1': xǁCtyCapsuleǁusable_as__mutmut_1, 
        'xǁCtyCapsuleǁusable_as__mutmut_2': xǁCtyCapsuleǁusable_as__mutmut_2
    }
    
    def usable_as(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleǁusable_as__mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleǁusable_as__mutmut_mutants"), args, kwargs, self)
        return result 
    
    usable_as.__signature__ = _mutmut_signature(xǁCtyCapsuleǁusable_as__mutmut_orig)
    xǁCtyCapsuleǁusable_as__mutmut_orig.__name__ = 'xǁCtyCapsuleǁusable_as'

    def _to_wire_json(self) -> Any:
        return None

    def __str__(self) -> str:
        return f"CtyCapsule({self.name})"

    def __repr__(self) -> str:
        return f"CtyCapsule({self.name}, {self._py_type.__name__})"

    def xǁCtyCapsuleǁ__hash____mutmut_orig(self) -> int:
        return hash((self.name, self._py_type))

    def xǁCtyCapsuleǁ__hash____mutmut_1(self) -> int:
        return hash(None)
    
    xǁCtyCapsuleǁ__hash____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleǁ__hash____mutmut_1': xǁCtyCapsuleǁ__hash____mutmut_1
    }
    
    def __hash__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleǁ__hash____mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleǁ__hash____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __hash__.__signature__ = _mutmut_signature(xǁCtyCapsuleǁ__hash____mutmut_orig)
    xǁCtyCapsuleǁ__hash____mutmut_orig.__name__ = 'xǁCtyCapsuleǁ__hash__'


class CtyCapsuleWithOps(CtyCapsule):
    """
    A CtyCapsule that supports custom operations like equality, hashing, and conversion.
    """

    def xǁCtyCapsuleWithOpsǁ__init____mutmut_orig(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(capsule_name, py_type)
        self.equal_fn = equal_fn
        self.hash_fn = hash_fn
        self.convert_fn = convert_fn
        self._validate_ops_arity()

    def xǁCtyCapsuleWithOpsǁ__init____mutmut_1(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(None, py_type)
        self.equal_fn = equal_fn
        self.hash_fn = hash_fn
        self.convert_fn = convert_fn
        self._validate_ops_arity()

    def xǁCtyCapsuleWithOpsǁ__init____mutmut_2(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(capsule_name, None)
        self.equal_fn = equal_fn
        self.hash_fn = hash_fn
        self.convert_fn = convert_fn
        self._validate_ops_arity()

    def xǁCtyCapsuleWithOpsǁ__init____mutmut_3(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(py_type)
        self.equal_fn = equal_fn
        self.hash_fn = hash_fn
        self.convert_fn = convert_fn
        self._validate_ops_arity()

    def xǁCtyCapsuleWithOpsǁ__init____mutmut_4(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(capsule_name, )
        self.equal_fn = equal_fn
        self.hash_fn = hash_fn
        self.convert_fn = convert_fn
        self._validate_ops_arity()

    def xǁCtyCapsuleWithOpsǁ__init____mutmut_5(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(capsule_name, py_type)
        self.equal_fn = None
        self.hash_fn = hash_fn
        self.convert_fn = convert_fn
        self._validate_ops_arity()

    def xǁCtyCapsuleWithOpsǁ__init____mutmut_6(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(capsule_name, py_type)
        self.equal_fn = equal_fn
        self.hash_fn = None
        self.convert_fn = convert_fn
        self._validate_ops_arity()

    def xǁCtyCapsuleWithOpsǁ__init____mutmut_7(
        self,
        capsule_name: str,
        py_type: type,
        *,
        equal_fn: Callable[[Any, Any], bool] | None = None,
        hash_fn: Callable[[Any], int] | None = None,
        convert_fn: Callable[[Any, CtyType[Any]], CtyValue[Any] | None] | None = None,
    ) -> None:
        """
        Initializes a CtyCapsule with custom operational functions.
        """
        super().__init__(capsule_name, py_type)
        self.equal_fn = equal_fn
        self.hash_fn = hash_fn
        self.convert_fn = None
        self._validate_ops_arity()
    
    xǁCtyCapsuleWithOpsǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleWithOpsǁ__init____mutmut_1': xǁCtyCapsuleWithOpsǁ__init____mutmut_1, 
        'xǁCtyCapsuleWithOpsǁ__init____mutmut_2': xǁCtyCapsuleWithOpsǁ__init____mutmut_2, 
        'xǁCtyCapsuleWithOpsǁ__init____mutmut_3': xǁCtyCapsuleWithOpsǁ__init____mutmut_3, 
        'xǁCtyCapsuleWithOpsǁ__init____mutmut_4': xǁCtyCapsuleWithOpsǁ__init____mutmut_4, 
        'xǁCtyCapsuleWithOpsǁ__init____mutmut_5': xǁCtyCapsuleWithOpsǁ__init____mutmut_5, 
        'xǁCtyCapsuleWithOpsǁ__init____mutmut_6': xǁCtyCapsuleWithOpsǁ__init____mutmut_6, 
        'xǁCtyCapsuleWithOpsǁ__init____mutmut_7': xǁCtyCapsuleWithOpsǁ__init____mutmut_7
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleWithOpsǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleWithOpsǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁCtyCapsuleWithOpsǁ__init____mutmut_orig)
    xǁCtyCapsuleWithOpsǁ__init____mutmut_orig.__name__ = 'xǁCtyCapsuleWithOpsǁ__init__'

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_orig(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_1(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn or len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_2(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) == 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_3(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 3:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_4(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError(None)
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_5(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("XX`equal_fn` must be a callable that accepts 2 argumentsXX")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_6(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`EQUAL_FN` MUST BE A CALLABLE THAT ACCEPTS 2 ARGUMENTS")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_7(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn or len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_8(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) == 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_9(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 2:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_10(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError(None)
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_11(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("XX`hash_fn` must be a callable that accepts 1 argumentXX")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_12(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`HASH_FN` MUST BE A CALLABLE THAT ACCEPTS 1 ARGUMENT")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_13(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn or len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_14(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) == 2:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_15(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 3:
            raise TypeError("`convert_fn` must be a callable that accepts 2 arguments")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_16(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError(None)

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_17(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("XX`convert_fn` must be a callable that accepts 2 argumentsXX")

    def xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_18(self) -> None:
        """Internal method to validate the arity of provided operational functions."""
        if self.equal_fn and len(inspect.signature(self.equal_fn).parameters) != 2:
            raise TypeError("`equal_fn` must be a callable that accepts 2 arguments")
        if self.hash_fn and len(inspect.signature(self.hash_fn).parameters) != 1:
            raise TypeError("`hash_fn` must be a callable that accepts 1 argument")
        if self.convert_fn and len(inspect.signature(self.convert_fn).parameters) != 2:
            raise TypeError("`CONVERT_FN` MUST BE A CALLABLE THAT ACCEPTS 2 ARGUMENTS")
    
    xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_1': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_1, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_2': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_2, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_3': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_3, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_4': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_4, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_5': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_5, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_6': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_6, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_7': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_7, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_8': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_8, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_9': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_9, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_10': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_10, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_11': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_11, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_12': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_12, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_13': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_13, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_14': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_14, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_15': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_15, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_16': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_16, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_17': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_17, 
        'xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_18': xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_18
    }
    
    def _validate_ops_arity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _validate_ops_arity.__signature__ = _mutmut_signature(xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_orig)
    xǁCtyCapsuleWithOpsǁ_validate_ops_arity__mutmut_orig.__name__ = 'xǁCtyCapsuleWithOpsǁ_validate_ops_arity'

    def xǁCtyCapsuleWithOpsǁequal__mutmut_orig(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type == other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_1(self, other: CtyType[Any]) -> bool:
        if isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type == other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_2(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return True
        return (
            self.name == other.name
            and self._py_type == other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_3(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type == other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn or self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_4(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type == other._py_type
            and self.equal_fn == other.equal_fn or self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_5(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type == other._py_type or self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_6(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name or self._py_type == other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_7(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name != other.name
            and self._py_type == other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_8(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type != other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_9(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type == other._py_type
            and self.equal_fn != other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_10(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type == other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn != other.hash_fn
            and self.convert_fn == other.convert_fn
        )

    def xǁCtyCapsuleWithOpsǁequal__mutmut_11(self, other: CtyType[Any]) -> bool:
        if not isinstance(other, CtyCapsuleWithOps):
            return False
        return (
            self.name == other.name
            and self._py_type == other._py_type
            and self.equal_fn == other.equal_fn
            and self.hash_fn == other.hash_fn
            and self.convert_fn != other.convert_fn
        )
    
    xǁCtyCapsuleWithOpsǁequal__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleWithOpsǁequal__mutmut_1': xǁCtyCapsuleWithOpsǁequal__mutmut_1, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_2': xǁCtyCapsuleWithOpsǁequal__mutmut_2, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_3': xǁCtyCapsuleWithOpsǁequal__mutmut_3, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_4': xǁCtyCapsuleWithOpsǁequal__mutmut_4, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_5': xǁCtyCapsuleWithOpsǁequal__mutmut_5, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_6': xǁCtyCapsuleWithOpsǁequal__mutmut_6, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_7': xǁCtyCapsuleWithOpsǁequal__mutmut_7, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_8': xǁCtyCapsuleWithOpsǁequal__mutmut_8, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_9': xǁCtyCapsuleWithOpsǁequal__mutmut_9, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_10': xǁCtyCapsuleWithOpsǁequal__mutmut_10, 
        'xǁCtyCapsuleWithOpsǁequal__mutmut_11': xǁCtyCapsuleWithOpsǁequal__mutmut_11
    }
    
    def equal(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleWithOpsǁequal__mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleWithOpsǁequal__mutmut_mutants"), args, kwargs, self)
        return result 
    
    equal.__signature__ = _mutmut_signature(xǁCtyCapsuleWithOpsǁequal__mutmut_orig)
    xǁCtyCapsuleWithOpsǁequal__mutmut_orig.__name__ = 'xǁCtyCapsuleWithOpsǁequal'

    def __repr__(self) -> str:
        return f"CtyCapsuleWithOps({self.name}, {self._py_type.__name__})"

    def xǁCtyCapsuleWithOpsǁ__hash____mutmut_orig(self) -> int:
        return hash((self.name, self._py_type, self.equal_fn, self.hash_fn, self.convert_fn))

    def xǁCtyCapsuleWithOpsǁ__hash____mutmut_1(self) -> int:
        return hash(None)
    
    xǁCtyCapsuleWithOpsǁ__hash____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁCtyCapsuleWithOpsǁ__hash____mutmut_1': xǁCtyCapsuleWithOpsǁ__hash____mutmut_1
    }
    
    def __hash__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁCtyCapsuleWithOpsǁ__hash____mutmut_orig"), object.__getattribute__(self, "xǁCtyCapsuleWithOpsǁ__hash____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __hash__.__signature__ = _mutmut_signature(xǁCtyCapsuleWithOpsǁ__hash____mutmut_orig)
    xǁCtyCapsuleWithOpsǁ__hash____mutmut_orig.__name__ = 'xǁCtyCapsuleWithOpsǁ__hash__'


# 🌊🪢🧱🪄
