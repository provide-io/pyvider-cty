# pyvider/cty/conversion/adapter.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from pyvider.cty.types import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyTuple,
)

# Local imports to break the circular dependency cycle.
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


def x_cty_to_native__mutmut_orig(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_1(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_2(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = None
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_3(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = None
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_4(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = None
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_5(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = None

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_6(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = None

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_7(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is not POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_8(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = None
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_9(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = None
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_10(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(None)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_11(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(None)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_12(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_13(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(None, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_14(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, None):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_15(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr("__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_16(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, ):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_17(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "XX__iter__XX"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_18(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__ITER__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_19(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = None
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_20(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = None
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_21(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = None
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_22(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                break

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_23(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = None
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_24(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(None)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_25(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = None
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_26(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = None
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_27(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(None, val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_28(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], None)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_29(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_30(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], )
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_31(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = None
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_32(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(None)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_33(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = None
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_34(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(None, val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_35(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], None)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_36(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_37(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], )
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_38(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = None
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_39(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(None)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_40(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = None
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_41(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(None, val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_42(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], None)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_43(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_44(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], )
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_45(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = None
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_46(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    None,
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_47(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=None,
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_48(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_49(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_50(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(None)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_51(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: None,
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_52(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(None),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_53(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = None
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_54(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(None, val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_55(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], None)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_56(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_57(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], )
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_58(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = None
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_59(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(None)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_60(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(None)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_61(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            break

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_62(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_63(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = None
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_64(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(None)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_65(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            break

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_66(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = ""
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_67(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(None)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_68(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            break
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_69(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = ""
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_70(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(None)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_71(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            break

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_72(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = None
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_73(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(None)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_74(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results and item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_75(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id not in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_76(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id not in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_77(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            break

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_78(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(None)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_79(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend(None)

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_80(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(None)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_81(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(None, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_82(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, None):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_83(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr("__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_84(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, ):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_85(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "XX__iter__XX"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_86(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__ITER__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_87(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = None
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_88(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(None, current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_89(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], None)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_90(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_91(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], )
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_92(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = None
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_93(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(None)
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_94(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = None
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_95(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(None, current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_96(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], None)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_97(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_98(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], )
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_99(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] & tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_100(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] & set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_101(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = None
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_102(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(None)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_103(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(None)
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_104(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(None))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_105(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = None
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_106(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = None
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_107(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) or exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_108(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent > 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_109(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 1:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_110(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = None
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_111(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(None)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_112(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = None
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_113(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(None)
            else:
                results[item_id] = inner_val

    return results.get(id(value))


def x_cty_to_native__mutmut_114(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = None

    return results.get(id(value))


def x_cty_to_native__mutmut_115(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(None)


def x_cty_to_native__mutmut_116(value: CtyValue[Any] | Any) -> Any:  # noqa: C901
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

    if value.is_unknown:
        return None  # Gracefully handle unknown values by returning None.

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, Any] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            val_to_process = work_stack.pop()
            val_id = id(val_to_process)
            processing.remove(val_id)

            # Robustness check for malformed collection values
            if not hasattr(val_to_process.value, "__iter__"):
                if isinstance(val_to_process.type, CtyList | CtySet):
                    results[val_id] = []
                elif isinstance(val_to_process.type, CtyTuple):
                    results[val_id] = ()
                elif isinstance(val_to_process.type, CtyMap | CtyObject):
                    results[val_id] = {}
                continue

            if isinstance(val_to_process.type, CtyDynamic):
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, CtyObject | CtyMap):
                dict_val = cast(dict[str, Any], val_to_process.value)
                results[val_id] = {k: results[id(v)] for k, v in dict_val.items()}
            elif isinstance(val_to_process.type, CtyList):
                list_val = cast(list[Any], val_to_process.value)
                results[val_id] = [results[id(item)] for item in list_val]
            elif isinstance(val_to_process.type, CtySet):
                # Use _canonical_sort_key for consistent sorting of set elements
                set_val = cast(set[Any], val_to_process.value)
                results[val_id] = sorted(
                    [results[id(item)] for item in set_val],
                    key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
                )
            elif isinstance(val_to_process.type, CtyTuple):
                tuple_val = cast(tuple[Any, ...], val_to_process.value)
                results[val_id] = tuple(results[id(item)] for item in tuple_val)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            results[id(current_item)] = None
            continue
        if current_item.is_null:
            results[id(current_item)] = None
            continue

        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        if isinstance(
            current_item.type,
            CtyObject | CtyMap | CtyList | CtySet | CtyTuple | CtyDynamic,
        ):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS])

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value)
            elif hasattr(current_item.value, "__iter__"):  # Robustness check
                if isinstance(current_item.value, dict):
                    dict_val = cast(dict[str, Any], current_item.value)
                    child_values = list(dict_val.values())
                else:
                    iterable_val = cast(list[Any] | set[Any] | tuple[Any, ...], current_item.value)
                    child_values = list(iterable_val)
                work_stack.extend(reversed(child_values))
        else:
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                exponent = inner_val.as_tuple().exponent
                if isinstance(exponent, int) and exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(None))

x_cty_to_native__mutmut_mutants : ClassVar[MutantDict] = {
'x_cty_to_native__mutmut_1': x_cty_to_native__mutmut_1, 
    'x_cty_to_native__mutmut_2': x_cty_to_native__mutmut_2, 
    'x_cty_to_native__mutmut_3': x_cty_to_native__mutmut_3, 
    'x_cty_to_native__mutmut_4': x_cty_to_native__mutmut_4, 
    'x_cty_to_native__mutmut_5': x_cty_to_native__mutmut_5, 
    'x_cty_to_native__mutmut_6': x_cty_to_native__mutmut_6, 
    'x_cty_to_native__mutmut_7': x_cty_to_native__mutmut_7, 
    'x_cty_to_native__mutmut_8': x_cty_to_native__mutmut_8, 
    'x_cty_to_native__mutmut_9': x_cty_to_native__mutmut_9, 
    'x_cty_to_native__mutmut_10': x_cty_to_native__mutmut_10, 
    'x_cty_to_native__mutmut_11': x_cty_to_native__mutmut_11, 
    'x_cty_to_native__mutmut_12': x_cty_to_native__mutmut_12, 
    'x_cty_to_native__mutmut_13': x_cty_to_native__mutmut_13, 
    'x_cty_to_native__mutmut_14': x_cty_to_native__mutmut_14, 
    'x_cty_to_native__mutmut_15': x_cty_to_native__mutmut_15, 
    'x_cty_to_native__mutmut_16': x_cty_to_native__mutmut_16, 
    'x_cty_to_native__mutmut_17': x_cty_to_native__mutmut_17, 
    'x_cty_to_native__mutmut_18': x_cty_to_native__mutmut_18, 
    'x_cty_to_native__mutmut_19': x_cty_to_native__mutmut_19, 
    'x_cty_to_native__mutmut_20': x_cty_to_native__mutmut_20, 
    'x_cty_to_native__mutmut_21': x_cty_to_native__mutmut_21, 
    'x_cty_to_native__mutmut_22': x_cty_to_native__mutmut_22, 
    'x_cty_to_native__mutmut_23': x_cty_to_native__mutmut_23, 
    'x_cty_to_native__mutmut_24': x_cty_to_native__mutmut_24, 
    'x_cty_to_native__mutmut_25': x_cty_to_native__mutmut_25, 
    'x_cty_to_native__mutmut_26': x_cty_to_native__mutmut_26, 
    'x_cty_to_native__mutmut_27': x_cty_to_native__mutmut_27, 
    'x_cty_to_native__mutmut_28': x_cty_to_native__mutmut_28, 
    'x_cty_to_native__mutmut_29': x_cty_to_native__mutmut_29, 
    'x_cty_to_native__mutmut_30': x_cty_to_native__mutmut_30, 
    'x_cty_to_native__mutmut_31': x_cty_to_native__mutmut_31, 
    'x_cty_to_native__mutmut_32': x_cty_to_native__mutmut_32, 
    'x_cty_to_native__mutmut_33': x_cty_to_native__mutmut_33, 
    'x_cty_to_native__mutmut_34': x_cty_to_native__mutmut_34, 
    'x_cty_to_native__mutmut_35': x_cty_to_native__mutmut_35, 
    'x_cty_to_native__mutmut_36': x_cty_to_native__mutmut_36, 
    'x_cty_to_native__mutmut_37': x_cty_to_native__mutmut_37, 
    'x_cty_to_native__mutmut_38': x_cty_to_native__mutmut_38, 
    'x_cty_to_native__mutmut_39': x_cty_to_native__mutmut_39, 
    'x_cty_to_native__mutmut_40': x_cty_to_native__mutmut_40, 
    'x_cty_to_native__mutmut_41': x_cty_to_native__mutmut_41, 
    'x_cty_to_native__mutmut_42': x_cty_to_native__mutmut_42, 
    'x_cty_to_native__mutmut_43': x_cty_to_native__mutmut_43, 
    'x_cty_to_native__mutmut_44': x_cty_to_native__mutmut_44, 
    'x_cty_to_native__mutmut_45': x_cty_to_native__mutmut_45, 
    'x_cty_to_native__mutmut_46': x_cty_to_native__mutmut_46, 
    'x_cty_to_native__mutmut_47': x_cty_to_native__mutmut_47, 
    'x_cty_to_native__mutmut_48': x_cty_to_native__mutmut_48, 
    'x_cty_to_native__mutmut_49': x_cty_to_native__mutmut_49, 
    'x_cty_to_native__mutmut_50': x_cty_to_native__mutmut_50, 
    'x_cty_to_native__mutmut_51': x_cty_to_native__mutmut_51, 
    'x_cty_to_native__mutmut_52': x_cty_to_native__mutmut_52, 
    'x_cty_to_native__mutmut_53': x_cty_to_native__mutmut_53, 
    'x_cty_to_native__mutmut_54': x_cty_to_native__mutmut_54, 
    'x_cty_to_native__mutmut_55': x_cty_to_native__mutmut_55, 
    'x_cty_to_native__mutmut_56': x_cty_to_native__mutmut_56, 
    'x_cty_to_native__mutmut_57': x_cty_to_native__mutmut_57, 
    'x_cty_to_native__mutmut_58': x_cty_to_native__mutmut_58, 
    'x_cty_to_native__mutmut_59': x_cty_to_native__mutmut_59, 
    'x_cty_to_native__mutmut_60': x_cty_to_native__mutmut_60, 
    'x_cty_to_native__mutmut_61': x_cty_to_native__mutmut_61, 
    'x_cty_to_native__mutmut_62': x_cty_to_native__mutmut_62, 
    'x_cty_to_native__mutmut_63': x_cty_to_native__mutmut_63, 
    'x_cty_to_native__mutmut_64': x_cty_to_native__mutmut_64, 
    'x_cty_to_native__mutmut_65': x_cty_to_native__mutmut_65, 
    'x_cty_to_native__mutmut_66': x_cty_to_native__mutmut_66, 
    'x_cty_to_native__mutmut_67': x_cty_to_native__mutmut_67, 
    'x_cty_to_native__mutmut_68': x_cty_to_native__mutmut_68, 
    'x_cty_to_native__mutmut_69': x_cty_to_native__mutmut_69, 
    'x_cty_to_native__mutmut_70': x_cty_to_native__mutmut_70, 
    'x_cty_to_native__mutmut_71': x_cty_to_native__mutmut_71, 
    'x_cty_to_native__mutmut_72': x_cty_to_native__mutmut_72, 
    'x_cty_to_native__mutmut_73': x_cty_to_native__mutmut_73, 
    'x_cty_to_native__mutmut_74': x_cty_to_native__mutmut_74, 
    'x_cty_to_native__mutmut_75': x_cty_to_native__mutmut_75, 
    'x_cty_to_native__mutmut_76': x_cty_to_native__mutmut_76, 
    'x_cty_to_native__mutmut_77': x_cty_to_native__mutmut_77, 
    'x_cty_to_native__mutmut_78': x_cty_to_native__mutmut_78, 
    'x_cty_to_native__mutmut_79': x_cty_to_native__mutmut_79, 
    'x_cty_to_native__mutmut_80': x_cty_to_native__mutmut_80, 
    'x_cty_to_native__mutmut_81': x_cty_to_native__mutmut_81, 
    'x_cty_to_native__mutmut_82': x_cty_to_native__mutmut_82, 
    'x_cty_to_native__mutmut_83': x_cty_to_native__mutmut_83, 
    'x_cty_to_native__mutmut_84': x_cty_to_native__mutmut_84, 
    'x_cty_to_native__mutmut_85': x_cty_to_native__mutmut_85, 
    'x_cty_to_native__mutmut_86': x_cty_to_native__mutmut_86, 
    'x_cty_to_native__mutmut_87': x_cty_to_native__mutmut_87, 
    'x_cty_to_native__mutmut_88': x_cty_to_native__mutmut_88, 
    'x_cty_to_native__mutmut_89': x_cty_to_native__mutmut_89, 
    'x_cty_to_native__mutmut_90': x_cty_to_native__mutmut_90, 
    'x_cty_to_native__mutmut_91': x_cty_to_native__mutmut_91, 
    'x_cty_to_native__mutmut_92': x_cty_to_native__mutmut_92, 
    'x_cty_to_native__mutmut_93': x_cty_to_native__mutmut_93, 
    'x_cty_to_native__mutmut_94': x_cty_to_native__mutmut_94, 
    'x_cty_to_native__mutmut_95': x_cty_to_native__mutmut_95, 
    'x_cty_to_native__mutmut_96': x_cty_to_native__mutmut_96, 
    'x_cty_to_native__mutmut_97': x_cty_to_native__mutmut_97, 
    'x_cty_to_native__mutmut_98': x_cty_to_native__mutmut_98, 
    'x_cty_to_native__mutmut_99': x_cty_to_native__mutmut_99, 
    'x_cty_to_native__mutmut_100': x_cty_to_native__mutmut_100, 
    'x_cty_to_native__mutmut_101': x_cty_to_native__mutmut_101, 
    'x_cty_to_native__mutmut_102': x_cty_to_native__mutmut_102, 
    'x_cty_to_native__mutmut_103': x_cty_to_native__mutmut_103, 
    'x_cty_to_native__mutmut_104': x_cty_to_native__mutmut_104, 
    'x_cty_to_native__mutmut_105': x_cty_to_native__mutmut_105, 
    'x_cty_to_native__mutmut_106': x_cty_to_native__mutmut_106, 
    'x_cty_to_native__mutmut_107': x_cty_to_native__mutmut_107, 
    'x_cty_to_native__mutmut_108': x_cty_to_native__mutmut_108, 
    'x_cty_to_native__mutmut_109': x_cty_to_native__mutmut_109, 
    'x_cty_to_native__mutmut_110': x_cty_to_native__mutmut_110, 
    'x_cty_to_native__mutmut_111': x_cty_to_native__mutmut_111, 
    'x_cty_to_native__mutmut_112': x_cty_to_native__mutmut_112, 
    'x_cty_to_native__mutmut_113': x_cty_to_native__mutmut_113, 
    'x_cty_to_native__mutmut_114': x_cty_to_native__mutmut_114, 
    'x_cty_to_native__mutmut_115': x_cty_to_native__mutmut_115, 
    'x_cty_to_native__mutmut_116': x_cty_to_native__mutmut_116
}

def cty_to_native(*args, **kwargs):
    result = _mutmut_trampoline(x_cty_to_native__mutmut_orig, x_cty_to_native__mutmut_mutants, args, kwargs)
    return result 

cty_to_native.__signature__ = _mutmut_signature(x_cty_to_native__mutmut_orig)
x_cty_to_native__mutmut_orig.__name__ = 'x_cty_to_native'


# 🌊🪢↔️🪄
