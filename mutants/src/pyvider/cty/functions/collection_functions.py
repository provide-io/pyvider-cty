# pyvider/cty/functions/collection_functions.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from itertools import product
from typing import Any, cast

from provide.foundation.errors import error_boundary

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
    unify,
)
from pyvider.cty.config.defaults import (
    ERR_DISTINCT_ELEMENT_NOT_HASHABLE,
    ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE,
)
from pyvider.cty.conversion import infer_cty_type_from_raw
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


def x_distinct__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = None
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=None)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null and input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = None
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = None
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(None)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(None)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = None
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=None, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=None)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, )
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(None) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = None  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_18(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(None, input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_19(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], None)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_20(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_21(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], )  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_22(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] & CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_23(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = None
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_24(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = None
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_distinct__mutmut_25(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(None)  # type: ignore[no-any-return]


def x_distinct__mutmut_26(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=None).validate(result_elements)  # type: ignore[no-any-return]

x_distinct__mutmut_mutants : ClassVar[MutantDict] = {
'x_distinct__mutmut_1': x_distinct__mutmut_1, 
    'x_distinct__mutmut_2': x_distinct__mutmut_2, 
    'x_distinct__mutmut_3': x_distinct__mutmut_3, 
    'x_distinct__mutmut_4': x_distinct__mutmut_4, 
    'x_distinct__mutmut_5': x_distinct__mutmut_5, 
    'x_distinct__mutmut_6': x_distinct__mutmut_6, 
    'x_distinct__mutmut_7': x_distinct__mutmut_7, 
    'x_distinct__mutmut_8': x_distinct__mutmut_8, 
    'x_distinct__mutmut_9': x_distinct__mutmut_9, 
    'x_distinct__mutmut_10': x_distinct__mutmut_10, 
    'x_distinct__mutmut_11': x_distinct__mutmut_11, 
    'x_distinct__mutmut_12': x_distinct__mutmut_12, 
    'x_distinct__mutmut_13': x_distinct__mutmut_13, 
    'x_distinct__mutmut_14': x_distinct__mutmut_14, 
    'x_distinct__mutmut_15': x_distinct__mutmut_15, 
    'x_distinct__mutmut_16': x_distinct__mutmut_16, 
    'x_distinct__mutmut_17': x_distinct__mutmut_17, 
    'x_distinct__mutmut_18': x_distinct__mutmut_18, 
    'x_distinct__mutmut_19': x_distinct__mutmut_19, 
    'x_distinct__mutmut_20': x_distinct__mutmut_20, 
    'x_distinct__mutmut_21': x_distinct__mutmut_21, 
    'x_distinct__mutmut_22': x_distinct__mutmut_22, 
    'x_distinct__mutmut_23': x_distinct__mutmut_23, 
    'x_distinct__mutmut_24': x_distinct__mutmut_24, 
    'x_distinct__mutmut_25': x_distinct__mutmut_25, 
    'x_distinct__mutmut_26': x_distinct__mutmut_26
}

def distinct(*args, **kwargs):
    result = _mutmut_trampoline(x_distinct__mutmut_orig, x_distinct__mutmut_mutants, args, kwargs)
    return result 

distinct.__signature__ = _mutmut_signature(x_distinct__mutmut_orig)
x_distinct__mutmut_orig.__name__ = 'x_distinct'


def x__extract_inner_value__mutmut_orig(outer_element_val: Any) -> Any:
    """Extract the inner value from a potentially dynamic outer element."""
    return (
        outer_element_val.value
        if isinstance(outer_element_val, CtyValue) and isinstance(outer_element_val.type, CtyDynamic)
        else outer_element_val
    )


def x__extract_inner_value__mutmut_1(outer_element_val: Any) -> Any:
    """Extract the inner value from a potentially dynamic outer element."""
    return (
        outer_element_val.value
        if isinstance(outer_element_val, CtyValue) or isinstance(outer_element_val.type, CtyDynamic)
        else outer_element_val
    )

x__extract_inner_value__mutmut_mutants : ClassVar[MutantDict] = {
'x__extract_inner_value__mutmut_1': x__extract_inner_value__mutmut_1
}

def _extract_inner_value(*args, **kwargs):
    result = _mutmut_trampoline(x__extract_inner_value__mutmut_orig, x__extract_inner_value__mutmut_mutants, args, kwargs)
    return result 

_extract_inner_value.__signature__ = _mutmut_signature(x__extract_inner_value__mutmut_orig)
x__extract_inner_value__mutmut_orig.__name__ = 'x__extract_inner_value'


def x__validate_collection_element__mutmut_orig(inner_val: Any) -> None:
    """Validate that an inner value is a proper collection for flattening."""
    if not isinstance(inner_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"flatten: all elements must be lists, sets, or tuples; found {inner_val.type.ctype}"
        )


def x__validate_collection_element__mutmut_1(inner_val: Any) -> None:
    """Validate that an inner value is a proper collection for flattening."""
    if isinstance(inner_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"flatten: all elements must be lists, sets, or tuples; found {inner_val.type.ctype}"
        )


def x__validate_collection_element__mutmut_2(inner_val: Any) -> None:
    """Validate that an inner value is a proper collection for flattening."""
    if not isinstance(inner_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            None
        )

x__validate_collection_element__mutmut_mutants : ClassVar[MutantDict] = {
'x__validate_collection_element__mutmut_1': x__validate_collection_element__mutmut_1, 
    'x__validate_collection_element__mutmut_2': x__validate_collection_element__mutmut_2
}

def _validate_collection_element(*args, **kwargs):
    result = _mutmut_trampoline(x__validate_collection_element__mutmut_orig, x__validate_collection_element__mutmut_mutants, args, kwargs)
    return result 

_validate_collection_element.__signature__ = _mutmut_signature(x__validate_collection_element__mutmut_orig)
x__validate_collection_element__mutmut_orig.__name__ = 'x__validate_collection_element'


def x__determine_unified_element_type__mutmut_orig(
    final_element_type: CtyType[Any] | None, new_element_type: CtyType[Any]
) -> CtyType[Any]:
    """Determine the unified element type for flattened elements."""
    if final_element_type is None:
        return new_element_type
    elif not final_element_type.equal(new_element_type):
        return CtyDynamic()
    return final_element_type


def x__determine_unified_element_type__mutmut_1(
    final_element_type: CtyType[Any] | None, new_element_type: CtyType[Any]
) -> CtyType[Any]:
    """Determine the unified element type for flattened elements."""
    if final_element_type is not None:
        return new_element_type
    elif not final_element_type.equal(new_element_type):
        return CtyDynamic()
    return final_element_type


def x__determine_unified_element_type__mutmut_2(
    final_element_type: CtyType[Any] | None, new_element_type: CtyType[Any]
) -> CtyType[Any]:
    """Determine the unified element type for flattened elements."""
    if final_element_type is None:
        return new_element_type
    elif final_element_type.equal(new_element_type):
        return CtyDynamic()
    return final_element_type


def x__determine_unified_element_type__mutmut_3(
    final_element_type: CtyType[Any] | None, new_element_type: CtyType[Any]
) -> CtyType[Any]:
    """Determine the unified element type for flattened elements."""
    if final_element_type is None:
        return new_element_type
    elif not final_element_type.equal(None):
        return CtyDynamic()
    return final_element_type

x__determine_unified_element_type__mutmut_mutants : ClassVar[MutantDict] = {
'x__determine_unified_element_type__mutmut_1': x__determine_unified_element_type__mutmut_1, 
    'x__determine_unified_element_type__mutmut_2': x__determine_unified_element_type__mutmut_2, 
    'x__determine_unified_element_type__mutmut_3': x__determine_unified_element_type__mutmut_3
}

def _determine_unified_element_type(*args, **kwargs):
    result = _mutmut_trampoline(x__determine_unified_element_type__mutmut_orig, x__determine_unified_element_type__mutmut_mutants, args, kwargs)
    return result 

_determine_unified_element_type.__signature__ = _mutmut_signature(x__determine_unified_element_type__mutmut_orig)
x__determine_unified_element_type__mutmut_orig.__name__ = 'x__determine_unified_element_type'


def x_flatten__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null and input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = None
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = ""

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = None
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(None)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) and inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            break
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(None)

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=None))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(None)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = None
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(None, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, None)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_18(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, )
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_19(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(None)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_20(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is not None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_21(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate(None)  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_22(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=None).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_flatten__mutmut_23(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=final_element_type).validate(None)  # type: ignore[no-any-return]


def x_flatten__mutmut_24(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType[Any] | None = None

    for outer_element_val in input_val.value:  # type: ignore[attr-defined]
        inner_val = _extract_inner_value(outer_element_val)
        if not isinstance(inner_val, CtyValue) or inner_val.is_null:
            continue
        if inner_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))

        _validate_collection_element(inner_val)

        for inner_element_val in inner_val.value:  # type: ignore[attr-defined]
            final_element_type = _determine_unified_element_type(final_element_type, inner_element_val.type)
            result_elements.append(inner_element_val)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
    return CtyList(element_type=None).validate(result_elements)  # type: ignore[no-any-return]

x_flatten__mutmut_mutants : ClassVar[MutantDict] = {
'x_flatten__mutmut_1': x_flatten__mutmut_1, 
    'x_flatten__mutmut_2': x_flatten__mutmut_2, 
    'x_flatten__mutmut_3': x_flatten__mutmut_3, 
    'x_flatten__mutmut_4': x_flatten__mutmut_4, 
    'x_flatten__mutmut_5': x_flatten__mutmut_5, 
    'x_flatten__mutmut_6': x_flatten__mutmut_6, 
    'x_flatten__mutmut_7': x_flatten__mutmut_7, 
    'x_flatten__mutmut_8': x_flatten__mutmut_8, 
    'x_flatten__mutmut_9': x_flatten__mutmut_9, 
    'x_flatten__mutmut_10': x_flatten__mutmut_10, 
    'x_flatten__mutmut_11': x_flatten__mutmut_11, 
    'x_flatten__mutmut_12': x_flatten__mutmut_12, 
    'x_flatten__mutmut_13': x_flatten__mutmut_13, 
    'x_flatten__mutmut_14': x_flatten__mutmut_14, 
    'x_flatten__mutmut_15': x_flatten__mutmut_15, 
    'x_flatten__mutmut_16': x_flatten__mutmut_16, 
    'x_flatten__mutmut_17': x_flatten__mutmut_17, 
    'x_flatten__mutmut_18': x_flatten__mutmut_18, 
    'x_flatten__mutmut_19': x_flatten__mutmut_19, 
    'x_flatten__mutmut_20': x_flatten__mutmut_20, 
    'x_flatten__mutmut_21': x_flatten__mutmut_21, 
    'x_flatten__mutmut_22': x_flatten__mutmut_22, 
    'x_flatten__mutmut_23': x_flatten__mutmut_23, 
    'x_flatten__mutmut_24': x_flatten__mutmut_24
}

def flatten(*args, **kwargs):
    result = _mutmut_trampoline(x_flatten__mutmut_orig, x_flatten__mutmut_mutants, args, kwargs)
    return result 

flatten.__signature__ = _mutmut_signature(x_flatten__mutmut_orig)
x_flatten__mutmut_orig.__name__ = 'x_flatten'


def x_sort__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(None)

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = None  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(None, input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], None)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], )  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] & CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = None
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = None
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(None)

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(None, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, None):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr("__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, ):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_18(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "XX__iter__XX"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_19(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__ITER__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_20(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError(None)

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_21(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("XXsort: input value is not iterableXX")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_22(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("SORT: INPUT VALUE IS NOT ITERABLE")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_23(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = None
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_24(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(None, input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_25(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], None)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_26(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_27(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], )
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_28(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] & tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_29(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(None):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_30(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null and cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_31(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(None)

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_32(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = None
    return result


def x_sort__mutmut_33(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        None
    )
    return result


def x_sort__mutmut_34(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=None).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_35(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(None, key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_36(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=None)
    )
    return result


def x_sort__mutmut_37(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(key=lambda x: x.value)
    )
    return result


def x_sort__mutmut_38(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, )
    )
    return result


def x_sort__mutmut_39(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: None)
    )
    return result

x_sort__mutmut_mutants : ClassVar[MutantDict] = {
'x_sort__mutmut_1': x_sort__mutmut_1, 
    'x_sort__mutmut_2': x_sort__mutmut_2, 
    'x_sort__mutmut_3': x_sort__mutmut_3, 
    'x_sort__mutmut_4': x_sort__mutmut_4, 
    'x_sort__mutmut_5': x_sort__mutmut_5, 
    'x_sort__mutmut_6': x_sort__mutmut_6, 
    'x_sort__mutmut_7': x_sort__mutmut_7, 
    'x_sort__mutmut_8': x_sort__mutmut_8, 
    'x_sort__mutmut_9': x_sort__mutmut_9, 
    'x_sort__mutmut_10': x_sort__mutmut_10, 
    'x_sort__mutmut_11': x_sort__mutmut_11, 
    'x_sort__mutmut_12': x_sort__mutmut_12, 
    'x_sort__mutmut_13': x_sort__mutmut_13, 
    'x_sort__mutmut_14': x_sort__mutmut_14, 
    'x_sort__mutmut_15': x_sort__mutmut_15, 
    'x_sort__mutmut_16': x_sort__mutmut_16, 
    'x_sort__mutmut_17': x_sort__mutmut_17, 
    'x_sort__mutmut_18': x_sort__mutmut_18, 
    'x_sort__mutmut_19': x_sort__mutmut_19, 
    'x_sort__mutmut_20': x_sort__mutmut_20, 
    'x_sort__mutmut_21': x_sort__mutmut_21, 
    'x_sort__mutmut_22': x_sort__mutmut_22, 
    'x_sort__mutmut_23': x_sort__mutmut_23, 
    'x_sort__mutmut_24': x_sort__mutmut_24, 
    'x_sort__mutmut_25': x_sort__mutmut_25, 
    'x_sort__mutmut_26': x_sort__mutmut_26, 
    'x_sort__mutmut_27': x_sort__mutmut_27, 
    'x_sort__mutmut_28': x_sort__mutmut_28, 
    'x_sort__mutmut_29': x_sort__mutmut_29, 
    'x_sort__mutmut_30': x_sort__mutmut_30, 
    'x_sort__mutmut_31': x_sort__mutmut_31, 
    'x_sort__mutmut_32': x_sort__mutmut_32, 
    'x_sort__mutmut_33': x_sort__mutmut_33, 
    'x_sort__mutmut_34': x_sort__mutmut_34, 
    'x_sort__mutmut_35': x_sort__mutmut_35, 
    'x_sort__mutmut_36': x_sort__mutmut_36, 
    'x_sort__mutmut_37': x_sort__mutmut_37, 
    'x_sort__mutmut_38': x_sort__mutmut_38, 
    'x_sort__mutmut_39': x_sort__mutmut_39
}

def sort(*args, **kwargs):
    result = _mutmut_trampoline(x_sort__mutmut_orig, x_sort__mutmut_mutants, args, kwargs)
    return result 

sort.__signature__ = _mutmut_signature(x_sort__mutmut_orig)
x_sort__mutmut_orig.__name__ = 'x_sort'


def x_length__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context=None
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "XXoperationXX": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "OPERATION": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "XXcty_function_lengthXX",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "CTY_FUNCTION_LENGTH",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "XXinput_typeXX": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "INPUT_TYPE": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(None),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "XXinput_is_nullXX": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "INPUT_IS_NULL": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "XXinput_is_unknownXX": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "INPUT_IS_UNKNOWN": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(None)
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = None
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = None
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None or lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_18(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_19(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower != upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_20(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(None)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_21(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(None)
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_22(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(None)
        return CtyNumber().validate(len(input_val.value))  # type: ignore[arg-type]


def x_length__mutmut_23(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
            raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
        if input_val.is_unknown:
            if isinstance(input_val.value, RefinedUnknownValue):
                lower = input_val.value.collection_length_lower_bound
                upper = input_val.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        if input_val.is_null:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(None)  # type: ignore[arg-type]

x_length__mutmut_mutants : ClassVar[MutantDict] = {
'x_length__mutmut_1': x_length__mutmut_1, 
    'x_length__mutmut_2': x_length__mutmut_2, 
    'x_length__mutmut_3': x_length__mutmut_3, 
    'x_length__mutmut_4': x_length__mutmut_4, 
    'x_length__mutmut_5': x_length__mutmut_5, 
    'x_length__mutmut_6': x_length__mutmut_6, 
    'x_length__mutmut_7': x_length__mutmut_7, 
    'x_length__mutmut_8': x_length__mutmut_8, 
    'x_length__mutmut_9': x_length__mutmut_9, 
    'x_length__mutmut_10': x_length__mutmut_10, 
    'x_length__mutmut_11': x_length__mutmut_11, 
    'x_length__mutmut_12': x_length__mutmut_12, 
    'x_length__mutmut_13': x_length__mutmut_13, 
    'x_length__mutmut_14': x_length__mutmut_14, 
    'x_length__mutmut_15': x_length__mutmut_15, 
    'x_length__mutmut_16': x_length__mutmut_16, 
    'x_length__mutmut_17': x_length__mutmut_17, 
    'x_length__mutmut_18': x_length__mutmut_18, 
    'x_length__mutmut_19': x_length__mutmut_19, 
    'x_length__mutmut_20': x_length__mutmut_20, 
    'x_length__mutmut_21': x_length__mutmut_21, 
    'x_length__mutmut_22': x_length__mutmut_22, 
    'x_length__mutmut_23': x_length__mutmut_23
}

def length(*args, **kwargs):
    result = _mutmut_trampoline(x_length__mutmut_orig, x_length__mutmut_mutants, args, kwargs)
    return result 

length.__signature__ = _mutmut_signature(x_length__mutmut_orig)
x_length__mutmut_orig.__name__ = 'x_length'


def x_slice__mutmut_orig(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_1(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_2(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(None)
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_3(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) and not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_4(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_5(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_6(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError(None)
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_7(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("XXslice: start and end must be numbersXX")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_8(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("SLICE: START AND END MUST BE NUMBERS")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_9(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = None
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_10(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null and end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_11(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown and end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_12(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null and start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_13(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown and start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_14(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null and input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_15(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(None)
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_16(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=None))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_17(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = None  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_18(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(None), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_19(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(None)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


def x_slice__mutmut_20(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(None)  # type: ignore[no-any-return,index]


def x_slice__mutmut_21(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=None).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]

x_slice__mutmut_mutants : ClassVar[MutantDict] = {
'x_slice__mutmut_1': x_slice__mutmut_1, 
    'x_slice__mutmut_2': x_slice__mutmut_2, 
    'x_slice__mutmut_3': x_slice__mutmut_3, 
    'x_slice__mutmut_4': x_slice__mutmut_4, 
    'x_slice__mutmut_5': x_slice__mutmut_5, 
    'x_slice__mutmut_6': x_slice__mutmut_6, 
    'x_slice__mutmut_7': x_slice__mutmut_7, 
    'x_slice__mutmut_8': x_slice__mutmut_8, 
    'x_slice__mutmut_9': x_slice__mutmut_9, 
    'x_slice__mutmut_10': x_slice__mutmut_10, 
    'x_slice__mutmut_11': x_slice__mutmut_11, 
    'x_slice__mutmut_12': x_slice__mutmut_12, 
    'x_slice__mutmut_13': x_slice__mutmut_13, 
    'x_slice__mutmut_14': x_slice__mutmut_14, 
    'x_slice__mutmut_15': x_slice__mutmut_15, 
    'x_slice__mutmut_16': x_slice__mutmut_16, 
    'x_slice__mutmut_17': x_slice__mutmut_17, 
    'x_slice__mutmut_18': x_slice__mutmut_18, 
    'x_slice__mutmut_19': x_slice__mutmut_19, 
    'x_slice__mutmut_20': x_slice__mutmut_20, 
    'x_slice__mutmut_21': x_slice__mutmut_21
}

def slice(*args, **kwargs):
    result = _mutmut_trampoline(x_slice__mutmut_orig, x_slice__mutmut_mutants, args, kwargs)
    return result 

slice.__signature__ = _mutmut_signature(x_slice__mutmut_orig)
x_slice__mutmut_orig.__name__ = 'x_slice'


def x_concat__mutmut_orig(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_1(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context=None
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_2(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "XXoperationXX": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_3(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "OPERATION": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_4(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "XXcty_function_concatXX",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_5(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "CTY_FUNCTION_CONCAT",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_6(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "XXnum_listsXX": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_7(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "NUM_LISTS": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_8(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "XXlist_typesXX": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_9(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "LIST_TYPES": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_10(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(None) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_11(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:4]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_12(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_13(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(None):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_14(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError(None)
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_15(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("XXconcat: all arguments must be lists or tuplesXX")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_16(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("CONCAT: ALL ARGUMENTS MUST BE LISTS OR TUPLES")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_17(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = None
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_18(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = ""
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_19(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(None):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_20(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(None)
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_21(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=None))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_22(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                break
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_23(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is not None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_24(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = None
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_25(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_26(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(None):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_27(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = None
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_28(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(None)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_29(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is not None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_30(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate(None)  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_31(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=None).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


def x_concat__mutmut_32(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(None)  # type: ignore[no-any-return]


def x_concat__mutmut_33(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=None).validate(result_elements)  # type: ignore[no-any-return]

x_concat__mutmut_mutants : ClassVar[MutantDict] = {
'x_concat__mutmut_1': x_concat__mutmut_1, 
    'x_concat__mutmut_2': x_concat__mutmut_2, 
    'x_concat__mutmut_3': x_concat__mutmut_3, 
    'x_concat__mutmut_4': x_concat__mutmut_4, 
    'x_concat__mutmut_5': x_concat__mutmut_5, 
    'x_concat__mutmut_6': x_concat__mutmut_6, 
    'x_concat__mutmut_7': x_concat__mutmut_7, 
    'x_concat__mutmut_8': x_concat__mutmut_8, 
    'x_concat__mutmut_9': x_concat__mutmut_9, 
    'x_concat__mutmut_10': x_concat__mutmut_10, 
    'x_concat__mutmut_11': x_concat__mutmut_11, 
    'x_concat__mutmut_12': x_concat__mutmut_12, 
    'x_concat__mutmut_13': x_concat__mutmut_13, 
    'x_concat__mutmut_14': x_concat__mutmut_14, 
    'x_concat__mutmut_15': x_concat__mutmut_15, 
    'x_concat__mutmut_16': x_concat__mutmut_16, 
    'x_concat__mutmut_17': x_concat__mutmut_17, 
    'x_concat__mutmut_18': x_concat__mutmut_18, 
    'x_concat__mutmut_19': x_concat__mutmut_19, 
    'x_concat__mutmut_20': x_concat__mutmut_20, 
    'x_concat__mutmut_21': x_concat__mutmut_21, 
    'x_concat__mutmut_22': x_concat__mutmut_22, 
    'x_concat__mutmut_23': x_concat__mutmut_23, 
    'x_concat__mutmut_24': x_concat__mutmut_24, 
    'x_concat__mutmut_25': x_concat__mutmut_25, 
    'x_concat__mutmut_26': x_concat__mutmut_26, 
    'x_concat__mutmut_27': x_concat__mutmut_27, 
    'x_concat__mutmut_28': x_concat__mutmut_28, 
    'x_concat__mutmut_29': x_concat__mutmut_29, 
    'x_concat__mutmut_30': x_concat__mutmut_30, 
    'x_concat__mutmut_31': x_concat__mutmut_31, 
    'x_concat__mutmut_32': x_concat__mutmut_32, 
    'x_concat__mutmut_33': x_concat__mutmut_33
}

def concat(*args, **kwargs):
    result = _mutmut_trampoline(x_concat__mutmut_orig, x_concat__mutmut_mutants, args, kwargs)
    return result 

concat.__signature__ = _mutmut_signature(x_concat__mutmut_orig)
x_concat__mutmut_orig.__name__ = 'x_concat'


def x_contains__mutmut_orig(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )
    if collection.is_null or collection.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(value in collection.value)  # type: ignore[operator]


def x_contains__mutmut_1(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )
    if collection.is_null or collection.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(value in collection.value)  # type: ignore[operator]


def x_contains__mutmut_2(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            None
        )
    if collection.is_null or collection.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(value in collection.value)  # type: ignore[operator]


def x_contains__mutmut_3(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )
    if collection.is_null and collection.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(value in collection.value)  # type: ignore[operator]


def x_contains__mutmut_4(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )
    if collection.is_null or collection.is_unknown:
        return CtyValue.unknown(None)
    return CtyBool().validate(value in collection.value)  # type: ignore[operator]


def x_contains__mutmut_5(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )
    if collection.is_null or collection.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(None)  # type: ignore[operator]


def x_contains__mutmut_6(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )
    if collection.is_null or collection.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(value not in collection.value)  # type: ignore[operator]

x_contains__mutmut_mutants : ClassVar[MutantDict] = {
'x_contains__mutmut_1': x_contains__mutmut_1, 
    'x_contains__mutmut_2': x_contains__mutmut_2, 
    'x_contains__mutmut_3': x_contains__mutmut_3, 
    'x_contains__mutmut_4': x_contains__mutmut_4, 
    'x_contains__mutmut_5': x_contains__mutmut_5, 
    'x_contains__mutmut_6': x_contains__mutmut_6
}

def contains(*args, **kwargs):
    result = _mutmut_trampoline(x_contains__mutmut_orig, x_contains__mutmut_mutants, args, kwargs)
    return result 

contains.__signature__ = _mutmut_signature(x_contains__mutmut_orig)
x_contains__mutmut_orig.__name__ = 'x_contains'


def x_keys__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context=None
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "XXoperationXX": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "OPERATION": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "XXcty_function_keysXX",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "CTY_FUNCTION_KEYS",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "XXinput_typeXX": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "INPUT_TYPE": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(None),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "XXinput_is_nullXX": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "INPUT_IS_NULL": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "XXinput_is_unknownXX": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "INPUT_IS_UNKNOWN": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(None)
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null and input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(None)
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=None))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_18(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = None
        return result


def x_keys__mutmut_19(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            None  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_20(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=None).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_21(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(None)  # type: ignore[attr-defined]
        )
        return result


def x_keys__mutmut_22(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(None))  # type: ignore[attr-defined]
        )
        return result

x_keys__mutmut_mutants : ClassVar[MutantDict] = {
'x_keys__mutmut_1': x_keys__mutmut_1, 
    'x_keys__mutmut_2': x_keys__mutmut_2, 
    'x_keys__mutmut_3': x_keys__mutmut_3, 
    'x_keys__mutmut_4': x_keys__mutmut_4, 
    'x_keys__mutmut_5': x_keys__mutmut_5, 
    'x_keys__mutmut_6': x_keys__mutmut_6, 
    'x_keys__mutmut_7': x_keys__mutmut_7, 
    'x_keys__mutmut_8': x_keys__mutmut_8, 
    'x_keys__mutmut_9': x_keys__mutmut_9, 
    'x_keys__mutmut_10': x_keys__mutmut_10, 
    'x_keys__mutmut_11': x_keys__mutmut_11, 
    'x_keys__mutmut_12': x_keys__mutmut_12, 
    'x_keys__mutmut_13': x_keys__mutmut_13, 
    'x_keys__mutmut_14': x_keys__mutmut_14, 
    'x_keys__mutmut_15': x_keys__mutmut_15, 
    'x_keys__mutmut_16': x_keys__mutmut_16, 
    'x_keys__mutmut_17': x_keys__mutmut_17, 
    'x_keys__mutmut_18': x_keys__mutmut_18, 
    'x_keys__mutmut_19': x_keys__mutmut_19, 
    'x_keys__mutmut_20': x_keys__mutmut_20, 
    'x_keys__mutmut_21': x_keys__mutmut_21, 
    'x_keys__mutmut_22': x_keys__mutmut_22
}

def keys(*args, **kwargs):
    result = _mutmut_trampoline(x_keys__mutmut_orig, x_keys__mutmut_mutants, args, kwargs)
    return result 

keys.__signature__ = _mutmut_signature(x_keys__mutmut_orig)
x_keys__mutmut_orig.__name__ = 'x_keys'


def x_values__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context=None
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "XXoperationXX": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "OPERATION": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "XXcty_function_valuesXX",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "CTY_FUNCTION_VALUES",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "XXinput_typeXX": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "INPUT_TYPE": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(None),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_9(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "XXinput_is_nullXX": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_10(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "INPUT_IS_NULL": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_11(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "XXinput_is_unknownXX": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_12(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "INPUT_IS_UNKNOWN": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_13(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_14(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(None)
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_15(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = None
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_16(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null and input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_17(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(None)
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_18(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=None))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_19(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_20(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError(None)
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_21(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("XXvalues: input value is not a map or objectXX")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_22(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("VALUES: INPUT VALUE IS NOT A MAP OR OBJECT")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_23(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(None)  # type: ignore[no-any-return]


def x_values__mutmut_24(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=None).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


def x_values__mutmut_25(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(None))  # type: ignore[no-any-return]

x_values__mutmut_mutants : ClassVar[MutantDict] = {
'x_values__mutmut_1': x_values__mutmut_1, 
    'x_values__mutmut_2': x_values__mutmut_2, 
    'x_values__mutmut_3': x_values__mutmut_3, 
    'x_values__mutmut_4': x_values__mutmut_4, 
    'x_values__mutmut_5': x_values__mutmut_5, 
    'x_values__mutmut_6': x_values__mutmut_6, 
    'x_values__mutmut_7': x_values__mutmut_7, 
    'x_values__mutmut_8': x_values__mutmut_8, 
    'x_values__mutmut_9': x_values__mutmut_9, 
    'x_values__mutmut_10': x_values__mutmut_10, 
    'x_values__mutmut_11': x_values__mutmut_11, 
    'x_values__mutmut_12': x_values__mutmut_12, 
    'x_values__mutmut_13': x_values__mutmut_13, 
    'x_values__mutmut_14': x_values__mutmut_14, 
    'x_values__mutmut_15': x_values__mutmut_15, 
    'x_values__mutmut_16': x_values__mutmut_16, 
    'x_values__mutmut_17': x_values__mutmut_17, 
    'x_values__mutmut_18': x_values__mutmut_18, 
    'x_values__mutmut_19': x_values__mutmut_19, 
    'x_values__mutmut_20': x_values__mutmut_20, 
    'x_values__mutmut_21': x_values__mutmut_21, 
    'x_values__mutmut_22': x_values__mutmut_22, 
    'x_values__mutmut_23': x_values__mutmut_23, 
    'x_values__mutmut_24': x_values__mutmut_24, 
    'x_values__mutmut_25': x_values__mutmut_25
}

def values(*args, **kwargs):
    result = _mutmut_trampoline(x_values__mutmut_orig, x_values__mutmut_mutants, args, kwargs)
    return result 

values.__signature__ = _mutmut_signature(x_values__mutmut_orig)
x_values__mutmut_orig.__name__ = 'x_values'


def x_reverse__mutmut_orig(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(input_val.value)))  # type: ignore[no-any-return,call-overload]


def x_reverse__mutmut_1(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(input_val.value)))  # type: ignore[no-any-return,call-overload]


def x_reverse__mutmut_2(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(None)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(input_val.value)))  # type: ignore[no-any-return,call-overload]


def x_reverse__mutmut_3(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("XXreverse: input must be a list or tupleXX")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(input_val.value)))  # type: ignore[no-any-return,call-overload]


def x_reverse__mutmut_4(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("REVERSE: INPUT MUST BE A LIST OR TUPLE")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(input_val.value)))  # type: ignore[no-any-return,call-overload]


def x_reverse__mutmut_5(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null and input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(input_val.value)))  # type: ignore[no-any-return,call-overload]


def x_reverse__mutmut_6(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(None)  # type: ignore[no-any-return,call-overload]


def x_reverse__mutmut_7(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(None))  # type: ignore[no-any-return,call-overload]


def x_reverse__mutmut_8(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(None)))  # type: ignore[no-any-return,call-overload]

x_reverse__mutmut_mutants : ClassVar[MutantDict] = {
'x_reverse__mutmut_1': x_reverse__mutmut_1, 
    'x_reverse__mutmut_2': x_reverse__mutmut_2, 
    'x_reverse__mutmut_3': x_reverse__mutmut_3, 
    'x_reverse__mutmut_4': x_reverse__mutmut_4, 
    'x_reverse__mutmut_5': x_reverse__mutmut_5, 
    'x_reverse__mutmut_6': x_reverse__mutmut_6, 
    'x_reverse__mutmut_7': x_reverse__mutmut_7, 
    'x_reverse__mutmut_8': x_reverse__mutmut_8
}

def reverse(*args, **kwargs):
    result = _mutmut_trampoline(x_reverse__mutmut_orig, x_reverse__mutmut_mutants, args, kwargs)
    return result 

reverse.__signature__ = _mutmut_signature(x_reverse__mutmut_orig)
x_reverse__mutmut_orig.__name__ = 'x_reverse'


def x_hasindex__mutmut_orig(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_1(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown and key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_2(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(None)
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_3(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(None)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_4(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(True)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_5(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) and key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_6(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_7(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(None)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_8(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(True)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_9(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = None  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_10(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(None)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_11(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(None)  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_12(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(1 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_13(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 < idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_14(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx <= len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_15(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) and key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_16(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_17(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(None)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_18(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(True)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_19(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(None)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_20(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value not in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


def x_hasindex__mutmut_21(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        None
    )

x_hasindex__mutmut_mutants : ClassVar[MutantDict] = {
'x_hasindex__mutmut_1': x_hasindex__mutmut_1, 
    'x_hasindex__mutmut_2': x_hasindex__mutmut_2, 
    'x_hasindex__mutmut_3': x_hasindex__mutmut_3, 
    'x_hasindex__mutmut_4': x_hasindex__mutmut_4, 
    'x_hasindex__mutmut_5': x_hasindex__mutmut_5, 
    'x_hasindex__mutmut_6': x_hasindex__mutmut_6, 
    'x_hasindex__mutmut_7': x_hasindex__mutmut_7, 
    'x_hasindex__mutmut_8': x_hasindex__mutmut_8, 
    'x_hasindex__mutmut_9': x_hasindex__mutmut_9, 
    'x_hasindex__mutmut_10': x_hasindex__mutmut_10, 
    'x_hasindex__mutmut_11': x_hasindex__mutmut_11, 
    'x_hasindex__mutmut_12': x_hasindex__mutmut_12, 
    'x_hasindex__mutmut_13': x_hasindex__mutmut_13, 
    'x_hasindex__mutmut_14': x_hasindex__mutmut_14, 
    'x_hasindex__mutmut_15': x_hasindex__mutmut_15, 
    'x_hasindex__mutmut_16': x_hasindex__mutmut_16, 
    'x_hasindex__mutmut_17': x_hasindex__mutmut_17, 
    'x_hasindex__mutmut_18': x_hasindex__mutmut_18, 
    'x_hasindex__mutmut_19': x_hasindex__mutmut_19, 
    'x_hasindex__mutmut_20': x_hasindex__mutmut_20, 
    'x_hasindex__mutmut_21': x_hasindex__mutmut_21
}

def hasindex(*args, **kwargs):
    result = _mutmut_trampoline(x_hasindex__mutmut_orig, x_hasindex__mutmut_mutants, args, kwargs)
    return result 

hasindex.__signature__ = _mutmut_signature(x_hasindex__mutmut_orig)
x_hasindex__mutmut_orig.__name__ = 'x_hasindex'


def x_index__mutmut_orig(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_1(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if hasindex(collection, key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_2(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(None, key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_3(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, None).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_4(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_5(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, ).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_6(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError(None)

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_7(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError("XXindex: key does not exist in collectionXX")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_8(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError("INDEX: KEY DOES NOT EXIST IN COLLECTION")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_9(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = None
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_10(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = None  # type: ignore[call-overload]

    return collection[key_val]


def x_index__mutmut_11(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(None)  # type: ignore[call-overload]

    return collection[key_val]

x_index__mutmut_mutants : ClassVar[MutantDict] = {
'x_index__mutmut_1': x_index__mutmut_1, 
    'x_index__mutmut_2': x_index__mutmut_2, 
    'x_index__mutmut_3': x_index__mutmut_3, 
    'x_index__mutmut_4': x_index__mutmut_4, 
    'x_index__mutmut_5': x_index__mutmut_5, 
    'x_index__mutmut_6': x_index__mutmut_6, 
    'x_index__mutmut_7': x_index__mutmut_7, 
    'x_index__mutmut_8': x_index__mutmut_8, 
    'x_index__mutmut_9': x_index__mutmut_9, 
    'x_index__mutmut_10': x_index__mutmut_10, 
    'x_index__mutmut_11': x_index__mutmut_11
}

def index(*args, **kwargs):
    result = _mutmut_trampoline(x_index__mutmut_orig, x_index__mutmut_mutants, args, kwargs)
    return result 

index.__signature__ = _mutmut_signature(x_index__mutmut_orig)
x_index__mutmut_orig.__name__ = 'x_index'


def x_element__mutmut_orig(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_1(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context=None
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_2(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "XXoperationXX": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_3(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "OPERATION": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_4(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "XXcty_function_elementXX",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_5(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "CTY_FUNCTION_ELEMENT",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_6(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "XXcollection_typeXX": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_7(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "COLLECTION_TYPE": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_8(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(None),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_9(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "XXindex_typeXX": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_10(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "INDEX_TYPE": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_11(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(None),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_12(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "XXcollection_is_nullXX": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_13(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "COLLECTION_IS_NULL": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_14(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "XXcollection_is_unknownXX": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_15(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "COLLECTION_IS_UNKNOWN": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_16(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_17(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(None)
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_18(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null and idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_19(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown and idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_20(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null and collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_21(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = None
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_22(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(None)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_23(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = None  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_24(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length != 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_25(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 1:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_26(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError(None)
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_27(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("XXelement: cannot use element function with an empty listXX")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_28(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("ELEMENT: CANNOT USE ELEMENT FUNCTION WITH AN EMPTY LIST")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_29(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) / length]  # type: ignore[no-any-return,index,call-overload]


def x_element__mutmut_30(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(None) % length]  # type: ignore[no-any-return,index,call-overload]

x_element__mutmut_mutants : ClassVar[MutantDict] = {
'x_element__mutmut_1': x_element__mutmut_1, 
    'x_element__mutmut_2': x_element__mutmut_2, 
    'x_element__mutmut_3': x_element__mutmut_3, 
    'x_element__mutmut_4': x_element__mutmut_4, 
    'x_element__mutmut_5': x_element__mutmut_5, 
    'x_element__mutmut_6': x_element__mutmut_6, 
    'x_element__mutmut_7': x_element__mutmut_7, 
    'x_element__mutmut_8': x_element__mutmut_8, 
    'x_element__mutmut_9': x_element__mutmut_9, 
    'x_element__mutmut_10': x_element__mutmut_10, 
    'x_element__mutmut_11': x_element__mutmut_11, 
    'x_element__mutmut_12': x_element__mutmut_12, 
    'x_element__mutmut_13': x_element__mutmut_13, 
    'x_element__mutmut_14': x_element__mutmut_14, 
    'x_element__mutmut_15': x_element__mutmut_15, 
    'x_element__mutmut_16': x_element__mutmut_16, 
    'x_element__mutmut_17': x_element__mutmut_17, 
    'x_element__mutmut_18': x_element__mutmut_18, 
    'x_element__mutmut_19': x_element__mutmut_19, 
    'x_element__mutmut_20': x_element__mutmut_20, 
    'x_element__mutmut_21': x_element__mutmut_21, 
    'x_element__mutmut_22': x_element__mutmut_22, 
    'x_element__mutmut_23': x_element__mutmut_23, 
    'x_element__mutmut_24': x_element__mutmut_24, 
    'x_element__mutmut_25': x_element__mutmut_25, 
    'x_element__mutmut_26': x_element__mutmut_26, 
    'x_element__mutmut_27': x_element__mutmut_27, 
    'x_element__mutmut_28': x_element__mutmut_28, 
    'x_element__mutmut_29': x_element__mutmut_29, 
    'x_element__mutmut_30': x_element__mutmut_30
}

def element(*args, **kwargs):
    result = _mutmut_trampoline(x_element__mutmut_orig, x_element__mutmut_mutants, args, kwargs)
    return result 

element.__signature__ = _mutmut_signature(x_element__mutmut_orig)
x_element__mutmut_orig.__name__ = 'x_element'


def x_coalescelist__mutmut_orig(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


def x_coalescelist__mutmut_1(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(None):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


def x_coalescelist__mutmut_2(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(None)
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


def x_coalescelist__mutmut_3(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null or len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


def x_coalescelist__mutmut_4(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) or not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


def x_coalescelist__mutmut_5(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


def x_coalescelist__mutmut_6(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) >= 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


def x_coalescelist__mutmut_7(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 1  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


def x_coalescelist__mutmut_8(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError(None)


def x_coalescelist__mutmut_9(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("XXcoalescelist: no non-empty list or tuple found in argumentsXX")


def x_coalescelist__mutmut_10(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("COALESCELIST: NO NON-EMPTY LIST OR TUPLE FOUND IN ARGUMENTS")

x_coalescelist__mutmut_mutants : ClassVar[MutantDict] = {
'x_coalescelist__mutmut_1': x_coalescelist__mutmut_1, 
    'x_coalescelist__mutmut_2': x_coalescelist__mutmut_2, 
    'x_coalescelist__mutmut_3': x_coalescelist__mutmut_3, 
    'x_coalescelist__mutmut_4': x_coalescelist__mutmut_4, 
    'x_coalescelist__mutmut_5': x_coalescelist__mutmut_5, 
    'x_coalescelist__mutmut_6': x_coalescelist__mutmut_6, 
    'x_coalescelist__mutmut_7': x_coalescelist__mutmut_7, 
    'x_coalescelist__mutmut_8': x_coalescelist__mutmut_8, 
    'x_coalescelist__mutmut_9': x_coalescelist__mutmut_9, 
    'x_coalescelist__mutmut_10': x_coalescelist__mutmut_10
}

def coalescelist(*args, **kwargs):
    result = _mutmut_trampoline(x_coalescelist__mutmut_orig, x_coalescelist__mutmut_mutants, args, kwargs)
    return result 

coalescelist.__signature__ = _mutmut_signature(x_coalescelist__mutmut_orig)
x_coalescelist__mutmut_orig.__name__ = 'x_coalescelist'


def x_compact__mutmut_orig(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_1(collection: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_2(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(None)
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_3(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("XXcompact: argument must be a list, set, or tuple of stringsXX")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_4(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("COMPACT: ARGUMENT MUST BE A LIST, SET, OR TUPLE OF STRINGS")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_5(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_6(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(None):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_7(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError(None)
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_8(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("XXcompact: argument must be a list, set, or tuple of stringsXX")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_9(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("COMPACT: ARGUMENT MUST BE A LIST, SET, OR TUPLE OF STRINGS")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_10(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = None  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_11(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(None, collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_12(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], None)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_13(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_14(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], )  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_15(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] & CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_16(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_17(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError(None)

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_18(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("XXcompact: argument must be a list, set, or tuple of stringsXX")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_19(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("COMPACT: ARGUMENT MUST BE A LIST, SET, OR TUPLE OF STRINGS")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_20(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null and collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_21(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = None
    return result


def x_compact__mutmut_22(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        None  # type: ignore[attr-defined]
    )
    return result


def x_compact__mutmut_23(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=None).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result

x_compact__mutmut_mutants : ClassVar[MutantDict] = {
'x_compact__mutmut_1': x_compact__mutmut_1, 
    'x_compact__mutmut_2': x_compact__mutmut_2, 
    'x_compact__mutmut_3': x_compact__mutmut_3, 
    'x_compact__mutmut_4': x_compact__mutmut_4, 
    'x_compact__mutmut_5': x_compact__mutmut_5, 
    'x_compact__mutmut_6': x_compact__mutmut_6, 
    'x_compact__mutmut_7': x_compact__mutmut_7, 
    'x_compact__mutmut_8': x_compact__mutmut_8, 
    'x_compact__mutmut_9': x_compact__mutmut_9, 
    'x_compact__mutmut_10': x_compact__mutmut_10, 
    'x_compact__mutmut_11': x_compact__mutmut_11, 
    'x_compact__mutmut_12': x_compact__mutmut_12, 
    'x_compact__mutmut_13': x_compact__mutmut_13, 
    'x_compact__mutmut_14': x_compact__mutmut_14, 
    'x_compact__mutmut_15': x_compact__mutmut_15, 
    'x_compact__mutmut_16': x_compact__mutmut_16, 
    'x_compact__mutmut_17': x_compact__mutmut_17, 
    'x_compact__mutmut_18': x_compact__mutmut_18, 
    'x_compact__mutmut_19': x_compact__mutmut_19, 
    'x_compact__mutmut_20': x_compact__mutmut_20, 
    'x_compact__mutmut_21': x_compact__mutmut_21, 
    'x_compact__mutmut_22': x_compact__mutmut_22, 
    'x_compact__mutmut_23': x_compact__mutmut_23
}

def compact(*args, **kwargs):
    result = _mutmut_trampoline(x_compact__mutmut_orig, x_compact__mutmut_mutants, args, kwargs)
    return result 

compact.__signature__ = _mutmut_signature(x_compact__mutmut_orig)
x_compact__mutmut_orig.__name__ = 'x_compact'


def x_chunklist__mutmut_orig(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_1(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) and not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_2(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_3(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_4(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError(None)
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_5(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("XXchunklist: arguments must be a list/tuple and a numberXX")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_6(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("CHUNKLIST: ARGUMENTS MUST BE A LIST/TUPLE AND A NUMBER")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_7(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null and size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_8(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown and size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_9(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null and collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_10(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(None)
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_11(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=None))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_12(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = None  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_13(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(None)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_14(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size < 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_15(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 1:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_16(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError(None)
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_17(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("XXchunklist: size must be a positive numberXX")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_18(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("CHUNKLIST: SIZE MUST BE A POSITIVE NUMBER")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_19(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = None
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_20(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i - chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_21(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(None, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_22(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, None, chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_23(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), None)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_24(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_25(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_26(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), )  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_27(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(1, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_28(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=CtyDynamic())).validate(None)  # type: ignore[no-any-return]


def x_chunklist__mutmut_29(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=None).validate(chunks)  # type: ignore[no-any-return]


def x_chunklist__mutmut_30(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    chunk_size = int(size.value)  # type: ignore[call-overload]
    if chunk_size <= 0:
        raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [
        collection.value[i : i + chunk_size]  # type: ignore[index]
        for i in range(0, len(collection.value), chunk_size)  # type: ignore[arg-type]
    ]
    return CtyList(element_type=CtyList(element_type=None)).validate(chunks)  # type: ignore[no-any-return]

x_chunklist__mutmut_mutants : ClassVar[MutantDict] = {
'x_chunklist__mutmut_1': x_chunklist__mutmut_1, 
    'x_chunklist__mutmut_2': x_chunklist__mutmut_2, 
    'x_chunklist__mutmut_3': x_chunklist__mutmut_3, 
    'x_chunklist__mutmut_4': x_chunklist__mutmut_4, 
    'x_chunklist__mutmut_5': x_chunklist__mutmut_5, 
    'x_chunklist__mutmut_6': x_chunklist__mutmut_6, 
    'x_chunklist__mutmut_7': x_chunklist__mutmut_7, 
    'x_chunklist__mutmut_8': x_chunklist__mutmut_8, 
    'x_chunklist__mutmut_9': x_chunklist__mutmut_9, 
    'x_chunklist__mutmut_10': x_chunklist__mutmut_10, 
    'x_chunklist__mutmut_11': x_chunklist__mutmut_11, 
    'x_chunklist__mutmut_12': x_chunklist__mutmut_12, 
    'x_chunklist__mutmut_13': x_chunklist__mutmut_13, 
    'x_chunklist__mutmut_14': x_chunklist__mutmut_14, 
    'x_chunklist__mutmut_15': x_chunklist__mutmut_15, 
    'x_chunklist__mutmut_16': x_chunklist__mutmut_16, 
    'x_chunklist__mutmut_17': x_chunklist__mutmut_17, 
    'x_chunklist__mutmut_18': x_chunklist__mutmut_18, 
    'x_chunklist__mutmut_19': x_chunklist__mutmut_19, 
    'x_chunklist__mutmut_20': x_chunklist__mutmut_20, 
    'x_chunklist__mutmut_21': x_chunklist__mutmut_21, 
    'x_chunklist__mutmut_22': x_chunklist__mutmut_22, 
    'x_chunklist__mutmut_23': x_chunklist__mutmut_23, 
    'x_chunklist__mutmut_24': x_chunklist__mutmut_24, 
    'x_chunklist__mutmut_25': x_chunklist__mutmut_25, 
    'x_chunklist__mutmut_26': x_chunklist__mutmut_26, 
    'x_chunklist__mutmut_27': x_chunklist__mutmut_27, 
    'x_chunklist__mutmut_28': x_chunklist__mutmut_28, 
    'x_chunklist__mutmut_29': x_chunklist__mutmut_29, 
    'x_chunklist__mutmut_30': x_chunklist__mutmut_30
}

def chunklist(*args, **kwargs):
    result = _mutmut_trampoline(x_chunklist__mutmut_orig, x_chunklist__mutmut_mutants, args, kwargs)
    return result 

chunklist.__signature__ = _mutmut_signature(x_chunklist__mutmut_orig)
x_chunklist__mutmut_orig.__name__ = 'x_chunklist'


def x_lookup__mutmut_orig(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_1(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_2(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError(None)

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_3(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("XXlookup: collection must be a map or objectXX")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_4(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("LOOKUP: COLLECTION MUST BE A MAP OR OBJECT")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_5(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = None

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_6(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown and key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_7(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(None)

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_8(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify(None))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_9(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict) and key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_10(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null and not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_11(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null and key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_12(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def x_lookup__mutmut_13(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]

x_lookup__mutmut_mutants : ClassVar[MutantDict] = {
'x_lookup__mutmut_1': x_lookup__mutmut_1, 
    'x_lookup__mutmut_2': x_lookup__mutmut_2, 
    'x_lookup__mutmut_3': x_lookup__mutmut_3, 
    'x_lookup__mutmut_4': x_lookup__mutmut_4, 
    'x_lookup__mutmut_5': x_lookup__mutmut_5, 
    'x_lookup__mutmut_6': x_lookup__mutmut_6, 
    'x_lookup__mutmut_7': x_lookup__mutmut_7, 
    'x_lookup__mutmut_8': x_lookup__mutmut_8, 
    'x_lookup__mutmut_9': x_lookup__mutmut_9, 
    'x_lookup__mutmut_10': x_lookup__mutmut_10, 
    'x_lookup__mutmut_11': x_lookup__mutmut_11, 
    'x_lookup__mutmut_12': x_lookup__mutmut_12, 
    'x_lookup__mutmut_13': x_lookup__mutmut_13
}

def lookup(*args, **kwargs):
    result = _mutmut_trampoline(x_lookup__mutmut_orig, x_lookup__mutmut_mutants, args, kwargs)
    return result 

lookup.__signature__ = _mutmut_signature(x_lookup__mutmut_orig)
x_lookup__mutmut_orig.__name__ = 'x_lookup'


def x_merge__mutmut_orig(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_1(*args: CtyValue[Any]) -> CtyValue[Any]:
    if all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_2(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(None):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_3(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError(None)
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_4(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("XXmerge: all arguments must be maps or objectsXX")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_5(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("MERGE: ALL ARGUMENTS MUST BE MAPS OR OBJECTS")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_6(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(None):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_7(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(None)
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_8(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = None
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_9(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_10(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(None)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


def x_merge__mutmut_11(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = None
    return inferred_type.validate(result)


def x_merge__mutmut_12(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(None)
    return inferred_type.validate(result)


def x_merge__mutmut_13(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(None)

x_merge__mutmut_mutants : ClassVar[MutantDict] = {
'x_merge__mutmut_1': x_merge__mutmut_1, 
    'x_merge__mutmut_2': x_merge__mutmut_2, 
    'x_merge__mutmut_3': x_merge__mutmut_3, 
    'x_merge__mutmut_4': x_merge__mutmut_4, 
    'x_merge__mutmut_5': x_merge__mutmut_5, 
    'x_merge__mutmut_6': x_merge__mutmut_6, 
    'x_merge__mutmut_7': x_merge__mutmut_7, 
    'x_merge__mutmut_8': x_merge__mutmut_8, 
    'x_merge__mutmut_9': x_merge__mutmut_9, 
    'x_merge__mutmut_10': x_merge__mutmut_10, 
    'x_merge__mutmut_11': x_merge__mutmut_11, 
    'x_merge__mutmut_12': x_merge__mutmut_12, 
    'x_merge__mutmut_13': x_merge__mutmut_13
}

def merge(*args, **kwargs):
    result = _mutmut_trampoline(x_merge__mutmut_orig, x_merge__mutmut_mutants, args, kwargs)
    return result 

merge.__signature__ = _mutmut_signature(x_merge__mutmut_orig)
x_merge__mutmut_orig.__name__ = 'x_merge'


def x_setproduct__mutmut_orig(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_1(*args: CtyValue[Any]) -> CtyValue[Any]:
    if all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_2(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(None):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_3(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError(None)
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_4(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("XXsetproduct: all arguments must be collectionsXX")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_5(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("SETPRODUCT: ALL ARGUMENTS MUST BE COLLECTIONS")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_6(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(None):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_7(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(None)

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_8(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=None))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_9(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = None  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_10(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(None) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_11(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_12(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_13(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate(None)  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_14(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=None).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_15(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = None
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_16(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = None

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_17(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(None) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_18(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = None
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_19(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_20(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = None  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_21(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(None, arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_22(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], None)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_23(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_24(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], )  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_25(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] & CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_26(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(None)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_27(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(None)
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_28(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = None

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_29(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=None)

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_30(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(None))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


def x_setproduct__mutmut_31(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(None)  # type: ignore[no-any-return]


def x_setproduct__mutmut_32(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=None).validate(result_tuples)  # type: ignore[no-any-return]

x_setproduct__mutmut_mutants : ClassVar[MutantDict] = {
'x_setproduct__mutmut_1': x_setproduct__mutmut_1, 
    'x_setproduct__mutmut_2': x_setproduct__mutmut_2, 
    'x_setproduct__mutmut_3': x_setproduct__mutmut_3, 
    'x_setproduct__mutmut_4': x_setproduct__mutmut_4, 
    'x_setproduct__mutmut_5': x_setproduct__mutmut_5, 
    'x_setproduct__mutmut_6': x_setproduct__mutmut_6, 
    'x_setproduct__mutmut_7': x_setproduct__mutmut_7, 
    'x_setproduct__mutmut_8': x_setproduct__mutmut_8, 
    'x_setproduct__mutmut_9': x_setproduct__mutmut_9, 
    'x_setproduct__mutmut_10': x_setproduct__mutmut_10, 
    'x_setproduct__mutmut_11': x_setproduct__mutmut_11, 
    'x_setproduct__mutmut_12': x_setproduct__mutmut_12, 
    'x_setproduct__mutmut_13': x_setproduct__mutmut_13, 
    'x_setproduct__mutmut_14': x_setproduct__mutmut_14, 
    'x_setproduct__mutmut_15': x_setproduct__mutmut_15, 
    'x_setproduct__mutmut_16': x_setproduct__mutmut_16, 
    'x_setproduct__mutmut_17': x_setproduct__mutmut_17, 
    'x_setproduct__mutmut_18': x_setproduct__mutmut_18, 
    'x_setproduct__mutmut_19': x_setproduct__mutmut_19, 
    'x_setproduct__mutmut_20': x_setproduct__mutmut_20, 
    'x_setproduct__mutmut_21': x_setproduct__mutmut_21, 
    'x_setproduct__mutmut_22': x_setproduct__mutmut_22, 
    'x_setproduct__mutmut_23': x_setproduct__mutmut_23, 
    'x_setproduct__mutmut_24': x_setproduct__mutmut_24, 
    'x_setproduct__mutmut_25': x_setproduct__mutmut_25, 
    'x_setproduct__mutmut_26': x_setproduct__mutmut_26, 
    'x_setproduct__mutmut_27': x_setproduct__mutmut_27, 
    'x_setproduct__mutmut_28': x_setproduct__mutmut_28, 
    'x_setproduct__mutmut_29': x_setproduct__mutmut_29, 
    'x_setproduct__mutmut_30': x_setproduct__mutmut_30, 
    'x_setproduct__mutmut_31': x_setproduct__mutmut_31, 
    'x_setproduct__mutmut_32': x_setproduct__mutmut_32
}

def setproduct(*args, **kwargs):
    result = _mutmut_trampoline(x_setproduct__mutmut_orig, x_setproduct__mutmut_mutants, args, kwargs)
    return result 

setproduct.__signature__ = _mutmut_signature(x_setproduct__mutmut_orig)
x_setproduct__mutmut_orig.__name__ = 'x_setproduct'


def x_zipmap__mutmut_orig(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_1(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) and not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_2(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_3(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_4(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError(None)
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_5(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("XXzipmap: arguments must be lists or tuplesXX")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_6(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("ZIPMAP: ARGUMENTS MUST BE LISTS OR TUPLES")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_7(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown and values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_8(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(None)
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_9(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=None))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_10(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null and values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_11(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate(None)  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_12(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=None).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_13(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = None  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_14(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = None  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_15(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(None)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_16(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = None

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_17(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(None)}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_18(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(None, len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_19(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), None))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_20(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_21(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), ))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_22(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = None
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


def x_zipmap__mutmut_23(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(None)  # type: ignore[no-any-return]


def x_zipmap__mutmut_24(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=None).validate(result_map)  # type: ignore[no-any-return]

x_zipmap__mutmut_mutants : ClassVar[MutantDict] = {
'x_zipmap__mutmut_1': x_zipmap__mutmut_1, 
    'x_zipmap__mutmut_2': x_zipmap__mutmut_2, 
    'x_zipmap__mutmut_3': x_zipmap__mutmut_3, 
    'x_zipmap__mutmut_4': x_zipmap__mutmut_4, 
    'x_zipmap__mutmut_5': x_zipmap__mutmut_5, 
    'x_zipmap__mutmut_6': x_zipmap__mutmut_6, 
    'x_zipmap__mutmut_7': x_zipmap__mutmut_7, 
    'x_zipmap__mutmut_8': x_zipmap__mutmut_8, 
    'x_zipmap__mutmut_9': x_zipmap__mutmut_9, 
    'x_zipmap__mutmut_10': x_zipmap__mutmut_10, 
    'x_zipmap__mutmut_11': x_zipmap__mutmut_11, 
    'x_zipmap__mutmut_12': x_zipmap__mutmut_12, 
    'x_zipmap__mutmut_13': x_zipmap__mutmut_13, 
    'x_zipmap__mutmut_14': x_zipmap__mutmut_14, 
    'x_zipmap__mutmut_15': x_zipmap__mutmut_15, 
    'x_zipmap__mutmut_16': x_zipmap__mutmut_16, 
    'x_zipmap__mutmut_17': x_zipmap__mutmut_17, 
    'x_zipmap__mutmut_18': x_zipmap__mutmut_18, 
    'x_zipmap__mutmut_19': x_zipmap__mutmut_19, 
    'x_zipmap__mutmut_20': x_zipmap__mutmut_20, 
    'x_zipmap__mutmut_21': x_zipmap__mutmut_21, 
    'x_zipmap__mutmut_22': x_zipmap__mutmut_22, 
    'x_zipmap__mutmut_23': x_zipmap__mutmut_23, 
    'x_zipmap__mutmut_24': x_zipmap__mutmut_24
}

def zipmap(*args, **kwargs):
    result = _mutmut_trampoline(x_zipmap__mutmut_orig, x_zipmap__mutmut_mutants, args, kwargs)
    return result 

zipmap.__signature__ = _mutmut_signature(x_zipmap__mutmut_orig)
x_zipmap__mutmut_orig.__name__ = 'x_zipmap'


# 🌊🪢🔣🪄
