# pyvider/cty/functions/numeric_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import math
from typing import Any, cast

from pyvider.cty import CtyNumber, CtyString, CtyValue
from pyvider.cty.config.defaults import POSITIVE_BOUNDARY, ZERO_VALUE
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.values.markers import RefinedUnknownValue
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


def x__get_refined_components__mutmut_orig(
    a: CtyValue[Any], b: CtyValue[Any]
) -> tuple[RefinedUnknownValue, RefinedUnknownValue, Any, Any]:
    """Extract refinement components from two values."""
    ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else RefinedUnknownValue()
    ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else RefinedUnknownValue()
    val_a = a.value if not a.is_unknown else None
    val_b = b.value if not b.is_unknown else None
    return ref_a, ref_b, val_a, val_b


def x__get_refined_components__mutmut_1(
    a: CtyValue[Any], b: CtyValue[Any]
) -> tuple[RefinedUnknownValue, RefinedUnknownValue, Any, Any]:
    """Extract refinement components from two values."""
    ref_a = None
    ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else RefinedUnknownValue()
    val_a = a.value if not a.is_unknown else None
    val_b = b.value if not b.is_unknown else None
    return ref_a, ref_b, val_a, val_b


def x__get_refined_components__mutmut_2(
    a: CtyValue[Any], b: CtyValue[Any]
) -> tuple[RefinedUnknownValue, RefinedUnknownValue, Any, Any]:
    """Extract refinement components from two values."""
    ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else RefinedUnknownValue()
    ref_b = None
    val_a = a.value if not a.is_unknown else None
    val_b = b.value if not b.is_unknown else None
    return ref_a, ref_b, val_a, val_b


def x__get_refined_components__mutmut_3(
    a: CtyValue[Any], b: CtyValue[Any]
) -> tuple[RefinedUnknownValue, RefinedUnknownValue, Any, Any]:
    """Extract refinement components from two values."""
    ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else RefinedUnknownValue()
    ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else RefinedUnknownValue()
    val_a = None
    val_b = b.value if not b.is_unknown else None
    return ref_a, ref_b, val_a, val_b


def x__get_refined_components__mutmut_4(
    a: CtyValue[Any], b: CtyValue[Any]
) -> tuple[RefinedUnknownValue, RefinedUnknownValue, Any, Any]:
    """Extract refinement components from two values."""
    ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else RefinedUnknownValue()
    ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else RefinedUnknownValue()
    val_a = a.value if a.is_unknown else None
    val_b = b.value if not b.is_unknown else None
    return ref_a, ref_b, val_a, val_b


def x__get_refined_components__mutmut_5(
    a: CtyValue[Any], b: CtyValue[Any]
) -> tuple[RefinedUnknownValue, RefinedUnknownValue, Any, Any]:
    """Extract refinement components from two values."""
    ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else RefinedUnknownValue()
    ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else RefinedUnknownValue()
    val_a = a.value if not a.is_unknown else None
    val_b = None
    return ref_a, ref_b, val_a, val_b


def x__get_refined_components__mutmut_6(
    a: CtyValue[Any], b: CtyValue[Any]
) -> tuple[RefinedUnknownValue, RefinedUnknownValue, Any, Any]:
    """Extract refinement components from two values."""
    ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else RefinedUnknownValue()
    ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else RefinedUnknownValue()
    val_a = a.value if not a.is_unknown else None
    val_b = b.value if b.is_unknown else None
    return ref_a, ref_b, val_a, val_b

x__get_refined_components__mutmut_mutants : ClassVar[MutantDict] = {
'x__get_refined_components__mutmut_1': x__get_refined_components__mutmut_1, 
    'x__get_refined_components__mutmut_2': x__get_refined_components__mutmut_2, 
    'x__get_refined_components__mutmut_3': x__get_refined_components__mutmut_3, 
    'x__get_refined_components__mutmut_4': x__get_refined_components__mutmut_4, 
    'x__get_refined_components__mutmut_5': x__get_refined_components__mutmut_5, 
    'x__get_refined_components__mutmut_6': x__get_refined_components__mutmut_6
}

def _get_refined_components(*args, **kwargs):
    result = _mutmut_trampoline(x__get_refined_components__mutmut_orig, x__get_refined_components__mutmut_mutants, args, kwargs)
    return result 

_get_refined_components.__signature__ = _mutmut_signature(x__get_refined_components__mutmut_orig)
x__get_refined_components__mutmut_orig.__name__ = 'x__get_refined_components'


def x__propagate_add_refinements__mutmut_orig(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_1(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = None
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_2(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_3(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = None
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_4(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["XXnumber_lower_boundXX"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_5(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["NUMBER_LOWER_BOUND"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_6(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_7(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[1],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_8(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[2],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_9(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = None
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_10(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["XXnumber_upper_boundXX"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_11(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["NUMBER_UPPER_BOUND"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_12(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_13(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[1],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_14(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[2],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_15(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_16(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = None
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_17(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["XXnumber_lower_boundXX"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_18(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["NUMBER_LOWER_BOUND"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_19(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_20(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[1] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_21(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[2],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_22(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = None
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_23(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["XXnumber_upper_boundXX"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_24(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["NUMBER_UPPER_BOUND"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_25(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_26(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[1] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_27(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[2],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_28(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound or ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_29(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = None
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_30(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["XXnumber_lower_boundXX"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_31(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["NUMBER_LOWER_BOUND"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_32(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_33(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[1] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_34(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[1],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_35(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] or ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_36(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[2] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_37(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[2],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_38(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound or ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_39(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = None
    return new_ref


def x__propagate_add_refinements__mutmut_40(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["XXnumber_upper_boundXX"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_41(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["NUMBER_UPPER_BOUND"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_42(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_43(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[1] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_44(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[1],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_45(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] or ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_46(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[2] and ref_b.number_upper_bound[1],
            )
    return new_ref


def x__propagate_add_refinements__mutmut_47(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for addition."""
    new_ref: dict[str, Any] = {}
    if val_a is not None:  # a is known, b is refined/unrefined
        if ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
        if ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
    elif val_b is not None:  # b is known, a is refined/unrefined
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    else:  # both are refined/unrefined
        if ref_a.number_lower_bound and ref_b.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_lower_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_upper_bound[2],
            )
    return new_ref

x__propagate_add_refinements__mutmut_mutants : ClassVar[MutantDict] = {
'x__propagate_add_refinements__mutmut_1': x__propagate_add_refinements__mutmut_1, 
    'x__propagate_add_refinements__mutmut_2': x__propagate_add_refinements__mutmut_2, 
    'x__propagate_add_refinements__mutmut_3': x__propagate_add_refinements__mutmut_3, 
    'x__propagate_add_refinements__mutmut_4': x__propagate_add_refinements__mutmut_4, 
    'x__propagate_add_refinements__mutmut_5': x__propagate_add_refinements__mutmut_5, 
    'x__propagate_add_refinements__mutmut_6': x__propagate_add_refinements__mutmut_6, 
    'x__propagate_add_refinements__mutmut_7': x__propagate_add_refinements__mutmut_7, 
    'x__propagate_add_refinements__mutmut_8': x__propagate_add_refinements__mutmut_8, 
    'x__propagate_add_refinements__mutmut_9': x__propagate_add_refinements__mutmut_9, 
    'x__propagate_add_refinements__mutmut_10': x__propagate_add_refinements__mutmut_10, 
    'x__propagate_add_refinements__mutmut_11': x__propagate_add_refinements__mutmut_11, 
    'x__propagate_add_refinements__mutmut_12': x__propagate_add_refinements__mutmut_12, 
    'x__propagate_add_refinements__mutmut_13': x__propagate_add_refinements__mutmut_13, 
    'x__propagate_add_refinements__mutmut_14': x__propagate_add_refinements__mutmut_14, 
    'x__propagate_add_refinements__mutmut_15': x__propagate_add_refinements__mutmut_15, 
    'x__propagate_add_refinements__mutmut_16': x__propagate_add_refinements__mutmut_16, 
    'x__propagate_add_refinements__mutmut_17': x__propagate_add_refinements__mutmut_17, 
    'x__propagate_add_refinements__mutmut_18': x__propagate_add_refinements__mutmut_18, 
    'x__propagate_add_refinements__mutmut_19': x__propagate_add_refinements__mutmut_19, 
    'x__propagate_add_refinements__mutmut_20': x__propagate_add_refinements__mutmut_20, 
    'x__propagate_add_refinements__mutmut_21': x__propagate_add_refinements__mutmut_21, 
    'x__propagate_add_refinements__mutmut_22': x__propagate_add_refinements__mutmut_22, 
    'x__propagate_add_refinements__mutmut_23': x__propagate_add_refinements__mutmut_23, 
    'x__propagate_add_refinements__mutmut_24': x__propagate_add_refinements__mutmut_24, 
    'x__propagate_add_refinements__mutmut_25': x__propagate_add_refinements__mutmut_25, 
    'x__propagate_add_refinements__mutmut_26': x__propagate_add_refinements__mutmut_26, 
    'x__propagate_add_refinements__mutmut_27': x__propagate_add_refinements__mutmut_27, 
    'x__propagate_add_refinements__mutmut_28': x__propagate_add_refinements__mutmut_28, 
    'x__propagate_add_refinements__mutmut_29': x__propagate_add_refinements__mutmut_29, 
    'x__propagate_add_refinements__mutmut_30': x__propagate_add_refinements__mutmut_30, 
    'x__propagate_add_refinements__mutmut_31': x__propagate_add_refinements__mutmut_31, 
    'x__propagate_add_refinements__mutmut_32': x__propagate_add_refinements__mutmut_32, 
    'x__propagate_add_refinements__mutmut_33': x__propagate_add_refinements__mutmut_33, 
    'x__propagate_add_refinements__mutmut_34': x__propagate_add_refinements__mutmut_34, 
    'x__propagate_add_refinements__mutmut_35': x__propagate_add_refinements__mutmut_35, 
    'x__propagate_add_refinements__mutmut_36': x__propagate_add_refinements__mutmut_36, 
    'x__propagate_add_refinements__mutmut_37': x__propagate_add_refinements__mutmut_37, 
    'x__propagate_add_refinements__mutmut_38': x__propagate_add_refinements__mutmut_38, 
    'x__propagate_add_refinements__mutmut_39': x__propagate_add_refinements__mutmut_39, 
    'x__propagate_add_refinements__mutmut_40': x__propagate_add_refinements__mutmut_40, 
    'x__propagate_add_refinements__mutmut_41': x__propagate_add_refinements__mutmut_41, 
    'x__propagate_add_refinements__mutmut_42': x__propagate_add_refinements__mutmut_42, 
    'x__propagate_add_refinements__mutmut_43': x__propagate_add_refinements__mutmut_43, 
    'x__propagate_add_refinements__mutmut_44': x__propagate_add_refinements__mutmut_44, 
    'x__propagate_add_refinements__mutmut_45': x__propagate_add_refinements__mutmut_45, 
    'x__propagate_add_refinements__mutmut_46': x__propagate_add_refinements__mutmut_46, 
    'x__propagate_add_refinements__mutmut_47': x__propagate_add_refinements__mutmut_47
}

def _propagate_add_refinements(*args, **kwargs):
    result = _mutmut_trampoline(x__propagate_add_refinements__mutmut_orig, x__propagate_add_refinements__mutmut_mutants, args, kwargs)
    return result 

_propagate_add_refinements.__signature__ = _mutmut_signature(x__propagate_add_refinements__mutmut_orig)
x__propagate_add_refinements__mutmut_orig.__name__ = 'x__propagate_add_refinements'


def x__propagate_subtract_refinements__mutmut_orig(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_1(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = None
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_2(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_3(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = None
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_4(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["XXnumber_lower_boundXX"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_5(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["NUMBER_LOWER_BOUND"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_6(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_7(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[1] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_8(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[2],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_9(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = None
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_10(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["XXnumber_upper_boundXX"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_11(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["NUMBER_UPPER_BOUND"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_12(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_13(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[1] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_14(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[2],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_15(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_16(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = None
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_17(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["XXnumber_lower_boundXX"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_18(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["NUMBER_LOWER_BOUND"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_19(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a + ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_20(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[1],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_21(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[2],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_22(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = None
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_23(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["XXnumber_upper_boundXX"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_24(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["NUMBER_UPPER_BOUND"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_25(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a + ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_26(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[1],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_27(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[2],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_28(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound or ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_29(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = None
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_30(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["XXnumber_lower_boundXX"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_31(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["NUMBER_LOWER_BOUND"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_32(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] + ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_33(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[1] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_34(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[1],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_35(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] or ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_36(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[2] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_37(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[2],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_38(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound or ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_39(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = None
    return new_ref


def x__propagate_subtract_refinements__mutmut_40(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["XXnumber_upper_boundXX"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_41(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["NUMBER_UPPER_BOUND"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_42(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] + ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_43(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[1] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_44(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[1],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_45(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] or ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_46(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[2] and ref_b.number_lower_bound[1],
            )
    return new_ref


def x__propagate_subtract_refinements__mutmut_47(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for subtraction."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if ref_a.number_lower_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - val_b,
                ref_a.number_lower_bound[1],
            )
        if ref_a.number_upper_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - val_b,
                ref_a.number_upper_bound[1],
            )
    elif val_a is not None:
        if ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                val_a - ref_b.number_upper_bound[0],
                ref_b.number_upper_bound[1],
            )
        if ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                val_a - ref_b.number_lower_bound[0],
                ref_b.number_lower_bound[1],
            )
    else:
        if ref_a.number_lower_bound and ref_b.number_upper_bound:
            new_ref["number_lower_bound"] = (
                ref_a.number_lower_bound[0] - ref_b.number_upper_bound[0],
                ref_a.number_lower_bound[1] and ref_b.number_upper_bound[1],
            )
        if ref_a.number_upper_bound and ref_b.number_lower_bound:
            new_ref["number_upper_bound"] = (
                ref_a.number_upper_bound[0] - ref_b.number_lower_bound[0],
                ref_a.number_upper_bound[1] and ref_b.number_lower_bound[2],
            )
    return new_ref

x__propagate_subtract_refinements__mutmut_mutants : ClassVar[MutantDict] = {
'x__propagate_subtract_refinements__mutmut_1': x__propagate_subtract_refinements__mutmut_1, 
    'x__propagate_subtract_refinements__mutmut_2': x__propagate_subtract_refinements__mutmut_2, 
    'x__propagate_subtract_refinements__mutmut_3': x__propagate_subtract_refinements__mutmut_3, 
    'x__propagate_subtract_refinements__mutmut_4': x__propagate_subtract_refinements__mutmut_4, 
    'x__propagate_subtract_refinements__mutmut_5': x__propagate_subtract_refinements__mutmut_5, 
    'x__propagate_subtract_refinements__mutmut_6': x__propagate_subtract_refinements__mutmut_6, 
    'x__propagate_subtract_refinements__mutmut_7': x__propagate_subtract_refinements__mutmut_7, 
    'x__propagate_subtract_refinements__mutmut_8': x__propagate_subtract_refinements__mutmut_8, 
    'x__propagate_subtract_refinements__mutmut_9': x__propagate_subtract_refinements__mutmut_9, 
    'x__propagate_subtract_refinements__mutmut_10': x__propagate_subtract_refinements__mutmut_10, 
    'x__propagate_subtract_refinements__mutmut_11': x__propagate_subtract_refinements__mutmut_11, 
    'x__propagate_subtract_refinements__mutmut_12': x__propagate_subtract_refinements__mutmut_12, 
    'x__propagate_subtract_refinements__mutmut_13': x__propagate_subtract_refinements__mutmut_13, 
    'x__propagate_subtract_refinements__mutmut_14': x__propagate_subtract_refinements__mutmut_14, 
    'x__propagate_subtract_refinements__mutmut_15': x__propagate_subtract_refinements__mutmut_15, 
    'x__propagate_subtract_refinements__mutmut_16': x__propagate_subtract_refinements__mutmut_16, 
    'x__propagate_subtract_refinements__mutmut_17': x__propagate_subtract_refinements__mutmut_17, 
    'x__propagate_subtract_refinements__mutmut_18': x__propagate_subtract_refinements__mutmut_18, 
    'x__propagate_subtract_refinements__mutmut_19': x__propagate_subtract_refinements__mutmut_19, 
    'x__propagate_subtract_refinements__mutmut_20': x__propagate_subtract_refinements__mutmut_20, 
    'x__propagate_subtract_refinements__mutmut_21': x__propagate_subtract_refinements__mutmut_21, 
    'x__propagate_subtract_refinements__mutmut_22': x__propagate_subtract_refinements__mutmut_22, 
    'x__propagate_subtract_refinements__mutmut_23': x__propagate_subtract_refinements__mutmut_23, 
    'x__propagate_subtract_refinements__mutmut_24': x__propagate_subtract_refinements__mutmut_24, 
    'x__propagate_subtract_refinements__mutmut_25': x__propagate_subtract_refinements__mutmut_25, 
    'x__propagate_subtract_refinements__mutmut_26': x__propagate_subtract_refinements__mutmut_26, 
    'x__propagate_subtract_refinements__mutmut_27': x__propagate_subtract_refinements__mutmut_27, 
    'x__propagate_subtract_refinements__mutmut_28': x__propagate_subtract_refinements__mutmut_28, 
    'x__propagate_subtract_refinements__mutmut_29': x__propagate_subtract_refinements__mutmut_29, 
    'x__propagate_subtract_refinements__mutmut_30': x__propagate_subtract_refinements__mutmut_30, 
    'x__propagate_subtract_refinements__mutmut_31': x__propagate_subtract_refinements__mutmut_31, 
    'x__propagate_subtract_refinements__mutmut_32': x__propagate_subtract_refinements__mutmut_32, 
    'x__propagate_subtract_refinements__mutmut_33': x__propagate_subtract_refinements__mutmut_33, 
    'x__propagate_subtract_refinements__mutmut_34': x__propagate_subtract_refinements__mutmut_34, 
    'x__propagate_subtract_refinements__mutmut_35': x__propagate_subtract_refinements__mutmut_35, 
    'x__propagate_subtract_refinements__mutmut_36': x__propagate_subtract_refinements__mutmut_36, 
    'x__propagate_subtract_refinements__mutmut_37': x__propagate_subtract_refinements__mutmut_37, 
    'x__propagate_subtract_refinements__mutmut_38': x__propagate_subtract_refinements__mutmut_38, 
    'x__propagate_subtract_refinements__mutmut_39': x__propagate_subtract_refinements__mutmut_39, 
    'x__propagate_subtract_refinements__mutmut_40': x__propagate_subtract_refinements__mutmut_40, 
    'x__propagate_subtract_refinements__mutmut_41': x__propagate_subtract_refinements__mutmut_41, 
    'x__propagate_subtract_refinements__mutmut_42': x__propagate_subtract_refinements__mutmut_42, 
    'x__propagate_subtract_refinements__mutmut_43': x__propagate_subtract_refinements__mutmut_43, 
    'x__propagate_subtract_refinements__mutmut_44': x__propagate_subtract_refinements__mutmut_44, 
    'x__propagate_subtract_refinements__mutmut_45': x__propagate_subtract_refinements__mutmut_45, 
    'x__propagate_subtract_refinements__mutmut_46': x__propagate_subtract_refinements__mutmut_46, 
    'x__propagate_subtract_refinements__mutmut_47': x__propagate_subtract_refinements__mutmut_47
}

def _propagate_subtract_refinements(*args, **kwargs):
    result = _mutmut_trampoline(x__propagate_subtract_refinements__mutmut_orig, x__propagate_subtract_refinements__mutmut_mutants, args, kwargs)
    return result 

_propagate_subtract_refinements.__signature__ = _mutmut_signature(x__propagate_subtract_refinements__mutmut_orig)
x__propagate_subtract_refinements__mutmut_orig.__name__ = 'x__propagate_subtract_refinements'


def x__propagate_multiply_refinements__mutmut_orig(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_1(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = None
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_2(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = None
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_3(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_4(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_5(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val >= POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_6(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = None
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_7(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["XXnumber_lower_boundXX"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_8(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["NUMBER_LOWER_BOUND"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_9(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] / known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_10(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[1] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_11(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[2],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_12(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = None
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_13(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["XXnumber_upper_boundXX"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_14(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["NUMBER_UPPER_BOUND"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_15(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] / known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_16(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[1] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_17(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[2],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_18(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val <= POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_19(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = None
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_20(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["XXnumber_lower_boundXX"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_21(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["NUMBER_LOWER_BOUND"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_22(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] / known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_23(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[1] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_24(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[2],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_25(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = None
    return new_ref


def x__propagate_multiply_refinements__mutmut_26(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["XXnumber_upper_boundXX"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_27(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["NUMBER_UPPER_BOUND"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_28(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] / known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_29(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[1] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
    return new_ref


def x__propagate_multiply_refinements__mutmut_30(
    ref_a: RefinedUnknownValue, ref_b: RefinedUnknownValue, val_a: Any, val_b: Any
) -> dict[str, Any]:
    """Handle refinement propagation for multiplication."""
    new_ref: dict[str, Any] = {}
    known_val, unknown_ref = (val_a, ref_b) if val_a is not None else (val_b, ref_a)
    if known_val is not None:
        if known_val > POSITIVE_BOUNDARY:
            if unknown_ref.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[1],
                )
            if unknown_ref.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
        elif known_val < POSITIVE_BOUNDARY:
            if unknown_ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    unknown_ref.number_upper_bound[0] * known_val,
                    unknown_ref.number_upper_bound[1],
                )
            if unknown_ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    unknown_ref.number_lower_bound[0] * known_val,
                    unknown_ref.number_lower_bound[2],
                )
    return new_ref

x__propagate_multiply_refinements__mutmut_mutants : ClassVar[MutantDict] = {
'x__propagate_multiply_refinements__mutmut_1': x__propagate_multiply_refinements__mutmut_1, 
    'x__propagate_multiply_refinements__mutmut_2': x__propagate_multiply_refinements__mutmut_2, 
    'x__propagate_multiply_refinements__mutmut_3': x__propagate_multiply_refinements__mutmut_3, 
    'x__propagate_multiply_refinements__mutmut_4': x__propagate_multiply_refinements__mutmut_4, 
    'x__propagate_multiply_refinements__mutmut_5': x__propagate_multiply_refinements__mutmut_5, 
    'x__propagate_multiply_refinements__mutmut_6': x__propagate_multiply_refinements__mutmut_6, 
    'x__propagate_multiply_refinements__mutmut_7': x__propagate_multiply_refinements__mutmut_7, 
    'x__propagate_multiply_refinements__mutmut_8': x__propagate_multiply_refinements__mutmut_8, 
    'x__propagate_multiply_refinements__mutmut_9': x__propagate_multiply_refinements__mutmut_9, 
    'x__propagate_multiply_refinements__mutmut_10': x__propagate_multiply_refinements__mutmut_10, 
    'x__propagate_multiply_refinements__mutmut_11': x__propagate_multiply_refinements__mutmut_11, 
    'x__propagate_multiply_refinements__mutmut_12': x__propagate_multiply_refinements__mutmut_12, 
    'x__propagate_multiply_refinements__mutmut_13': x__propagate_multiply_refinements__mutmut_13, 
    'x__propagate_multiply_refinements__mutmut_14': x__propagate_multiply_refinements__mutmut_14, 
    'x__propagate_multiply_refinements__mutmut_15': x__propagate_multiply_refinements__mutmut_15, 
    'x__propagate_multiply_refinements__mutmut_16': x__propagate_multiply_refinements__mutmut_16, 
    'x__propagate_multiply_refinements__mutmut_17': x__propagate_multiply_refinements__mutmut_17, 
    'x__propagate_multiply_refinements__mutmut_18': x__propagate_multiply_refinements__mutmut_18, 
    'x__propagate_multiply_refinements__mutmut_19': x__propagate_multiply_refinements__mutmut_19, 
    'x__propagate_multiply_refinements__mutmut_20': x__propagate_multiply_refinements__mutmut_20, 
    'x__propagate_multiply_refinements__mutmut_21': x__propagate_multiply_refinements__mutmut_21, 
    'x__propagate_multiply_refinements__mutmut_22': x__propagate_multiply_refinements__mutmut_22, 
    'x__propagate_multiply_refinements__mutmut_23': x__propagate_multiply_refinements__mutmut_23, 
    'x__propagate_multiply_refinements__mutmut_24': x__propagate_multiply_refinements__mutmut_24, 
    'x__propagate_multiply_refinements__mutmut_25': x__propagate_multiply_refinements__mutmut_25, 
    'x__propagate_multiply_refinements__mutmut_26': x__propagate_multiply_refinements__mutmut_26, 
    'x__propagate_multiply_refinements__mutmut_27': x__propagate_multiply_refinements__mutmut_27, 
    'x__propagate_multiply_refinements__mutmut_28': x__propagate_multiply_refinements__mutmut_28, 
    'x__propagate_multiply_refinements__mutmut_29': x__propagate_multiply_refinements__mutmut_29, 
    'x__propagate_multiply_refinements__mutmut_30': x__propagate_multiply_refinements__mutmut_30
}

def _propagate_multiply_refinements(*args, **kwargs):
    result = _mutmut_trampoline(x__propagate_multiply_refinements__mutmut_orig, x__propagate_multiply_refinements__mutmut_mutants, args, kwargs)
    return result 

_propagate_multiply_refinements.__signature__ = _mutmut_signature(x__propagate_multiply_refinements__mutmut_orig)
x__propagate_multiply_refinements__mutmut_orig.__name__ = 'x__propagate_multiply_refinements'


def x__propagate_divide_refinements__mutmut_orig(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_1(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = None
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_2(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_3(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b >= POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_4(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = None
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_5(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["XXnumber_lower_boundXX"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_6(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["NUMBER_LOWER_BOUND"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_7(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] * val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_8(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[1] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_9(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[2],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_10(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = None
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_11(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["XXnumber_upper_boundXX"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_12(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["NUMBER_UPPER_BOUND"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_13(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] * val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_14(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[1] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_15(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[2],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_16(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b <= POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_17(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = None
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_18(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["XXnumber_lower_boundXX"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_19(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["NUMBER_LOWER_BOUND"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_20(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] * val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_21(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[1] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_22(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[2],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_23(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = None
    return new_ref


def x__propagate_divide_refinements__mutmut_24(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["XXnumber_upper_boundXX"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_25(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["NUMBER_UPPER_BOUND"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_26(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] * val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_27(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[1] / val_b,
                    ref_a.number_lower_bound[1],
                )
    return new_ref


def x__propagate_divide_refinements__mutmut_28(ref_a: RefinedUnknownValue, val_b: Any) -> dict[str, Any]:
    """Handle refinement propagation for division."""
    new_ref: dict[str, Any] = {}
    if val_b is not None:
        if val_b > POSITIVE_BOUNDARY:
            if ref_a.number_lower_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[1],
                )
            if ref_a.number_upper_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
        elif val_b < POSITIVE_BOUNDARY:
            if ref_a.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    ref_a.number_upper_bound[0] / val_b,
                    ref_a.number_upper_bound[1],
                )
            if ref_a.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    ref_a.number_lower_bound[0] / val_b,
                    ref_a.number_lower_bound[2],
                )
    return new_ref

x__propagate_divide_refinements__mutmut_mutants : ClassVar[MutantDict] = {
'x__propagate_divide_refinements__mutmut_1': x__propagate_divide_refinements__mutmut_1, 
    'x__propagate_divide_refinements__mutmut_2': x__propagate_divide_refinements__mutmut_2, 
    'x__propagate_divide_refinements__mutmut_3': x__propagate_divide_refinements__mutmut_3, 
    'x__propagate_divide_refinements__mutmut_4': x__propagate_divide_refinements__mutmut_4, 
    'x__propagate_divide_refinements__mutmut_5': x__propagate_divide_refinements__mutmut_5, 
    'x__propagate_divide_refinements__mutmut_6': x__propagate_divide_refinements__mutmut_6, 
    'x__propagate_divide_refinements__mutmut_7': x__propagate_divide_refinements__mutmut_7, 
    'x__propagate_divide_refinements__mutmut_8': x__propagate_divide_refinements__mutmut_8, 
    'x__propagate_divide_refinements__mutmut_9': x__propagate_divide_refinements__mutmut_9, 
    'x__propagate_divide_refinements__mutmut_10': x__propagate_divide_refinements__mutmut_10, 
    'x__propagate_divide_refinements__mutmut_11': x__propagate_divide_refinements__mutmut_11, 
    'x__propagate_divide_refinements__mutmut_12': x__propagate_divide_refinements__mutmut_12, 
    'x__propagate_divide_refinements__mutmut_13': x__propagate_divide_refinements__mutmut_13, 
    'x__propagate_divide_refinements__mutmut_14': x__propagate_divide_refinements__mutmut_14, 
    'x__propagate_divide_refinements__mutmut_15': x__propagate_divide_refinements__mutmut_15, 
    'x__propagate_divide_refinements__mutmut_16': x__propagate_divide_refinements__mutmut_16, 
    'x__propagate_divide_refinements__mutmut_17': x__propagate_divide_refinements__mutmut_17, 
    'x__propagate_divide_refinements__mutmut_18': x__propagate_divide_refinements__mutmut_18, 
    'x__propagate_divide_refinements__mutmut_19': x__propagate_divide_refinements__mutmut_19, 
    'x__propagate_divide_refinements__mutmut_20': x__propagate_divide_refinements__mutmut_20, 
    'x__propagate_divide_refinements__mutmut_21': x__propagate_divide_refinements__mutmut_21, 
    'x__propagate_divide_refinements__mutmut_22': x__propagate_divide_refinements__mutmut_22, 
    'x__propagate_divide_refinements__mutmut_23': x__propagate_divide_refinements__mutmut_23, 
    'x__propagate_divide_refinements__mutmut_24': x__propagate_divide_refinements__mutmut_24, 
    'x__propagate_divide_refinements__mutmut_25': x__propagate_divide_refinements__mutmut_25, 
    'x__propagate_divide_refinements__mutmut_26': x__propagate_divide_refinements__mutmut_26, 
    'x__propagate_divide_refinements__mutmut_27': x__propagate_divide_refinements__mutmut_27, 
    'x__propagate_divide_refinements__mutmut_28': x__propagate_divide_refinements__mutmut_28
}

def _propagate_divide_refinements(*args, **kwargs):
    result = _mutmut_trampoline(x__propagate_divide_refinements__mutmut_orig, x__propagate_divide_refinements__mutmut_mutants, args, kwargs)
    return result 

_propagate_divide_refinements.__signature__ = _mutmut_signature(x__propagate_divide_refinements__mutmut_orig)
x__propagate_divide_refinements__mutmut_orig.__name__ = 'x__propagate_divide_refinements'


def x__propagate_refined_unknowns__mutmut_orig(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_1(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_2(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) and isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_3(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(None)

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_4(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = None

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_5(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(None, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_6(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, None)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_7(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_8(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, )

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_9(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op != "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_10(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "XXaddXX":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_11(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "ADD":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_12(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = None
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_13(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(None, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_14(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, None, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_15(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, None, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_16(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, None)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_17(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_18(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_19(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_20(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, )
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_21(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op != "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_22(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "XXsubtractXX":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_23(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "SUBTRACT":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_24(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = None
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_25(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(None, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_26(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, None, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_27(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, None, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_28(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, None)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_29(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_30(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_31(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_32(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, )
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_33(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op != "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_34(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "XXmultiplyXX":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_35(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "MULTIPLY":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_36(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = None
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_37(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(None, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_38(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, None, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_39(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, None, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_40(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, None)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_41(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_42(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_43(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_44(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, )
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_45(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op != "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_46(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "XXdivideXX":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_47(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "DIVIDE":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_48(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = None
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_49(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(None, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_50(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, None)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_51(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_52(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, )
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_53(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = None

    return CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_54(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(None, value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_55(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), value=None)


def x__propagate_refined_unknowns__mutmut_56(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(value=RefinedUnknownValue(**new_ref))


def x__propagate_refined_unknowns__mutmut_57(op: str, a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    """Helper to propagate refinements for binary numeric operations."""
    if not (isinstance(a.value, RefinedUnknownValue) or isinstance(b.value, RefinedUnknownValue)):
        return CtyValue.unknown(CtyNumber())

    ref_a, ref_b, val_a, val_b = _get_refined_components(a, b)

    if op == "add":
        new_ref = _propagate_add_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "subtract":
        new_ref = _propagate_subtract_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "multiply":
        new_ref = _propagate_multiply_refinements(ref_a, ref_b, val_a, val_b)
    elif op == "divide":
        new_ref = _propagate_divide_refinements(ref_a, val_b)
    else:
        new_ref = {}

    return CtyValue.unknown(CtyNumber(), )

x__propagate_refined_unknowns__mutmut_mutants : ClassVar[MutantDict] = {
'x__propagate_refined_unknowns__mutmut_1': x__propagate_refined_unknowns__mutmut_1, 
    'x__propagate_refined_unknowns__mutmut_2': x__propagate_refined_unknowns__mutmut_2, 
    'x__propagate_refined_unknowns__mutmut_3': x__propagate_refined_unknowns__mutmut_3, 
    'x__propagate_refined_unknowns__mutmut_4': x__propagate_refined_unknowns__mutmut_4, 
    'x__propagate_refined_unknowns__mutmut_5': x__propagate_refined_unknowns__mutmut_5, 
    'x__propagate_refined_unknowns__mutmut_6': x__propagate_refined_unknowns__mutmut_6, 
    'x__propagate_refined_unknowns__mutmut_7': x__propagate_refined_unknowns__mutmut_7, 
    'x__propagate_refined_unknowns__mutmut_8': x__propagate_refined_unknowns__mutmut_8, 
    'x__propagate_refined_unknowns__mutmut_9': x__propagate_refined_unknowns__mutmut_9, 
    'x__propagate_refined_unknowns__mutmut_10': x__propagate_refined_unknowns__mutmut_10, 
    'x__propagate_refined_unknowns__mutmut_11': x__propagate_refined_unknowns__mutmut_11, 
    'x__propagate_refined_unknowns__mutmut_12': x__propagate_refined_unknowns__mutmut_12, 
    'x__propagate_refined_unknowns__mutmut_13': x__propagate_refined_unknowns__mutmut_13, 
    'x__propagate_refined_unknowns__mutmut_14': x__propagate_refined_unknowns__mutmut_14, 
    'x__propagate_refined_unknowns__mutmut_15': x__propagate_refined_unknowns__mutmut_15, 
    'x__propagate_refined_unknowns__mutmut_16': x__propagate_refined_unknowns__mutmut_16, 
    'x__propagate_refined_unknowns__mutmut_17': x__propagate_refined_unknowns__mutmut_17, 
    'x__propagate_refined_unknowns__mutmut_18': x__propagate_refined_unknowns__mutmut_18, 
    'x__propagate_refined_unknowns__mutmut_19': x__propagate_refined_unknowns__mutmut_19, 
    'x__propagate_refined_unknowns__mutmut_20': x__propagate_refined_unknowns__mutmut_20, 
    'x__propagate_refined_unknowns__mutmut_21': x__propagate_refined_unknowns__mutmut_21, 
    'x__propagate_refined_unknowns__mutmut_22': x__propagate_refined_unknowns__mutmut_22, 
    'x__propagate_refined_unknowns__mutmut_23': x__propagate_refined_unknowns__mutmut_23, 
    'x__propagate_refined_unknowns__mutmut_24': x__propagate_refined_unknowns__mutmut_24, 
    'x__propagate_refined_unknowns__mutmut_25': x__propagate_refined_unknowns__mutmut_25, 
    'x__propagate_refined_unknowns__mutmut_26': x__propagate_refined_unknowns__mutmut_26, 
    'x__propagate_refined_unknowns__mutmut_27': x__propagate_refined_unknowns__mutmut_27, 
    'x__propagate_refined_unknowns__mutmut_28': x__propagate_refined_unknowns__mutmut_28, 
    'x__propagate_refined_unknowns__mutmut_29': x__propagate_refined_unknowns__mutmut_29, 
    'x__propagate_refined_unknowns__mutmut_30': x__propagate_refined_unknowns__mutmut_30, 
    'x__propagate_refined_unknowns__mutmut_31': x__propagate_refined_unknowns__mutmut_31, 
    'x__propagate_refined_unknowns__mutmut_32': x__propagate_refined_unknowns__mutmut_32, 
    'x__propagate_refined_unknowns__mutmut_33': x__propagate_refined_unknowns__mutmut_33, 
    'x__propagate_refined_unknowns__mutmut_34': x__propagate_refined_unknowns__mutmut_34, 
    'x__propagate_refined_unknowns__mutmut_35': x__propagate_refined_unknowns__mutmut_35, 
    'x__propagate_refined_unknowns__mutmut_36': x__propagate_refined_unknowns__mutmut_36, 
    'x__propagate_refined_unknowns__mutmut_37': x__propagate_refined_unknowns__mutmut_37, 
    'x__propagate_refined_unknowns__mutmut_38': x__propagate_refined_unknowns__mutmut_38, 
    'x__propagate_refined_unknowns__mutmut_39': x__propagate_refined_unknowns__mutmut_39, 
    'x__propagate_refined_unknowns__mutmut_40': x__propagate_refined_unknowns__mutmut_40, 
    'x__propagate_refined_unknowns__mutmut_41': x__propagate_refined_unknowns__mutmut_41, 
    'x__propagate_refined_unknowns__mutmut_42': x__propagate_refined_unknowns__mutmut_42, 
    'x__propagate_refined_unknowns__mutmut_43': x__propagate_refined_unknowns__mutmut_43, 
    'x__propagate_refined_unknowns__mutmut_44': x__propagate_refined_unknowns__mutmut_44, 
    'x__propagate_refined_unknowns__mutmut_45': x__propagate_refined_unknowns__mutmut_45, 
    'x__propagate_refined_unknowns__mutmut_46': x__propagate_refined_unknowns__mutmut_46, 
    'x__propagate_refined_unknowns__mutmut_47': x__propagate_refined_unknowns__mutmut_47, 
    'x__propagate_refined_unknowns__mutmut_48': x__propagate_refined_unknowns__mutmut_48, 
    'x__propagate_refined_unknowns__mutmut_49': x__propagate_refined_unknowns__mutmut_49, 
    'x__propagate_refined_unknowns__mutmut_50': x__propagate_refined_unknowns__mutmut_50, 
    'x__propagate_refined_unknowns__mutmut_51': x__propagate_refined_unknowns__mutmut_51, 
    'x__propagate_refined_unknowns__mutmut_52': x__propagate_refined_unknowns__mutmut_52, 
    'x__propagate_refined_unknowns__mutmut_53': x__propagate_refined_unknowns__mutmut_53, 
    'x__propagate_refined_unknowns__mutmut_54': x__propagate_refined_unknowns__mutmut_54, 
    'x__propagate_refined_unknowns__mutmut_55': x__propagate_refined_unknowns__mutmut_55, 
    'x__propagate_refined_unknowns__mutmut_56': x__propagate_refined_unknowns__mutmut_56, 
    'x__propagate_refined_unknowns__mutmut_57': x__propagate_refined_unknowns__mutmut_57
}

def _propagate_refined_unknowns(*args, **kwargs):
    result = _mutmut_trampoline(x__propagate_refined_unknowns__mutmut_orig, x__propagate_refined_unknowns__mutmut_mutants, args, kwargs)
    return result 

_propagate_refined_unknowns.__signature__ = _mutmut_signature(x__propagate_refined_unknowns__mutmut_orig)
x__propagate_refined_unknowns__mutmut_orig.__name__ = 'x__propagate_refined_unknowns'


def x_add__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) and not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError(None)
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("XXadd: arguments must be numbersXX")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("ADD: ARGUMENTS MUST BE NUMBERS")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null and b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_8(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(None)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_9(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown and b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_10(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns(None, a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_11(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", None, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_12(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, None)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_13(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns(a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_14(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_15(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, )
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_16(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("XXaddXX", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_17(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("ADD", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_18(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = None
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_19(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(None, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_20(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, None)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_21(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_22(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, )
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_23(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = None
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_24(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(None, b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_25(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, None)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_26(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(b.value)
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_27(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, )
    return CtyNumber().validate(a_val + b_val)


def x_add__mutmut_28(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(None)


def x_add__mutmut_29(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("add: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("add", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)

x_add__mutmut_mutants : ClassVar[MutantDict] = {
'x_add__mutmut_1': x_add__mutmut_1, 
    'x_add__mutmut_2': x_add__mutmut_2, 
    'x_add__mutmut_3': x_add__mutmut_3, 
    'x_add__mutmut_4': x_add__mutmut_4, 
    'x_add__mutmut_5': x_add__mutmut_5, 
    'x_add__mutmut_6': x_add__mutmut_6, 
    'x_add__mutmut_7': x_add__mutmut_7, 
    'x_add__mutmut_8': x_add__mutmut_8, 
    'x_add__mutmut_9': x_add__mutmut_9, 
    'x_add__mutmut_10': x_add__mutmut_10, 
    'x_add__mutmut_11': x_add__mutmut_11, 
    'x_add__mutmut_12': x_add__mutmut_12, 
    'x_add__mutmut_13': x_add__mutmut_13, 
    'x_add__mutmut_14': x_add__mutmut_14, 
    'x_add__mutmut_15': x_add__mutmut_15, 
    'x_add__mutmut_16': x_add__mutmut_16, 
    'x_add__mutmut_17': x_add__mutmut_17, 
    'x_add__mutmut_18': x_add__mutmut_18, 
    'x_add__mutmut_19': x_add__mutmut_19, 
    'x_add__mutmut_20': x_add__mutmut_20, 
    'x_add__mutmut_21': x_add__mutmut_21, 
    'x_add__mutmut_22': x_add__mutmut_22, 
    'x_add__mutmut_23': x_add__mutmut_23, 
    'x_add__mutmut_24': x_add__mutmut_24, 
    'x_add__mutmut_25': x_add__mutmut_25, 
    'x_add__mutmut_26': x_add__mutmut_26, 
    'x_add__mutmut_27': x_add__mutmut_27, 
    'x_add__mutmut_28': x_add__mutmut_28, 
    'x_add__mutmut_29': x_add__mutmut_29
}

def add(*args, **kwargs):
    result = _mutmut_trampoline(x_add__mutmut_orig, x_add__mutmut_mutants, args, kwargs)
    return result 

add.__signature__ = _mutmut_signature(x_add__mutmut_orig)
x_add__mutmut_orig.__name__ = 'x_add'


def x_subtract__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) and not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError(None)
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("XXsubtract: arguments must be numbersXX")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("SUBTRACT: ARGUMENTS MUST BE NUMBERS")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null and b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_8(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(None)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_9(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown and b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_10(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns(None, a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_11(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", None, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_12(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, None)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_13(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns(a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_14(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_15(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, )
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_16(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("XXsubtractXX", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_17(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("SUBTRACT", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_18(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = None
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_19(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(None, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_20(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, None)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_21(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_22(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, )
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_23(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = None
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_24(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(None, b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_25(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, None)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_26(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(b.value)
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_27(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, )
    return CtyNumber().validate(a_val - b_val)


def x_subtract__mutmut_28(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(None)


def x_subtract__mutmut_29(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("subtract: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("subtract", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val + b_val)

x_subtract__mutmut_mutants : ClassVar[MutantDict] = {
'x_subtract__mutmut_1': x_subtract__mutmut_1, 
    'x_subtract__mutmut_2': x_subtract__mutmut_2, 
    'x_subtract__mutmut_3': x_subtract__mutmut_3, 
    'x_subtract__mutmut_4': x_subtract__mutmut_4, 
    'x_subtract__mutmut_5': x_subtract__mutmut_5, 
    'x_subtract__mutmut_6': x_subtract__mutmut_6, 
    'x_subtract__mutmut_7': x_subtract__mutmut_7, 
    'x_subtract__mutmut_8': x_subtract__mutmut_8, 
    'x_subtract__mutmut_9': x_subtract__mutmut_9, 
    'x_subtract__mutmut_10': x_subtract__mutmut_10, 
    'x_subtract__mutmut_11': x_subtract__mutmut_11, 
    'x_subtract__mutmut_12': x_subtract__mutmut_12, 
    'x_subtract__mutmut_13': x_subtract__mutmut_13, 
    'x_subtract__mutmut_14': x_subtract__mutmut_14, 
    'x_subtract__mutmut_15': x_subtract__mutmut_15, 
    'x_subtract__mutmut_16': x_subtract__mutmut_16, 
    'x_subtract__mutmut_17': x_subtract__mutmut_17, 
    'x_subtract__mutmut_18': x_subtract__mutmut_18, 
    'x_subtract__mutmut_19': x_subtract__mutmut_19, 
    'x_subtract__mutmut_20': x_subtract__mutmut_20, 
    'x_subtract__mutmut_21': x_subtract__mutmut_21, 
    'x_subtract__mutmut_22': x_subtract__mutmut_22, 
    'x_subtract__mutmut_23': x_subtract__mutmut_23, 
    'x_subtract__mutmut_24': x_subtract__mutmut_24, 
    'x_subtract__mutmut_25': x_subtract__mutmut_25, 
    'x_subtract__mutmut_26': x_subtract__mutmut_26, 
    'x_subtract__mutmut_27': x_subtract__mutmut_27, 
    'x_subtract__mutmut_28': x_subtract__mutmut_28, 
    'x_subtract__mutmut_29': x_subtract__mutmut_29
}

def subtract(*args, **kwargs):
    result = _mutmut_trampoline(x_subtract__mutmut_orig, x_subtract__mutmut_mutants, args, kwargs)
    return result 

subtract.__signature__ = _mutmut_signature(x_subtract__mutmut_orig)
x_subtract__mutmut_orig.__name__ = 'x_subtract'


def x_multiply__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) and not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError(None)
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("XXmultiply: arguments must be numbersXX")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("MULTIPLY: ARGUMENTS MUST BE NUMBERS")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null and b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_8(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(None)
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_9(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) and (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_10(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown or a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_11(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_12(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value != ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_13(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown or b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_14(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_15(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value != ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_16(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(None)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_17(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown and b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_18(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns(None, a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_19(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", None, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_20(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, None)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_21(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns(a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_22(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_23(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, )
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_24(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("XXmultiplyXX", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_25(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("MULTIPLY", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_26(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = None
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_27(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(None, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_28(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, None)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_29(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_30(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, )
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_31(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = None
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_32(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(None, b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_33(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, None)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_34(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(b.value)
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_35(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, )
    return CtyNumber().validate(a_val * b_val)


def x_multiply__mutmut_36(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(None)


def x_multiply__mutmut_37(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("multiply: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if (not a.is_unknown and a.value == ZERO_VALUE) or (not b.is_unknown and b.value == ZERO_VALUE):
        return CtyNumber().validate(ZERO_VALUE)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("multiply", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)

x_multiply__mutmut_mutants : ClassVar[MutantDict] = {
'x_multiply__mutmut_1': x_multiply__mutmut_1, 
    'x_multiply__mutmut_2': x_multiply__mutmut_2, 
    'x_multiply__mutmut_3': x_multiply__mutmut_3, 
    'x_multiply__mutmut_4': x_multiply__mutmut_4, 
    'x_multiply__mutmut_5': x_multiply__mutmut_5, 
    'x_multiply__mutmut_6': x_multiply__mutmut_6, 
    'x_multiply__mutmut_7': x_multiply__mutmut_7, 
    'x_multiply__mutmut_8': x_multiply__mutmut_8, 
    'x_multiply__mutmut_9': x_multiply__mutmut_9, 
    'x_multiply__mutmut_10': x_multiply__mutmut_10, 
    'x_multiply__mutmut_11': x_multiply__mutmut_11, 
    'x_multiply__mutmut_12': x_multiply__mutmut_12, 
    'x_multiply__mutmut_13': x_multiply__mutmut_13, 
    'x_multiply__mutmut_14': x_multiply__mutmut_14, 
    'x_multiply__mutmut_15': x_multiply__mutmut_15, 
    'x_multiply__mutmut_16': x_multiply__mutmut_16, 
    'x_multiply__mutmut_17': x_multiply__mutmut_17, 
    'x_multiply__mutmut_18': x_multiply__mutmut_18, 
    'x_multiply__mutmut_19': x_multiply__mutmut_19, 
    'x_multiply__mutmut_20': x_multiply__mutmut_20, 
    'x_multiply__mutmut_21': x_multiply__mutmut_21, 
    'x_multiply__mutmut_22': x_multiply__mutmut_22, 
    'x_multiply__mutmut_23': x_multiply__mutmut_23, 
    'x_multiply__mutmut_24': x_multiply__mutmut_24, 
    'x_multiply__mutmut_25': x_multiply__mutmut_25, 
    'x_multiply__mutmut_26': x_multiply__mutmut_26, 
    'x_multiply__mutmut_27': x_multiply__mutmut_27, 
    'x_multiply__mutmut_28': x_multiply__mutmut_28, 
    'x_multiply__mutmut_29': x_multiply__mutmut_29, 
    'x_multiply__mutmut_30': x_multiply__mutmut_30, 
    'x_multiply__mutmut_31': x_multiply__mutmut_31, 
    'x_multiply__mutmut_32': x_multiply__mutmut_32, 
    'x_multiply__mutmut_33': x_multiply__mutmut_33, 
    'x_multiply__mutmut_34': x_multiply__mutmut_34, 
    'x_multiply__mutmut_35': x_multiply__mutmut_35, 
    'x_multiply__mutmut_36': x_multiply__mutmut_36, 
    'x_multiply__mutmut_37': x_multiply__mutmut_37
}

def multiply(*args, **kwargs):
    result = _mutmut_trampoline(x_multiply__mutmut_orig, x_multiply__mutmut_mutants, args, kwargs)
    return result 

multiply.__signature__ = _mutmut_signature(x_multiply__mutmut_orig)
x_multiply__mutmut_orig.__name__ = 'x_multiply'


def x_divide__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) and not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError(None)
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("XXdivide: arguments must be numbersXX")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("DIVIDE: ARGUMENTS MUST BE NUMBERS")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null and b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_8(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(None)
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_9(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown or b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_10(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_11(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value != ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_12(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError(None)
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_13(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("XXdivide by zeroXX")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_14(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("DIVIDE BY ZERO")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_15(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown and b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_16(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns(None, a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_17(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", None, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_18(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, None)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_19(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns(a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_20(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_21(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, )
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_22(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("XXdivideXX", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_23(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("DIVIDE", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_24(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = None
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_25(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(None, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_26(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, None)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_27(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_28(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, )
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_29(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = None
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_30(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(None, b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_31(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, None)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_32(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(b.value)
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_33(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, )
    return CtyNumber().validate(a_val / b_val)


def x_divide__mutmut_34(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(None)


def x_divide__mutmut_35(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("divide: arguments must be numbers")
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyNumber())
    if not b.is_unknown and b.value == ZERO_VALUE:
        raise CtyFunctionError("divide by zero")
    if a.is_unknown or b.is_unknown:
        return _propagate_refined_unknowns("divide", a, b)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(a_val * b_val)

x_divide__mutmut_mutants : ClassVar[MutantDict] = {
'x_divide__mutmut_1': x_divide__mutmut_1, 
    'x_divide__mutmut_2': x_divide__mutmut_2, 
    'x_divide__mutmut_3': x_divide__mutmut_3, 
    'x_divide__mutmut_4': x_divide__mutmut_4, 
    'x_divide__mutmut_5': x_divide__mutmut_5, 
    'x_divide__mutmut_6': x_divide__mutmut_6, 
    'x_divide__mutmut_7': x_divide__mutmut_7, 
    'x_divide__mutmut_8': x_divide__mutmut_8, 
    'x_divide__mutmut_9': x_divide__mutmut_9, 
    'x_divide__mutmut_10': x_divide__mutmut_10, 
    'x_divide__mutmut_11': x_divide__mutmut_11, 
    'x_divide__mutmut_12': x_divide__mutmut_12, 
    'x_divide__mutmut_13': x_divide__mutmut_13, 
    'x_divide__mutmut_14': x_divide__mutmut_14, 
    'x_divide__mutmut_15': x_divide__mutmut_15, 
    'x_divide__mutmut_16': x_divide__mutmut_16, 
    'x_divide__mutmut_17': x_divide__mutmut_17, 
    'x_divide__mutmut_18': x_divide__mutmut_18, 
    'x_divide__mutmut_19': x_divide__mutmut_19, 
    'x_divide__mutmut_20': x_divide__mutmut_20, 
    'x_divide__mutmut_21': x_divide__mutmut_21, 
    'x_divide__mutmut_22': x_divide__mutmut_22, 
    'x_divide__mutmut_23': x_divide__mutmut_23, 
    'x_divide__mutmut_24': x_divide__mutmut_24, 
    'x_divide__mutmut_25': x_divide__mutmut_25, 
    'x_divide__mutmut_26': x_divide__mutmut_26, 
    'x_divide__mutmut_27': x_divide__mutmut_27, 
    'x_divide__mutmut_28': x_divide__mutmut_28, 
    'x_divide__mutmut_29': x_divide__mutmut_29, 
    'x_divide__mutmut_30': x_divide__mutmut_30, 
    'x_divide__mutmut_31': x_divide__mutmut_31, 
    'x_divide__mutmut_32': x_divide__mutmut_32, 
    'x_divide__mutmut_33': x_divide__mutmut_33, 
    'x_divide__mutmut_34': x_divide__mutmut_34, 
    'x_divide__mutmut_35': x_divide__mutmut_35
}

def divide(*args, **kwargs):
    result = _mutmut_trampoline(x_divide__mutmut_orig, x_divide__mutmut_mutants, args, kwargs)
    return result 

divide.__signature__ = _mutmut_signature(x_divide__mutmut_orig)
x_divide__mutmut_orig.__name__ = 'x_divide'


def x_modulo__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) and not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError(None)
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("XXmodulo: arguments must be numbersXX")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("MODULO: ARGUMENTS MUST BE NUMBERS")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null and b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_8(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown and b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_9(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null and a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_10(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(None)
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_11(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value != ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_12(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError(None)
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_13(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("XXmodulo by zeroXX")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_14(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("MODULO BY ZERO")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_15(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = None
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_16(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(None, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_17(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, None)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_18(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_19(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, )
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_20(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = None
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_21(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(None, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_22(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, None)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_23(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_24(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, )
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(b_val)))))


def x_modulo__mutmut_25(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(None)


def x_modulo__mutmut_26(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(None))


def x_modulo__mutmut_27(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(None)))


def x_modulo__mutmut_28(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(None, float(b_val)))))


def x_modulo__mutmut_29(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), None))))


def x_modulo__mutmut_30(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(b_val)))))


def x_modulo__mutmut_31(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), ))))


def x_modulo__mutmut_32(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(None), float(b_val)))))


def x_modulo__mutmut_33(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber) or not isinstance(b.type, CtyNumber):
        raise CtyFunctionError("modulo: arguments must be numbers")
    if a.is_null or a.is_unknown or b.is_null or b.is_unknown:
        return CtyValue.unknown(CtyNumber())
    if b.value == ZERO_VALUE:
        raise CtyFunctionError("modulo by zero")
    a_val = cast(Decimal, a.value)
    b_val = cast(Decimal, b.value)
    return CtyNumber().validate(Decimal(str(math.fmod(float(a_val), float(None)))))

x_modulo__mutmut_mutants : ClassVar[MutantDict] = {
'x_modulo__mutmut_1': x_modulo__mutmut_1, 
    'x_modulo__mutmut_2': x_modulo__mutmut_2, 
    'x_modulo__mutmut_3': x_modulo__mutmut_3, 
    'x_modulo__mutmut_4': x_modulo__mutmut_4, 
    'x_modulo__mutmut_5': x_modulo__mutmut_5, 
    'x_modulo__mutmut_6': x_modulo__mutmut_6, 
    'x_modulo__mutmut_7': x_modulo__mutmut_7, 
    'x_modulo__mutmut_8': x_modulo__mutmut_8, 
    'x_modulo__mutmut_9': x_modulo__mutmut_9, 
    'x_modulo__mutmut_10': x_modulo__mutmut_10, 
    'x_modulo__mutmut_11': x_modulo__mutmut_11, 
    'x_modulo__mutmut_12': x_modulo__mutmut_12, 
    'x_modulo__mutmut_13': x_modulo__mutmut_13, 
    'x_modulo__mutmut_14': x_modulo__mutmut_14, 
    'x_modulo__mutmut_15': x_modulo__mutmut_15, 
    'x_modulo__mutmut_16': x_modulo__mutmut_16, 
    'x_modulo__mutmut_17': x_modulo__mutmut_17, 
    'x_modulo__mutmut_18': x_modulo__mutmut_18, 
    'x_modulo__mutmut_19': x_modulo__mutmut_19, 
    'x_modulo__mutmut_20': x_modulo__mutmut_20, 
    'x_modulo__mutmut_21': x_modulo__mutmut_21, 
    'x_modulo__mutmut_22': x_modulo__mutmut_22, 
    'x_modulo__mutmut_23': x_modulo__mutmut_23, 
    'x_modulo__mutmut_24': x_modulo__mutmut_24, 
    'x_modulo__mutmut_25': x_modulo__mutmut_25, 
    'x_modulo__mutmut_26': x_modulo__mutmut_26, 
    'x_modulo__mutmut_27': x_modulo__mutmut_27, 
    'x_modulo__mutmut_28': x_modulo__mutmut_28, 
    'x_modulo__mutmut_29': x_modulo__mutmut_29, 
    'x_modulo__mutmut_30': x_modulo__mutmut_30, 
    'x_modulo__mutmut_31': x_modulo__mutmut_31, 
    'x_modulo__mutmut_32': x_modulo__mutmut_32, 
    'x_modulo__mutmut_33': x_modulo__mutmut_33
}

def modulo(*args, **kwargs):
    result = _mutmut_trampoline(x_modulo__mutmut_orig, x_modulo__mutmut_mutants, args, kwargs)
    return result 

modulo.__signature__ = _mutmut_signature(x_modulo__mutmut_orig)
x_modulo__mutmut_orig.__name__ = 'x_modulo'


def x_negate__mutmut_orig(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_1(a: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_2(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError(None)
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_3(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("XXnegate: argument must be a numberXX")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_4(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("NEGATE: ARGUMENT MUST BE A NUMBER")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_5(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(None)
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_6(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = None
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_7(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = None
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_8(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = None
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_9(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["XXnumber_lower_boundXX"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_10(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["NUMBER_LOWER_BOUND"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_11(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    +ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_12(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[1],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_13(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[2],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_14(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = None
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_15(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["XXnumber_upper_boundXX"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_16(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["NUMBER_UPPER_BOUND"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_17(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    +ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_18(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[1],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_19(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[2],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_20(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(None, value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_21(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=None)  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_22(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_23(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), )  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_24(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(None)
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_25(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(None)
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_26(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = None
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_27(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(None, a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_28(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, None)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_29(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(a.value)
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_30(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, )
    return CtyNumber().validate(-a_val)


def x_negate__mutmut_31(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(None)


def x_negate__mutmut_32(a: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(a.type, CtyNumber):
        raise CtyFunctionError("negate: argument must be a number")
    if a.is_null:
        return CtyValue.null(CtyNumber())
    if a.is_unknown:
        if isinstance(a.value, RefinedUnknownValue):
            ref = a.value
            new_ref = {}
            if ref.number_upper_bound:
                new_ref["number_lower_bound"] = (
                    -ref.number_upper_bound[0],
                    ref.number_upper_bound[1],
                )
            if ref.number_lower_bound:
                new_ref["number_upper_bound"] = (
                    -ref.number_lower_bound[0],
                    ref.number_lower_bound[1],
                )
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    a_val = cast(Decimal, a.value)
    return CtyNumber().validate(+a_val)

x_negate__mutmut_mutants : ClassVar[MutantDict] = {
'x_negate__mutmut_1': x_negate__mutmut_1, 
    'x_negate__mutmut_2': x_negate__mutmut_2, 
    'x_negate__mutmut_3': x_negate__mutmut_3, 
    'x_negate__mutmut_4': x_negate__mutmut_4, 
    'x_negate__mutmut_5': x_negate__mutmut_5, 
    'x_negate__mutmut_6': x_negate__mutmut_6, 
    'x_negate__mutmut_7': x_negate__mutmut_7, 
    'x_negate__mutmut_8': x_negate__mutmut_8, 
    'x_negate__mutmut_9': x_negate__mutmut_9, 
    'x_negate__mutmut_10': x_negate__mutmut_10, 
    'x_negate__mutmut_11': x_negate__mutmut_11, 
    'x_negate__mutmut_12': x_negate__mutmut_12, 
    'x_negate__mutmut_13': x_negate__mutmut_13, 
    'x_negate__mutmut_14': x_negate__mutmut_14, 
    'x_negate__mutmut_15': x_negate__mutmut_15, 
    'x_negate__mutmut_16': x_negate__mutmut_16, 
    'x_negate__mutmut_17': x_negate__mutmut_17, 
    'x_negate__mutmut_18': x_negate__mutmut_18, 
    'x_negate__mutmut_19': x_negate__mutmut_19, 
    'x_negate__mutmut_20': x_negate__mutmut_20, 
    'x_negate__mutmut_21': x_negate__mutmut_21, 
    'x_negate__mutmut_22': x_negate__mutmut_22, 
    'x_negate__mutmut_23': x_negate__mutmut_23, 
    'x_negate__mutmut_24': x_negate__mutmut_24, 
    'x_negate__mutmut_25': x_negate__mutmut_25, 
    'x_negate__mutmut_26': x_negate__mutmut_26, 
    'x_negate__mutmut_27': x_negate__mutmut_27, 
    'x_negate__mutmut_28': x_negate__mutmut_28, 
    'x_negate__mutmut_29': x_negate__mutmut_29, 
    'x_negate__mutmut_30': x_negate__mutmut_30, 
    'x_negate__mutmut_31': x_negate__mutmut_31, 
    'x_negate__mutmut_32': x_negate__mutmut_32
}

def negate(*args, **kwargs):
    result = _mutmut_trampoline(x_negate__mutmut_orig, x_negate__mutmut_mutants, args, kwargs)
    return result 

negate.__signature__ = _mutmut_signature(x_negate__mutmut_orig)
x_negate__mutmut_orig.__name__ = 'x_negate'


def x_abs_fn__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(None)
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(None)
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = None
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = None
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = None
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower or upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = None
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = None
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val > 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 1:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val < 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 1:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = None
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["XXnumber_lower_boundXX"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["NUMBER_LOWER_BOUND"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (+u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_18(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = None
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_19(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["XXnumber_upper_boundXX"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_20(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["NUMBER_UPPER_BOUND"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_21(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (+l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_22(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = None
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_23(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["XXnumber_lower_boundXX"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_24(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["NUMBER_LOWER_BOUND"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_25(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(None), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_26(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(1), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_27(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), False)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_28(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = None
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_29(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(None, abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_30(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), None)
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_31(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_32(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), )
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_33(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(None), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_34(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(None))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_35(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = None
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_36(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(None) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_37(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) > abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_38(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(None) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_39(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = None
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_40(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["XXnumber_upper_boundXX"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_41(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["NUMBER_UPPER_BOUND"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_42(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower or lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_43(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[1] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_44(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] > 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_45(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 1:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_46(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper or upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_47(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[1] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_48(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] < 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_49(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 1:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_50(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = None
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_51(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["XXnumber_lower_boundXX"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_52(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["NUMBER_LOWER_BOUND"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_53(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (+upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_54(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[1], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_55(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[2])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_56(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(None, value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_57(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=None)  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_58(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_59(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), )  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_60(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(None)
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_61(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(None)
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_62(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = None
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_63(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(None, input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_64(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, None)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_65(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(input_val.value)
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_66(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, )
    return CtyNumber().validate(abs(val))


def x_abs_fn__mutmut_67(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(None)


def x_abs_fn__mutmut_68(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"abs: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null:
        return CtyValue.null(CtyNumber())
    if input_val.is_unknown:
        if isinstance(input_val.value, RefinedUnknownValue):
            ref = input_val.value
            new_ref = {}
            lower, upper = ref.number_lower_bound, ref.number_upper_bound
            if lower and upper:
                l_val, l_inc = lower
                u_val, u_inc = upper
                if l_val >= 0:
                    return input_val
                if u_val <= 0:
                    new_ref["number_lower_bound"] = (-u_val, u_inc)
                    new_ref["number_upper_bound"] = (-l_val, l_inc)
                else:
                    new_ref["number_lower_bound"] = (Decimal(0), True)
                    new_upper_val = max(abs(l_val), abs(u_val))
                    new_upper_inc = l_inc if abs(l_val) >= abs(u_val) else u_inc
                    new_ref["number_upper_bound"] = (new_upper_val, new_upper_inc)
            elif lower and lower[0] >= 0:
                return input_val
            elif upper and upper[0] <= 0:
                new_ref["number_lower_bound"] = (-upper[0], upper[1])
            return (
                CtyValue.unknown(CtyNumber(), value=RefinedUnknownValue(**new_ref))  # type: ignore[arg-type]
                if new_ref
                else CtyValue.unknown(CtyNumber())
            )
        return CtyValue.unknown(CtyNumber())
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(abs(None))

x_abs_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_abs_fn__mutmut_1': x_abs_fn__mutmut_1, 
    'x_abs_fn__mutmut_2': x_abs_fn__mutmut_2, 
    'x_abs_fn__mutmut_3': x_abs_fn__mutmut_3, 
    'x_abs_fn__mutmut_4': x_abs_fn__mutmut_4, 
    'x_abs_fn__mutmut_5': x_abs_fn__mutmut_5, 
    'x_abs_fn__mutmut_6': x_abs_fn__mutmut_6, 
    'x_abs_fn__mutmut_7': x_abs_fn__mutmut_7, 
    'x_abs_fn__mutmut_8': x_abs_fn__mutmut_8, 
    'x_abs_fn__mutmut_9': x_abs_fn__mutmut_9, 
    'x_abs_fn__mutmut_10': x_abs_fn__mutmut_10, 
    'x_abs_fn__mutmut_11': x_abs_fn__mutmut_11, 
    'x_abs_fn__mutmut_12': x_abs_fn__mutmut_12, 
    'x_abs_fn__mutmut_13': x_abs_fn__mutmut_13, 
    'x_abs_fn__mutmut_14': x_abs_fn__mutmut_14, 
    'x_abs_fn__mutmut_15': x_abs_fn__mutmut_15, 
    'x_abs_fn__mutmut_16': x_abs_fn__mutmut_16, 
    'x_abs_fn__mutmut_17': x_abs_fn__mutmut_17, 
    'x_abs_fn__mutmut_18': x_abs_fn__mutmut_18, 
    'x_abs_fn__mutmut_19': x_abs_fn__mutmut_19, 
    'x_abs_fn__mutmut_20': x_abs_fn__mutmut_20, 
    'x_abs_fn__mutmut_21': x_abs_fn__mutmut_21, 
    'x_abs_fn__mutmut_22': x_abs_fn__mutmut_22, 
    'x_abs_fn__mutmut_23': x_abs_fn__mutmut_23, 
    'x_abs_fn__mutmut_24': x_abs_fn__mutmut_24, 
    'x_abs_fn__mutmut_25': x_abs_fn__mutmut_25, 
    'x_abs_fn__mutmut_26': x_abs_fn__mutmut_26, 
    'x_abs_fn__mutmut_27': x_abs_fn__mutmut_27, 
    'x_abs_fn__mutmut_28': x_abs_fn__mutmut_28, 
    'x_abs_fn__mutmut_29': x_abs_fn__mutmut_29, 
    'x_abs_fn__mutmut_30': x_abs_fn__mutmut_30, 
    'x_abs_fn__mutmut_31': x_abs_fn__mutmut_31, 
    'x_abs_fn__mutmut_32': x_abs_fn__mutmut_32, 
    'x_abs_fn__mutmut_33': x_abs_fn__mutmut_33, 
    'x_abs_fn__mutmut_34': x_abs_fn__mutmut_34, 
    'x_abs_fn__mutmut_35': x_abs_fn__mutmut_35, 
    'x_abs_fn__mutmut_36': x_abs_fn__mutmut_36, 
    'x_abs_fn__mutmut_37': x_abs_fn__mutmut_37, 
    'x_abs_fn__mutmut_38': x_abs_fn__mutmut_38, 
    'x_abs_fn__mutmut_39': x_abs_fn__mutmut_39, 
    'x_abs_fn__mutmut_40': x_abs_fn__mutmut_40, 
    'x_abs_fn__mutmut_41': x_abs_fn__mutmut_41, 
    'x_abs_fn__mutmut_42': x_abs_fn__mutmut_42, 
    'x_abs_fn__mutmut_43': x_abs_fn__mutmut_43, 
    'x_abs_fn__mutmut_44': x_abs_fn__mutmut_44, 
    'x_abs_fn__mutmut_45': x_abs_fn__mutmut_45, 
    'x_abs_fn__mutmut_46': x_abs_fn__mutmut_46, 
    'x_abs_fn__mutmut_47': x_abs_fn__mutmut_47, 
    'x_abs_fn__mutmut_48': x_abs_fn__mutmut_48, 
    'x_abs_fn__mutmut_49': x_abs_fn__mutmut_49, 
    'x_abs_fn__mutmut_50': x_abs_fn__mutmut_50, 
    'x_abs_fn__mutmut_51': x_abs_fn__mutmut_51, 
    'x_abs_fn__mutmut_52': x_abs_fn__mutmut_52, 
    'x_abs_fn__mutmut_53': x_abs_fn__mutmut_53, 
    'x_abs_fn__mutmut_54': x_abs_fn__mutmut_54, 
    'x_abs_fn__mutmut_55': x_abs_fn__mutmut_55, 
    'x_abs_fn__mutmut_56': x_abs_fn__mutmut_56, 
    'x_abs_fn__mutmut_57': x_abs_fn__mutmut_57, 
    'x_abs_fn__mutmut_58': x_abs_fn__mutmut_58, 
    'x_abs_fn__mutmut_59': x_abs_fn__mutmut_59, 
    'x_abs_fn__mutmut_60': x_abs_fn__mutmut_60, 
    'x_abs_fn__mutmut_61': x_abs_fn__mutmut_61, 
    'x_abs_fn__mutmut_62': x_abs_fn__mutmut_62, 
    'x_abs_fn__mutmut_63': x_abs_fn__mutmut_63, 
    'x_abs_fn__mutmut_64': x_abs_fn__mutmut_64, 
    'x_abs_fn__mutmut_65': x_abs_fn__mutmut_65, 
    'x_abs_fn__mutmut_66': x_abs_fn__mutmut_66, 
    'x_abs_fn__mutmut_67': x_abs_fn__mutmut_67, 
    'x_abs_fn__mutmut_68': x_abs_fn__mutmut_68
}

def abs_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_abs_fn__mutmut_orig, x_abs_fn__mutmut_mutants, args, kwargs)
    return result 

abs_fn.__signature__ = _mutmut_signature(x_abs_fn__mutmut_orig)
x_abs_fn__mutmut_orig.__name__ = 'x_abs_fn'


def x_ceil_fn__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = None
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(None, input_val.value)
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, None)
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(input_val.value)
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, )
    return CtyNumber().validate(Decimal(math.ceil(val)))


def x_ceil_fn__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(None)


def x_ceil_fn__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(None))


def x_ceil_fn__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"ceil: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.ceil(None)))

x_ceil_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_ceil_fn__mutmut_1': x_ceil_fn__mutmut_1, 
    'x_ceil_fn__mutmut_2': x_ceil_fn__mutmut_2, 
    'x_ceil_fn__mutmut_3': x_ceil_fn__mutmut_3, 
    'x_ceil_fn__mutmut_4': x_ceil_fn__mutmut_4, 
    'x_ceil_fn__mutmut_5': x_ceil_fn__mutmut_5, 
    'x_ceil_fn__mutmut_6': x_ceil_fn__mutmut_6, 
    'x_ceil_fn__mutmut_7': x_ceil_fn__mutmut_7, 
    'x_ceil_fn__mutmut_8': x_ceil_fn__mutmut_8, 
    'x_ceil_fn__mutmut_9': x_ceil_fn__mutmut_9, 
    'x_ceil_fn__mutmut_10': x_ceil_fn__mutmut_10, 
    'x_ceil_fn__mutmut_11': x_ceil_fn__mutmut_11
}

def ceil_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_ceil_fn__mutmut_orig, x_ceil_fn__mutmut_mutants, args, kwargs)
    return result 

ceil_fn.__signature__ = _mutmut_signature(x_ceil_fn__mutmut_orig)
x_ceil_fn__mutmut_orig.__name__ = 'x_ceil_fn'


def x_floor_fn__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = None
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(None, input_val.value)
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, None)
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(input_val.value)
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, )
    return CtyNumber().validate(Decimal(math.floor(val)))


def x_floor_fn__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(None)


def x_floor_fn__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(None))


def x_floor_fn__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"floor: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    return CtyNumber().validate(Decimal(math.floor(None)))

x_floor_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_floor_fn__mutmut_1': x_floor_fn__mutmut_1, 
    'x_floor_fn__mutmut_2': x_floor_fn__mutmut_2, 
    'x_floor_fn__mutmut_3': x_floor_fn__mutmut_3, 
    'x_floor_fn__mutmut_4': x_floor_fn__mutmut_4, 
    'x_floor_fn__mutmut_5': x_floor_fn__mutmut_5, 
    'x_floor_fn__mutmut_6': x_floor_fn__mutmut_6, 
    'x_floor_fn__mutmut_7': x_floor_fn__mutmut_7, 
    'x_floor_fn__mutmut_8': x_floor_fn__mutmut_8, 
    'x_floor_fn__mutmut_9': x_floor_fn__mutmut_9, 
    'x_floor_fn__mutmut_10': x_floor_fn__mutmut_10, 
    'x_floor_fn__mutmut_11': x_floor_fn__mutmut_11
}

def floor_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_floor_fn__mutmut_orig, x_floor_fn__mutmut_mutants, args, kwargs)
    return result 

floor_fn.__signature__ = _mutmut_signature(x_floor_fn__mutmut_orig)
x_floor_fn__mutmut_orig.__name__ = 'x_floor_fn'


def x_log_fn__mutmut_orig(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_1(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) and not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_2(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_3(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_4(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError(None)
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_5(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("XXlog: arguments must be numbersXX")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_6(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("LOG: ARGUMENTS MUST BE NUMBERS")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_7(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null and base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_8(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown and base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_9(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null and num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_10(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(None)
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_11(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = None
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_12(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(None, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_13(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, None)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_14(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_15(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, )
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_16(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = None
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_17(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(None, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_18(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, None)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_19(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_20(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, )
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_21(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num < 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_22(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 1:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_23(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(None)
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_24(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base < 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_25(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 1:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_26(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(None)
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_27(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base != 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_28(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 2:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_29(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError(None)
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_30(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("XXlog: base cannot be 1XX")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_31(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("LOG: BASE CANNOT BE 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_32(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = None
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_33(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(None)
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_34(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(None))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_35(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(None, float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_36(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), None)))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_37(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_38(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), )))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_39(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(None), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_40(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(None))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_41(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(None)
    except ValueError as e:
        raise CtyFunctionError(f"log: math domain error: {e}") from e


def x_log_fn__mutmut_42(num_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("log: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or base_val.is_null or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    num = cast(Decimal, num_val.value)
    base = cast(Decimal, base_val.value)
    if num <= 0:
        raise CtyFunctionError(f"log: number must be positive, got {num}")
    if base <= 0:
        raise CtyFunctionError(f"log: base must be positive, got {base}")
    if base == 1:
        raise CtyFunctionError("log: base cannot be 1")
    try:
        result = Decimal(str(math.log(float(num), float(base))))
        return CtyNumber().validate(result)
    except ValueError as e:
        raise CtyFunctionError(None) from e

x_log_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_log_fn__mutmut_1': x_log_fn__mutmut_1, 
    'x_log_fn__mutmut_2': x_log_fn__mutmut_2, 
    'x_log_fn__mutmut_3': x_log_fn__mutmut_3, 
    'x_log_fn__mutmut_4': x_log_fn__mutmut_4, 
    'x_log_fn__mutmut_5': x_log_fn__mutmut_5, 
    'x_log_fn__mutmut_6': x_log_fn__mutmut_6, 
    'x_log_fn__mutmut_7': x_log_fn__mutmut_7, 
    'x_log_fn__mutmut_8': x_log_fn__mutmut_8, 
    'x_log_fn__mutmut_9': x_log_fn__mutmut_9, 
    'x_log_fn__mutmut_10': x_log_fn__mutmut_10, 
    'x_log_fn__mutmut_11': x_log_fn__mutmut_11, 
    'x_log_fn__mutmut_12': x_log_fn__mutmut_12, 
    'x_log_fn__mutmut_13': x_log_fn__mutmut_13, 
    'x_log_fn__mutmut_14': x_log_fn__mutmut_14, 
    'x_log_fn__mutmut_15': x_log_fn__mutmut_15, 
    'x_log_fn__mutmut_16': x_log_fn__mutmut_16, 
    'x_log_fn__mutmut_17': x_log_fn__mutmut_17, 
    'x_log_fn__mutmut_18': x_log_fn__mutmut_18, 
    'x_log_fn__mutmut_19': x_log_fn__mutmut_19, 
    'x_log_fn__mutmut_20': x_log_fn__mutmut_20, 
    'x_log_fn__mutmut_21': x_log_fn__mutmut_21, 
    'x_log_fn__mutmut_22': x_log_fn__mutmut_22, 
    'x_log_fn__mutmut_23': x_log_fn__mutmut_23, 
    'x_log_fn__mutmut_24': x_log_fn__mutmut_24, 
    'x_log_fn__mutmut_25': x_log_fn__mutmut_25, 
    'x_log_fn__mutmut_26': x_log_fn__mutmut_26, 
    'x_log_fn__mutmut_27': x_log_fn__mutmut_27, 
    'x_log_fn__mutmut_28': x_log_fn__mutmut_28, 
    'x_log_fn__mutmut_29': x_log_fn__mutmut_29, 
    'x_log_fn__mutmut_30': x_log_fn__mutmut_30, 
    'x_log_fn__mutmut_31': x_log_fn__mutmut_31, 
    'x_log_fn__mutmut_32': x_log_fn__mutmut_32, 
    'x_log_fn__mutmut_33': x_log_fn__mutmut_33, 
    'x_log_fn__mutmut_34': x_log_fn__mutmut_34, 
    'x_log_fn__mutmut_35': x_log_fn__mutmut_35, 
    'x_log_fn__mutmut_36': x_log_fn__mutmut_36, 
    'x_log_fn__mutmut_37': x_log_fn__mutmut_37, 
    'x_log_fn__mutmut_38': x_log_fn__mutmut_38, 
    'x_log_fn__mutmut_39': x_log_fn__mutmut_39, 
    'x_log_fn__mutmut_40': x_log_fn__mutmut_40, 
    'x_log_fn__mutmut_41': x_log_fn__mutmut_41, 
    'x_log_fn__mutmut_42': x_log_fn__mutmut_42
}

def log_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_log_fn__mutmut_orig, x_log_fn__mutmut_mutants, args, kwargs)
    return result 

log_fn.__signature__ = _mutmut_signature(x_log_fn__mutmut_orig)
x_log_fn__mutmut_orig.__name__ = 'x_log_fn'


def x_pow_fn__mutmut_orig(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_1(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) and not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_2(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_3(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_4(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError(None)
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_5(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("XXpow: arguments must be numbersXX")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_6(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("POW: ARGUMENTS MUST BE NUMBERS")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_7(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null and power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_8(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown and power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_9(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null and num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_10(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(None)
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_11(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = None
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_12(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(None, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_13(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, None)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_14(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_15(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, )
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_16(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = None
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_17(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(None, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_18(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, None)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_19(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_20(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, )
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_21(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = None
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_22(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num * power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_23(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(None)
    except InvalidOperation as e:
        raise CtyFunctionError(f"pow: invalid operation: {e}") from e


def x_pow_fn__mutmut_24(num_val: CtyValue[Any], power_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(num_val.type, CtyNumber) or not isinstance(power_val.type, CtyNumber):
        raise CtyFunctionError("pow: arguments must be numbers")
    if num_val.is_null or num_val.is_unknown or power_val.is_null or power_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    try:
        num = cast(Decimal, num_val.value)
        power = cast(Decimal, power_val.value)
        result = num**power
        return CtyNumber().validate(result)
    except InvalidOperation as e:
        raise CtyFunctionError(None) from e

x_pow_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_pow_fn__mutmut_1': x_pow_fn__mutmut_1, 
    'x_pow_fn__mutmut_2': x_pow_fn__mutmut_2, 
    'x_pow_fn__mutmut_3': x_pow_fn__mutmut_3, 
    'x_pow_fn__mutmut_4': x_pow_fn__mutmut_4, 
    'x_pow_fn__mutmut_5': x_pow_fn__mutmut_5, 
    'x_pow_fn__mutmut_6': x_pow_fn__mutmut_6, 
    'x_pow_fn__mutmut_7': x_pow_fn__mutmut_7, 
    'x_pow_fn__mutmut_8': x_pow_fn__mutmut_8, 
    'x_pow_fn__mutmut_9': x_pow_fn__mutmut_9, 
    'x_pow_fn__mutmut_10': x_pow_fn__mutmut_10, 
    'x_pow_fn__mutmut_11': x_pow_fn__mutmut_11, 
    'x_pow_fn__mutmut_12': x_pow_fn__mutmut_12, 
    'x_pow_fn__mutmut_13': x_pow_fn__mutmut_13, 
    'x_pow_fn__mutmut_14': x_pow_fn__mutmut_14, 
    'x_pow_fn__mutmut_15': x_pow_fn__mutmut_15, 
    'x_pow_fn__mutmut_16': x_pow_fn__mutmut_16, 
    'x_pow_fn__mutmut_17': x_pow_fn__mutmut_17, 
    'x_pow_fn__mutmut_18': x_pow_fn__mutmut_18, 
    'x_pow_fn__mutmut_19': x_pow_fn__mutmut_19, 
    'x_pow_fn__mutmut_20': x_pow_fn__mutmut_20, 
    'x_pow_fn__mutmut_21': x_pow_fn__mutmut_21, 
    'x_pow_fn__mutmut_22': x_pow_fn__mutmut_22, 
    'x_pow_fn__mutmut_23': x_pow_fn__mutmut_23, 
    'x_pow_fn__mutmut_24': x_pow_fn__mutmut_24
}

def pow_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_pow_fn__mutmut_orig, x_pow_fn__mutmut_mutants, args, kwargs)
    return result 

pow_fn.__signature__ = _mutmut_signature(x_pow_fn__mutmut_orig)
x_pow_fn__mutmut_orig.__name__ = 'x_pow_fn'


def x_signum_fn__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = None
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(None, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, None)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, )
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val <= 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 1:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(None)
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal(None))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("XX-1XX"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val >= 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 1:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(None)
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal(None))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_18(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("XX1XX"))
    return CtyNumber().validate(Decimal("0"))


def x_signum_fn__mutmut_19(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(None)


def x_signum_fn__mutmut_20(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal(None))


def x_signum_fn__mutmut_21(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyNumber):
        raise CtyFunctionError(f"signum: input must be a number, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    val = cast(Decimal, input_val.value)
    if val < 0:
        return CtyNumber().validate(Decimal("-1"))
    if val > 0:
        return CtyNumber().validate(Decimal("1"))
    return CtyNumber().validate(Decimal("XX0XX"))

x_signum_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_signum_fn__mutmut_1': x_signum_fn__mutmut_1, 
    'x_signum_fn__mutmut_2': x_signum_fn__mutmut_2, 
    'x_signum_fn__mutmut_3': x_signum_fn__mutmut_3, 
    'x_signum_fn__mutmut_4': x_signum_fn__mutmut_4, 
    'x_signum_fn__mutmut_5': x_signum_fn__mutmut_5, 
    'x_signum_fn__mutmut_6': x_signum_fn__mutmut_6, 
    'x_signum_fn__mutmut_7': x_signum_fn__mutmut_7, 
    'x_signum_fn__mutmut_8': x_signum_fn__mutmut_8, 
    'x_signum_fn__mutmut_9': x_signum_fn__mutmut_9, 
    'x_signum_fn__mutmut_10': x_signum_fn__mutmut_10, 
    'x_signum_fn__mutmut_11': x_signum_fn__mutmut_11, 
    'x_signum_fn__mutmut_12': x_signum_fn__mutmut_12, 
    'x_signum_fn__mutmut_13': x_signum_fn__mutmut_13, 
    'x_signum_fn__mutmut_14': x_signum_fn__mutmut_14, 
    'x_signum_fn__mutmut_15': x_signum_fn__mutmut_15, 
    'x_signum_fn__mutmut_16': x_signum_fn__mutmut_16, 
    'x_signum_fn__mutmut_17': x_signum_fn__mutmut_17, 
    'x_signum_fn__mutmut_18': x_signum_fn__mutmut_18, 
    'x_signum_fn__mutmut_19': x_signum_fn__mutmut_19, 
    'x_signum_fn__mutmut_20': x_signum_fn__mutmut_20, 
    'x_signum_fn__mutmut_21': x_signum_fn__mutmut_21
}

def signum_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_signum_fn__mutmut_orig, x_signum_fn__mutmut_mutants, args, kwargs)
    return result 

signum_fn.__signature__ = _mutmut_signature(x_signum_fn__mutmut_orig)
x_signum_fn__mutmut_orig.__name__ = 'x_signum_fn'


def x_parseint_fn__mutmut_orig(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_1(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) and not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_2(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_3(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_4(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError(None)
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_5(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("XXparseint: arguments must be string and numberXX")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_6(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("PARSEINT: ARGUMENTS MUST BE STRING AND NUMBER")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_7(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null and base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_8(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(None)
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_9(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown and base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_10(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(None)
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_11(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = None
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_12(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(None, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_13(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, None)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_14(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_15(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, )
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_16(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = None
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_17(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(None)
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_18(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(None, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_19(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, None))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_20(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_21(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, ))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_22(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_23(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 and 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_24(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base != 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_25(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 1 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_26(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 3 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_27(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 < base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_28(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base < 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_29(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 37):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_30(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(None)
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_31(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = None
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_32(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(None, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_33(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, None)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_34(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_35(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, )
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_36(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(None)
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_37(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(None))
    except (ValueError, TypeError):
        return CtyValue.null(CtyNumber())


def x_parseint_fn__mutmut_38(str_val: CtyValue[Any], base_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(str_val.type, CtyString) or not isinstance(base_val.type, CtyNumber):
        raise CtyFunctionError("parseint: arguments must be string and number")
    if str_val.is_null or base_val.is_null:
        return CtyValue.null(CtyNumber())
    if str_val.is_unknown or base_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    s = cast(str, str_val.value)
    base = int(cast(Decimal, base_val.value))
    if not (base == 0 or 2 <= base <= 36):
        raise CtyFunctionError(f"parseint: base must be 0 or between 2 and 36, got {base}")
    try:
        parsed_int = int(s, base)
        return CtyNumber().validate(Decimal(parsed_int))
    except (ValueError, TypeError):
        return CtyValue.null(None)

x_parseint_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_parseint_fn__mutmut_1': x_parseint_fn__mutmut_1, 
    'x_parseint_fn__mutmut_2': x_parseint_fn__mutmut_2, 
    'x_parseint_fn__mutmut_3': x_parseint_fn__mutmut_3, 
    'x_parseint_fn__mutmut_4': x_parseint_fn__mutmut_4, 
    'x_parseint_fn__mutmut_5': x_parseint_fn__mutmut_5, 
    'x_parseint_fn__mutmut_6': x_parseint_fn__mutmut_6, 
    'x_parseint_fn__mutmut_7': x_parseint_fn__mutmut_7, 
    'x_parseint_fn__mutmut_8': x_parseint_fn__mutmut_8, 
    'x_parseint_fn__mutmut_9': x_parseint_fn__mutmut_9, 
    'x_parseint_fn__mutmut_10': x_parseint_fn__mutmut_10, 
    'x_parseint_fn__mutmut_11': x_parseint_fn__mutmut_11, 
    'x_parseint_fn__mutmut_12': x_parseint_fn__mutmut_12, 
    'x_parseint_fn__mutmut_13': x_parseint_fn__mutmut_13, 
    'x_parseint_fn__mutmut_14': x_parseint_fn__mutmut_14, 
    'x_parseint_fn__mutmut_15': x_parseint_fn__mutmut_15, 
    'x_parseint_fn__mutmut_16': x_parseint_fn__mutmut_16, 
    'x_parseint_fn__mutmut_17': x_parseint_fn__mutmut_17, 
    'x_parseint_fn__mutmut_18': x_parseint_fn__mutmut_18, 
    'x_parseint_fn__mutmut_19': x_parseint_fn__mutmut_19, 
    'x_parseint_fn__mutmut_20': x_parseint_fn__mutmut_20, 
    'x_parseint_fn__mutmut_21': x_parseint_fn__mutmut_21, 
    'x_parseint_fn__mutmut_22': x_parseint_fn__mutmut_22, 
    'x_parseint_fn__mutmut_23': x_parseint_fn__mutmut_23, 
    'x_parseint_fn__mutmut_24': x_parseint_fn__mutmut_24, 
    'x_parseint_fn__mutmut_25': x_parseint_fn__mutmut_25, 
    'x_parseint_fn__mutmut_26': x_parseint_fn__mutmut_26, 
    'x_parseint_fn__mutmut_27': x_parseint_fn__mutmut_27, 
    'x_parseint_fn__mutmut_28': x_parseint_fn__mutmut_28, 
    'x_parseint_fn__mutmut_29': x_parseint_fn__mutmut_29, 
    'x_parseint_fn__mutmut_30': x_parseint_fn__mutmut_30, 
    'x_parseint_fn__mutmut_31': x_parseint_fn__mutmut_31, 
    'x_parseint_fn__mutmut_32': x_parseint_fn__mutmut_32, 
    'x_parseint_fn__mutmut_33': x_parseint_fn__mutmut_33, 
    'x_parseint_fn__mutmut_34': x_parseint_fn__mutmut_34, 
    'x_parseint_fn__mutmut_35': x_parseint_fn__mutmut_35, 
    'x_parseint_fn__mutmut_36': x_parseint_fn__mutmut_36, 
    'x_parseint_fn__mutmut_37': x_parseint_fn__mutmut_37, 
    'x_parseint_fn__mutmut_38': x_parseint_fn__mutmut_38
}

def parseint_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_parseint_fn__mutmut_orig, x_parseint_fn__mutmut_mutants, args, kwargs)
    return result 

parseint_fn.__signature__ = _mutmut_signature(x_parseint_fn__mutmut_orig)
x_parseint_fn__mutmut_orig.__name__ = 'x_parseint_fn'


def x_int_fn__mutmut_orig(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(Decimal, val.value)
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_1(val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(Decimal, val.value)
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_2(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(None)
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(Decimal, val.value)
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_3(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null and val.is_unknown:
        return val
    val_decimal = cast(Decimal, val.value)
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_4(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = None
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_5(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(None, val.value)
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_6(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(Decimal, None)
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_7(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(val.value)
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_8(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(Decimal, )
    return CtyNumber().validate(Decimal(int(val_decimal)))


def x_int_fn__mutmut_9(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(Decimal, val.value)
    return CtyNumber().validate(None)


def x_int_fn__mutmut_10(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(Decimal, val.value)
    return CtyNumber().validate(Decimal(None))


def x_int_fn__mutmut_11(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyNumber):
        raise CtyFunctionError(f"int: argument must be a number, got {val.type.ctype}")
    if val.is_null or val.is_unknown:
        return val
    val_decimal = cast(Decimal, val.value)
    return CtyNumber().validate(Decimal(int(None)))

x_int_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_int_fn__mutmut_1': x_int_fn__mutmut_1, 
    'x_int_fn__mutmut_2': x_int_fn__mutmut_2, 
    'x_int_fn__mutmut_3': x_int_fn__mutmut_3, 
    'x_int_fn__mutmut_4': x_int_fn__mutmut_4, 
    'x_int_fn__mutmut_5': x_int_fn__mutmut_5, 
    'x_int_fn__mutmut_6': x_int_fn__mutmut_6, 
    'x_int_fn__mutmut_7': x_int_fn__mutmut_7, 
    'x_int_fn__mutmut_8': x_int_fn__mutmut_8, 
    'x_int_fn__mutmut_9': x_int_fn__mutmut_9, 
    'x_int_fn__mutmut_10': x_int_fn__mutmut_10, 
    'x_int_fn__mutmut_11': x_int_fn__mutmut_11
}

def int_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_int_fn__mutmut_orig, x_int_fn__mutmut_mutants, args, kwargs)
    return result 

int_fn.__signature__ = _mutmut_signature(x_int_fn__mutmut_orig)
x_int_fn__mutmut_orig.__name__ = 'x_int_fn'


# 🌊🪢🔣🪄
