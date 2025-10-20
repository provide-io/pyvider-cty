# pyvider/cty/conversion/_utils.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from pyvider.cty.config.defaults import (
    ERR_CANNOT_INFER_FROM_CTY_TYPE,
    ERR_CANNOT_INFER_FROM_CTY_VALUE,
)

# pyvider-cty/src/pyvider/cty/conversion/_utils.py
"""Internal conversion utilities to avoid circular dependencies."""
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


def x__attrs_to_dict_safe__mutmut_orig(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_1(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = None
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_2(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=None)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_3(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(None).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_4(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(None)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_5(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = None
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_6(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=None)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_7(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(None).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_8(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(None)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_9(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = None
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_10(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(None, "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_11(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), None, []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_12(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", None):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_13(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr("__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_14(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_15(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", ):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_16(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(None), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_17(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "XX__attrs_attrs__XX", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_18(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__ATTRS_ATTRS__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_19(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = None
    return res


def x__attrs_to_dict_safe__mutmut_20(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(None, a.name)
    return res


def x__attrs_to_dict_safe__mutmut_21(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, None)
    return res


def x__attrs_to_dict_safe__mutmut_22(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(a.name)
    return res


def x__attrs_to_dict_safe__mutmut_23(inst: Any) -> dict[str, Any]:
    """
    Safely converts an attrs instance to a dict, raising TypeError for CTY
    framework types to prevent accidental misuse during type inference.
    """
    # Local imports to prevent circular dependencies at module load time.
    from pyvider.cty.types import CtyType
    from pyvider.cty.values import CtyValue

    if isinstance(inst, CtyType):
        error_message = ERR_CANNOT_INFER_FROM_CTY_TYPE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)
    if isinstance(inst, CtyValue):
        error_message = ERR_CANNOT_INFER_FROM_CTY_VALUE.format(type_name=type(inst).__name__)
        raise TypeError(error_message)

    res = {}
    # Use getattr to safely access __attrs_attrs__ which may not exist.
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, )
    return res

x__attrs_to_dict_safe__mutmut_mutants : ClassVar[MutantDict] = {
'x__attrs_to_dict_safe__mutmut_1': x__attrs_to_dict_safe__mutmut_1, 
    'x__attrs_to_dict_safe__mutmut_2': x__attrs_to_dict_safe__mutmut_2, 
    'x__attrs_to_dict_safe__mutmut_3': x__attrs_to_dict_safe__mutmut_3, 
    'x__attrs_to_dict_safe__mutmut_4': x__attrs_to_dict_safe__mutmut_4, 
    'x__attrs_to_dict_safe__mutmut_5': x__attrs_to_dict_safe__mutmut_5, 
    'x__attrs_to_dict_safe__mutmut_6': x__attrs_to_dict_safe__mutmut_6, 
    'x__attrs_to_dict_safe__mutmut_7': x__attrs_to_dict_safe__mutmut_7, 
    'x__attrs_to_dict_safe__mutmut_8': x__attrs_to_dict_safe__mutmut_8, 
    'x__attrs_to_dict_safe__mutmut_9': x__attrs_to_dict_safe__mutmut_9, 
    'x__attrs_to_dict_safe__mutmut_10': x__attrs_to_dict_safe__mutmut_10, 
    'x__attrs_to_dict_safe__mutmut_11': x__attrs_to_dict_safe__mutmut_11, 
    'x__attrs_to_dict_safe__mutmut_12': x__attrs_to_dict_safe__mutmut_12, 
    'x__attrs_to_dict_safe__mutmut_13': x__attrs_to_dict_safe__mutmut_13, 
    'x__attrs_to_dict_safe__mutmut_14': x__attrs_to_dict_safe__mutmut_14, 
    'x__attrs_to_dict_safe__mutmut_15': x__attrs_to_dict_safe__mutmut_15, 
    'x__attrs_to_dict_safe__mutmut_16': x__attrs_to_dict_safe__mutmut_16, 
    'x__attrs_to_dict_safe__mutmut_17': x__attrs_to_dict_safe__mutmut_17, 
    'x__attrs_to_dict_safe__mutmut_18': x__attrs_to_dict_safe__mutmut_18, 
    'x__attrs_to_dict_safe__mutmut_19': x__attrs_to_dict_safe__mutmut_19, 
    'x__attrs_to_dict_safe__mutmut_20': x__attrs_to_dict_safe__mutmut_20, 
    'x__attrs_to_dict_safe__mutmut_21': x__attrs_to_dict_safe__mutmut_21, 
    'x__attrs_to_dict_safe__mutmut_22': x__attrs_to_dict_safe__mutmut_22, 
    'x__attrs_to_dict_safe__mutmut_23': x__attrs_to_dict_safe__mutmut_23
}

def _attrs_to_dict_safe(*args, **kwargs):
    result = _mutmut_trampoline(x__attrs_to_dict_safe__mutmut_orig, x__attrs_to_dict_safe__mutmut_mutants, args, kwargs)
    return result 

_attrs_to_dict_safe.__signature__ = _mutmut_signature(x__attrs_to_dict_safe__mutmut_orig)
x__attrs_to_dict_safe__mutmut_orig.__name__ = 'x__attrs_to_dict_safe'


# 🌊🪢↔️🪄
