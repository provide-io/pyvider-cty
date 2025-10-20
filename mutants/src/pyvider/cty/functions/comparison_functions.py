# pyvider/cty/functions/comparison_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from pyvider.cty import CtyBool, CtyNumber, CtyString, CtyValue
from pyvider.cty.config.defaults import (
    COMPARISON_OPS_MAP,
    ERR_ALL_ARGS_SAME_TYPE,
    ERR_CANNOT_COMPARE,
    ERR_MIN_ONE_ARG,
)
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


def x_equal__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(a == b)


def x_equal__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown and b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(a == b)


def x_equal__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(None)
    return CtyBool().validate(a == b)


def x_equal__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(None)


def x_equal__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(a != b)

x_equal__mutmut_mutants : ClassVar[MutantDict] = {
'x_equal__mutmut_1': x_equal__mutmut_1, 
    'x_equal__mutmut_2': x_equal__mutmut_2, 
    'x_equal__mutmut_3': x_equal__mutmut_3, 
    'x_equal__mutmut_4': x_equal__mutmut_4
}

def equal(*args, **kwargs):
    result = _mutmut_trampoline(x_equal__mutmut_orig, x_equal__mutmut_mutants, args, kwargs)
    return result 

equal.__signature__ = _mutmut_signature(x_equal__mutmut_orig)
x_equal__mutmut_orig.__name__ = 'x_equal'


def x_not_equal__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(a != b)


def x_not_equal__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown and b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(a != b)


def x_not_equal__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(None)
    return CtyBool().validate(a != b)


def x_not_equal__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(None)


def x_not_equal__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    if a.is_unknown or b.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(a == b)

x_not_equal__mutmut_mutants : ClassVar[MutantDict] = {
'x_not_equal__mutmut_1': x_not_equal__mutmut_1, 
    'x_not_equal__mutmut_2': x_not_equal__mutmut_2, 
    'x_not_equal__mutmut_3': x_not_equal__mutmut_3, 
    'x_not_equal__mutmut_4': x_not_equal__mutmut_4
}

def not_equal(*args, **kwargs):
    result = _mutmut_trampoline(x_not_equal__mutmut_orig, x_not_equal__mutmut_mutants, args, kwargs)
    return result 

not_equal.__signature__ = _mutmut_signature(x_not_equal__mutmut_orig)
x_not_equal__mutmut_orig.__name__ = 'x_not_equal'


def x__compare__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_1(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null and b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_2(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(None)

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_3(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown and b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_4(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_5(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_6(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown or ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_7(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown or not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_8(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_9(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = None
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_10(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(None, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_11(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, None)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_12(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_13(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, )
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_14(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = None
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_15(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper and (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_16(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val >= upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_17(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper or not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_18(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val != upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_19(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_20(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op not in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_21(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in ("XX>XX", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_22(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", "XX>=XX"):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_23(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(None)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_24(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_25(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op not in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_26(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("XX<XX", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_27(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "XX<=XX"):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_28(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(None)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_29(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_30(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = None
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_31(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower and (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_32(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val <= lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_33(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower or not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_34(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val != lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_35(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_36(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op not in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_37(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("XX<XX", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_38(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "XX<=XX"):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_39(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(None)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_40(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_41(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op not in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_42(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in ("XX>XX", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_43(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", "XX>=XX"):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_44(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(None)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_45(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_46(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown or ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_47(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown or not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_48(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_49(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = None
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_50(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(None, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_51(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, None)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_52(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_53(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, )
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_54(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = None
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_55(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper and (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_56(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val >= upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_57(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper or not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_58(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val != upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_59(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_60(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op not in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_61(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("XX<XX", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_62(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "XX<=XX"):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_63(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(None)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_64(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_65(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op not in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_66(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in ("XX>XX", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_67(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", "XX>=XX"):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_68(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(None)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_69(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_70(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = None
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_71(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower and (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_72(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val <= lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_73(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower or not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_74(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val != lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_75(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_76(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op not in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_77(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in ("XX>XX", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_78(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", "XX>=XX"):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_79(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(None)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_80(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_81(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op not in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_82(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("XX<XX", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_83(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "XX<=XX"):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_84(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(None)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_85(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_86(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a or ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_87(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown or ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_88(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown or b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_89(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound or ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_90(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = None
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_91(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = None
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_92(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower and (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_93(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper <= b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_94(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower or not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_95(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper != b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_96(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_97(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc or b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_98(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op not in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_99(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("XX<XX", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_100(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "XX<=XX"):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_101(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(None)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_102(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_103(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op not in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_104(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in ("XX>XX", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_105(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", "XX>=XX"):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_106(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(None)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_107(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_108(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound or ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_109(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = None
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_110(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = None
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_111(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper and (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_112(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower >= b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_113(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper or not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_114(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower != b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_115(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_116(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc or b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_117(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op not in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_118(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in ("XX>XX", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_119(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", "XX>=XX"):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_120(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(None)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_121(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_122(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op not in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_123(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("XX<XX", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_124(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "XX<=XX"):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_125(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(None)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_126(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_127(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(None)

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_128(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) and not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_129(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_130(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_131(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(None):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_132(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = None
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_133(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=None, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_134(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=None)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_135(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_136(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, )
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_137(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(None)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_138(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = None
    return CtyBool().validate(ops[op](a.value, b.value))


def x__compare__mutmut_139(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(None)


def x__compare__mutmut_140(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](None, b.value))


def x__compare__mutmut_141(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, None))


def x__compare__mutmut_142(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](b.value))


def x__compare__mutmut_143(a: CtyValue[Any], b: CtyValue[Any], op: str) -> CtyValue[Any]:  # noqa: C901
    if a.is_null or b.is_null:
        return CtyValue.unknown(CtyBool())

    # Handle refined unknown comparisons
    if a.is_unknown or b.is_unknown:
        ref_a = a.value if isinstance(a.value, RefinedUnknownValue) else None
        ref_b = b.value if isinstance(b.value, RefinedUnknownValue) else None

        # Case 1: One is known, one is refined unknown
        if a.is_unknown and not b.is_unknown and ref_a:
            b_val = cast(Decimal, b.value)
            if ref_a.number_upper_bound:
                upper, inclusive = ref_a.number_upper_bound
                if b_val > upper or (b_val == upper and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
            if ref_a.number_lower_bound:
                lower, inclusive = ref_a.number_lower_bound
                if b_val < lower or (b_val == lower and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
        elif b.is_unknown and not a.is_unknown and ref_b:
            a_val = cast(Decimal, a.value)
            if ref_b.number_upper_bound:
                upper, inclusive = ref_b.number_upper_bound
                if a_val > upper or (a_val == upper and not inclusive):
                    if op in ("<", "<="):
                        return CtyBool().validate(False)
                    if op in (">", ">="):
                        return CtyBool().validate(True)
            if ref_b.number_lower_bound:
                lower, inclusive = ref_b.number_lower_bound
                if a_val < lower or (a_val == lower and not inclusive):
                    if op in (">", ">="):
                        return CtyBool().validate(False)
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
        # Case 2: Both are refined unknowns
        elif a.is_unknown and b.is_unknown and ref_a and ref_b:
            if ref_a.number_upper_bound and ref_b.number_lower_bound:
                a_upper, a_inc = ref_a.number_upper_bound
                b_lower, b_inc = ref_b.number_lower_bound
                if a_upper < b_lower or (a_upper == b_lower and not (a_inc and b_inc)):
                    if op in ("<", "<="):
                        return CtyBool().validate(True)
                    if op in (">", ">="):
                        return CtyBool().validate(False)
            if ref_a.number_lower_bound and ref_b.number_upper_bound:
                a_lower, a_inc = ref_a.number_lower_bound
                b_upper, b_inc = ref_b.number_upper_bound
                if a_lower > b_upper or (a_lower == b_upper and not (a_inc and b_inc)):
                    if op in (">", ">="):
                        return CtyBool().validate(True)
                    if op in ("<", "<="):
                        return CtyBool().validate(False)

        return CtyValue.unknown(CtyBool())

    # Handle known value comparisons
    if not isinstance(a.type, CtyNumber | CtyString) or not a.type.equal(b.type):
        error_message = ERR_CANNOT_COMPARE.format(type1=a.type.ctype, type2=b.type.ctype)
        raise CtyFunctionError(error_message)

    ops = COMPARISON_OPS_MAP
    return CtyBool().validate(ops[op](a.value, ))

x__compare__mutmut_mutants : ClassVar[MutantDict] = {
'x__compare__mutmut_1': x__compare__mutmut_1, 
    'x__compare__mutmut_2': x__compare__mutmut_2, 
    'x__compare__mutmut_3': x__compare__mutmut_3, 
    'x__compare__mutmut_4': x__compare__mutmut_4, 
    'x__compare__mutmut_5': x__compare__mutmut_5, 
    'x__compare__mutmut_6': x__compare__mutmut_6, 
    'x__compare__mutmut_7': x__compare__mutmut_7, 
    'x__compare__mutmut_8': x__compare__mutmut_8, 
    'x__compare__mutmut_9': x__compare__mutmut_9, 
    'x__compare__mutmut_10': x__compare__mutmut_10, 
    'x__compare__mutmut_11': x__compare__mutmut_11, 
    'x__compare__mutmut_12': x__compare__mutmut_12, 
    'x__compare__mutmut_13': x__compare__mutmut_13, 
    'x__compare__mutmut_14': x__compare__mutmut_14, 
    'x__compare__mutmut_15': x__compare__mutmut_15, 
    'x__compare__mutmut_16': x__compare__mutmut_16, 
    'x__compare__mutmut_17': x__compare__mutmut_17, 
    'x__compare__mutmut_18': x__compare__mutmut_18, 
    'x__compare__mutmut_19': x__compare__mutmut_19, 
    'x__compare__mutmut_20': x__compare__mutmut_20, 
    'x__compare__mutmut_21': x__compare__mutmut_21, 
    'x__compare__mutmut_22': x__compare__mutmut_22, 
    'x__compare__mutmut_23': x__compare__mutmut_23, 
    'x__compare__mutmut_24': x__compare__mutmut_24, 
    'x__compare__mutmut_25': x__compare__mutmut_25, 
    'x__compare__mutmut_26': x__compare__mutmut_26, 
    'x__compare__mutmut_27': x__compare__mutmut_27, 
    'x__compare__mutmut_28': x__compare__mutmut_28, 
    'x__compare__mutmut_29': x__compare__mutmut_29, 
    'x__compare__mutmut_30': x__compare__mutmut_30, 
    'x__compare__mutmut_31': x__compare__mutmut_31, 
    'x__compare__mutmut_32': x__compare__mutmut_32, 
    'x__compare__mutmut_33': x__compare__mutmut_33, 
    'x__compare__mutmut_34': x__compare__mutmut_34, 
    'x__compare__mutmut_35': x__compare__mutmut_35, 
    'x__compare__mutmut_36': x__compare__mutmut_36, 
    'x__compare__mutmut_37': x__compare__mutmut_37, 
    'x__compare__mutmut_38': x__compare__mutmut_38, 
    'x__compare__mutmut_39': x__compare__mutmut_39, 
    'x__compare__mutmut_40': x__compare__mutmut_40, 
    'x__compare__mutmut_41': x__compare__mutmut_41, 
    'x__compare__mutmut_42': x__compare__mutmut_42, 
    'x__compare__mutmut_43': x__compare__mutmut_43, 
    'x__compare__mutmut_44': x__compare__mutmut_44, 
    'x__compare__mutmut_45': x__compare__mutmut_45, 
    'x__compare__mutmut_46': x__compare__mutmut_46, 
    'x__compare__mutmut_47': x__compare__mutmut_47, 
    'x__compare__mutmut_48': x__compare__mutmut_48, 
    'x__compare__mutmut_49': x__compare__mutmut_49, 
    'x__compare__mutmut_50': x__compare__mutmut_50, 
    'x__compare__mutmut_51': x__compare__mutmut_51, 
    'x__compare__mutmut_52': x__compare__mutmut_52, 
    'x__compare__mutmut_53': x__compare__mutmut_53, 
    'x__compare__mutmut_54': x__compare__mutmut_54, 
    'x__compare__mutmut_55': x__compare__mutmut_55, 
    'x__compare__mutmut_56': x__compare__mutmut_56, 
    'x__compare__mutmut_57': x__compare__mutmut_57, 
    'x__compare__mutmut_58': x__compare__mutmut_58, 
    'x__compare__mutmut_59': x__compare__mutmut_59, 
    'x__compare__mutmut_60': x__compare__mutmut_60, 
    'x__compare__mutmut_61': x__compare__mutmut_61, 
    'x__compare__mutmut_62': x__compare__mutmut_62, 
    'x__compare__mutmut_63': x__compare__mutmut_63, 
    'x__compare__mutmut_64': x__compare__mutmut_64, 
    'x__compare__mutmut_65': x__compare__mutmut_65, 
    'x__compare__mutmut_66': x__compare__mutmut_66, 
    'x__compare__mutmut_67': x__compare__mutmut_67, 
    'x__compare__mutmut_68': x__compare__mutmut_68, 
    'x__compare__mutmut_69': x__compare__mutmut_69, 
    'x__compare__mutmut_70': x__compare__mutmut_70, 
    'x__compare__mutmut_71': x__compare__mutmut_71, 
    'x__compare__mutmut_72': x__compare__mutmut_72, 
    'x__compare__mutmut_73': x__compare__mutmut_73, 
    'x__compare__mutmut_74': x__compare__mutmut_74, 
    'x__compare__mutmut_75': x__compare__mutmut_75, 
    'x__compare__mutmut_76': x__compare__mutmut_76, 
    'x__compare__mutmut_77': x__compare__mutmut_77, 
    'x__compare__mutmut_78': x__compare__mutmut_78, 
    'x__compare__mutmut_79': x__compare__mutmut_79, 
    'x__compare__mutmut_80': x__compare__mutmut_80, 
    'x__compare__mutmut_81': x__compare__mutmut_81, 
    'x__compare__mutmut_82': x__compare__mutmut_82, 
    'x__compare__mutmut_83': x__compare__mutmut_83, 
    'x__compare__mutmut_84': x__compare__mutmut_84, 
    'x__compare__mutmut_85': x__compare__mutmut_85, 
    'x__compare__mutmut_86': x__compare__mutmut_86, 
    'x__compare__mutmut_87': x__compare__mutmut_87, 
    'x__compare__mutmut_88': x__compare__mutmut_88, 
    'x__compare__mutmut_89': x__compare__mutmut_89, 
    'x__compare__mutmut_90': x__compare__mutmut_90, 
    'x__compare__mutmut_91': x__compare__mutmut_91, 
    'x__compare__mutmut_92': x__compare__mutmut_92, 
    'x__compare__mutmut_93': x__compare__mutmut_93, 
    'x__compare__mutmut_94': x__compare__mutmut_94, 
    'x__compare__mutmut_95': x__compare__mutmut_95, 
    'x__compare__mutmut_96': x__compare__mutmut_96, 
    'x__compare__mutmut_97': x__compare__mutmut_97, 
    'x__compare__mutmut_98': x__compare__mutmut_98, 
    'x__compare__mutmut_99': x__compare__mutmut_99, 
    'x__compare__mutmut_100': x__compare__mutmut_100, 
    'x__compare__mutmut_101': x__compare__mutmut_101, 
    'x__compare__mutmut_102': x__compare__mutmut_102, 
    'x__compare__mutmut_103': x__compare__mutmut_103, 
    'x__compare__mutmut_104': x__compare__mutmut_104, 
    'x__compare__mutmut_105': x__compare__mutmut_105, 
    'x__compare__mutmut_106': x__compare__mutmut_106, 
    'x__compare__mutmut_107': x__compare__mutmut_107, 
    'x__compare__mutmut_108': x__compare__mutmut_108, 
    'x__compare__mutmut_109': x__compare__mutmut_109, 
    'x__compare__mutmut_110': x__compare__mutmut_110, 
    'x__compare__mutmut_111': x__compare__mutmut_111, 
    'x__compare__mutmut_112': x__compare__mutmut_112, 
    'x__compare__mutmut_113': x__compare__mutmut_113, 
    'x__compare__mutmut_114': x__compare__mutmut_114, 
    'x__compare__mutmut_115': x__compare__mutmut_115, 
    'x__compare__mutmut_116': x__compare__mutmut_116, 
    'x__compare__mutmut_117': x__compare__mutmut_117, 
    'x__compare__mutmut_118': x__compare__mutmut_118, 
    'x__compare__mutmut_119': x__compare__mutmut_119, 
    'x__compare__mutmut_120': x__compare__mutmut_120, 
    'x__compare__mutmut_121': x__compare__mutmut_121, 
    'x__compare__mutmut_122': x__compare__mutmut_122, 
    'x__compare__mutmut_123': x__compare__mutmut_123, 
    'x__compare__mutmut_124': x__compare__mutmut_124, 
    'x__compare__mutmut_125': x__compare__mutmut_125, 
    'x__compare__mutmut_126': x__compare__mutmut_126, 
    'x__compare__mutmut_127': x__compare__mutmut_127, 
    'x__compare__mutmut_128': x__compare__mutmut_128, 
    'x__compare__mutmut_129': x__compare__mutmut_129, 
    'x__compare__mutmut_130': x__compare__mutmut_130, 
    'x__compare__mutmut_131': x__compare__mutmut_131, 
    'x__compare__mutmut_132': x__compare__mutmut_132, 
    'x__compare__mutmut_133': x__compare__mutmut_133, 
    'x__compare__mutmut_134': x__compare__mutmut_134, 
    'x__compare__mutmut_135': x__compare__mutmut_135, 
    'x__compare__mutmut_136': x__compare__mutmut_136, 
    'x__compare__mutmut_137': x__compare__mutmut_137, 
    'x__compare__mutmut_138': x__compare__mutmut_138, 
    'x__compare__mutmut_139': x__compare__mutmut_139, 
    'x__compare__mutmut_140': x__compare__mutmut_140, 
    'x__compare__mutmut_141': x__compare__mutmut_141, 
    'x__compare__mutmut_142': x__compare__mutmut_142, 
    'x__compare__mutmut_143': x__compare__mutmut_143
}

def _compare(*args, **kwargs):
    result = _mutmut_trampoline(x__compare__mutmut_orig, x__compare__mutmut_mutants, args, kwargs)
    return result 

_compare.__signature__ = _mutmut_signature(x__compare__mutmut_orig)
x__compare__mutmut_orig.__name__ = 'x__compare'


def x_greater_than__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, ">")


def x_greater_than__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(None, b, ">")


def x_greater_than__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, None, ">")


def x_greater_than__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, None)


def x_greater_than__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(b, ">")


def x_greater_than__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, ">")


def x_greater_than__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, )


def x_greater_than__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, "XX>XX")

x_greater_than__mutmut_mutants : ClassVar[MutantDict] = {
'x_greater_than__mutmut_1': x_greater_than__mutmut_1, 
    'x_greater_than__mutmut_2': x_greater_than__mutmut_2, 
    'x_greater_than__mutmut_3': x_greater_than__mutmut_3, 
    'x_greater_than__mutmut_4': x_greater_than__mutmut_4, 
    'x_greater_than__mutmut_5': x_greater_than__mutmut_5, 
    'x_greater_than__mutmut_6': x_greater_than__mutmut_6, 
    'x_greater_than__mutmut_7': x_greater_than__mutmut_7
}

def greater_than(*args, **kwargs):
    result = _mutmut_trampoline(x_greater_than__mutmut_orig, x_greater_than__mutmut_mutants, args, kwargs)
    return result 

greater_than.__signature__ = _mutmut_signature(x_greater_than__mutmut_orig)
x_greater_than__mutmut_orig.__name__ = 'x_greater_than'


def x_greater_than_or_equal_to__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, ">=")


def x_greater_than_or_equal_to__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(None, b, ">=")


def x_greater_than_or_equal_to__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, None, ">=")


def x_greater_than_or_equal_to__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, None)


def x_greater_than_or_equal_to__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(b, ">=")


def x_greater_than_or_equal_to__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, ">=")


def x_greater_than_or_equal_to__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, )


def x_greater_than_or_equal_to__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, "XX>=XX")

x_greater_than_or_equal_to__mutmut_mutants : ClassVar[MutantDict] = {
'x_greater_than_or_equal_to__mutmut_1': x_greater_than_or_equal_to__mutmut_1, 
    'x_greater_than_or_equal_to__mutmut_2': x_greater_than_or_equal_to__mutmut_2, 
    'x_greater_than_or_equal_to__mutmut_3': x_greater_than_or_equal_to__mutmut_3, 
    'x_greater_than_or_equal_to__mutmut_4': x_greater_than_or_equal_to__mutmut_4, 
    'x_greater_than_or_equal_to__mutmut_5': x_greater_than_or_equal_to__mutmut_5, 
    'x_greater_than_or_equal_to__mutmut_6': x_greater_than_or_equal_to__mutmut_6, 
    'x_greater_than_or_equal_to__mutmut_7': x_greater_than_or_equal_to__mutmut_7
}

def greater_than_or_equal_to(*args, **kwargs):
    result = _mutmut_trampoline(x_greater_than_or_equal_to__mutmut_orig, x_greater_than_or_equal_to__mutmut_mutants, args, kwargs)
    return result 

greater_than_or_equal_to.__signature__ = _mutmut_signature(x_greater_than_or_equal_to__mutmut_orig)
x_greater_than_or_equal_to__mutmut_orig.__name__ = 'x_greater_than_or_equal_to'


def x_less_than__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, "<")


def x_less_than__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(None, b, "<")


def x_less_than__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, None, "<")


def x_less_than__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, None)


def x_less_than__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(b, "<")


def x_less_than__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, "<")


def x_less_than__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, )


def x_less_than__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, "XX<XX")

x_less_than__mutmut_mutants : ClassVar[MutantDict] = {
'x_less_than__mutmut_1': x_less_than__mutmut_1, 
    'x_less_than__mutmut_2': x_less_than__mutmut_2, 
    'x_less_than__mutmut_3': x_less_than__mutmut_3, 
    'x_less_than__mutmut_4': x_less_than__mutmut_4, 
    'x_less_than__mutmut_5': x_less_than__mutmut_5, 
    'x_less_than__mutmut_6': x_less_than__mutmut_6, 
    'x_less_than__mutmut_7': x_less_than__mutmut_7
}

def less_than(*args, **kwargs):
    result = _mutmut_trampoline(x_less_than__mutmut_orig, x_less_than__mutmut_mutants, args, kwargs)
    return result 

less_than.__signature__ = _mutmut_signature(x_less_than__mutmut_orig)
x_less_than__mutmut_orig.__name__ = 'x_less_than'


def x_less_than_or_equal_to__mutmut_orig(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, "<=")


def x_less_than_or_equal_to__mutmut_1(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(None, b, "<=")


def x_less_than_or_equal_to__mutmut_2(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, None, "<=")


def x_less_than_or_equal_to__mutmut_3(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, None)


def x_less_than_or_equal_to__mutmut_4(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(b, "<=")


def x_less_than_or_equal_to__mutmut_5(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, "<=")


def x_less_than_or_equal_to__mutmut_6(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, )


def x_less_than_or_equal_to__mutmut_7(a: CtyValue[Any], b: CtyValue[Any]) -> CtyValue[Any]:
    return _compare(a, b, "XX<=XX")

x_less_than_or_equal_to__mutmut_mutants : ClassVar[MutantDict] = {
'x_less_than_or_equal_to__mutmut_1': x_less_than_or_equal_to__mutmut_1, 
    'x_less_than_or_equal_to__mutmut_2': x_less_than_or_equal_to__mutmut_2, 
    'x_less_than_or_equal_to__mutmut_3': x_less_than_or_equal_to__mutmut_3, 
    'x_less_than_or_equal_to__mutmut_4': x_less_than_or_equal_to__mutmut_4, 
    'x_less_than_or_equal_to__mutmut_5': x_less_than_or_equal_to__mutmut_5, 
    'x_less_than_or_equal_to__mutmut_6': x_less_than_or_equal_to__mutmut_6, 
    'x_less_than_or_equal_to__mutmut_7': x_less_than_or_equal_to__mutmut_7
}

def less_than_or_equal_to(*args, **kwargs):
    result = _mutmut_trampoline(x_less_than_or_equal_to__mutmut_orig, x_less_than_or_equal_to__mutmut_mutants, args, kwargs)
    return result 

less_than_or_equal_to.__signature__ = _mutmut_signature(x_less_than_or_equal_to__mutmut_orig)
x_less_than_or_equal_to__mutmut_orig.__name__ = 'x_less_than_or_equal_to'


def x__partition_args__mutmut_orig(
    *args: CtyValue[Any],
) -> tuple[list[CtyValue[Any]], list[CtyValue[Any]]]:
    """Separate arguments into known and unknown values."""
    known_args, unknown_args = [], []
    for v in args:
        if v.is_unknown:
            unknown_args.append(v)
        elif not v.is_null:
            known_args.append(v)
    return known_args, unknown_args


def x__partition_args__mutmut_1(
    *args: CtyValue[Any],
) -> tuple[list[CtyValue[Any]], list[CtyValue[Any]]]:
    """Separate arguments into known and unknown values."""
    known_args, unknown_args = None
    for v in args:
        if v.is_unknown:
            unknown_args.append(v)
        elif not v.is_null:
            known_args.append(v)
    return known_args, unknown_args


def x__partition_args__mutmut_2(
    *args: CtyValue[Any],
) -> tuple[list[CtyValue[Any]], list[CtyValue[Any]]]:
    """Separate arguments into known and unknown values."""
    known_args, unknown_args = [], []
    for v in args:
        if v.is_unknown:
            unknown_args.append(None)
        elif not v.is_null:
            known_args.append(v)
    return known_args, unknown_args


def x__partition_args__mutmut_3(
    *args: CtyValue[Any],
) -> tuple[list[CtyValue[Any]], list[CtyValue[Any]]]:
    """Separate arguments into known and unknown values."""
    known_args, unknown_args = [], []
    for v in args:
        if v.is_unknown:
            unknown_args.append(v)
        elif v.is_null:
            known_args.append(v)
    return known_args, unknown_args


def x__partition_args__mutmut_4(
    *args: CtyValue[Any],
) -> tuple[list[CtyValue[Any]], list[CtyValue[Any]]]:
    """Separate arguments into known and unknown values."""
    known_args, unknown_args = [], []
    for v in args:
        if v.is_unknown:
            unknown_args.append(v)
        elif not v.is_null:
            known_args.append(None)
    return known_args, unknown_args

x__partition_args__mutmut_mutants : ClassVar[MutantDict] = {
'x__partition_args__mutmut_1': x__partition_args__mutmut_1, 
    'x__partition_args__mutmut_2': x__partition_args__mutmut_2, 
    'x__partition_args__mutmut_3': x__partition_args__mutmut_3, 
    'x__partition_args__mutmut_4': x__partition_args__mutmut_4
}

def _partition_args(*args, **kwargs):
    result = _mutmut_trampoline(x__partition_args__mutmut_orig, x__partition_args__mutmut_mutants, args, kwargs)
    return result 

_partition_args.__signature__ = _mutmut_signature(x__partition_args__mutmut_orig)
x__partition_args__mutmut_orig.__name__ = 'x__partition_args'


def x__validate_homogeneous_types__mutmut_orig(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if not (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_1(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if not (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_2(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = None
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if not (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_3(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(None)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if not (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_4(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = None
    if not (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_5(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(None)
    if not (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_6(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_7(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if not (is_all_numbers and is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_8(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if not (is_all_numbers or is_all_strings):
        error_message = None
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_9(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if not (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=None)
        raise CtyFunctionError(error_message)


def x__validate_homogeneous_types__mutmut_10(known_args: list[CtyValue[Any]], op: str) -> None:
    """Ensure all known arguments have compatible types."""
    if not known_args:
        return
    is_all_numbers = all(isinstance(v.type, CtyNumber) for v in known_args)
    is_all_strings = all(isinstance(v.type, CtyString) for v in known_args)
    if not (is_all_numbers or is_all_strings):
        error_message = ERR_ALL_ARGS_SAME_TYPE.format(op=op)
        raise CtyFunctionError(None)

x__validate_homogeneous_types__mutmut_mutants : ClassVar[MutantDict] = {
'x__validate_homogeneous_types__mutmut_1': x__validate_homogeneous_types__mutmut_1, 
    'x__validate_homogeneous_types__mutmut_2': x__validate_homogeneous_types__mutmut_2, 
    'x__validate_homogeneous_types__mutmut_3': x__validate_homogeneous_types__mutmut_3, 
    'x__validate_homogeneous_types__mutmut_4': x__validate_homogeneous_types__mutmut_4, 
    'x__validate_homogeneous_types__mutmut_5': x__validate_homogeneous_types__mutmut_5, 
    'x__validate_homogeneous_types__mutmut_6': x__validate_homogeneous_types__mutmut_6, 
    'x__validate_homogeneous_types__mutmut_7': x__validate_homogeneous_types__mutmut_7, 
    'x__validate_homogeneous_types__mutmut_8': x__validate_homogeneous_types__mutmut_8, 
    'x__validate_homogeneous_types__mutmut_9': x__validate_homogeneous_types__mutmut_9, 
    'x__validate_homogeneous_types__mutmut_10': x__validate_homogeneous_types__mutmut_10
}

def _validate_homogeneous_types(*args, **kwargs):
    result = _mutmut_trampoline(x__validate_homogeneous_types__mutmut_orig, x__validate_homogeneous_types__mutmut_mutants, args, kwargs)
    return result 

_validate_homogeneous_types.__signature__ = _mutmut_signature(x__validate_homogeneous_types__mutmut_orig)
x__validate_homogeneous_types__mutmut_orig.__name__ = 'x__validate_homogeneous_types'


def x__find_extreme_value__mutmut_orig(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_1(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_2(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op != "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_3(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "XXmaxXX":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_4(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "MAX":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_5(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = None  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_6(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(None, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_7(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=None)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_8(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_9(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, )  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_10(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: None)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_11(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = None  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_12(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(None, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_13(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=None)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_14(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_15(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, )  # type: ignore[arg-type,return-value]
        return result


def x__find_extreme_value__mutmut_16(known_args: list[CtyValue[Any]], op: str) -> CtyValue[Any] | None:
    """Find the extreme (min/max) value among known arguments."""
    if not known_args:
        return None
    if op == "max":
        result: CtyValue[Any] = max(known_args, key=lambda v: v.value)  # type: ignore[arg-type,return-value]
        return result
    else:
        result = min(known_args, key=lambda v: None)  # type: ignore[arg-type,return-value]
        return result

x__find_extreme_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__find_extreme_value__mutmut_1': x__find_extreme_value__mutmut_1, 
    'x__find_extreme_value__mutmut_2': x__find_extreme_value__mutmut_2, 
    'x__find_extreme_value__mutmut_3': x__find_extreme_value__mutmut_3, 
    'x__find_extreme_value__mutmut_4': x__find_extreme_value__mutmut_4, 
    'x__find_extreme_value__mutmut_5': x__find_extreme_value__mutmut_5, 
    'x__find_extreme_value__mutmut_6': x__find_extreme_value__mutmut_6, 
    'x__find_extreme_value__mutmut_7': x__find_extreme_value__mutmut_7, 
    'x__find_extreme_value__mutmut_8': x__find_extreme_value__mutmut_8, 
    'x__find_extreme_value__mutmut_9': x__find_extreme_value__mutmut_9, 
    'x__find_extreme_value__mutmut_10': x__find_extreme_value__mutmut_10, 
    'x__find_extreme_value__mutmut_11': x__find_extreme_value__mutmut_11, 
    'x__find_extreme_value__mutmut_12': x__find_extreme_value__mutmut_12, 
    'x__find_extreme_value__mutmut_13': x__find_extreme_value__mutmut_13, 
    'x__find_extreme_value__mutmut_14': x__find_extreme_value__mutmut_14, 
    'x__find_extreme_value__mutmut_15': x__find_extreme_value__mutmut_15, 
    'x__find_extreme_value__mutmut_16': x__find_extreme_value__mutmut_16
}

def _find_extreme_value(*args, **kwargs):
    result = _mutmut_trampoline(x__find_extreme_value__mutmut_orig, x__find_extreme_value__mutmut_mutants, args, kwargs)
    return result 

_find_extreme_value.__signature__ = _mutmut_signature(x__find_extreme_value__mutmut_orig)
x__find_extreme_value__mutmut_orig.__name__ = 'x__find_extreme_value'


def x__filter_dominated_unknowns__mutmut_orig(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_1(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = None
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_2(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = None
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_3(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(None, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_4(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, None)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_5(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_6(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, )
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_7(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = None
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_8(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op != "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_9(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "XXmaxXX":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_10(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "MAX":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_11(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound or (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_12(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val > ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_13(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[1]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_14(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    break
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_15(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound or (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_16(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" or ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_17(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op != "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_18(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "XXminXX" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_19(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "MIN" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_20(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val < ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_21(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[1]):
                continue
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_22(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                break
        remaining_unknowns.append(unk)
    return remaining_unknowns


def x__filter_dominated_unknowns__mutmut_23(
    unknown_args: list[CtyValue[Any]], extreme_known: CtyValue[Any], op: str
) -> list[CtyValue[Any]]:
    """Remove unknown values that are definitely dominated by the extreme known value."""
    remaining_unknowns = []
    extreme_val = cast(Decimal, extreme_known.value)
    for unk in unknown_args:
        if isinstance(unk.value, RefinedUnknownValue):
            ref = unk.value
            if op == "max":
                if ref.number_upper_bound and (extreme_val >= ref.number_upper_bound[0]):
                    continue
            elif op == "min" and ref.number_lower_bound and (extreme_val <= ref.number_lower_bound[0]):
                continue
        remaining_unknowns.append(None)
    return remaining_unknowns

x__filter_dominated_unknowns__mutmut_mutants : ClassVar[MutantDict] = {
'x__filter_dominated_unknowns__mutmut_1': x__filter_dominated_unknowns__mutmut_1, 
    'x__filter_dominated_unknowns__mutmut_2': x__filter_dominated_unknowns__mutmut_2, 
    'x__filter_dominated_unknowns__mutmut_3': x__filter_dominated_unknowns__mutmut_3, 
    'x__filter_dominated_unknowns__mutmut_4': x__filter_dominated_unknowns__mutmut_4, 
    'x__filter_dominated_unknowns__mutmut_5': x__filter_dominated_unknowns__mutmut_5, 
    'x__filter_dominated_unknowns__mutmut_6': x__filter_dominated_unknowns__mutmut_6, 
    'x__filter_dominated_unknowns__mutmut_7': x__filter_dominated_unknowns__mutmut_7, 
    'x__filter_dominated_unknowns__mutmut_8': x__filter_dominated_unknowns__mutmut_8, 
    'x__filter_dominated_unknowns__mutmut_9': x__filter_dominated_unknowns__mutmut_9, 
    'x__filter_dominated_unknowns__mutmut_10': x__filter_dominated_unknowns__mutmut_10, 
    'x__filter_dominated_unknowns__mutmut_11': x__filter_dominated_unknowns__mutmut_11, 
    'x__filter_dominated_unknowns__mutmut_12': x__filter_dominated_unknowns__mutmut_12, 
    'x__filter_dominated_unknowns__mutmut_13': x__filter_dominated_unknowns__mutmut_13, 
    'x__filter_dominated_unknowns__mutmut_14': x__filter_dominated_unknowns__mutmut_14, 
    'x__filter_dominated_unknowns__mutmut_15': x__filter_dominated_unknowns__mutmut_15, 
    'x__filter_dominated_unknowns__mutmut_16': x__filter_dominated_unknowns__mutmut_16, 
    'x__filter_dominated_unknowns__mutmut_17': x__filter_dominated_unknowns__mutmut_17, 
    'x__filter_dominated_unknowns__mutmut_18': x__filter_dominated_unknowns__mutmut_18, 
    'x__filter_dominated_unknowns__mutmut_19': x__filter_dominated_unknowns__mutmut_19, 
    'x__filter_dominated_unknowns__mutmut_20': x__filter_dominated_unknowns__mutmut_20, 
    'x__filter_dominated_unknowns__mutmut_21': x__filter_dominated_unknowns__mutmut_21, 
    'x__filter_dominated_unknowns__mutmut_22': x__filter_dominated_unknowns__mutmut_22, 
    'x__filter_dominated_unknowns__mutmut_23': x__filter_dominated_unknowns__mutmut_23
}

def _filter_dominated_unknowns(*args, **kwargs):
    result = _mutmut_trampoline(x__filter_dominated_unknowns__mutmut_orig, x__filter_dominated_unknowns__mutmut_mutants, args, kwargs)
    return result 

_filter_dominated_unknowns.__signature__ = _mutmut_signature(x__filter_dominated_unknowns__mutmut_orig)
x__filter_dominated_unknowns__mutmut_orig.__name__ = 'x__filter_dominated_unknowns'


def x__multi_compare__mutmut_orig(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_1(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_2(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = None
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_3(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=None)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_4(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(None)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_5(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = None

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_6(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args or not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_7(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_8(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_9(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(None)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_10(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[1].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_11(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(None, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_12(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, None)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_13(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_14(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, )
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_15(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = None

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_16(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(None, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_17(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, None)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_18(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_19(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, )

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_20(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = None

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_21(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(None, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_22(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, None, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_23(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, None)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_24(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_25(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_26(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, )

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_27(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_28(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(None)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_29(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[1].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_30(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args or len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_31(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_32(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) != 1:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_33(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 2:
        return unknown_args[0]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_34(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[1]
    return CtyValue.unknown(args[0].type)


def x__multi_compare__mutmut_35(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(None)


def x__multi_compare__mutmut_36(*args: CtyValue[Any], op: str) -> CtyValue[Any]:
    if not args:
        error_message = ERR_MIN_ONE_ARG.format(op=op)
        raise CtyFunctionError(error_message)

    known_args, unknown_args = _partition_args(*args)

    if not known_args and not unknown_args:
        return CtyValue.null(args[0].type)

    _validate_homogeneous_types(known_args, op)
    extreme_known = _find_extreme_value(known_args, op)

    if extreme_known:
        unknown_args = _filter_dominated_unknowns(unknown_args, extreme_known, op)

    if not unknown_args:
        return extreme_known if extreme_known else CtyValue.null(args[0].type)
    if not known_args and len(unknown_args) == 1:
        return unknown_args[0]
    return CtyValue.unknown(args[1].type)

x__multi_compare__mutmut_mutants : ClassVar[MutantDict] = {
'x__multi_compare__mutmut_1': x__multi_compare__mutmut_1, 
    'x__multi_compare__mutmut_2': x__multi_compare__mutmut_2, 
    'x__multi_compare__mutmut_3': x__multi_compare__mutmut_3, 
    'x__multi_compare__mutmut_4': x__multi_compare__mutmut_4, 
    'x__multi_compare__mutmut_5': x__multi_compare__mutmut_5, 
    'x__multi_compare__mutmut_6': x__multi_compare__mutmut_6, 
    'x__multi_compare__mutmut_7': x__multi_compare__mutmut_7, 
    'x__multi_compare__mutmut_8': x__multi_compare__mutmut_8, 
    'x__multi_compare__mutmut_9': x__multi_compare__mutmut_9, 
    'x__multi_compare__mutmut_10': x__multi_compare__mutmut_10, 
    'x__multi_compare__mutmut_11': x__multi_compare__mutmut_11, 
    'x__multi_compare__mutmut_12': x__multi_compare__mutmut_12, 
    'x__multi_compare__mutmut_13': x__multi_compare__mutmut_13, 
    'x__multi_compare__mutmut_14': x__multi_compare__mutmut_14, 
    'x__multi_compare__mutmut_15': x__multi_compare__mutmut_15, 
    'x__multi_compare__mutmut_16': x__multi_compare__mutmut_16, 
    'x__multi_compare__mutmut_17': x__multi_compare__mutmut_17, 
    'x__multi_compare__mutmut_18': x__multi_compare__mutmut_18, 
    'x__multi_compare__mutmut_19': x__multi_compare__mutmut_19, 
    'x__multi_compare__mutmut_20': x__multi_compare__mutmut_20, 
    'x__multi_compare__mutmut_21': x__multi_compare__mutmut_21, 
    'x__multi_compare__mutmut_22': x__multi_compare__mutmut_22, 
    'x__multi_compare__mutmut_23': x__multi_compare__mutmut_23, 
    'x__multi_compare__mutmut_24': x__multi_compare__mutmut_24, 
    'x__multi_compare__mutmut_25': x__multi_compare__mutmut_25, 
    'x__multi_compare__mutmut_26': x__multi_compare__mutmut_26, 
    'x__multi_compare__mutmut_27': x__multi_compare__mutmut_27, 
    'x__multi_compare__mutmut_28': x__multi_compare__mutmut_28, 
    'x__multi_compare__mutmut_29': x__multi_compare__mutmut_29, 
    'x__multi_compare__mutmut_30': x__multi_compare__mutmut_30, 
    'x__multi_compare__mutmut_31': x__multi_compare__mutmut_31, 
    'x__multi_compare__mutmut_32': x__multi_compare__mutmut_32, 
    'x__multi_compare__mutmut_33': x__multi_compare__mutmut_33, 
    'x__multi_compare__mutmut_34': x__multi_compare__mutmut_34, 
    'x__multi_compare__mutmut_35': x__multi_compare__mutmut_35, 
    'x__multi_compare__mutmut_36': x__multi_compare__mutmut_36
}

def _multi_compare(*args, **kwargs):
    result = _mutmut_trampoline(x__multi_compare__mutmut_orig, x__multi_compare__mutmut_mutants, args, kwargs)
    return result 

_multi_compare.__signature__ = _mutmut_signature(x__multi_compare__mutmut_orig)
x__multi_compare__mutmut_orig.__name__ = 'x__multi_compare'


def x_max_fn__mutmut_orig(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, op="max")


def x_max_fn__mutmut_1(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, op=None)


def x_max_fn__mutmut_2(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(op="max")


def x_max_fn__mutmut_3(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, )


def x_max_fn__mutmut_4(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, op="XXmaxXX")


def x_max_fn__mutmut_5(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, op="MAX")

x_max_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_max_fn__mutmut_1': x_max_fn__mutmut_1, 
    'x_max_fn__mutmut_2': x_max_fn__mutmut_2, 
    'x_max_fn__mutmut_3': x_max_fn__mutmut_3, 
    'x_max_fn__mutmut_4': x_max_fn__mutmut_4, 
    'x_max_fn__mutmut_5': x_max_fn__mutmut_5
}

def max_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_max_fn__mutmut_orig, x_max_fn__mutmut_mutants, args, kwargs)
    return result 

max_fn.__signature__ = _mutmut_signature(x_max_fn__mutmut_orig)
x_max_fn__mutmut_orig.__name__ = 'x_max_fn'


def x_min_fn__mutmut_orig(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, op="min")


def x_min_fn__mutmut_1(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, op=None)


def x_min_fn__mutmut_2(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(op="min")


def x_min_fn__mutmut_3(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, )


def x_min_fn__mutmut_4(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, op="XXminXX")


def x_min_fn__mutmut_5(*args: CtyValue[Any]) -> CtyValue[Any]:
    return _multi_compare(*args, op="MIN")

x_min_fn__mutmut_mutants : ClassVar[MutantDict] = {
'x_min_fn__mutmut_1': x_min_fn__mutmut_1, 
    'x_min_fn__mutmut_2': x_min_fn__mutmut_2, 
    'x_min_fn__mutmut_3': x_min_fn__mutmut_3, 
    'x_min_fn__mutmut_4': x_min_fn__mutmut_4, 
    'x_min_fn__mutmut_5': x_min_fn__mutmut_5
}

def min_fn(*args, **kwargs):
    result = _mutmut_trampoline(x_min_fn__mutmut_orig, x_min_fn__mutmut_mutants, args, kwargs)
    return result 

min_fn.__signature__ = _mutmut_signature(x_min_fn__mutmut_orig)
x_min_fn__mutmut_orig.__name__ = 'x_min_fn'


# 🌊🪢🔣🪄
