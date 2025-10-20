# pyvider/cty/conversion/raw_to_cty.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from decimal import Decimal
from typing import Any

# pyvider-cty/src/pyvider/cty/conversion/raw_to_cty.py
import unicodedata

import attrs
from provide.foundation.errors import error_boundary

from pyvider.cty.conversion._utils import _attrs_to_dict_safe
from pyvider.cty.conversion.inference_cache import (
    get_container_schema_cache,
    get_structural_key_cache,
    with_inference_cache,
)
from pyvider.cty.types import CtyType
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


def x__extract_container_children__mutmut_orig(container: Any) -> list[Any]:
    """Extract child elements from a container for cache key generation."""
    children: list[Any] = []
    if isinstance(container, dict):
        children.extend(container.values())
    elif isinstance(container, list | tuple | set | frozenset):
        children.extend(container)
    return children


def x__extract_container_children__mutmut_1(container: Any) -> list[Any]:
    """Extract child elements from a container for cache key generation."""
    children: list[Any] = None
    if isinstance(container, dict):
        children.extend(container.values())
    elif isinstance(container, list | tuple | set | frozenset):
        children.extend(container)
    return children


def x__extract_container_children__mutmut_2(container: Any) -> list[Any]:
    """Extract child elements from a container for cache key generation."""
    children: list[Any] = []
    if isinstance(container, dict):
        children.extend(None)
    elif isinstance(container, list | tuple | set | frozenset):
        children.extend(container)
    return children


def x__extract_container_children__mutmut_3(container: Any) -> list[Any]:
    """Extract child elements from a container for cache key generation."""
    children: list[Any] = []
    if isinstance(container, dict):
        children.extend(container.values())
    elif isinstance(container, list | tuple | set | frozenset):
        children.extend(None)
    return children

x__extract_container_children__mutmut_mutants : ClassVar[MutantDict] = {
'x__extract_container_children__mutmut_1': x__extract_container_children__mutmut_1, 
    'x__extract_container_children__mutmut_2': x__extract_container_children__mutmut_2, 
    'x__extract_container_children__mutmut_3': x__extract_container_children__mutmut_3
}

def _extract_container_children(*args, **kwargs):
    result = _mutmut_trampoline(x__extract_container_children__mutmut_orig, x__extract_container_children__mutmut_mutants, args, kwargs)
    return result 

_extract_container_children.__signature__ = _mutmut_signature(x__extract_container_children__mutmut_orig)
x__extract_container_children__mutmut_orig.__name__ = 'x__extract_container_children'


def x__generate_container_cache_key__mutmut_orig(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_1(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 or all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_2(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) < 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_3(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 6 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_4(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            None
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_5(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = None
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_6(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(None, key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_7(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=None)
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_8(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_9(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), )
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_10(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: None)
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_11(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(None))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_12(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[1]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_13(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset(None))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_14(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = None
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_15(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(None, key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_16(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=None)
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_17(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_18(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), )
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_19(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: None)
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_20(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(None))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_21(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[1]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_22(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset(None),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_23(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(None)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_24(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 or all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_25(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) < 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_26(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 101 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_27(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            None
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_28(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(None))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_29(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(None))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_30(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(None)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_31(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 or all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_32(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) < 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_33(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 101 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_34(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            None
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_35(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(None))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_36(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(None)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_37(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 or all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_38(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) < 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_39(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 101 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_40(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            None
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_41(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = None
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_42(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(None, key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_43(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=None)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_44(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_45(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), )
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_46(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(None), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_47(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(None))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_48(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = None
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_49(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(None, key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_50(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=None)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_51(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_52(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), )
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_53(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(None), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_54(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(None))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_55(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(None)] for v in sorted_items))
    else:
        return (type(container),)


def x__generate_container_cache_key__mutmut_56(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    if isinstance(container, dict):
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container.values()
        ):
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            return (dict, frozenset((k, v) for k, v in sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        # Increased threshold to handle test cases with larger datasets
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(
            isinstance(v, (bool, int, float, str, bytes, type(None))) for v in container
        ):
            sorted_items = sorted(list(container), key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(list(container), key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(None),)

x__generate_container_cache_key__mutmut_mutants : ClassVar[MutantDict] = {
'x__generate_container_cache_key__mutmut_1': x__generate_container_cache_key__mutmut_1, 
    'x__generate_container_cache_key__mutmut_2': x__generate_container_cache_key__mutmut_2, 
    'x__generate_container_cache_key__mutmut_3': x__generate_container_cache_key__mutmut_3, 
    'x__generate_container_cache_key__mutmut_4': x__generate_container_cache_key__mutmut_4, 
    'x__generate_container_cache_key__mutmut_5': x__generate_container_cache_key__mutmut_5, 
    'x__generate_container_cache_key__mutmut_6': x__generate_container_cache_key__mutmut_6, 
    'x__generate_container_cache_key__mutmut_7': x__generate_container_cache_key__mutmut_7, 
    'x__generate_container_cache_key__mutmut_8': x__generate_container_cache_key__mutmut_8, 
    'x__generate_container_cache_key__mutmut_9': x__generate_container_cache_key__mutmut_9, 
    'x__generate_container_cache_key__mutmut_10': x__generate_container_cache_key__mutmut_10, 
    'x__generate_container_cache_key__mutmut_11': x__generate_container_cache_key__mutmut_11, 
    'x__generate_container_cache_key__mutmut_12': x__generate_container_cache_key__mutmut_12, 
    'x__generate_container_cache_key__mutmut_13': x__generate_container_cache_key__mutmut_13, 
    'x__generate_container_cache_key__mutmut_14': x__generate_container_cache_key__mutmut_14, 
    'x__generate_container_cache_key__mutmut_15': x__generate_container_cache_key__mutmut_15, 
    'x__generate_container_cache_key__mutmut_16': x__generate_container_cache_key__mutmut_16, 
    'x__generate_container_cache_key__mutmut_17': x__generate_container_cache_key__mutmut_17, 
    'x__generate_container_cache_key__mutmut_18': x__generate_container_cache_key__mutmut_18, 
    'x__generate_container_cache_key__mutmut_19': x__generate_container_cache_key__mutmut_19, 
    'x__generate_container_cache_key__mutmut_20': x__generate_container_cache_key__mutmut_20, 
    'x__generate_container_cache_key__mutmut_21': x__generate_container_cache_key__mutmut_21, 
    'x__generate_container_cache_key__mutmut_22': x__generate_container_cache_key__mutmut_22, 
    'x__generate_container_cache_key__mutmut_23': x__generate_container_cache_key__mutmut_23, 
    'x__generate_container_cache_key__mutmut_24': x__generate_container_cache_key__mutmut_24, 
    'x__generate_container_cache_key__mutmut_25': x__generate_container_cache_key__mutmut_25, 
    'x__generate_container_cache_key__mutmut_26': x__generate_container_cache_key__mutmut_26, 
    'x__generate_container_cache_key__mutmut_27': x__generate_container_cache_key__mutmut_27, 
    'x__generate_container_cache_key__mutmut_28': x__generate_container_cache_key__mutmut_28, 
    'x__generate_container_cache_key__mutmut_29': x__generate_container_cache_key__mutmut_29, 
    'x__generate_container_cache_key__mutmut_30': x__generate_container_cache_key__mutmut_30, 
    'x__generate_container_cache_key__mutmut_31': x__generate_container_cache_key__mutmut_31, 
    'x__generate_container_cache_key__mutmut_32': x__generate_container_cache_key__mutmut_32, 
    'x__generate_container_cache_key__mutmut_33': x__generate_container_cache_key__mutmut_33, 
    'x__generate_container_cache_key__mutmut_34': x__generate_container_cache_key__mutmut_34, 
    'x__generate_container_cache_key__mutmut_35': x__generate_container_cache_key__mutmut_35, 
    'x__generate_container_cache_key__mutmut_36': x__generate_container_cache_key__mutmut_36, 
    'x__generate_container_cache_key__mutmut_37': x__generate_container_cache_key__mutmut_37, 
    'x__generate_container_cache_key__mutmut_38': x__generate_container_cache_key__mutmut_38, 
    'x__generate_container_cache_key__mutmut_39': x__generate_container_cache_key__mutmut_39, 
    'x__generate_container_cache_key__mutmut_40': x__generate_container_cache_key__mutmut_40, 
    'x__generate_container_cache_key__mutmut_41': x__generate_container_cache_key__mutmut_41, 
    'x__generate_container_cache_key__mutmut_42': x__generate_container_cache_key__mutmut_42, 
    'x__generate_container_cache_key__mutmut_43': x__generate_container_cache_key__mutmut_43, 
    'x__generate_container_cache_key__mutmut_44': x__generate_container_cache_key__mutmut_44, 
    'x__generate_container_cache_key__mutmut_45': x__generate_container_cache_key__mutmut_45, 
    'x__generate_container_cache_key__mutmut_46': x__generate_container_cache_key__mutmut_46, 
    'x__generate_container_cache_key__mutmut_47': x__generate_container_cache_key__mutmut_47, 
    'x__generate_container_cache_key__mutmut_48': x__generate_container_cache_key__mutmut_48, 
    'x__generate_container_cache_key__mutmut_49': x__generate_container_cache_key__mutmut_49, 
    'x__generate_container_cache_key__mutmut_50': x__generate_container_cache_key__mutmut_50, 
    'x__generate_container_cache_key__mutmut_51': x__generate_container_cache_key__mutmut_51, 
    'x__generate_container_cache_key__mutmut_52': x__generate_container_cache_key__mutmut_52, 
    'x__generate_container_cache_key__mutmut_53': x__generate_container_cache_key__mutmut_53, 
    'x__generate_container_cache_key__mutmut_54': x__generate_container_cache_key__mutmut_54, 
    'x__generate_container_cache_key__mutmut_55': x__generate_container_cache_key__mutmut_55, 
    'x__generate_container_cache_key__mutmut_56': x__generate_container_cache_key__mutmut_56
}

def _generate_container_cache_key(*args, **kwargs):
    result = _mutmut_trampoline(x__generate_container_cache_key__mutmut_orig, x__generate_container_cache_key__mutmut_mutants, args, kwargs)
    return result 

_generate_container_cache_key.__signature__ = _mutmut_signature(x__generate_container_cache_key__mutmut_orig)
x__generate_container_cache_key__mutmut_orig.__name__ = 'x__generate_container_cache_key'


def x__process_container_children__mutmut_orig(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_1(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = None

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_2(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(None)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_3(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id not in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_4(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(None)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_5(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = None
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_6(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(None), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_7(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "XXplaceholderXX")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_8(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "PLACEHOLDER")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_9(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(None)

    children = _extract_container_children(current_item)
    work_stack.extend(children)


def x__process_container_children__mutmut_10(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = None
    work_stack.extend(children)


def x__process_container_children__mutmut_11(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = _extract_container_children(None)
    work_stack.extend(children)


def x__process_container_children__mutmut_12(
    current_item: Any,
    work_stack: list[Any],
    post_process_stack: list[Any],
    structural_cache: dict[int, tuple[Any, ...]],
    visited_ids: set[int],
) -> None:
    """Process a container item and add its children to the work stack."""
    item_id = id(current_item)

    if item_id in visited_ids:
        return

    visited_ids.add(item_id)

    # Placeholder is essential for cycle detection.
    structural_cache[item_id] = (type(current_item), item_id, "placeholder")
    post_process_stack.append(current_item)

    children = _extract_container_children(current_item)
    work_stack.extend(None)

x__process_container_children__mutmut_mutants : ClassVar[MutantDict] = {
'x__process_container_children__mutmut_1': x__process_container_children__mutmut_1, 
    'x__process_container_children__mutmut_2': x__process_container_children__mutmut_2, 
    'x__process_container_children__mutmut_3': x__process_container_children__mutmut_3, 
    'x__process_container_children__mutmut_4': x__process_container_children__mutmut_4, 
    'x__process_container_children__mutmut_5': x__process_container_children__mutmut_5, 
    'x__process_container_children__mutmut_6': x__process_container_children__mutmut_6, 
    'x__process_container_children__mutmut_7': x__process_container_children__mutmut_7, 
    'x__process_container_children__mutmut_8': x__process_container_children__mutmut_8, 
    'x__process_container_children__mutmut_9': x__process_container_children__mutmut_9, 
    'x__process_container_children__mutmut_10': x__process_container_children__mutmut_10, 
    'x__process_container_children__mutmut_11': x__process_container_children__mutmut_11, 
    'x__process_container_children__mutmut_12': x__process_container_children__mutmut_12
}

def _process_container_children(*args, **kwargs):
    result = _mutmut_trampoline(x__process_container_children__mutmut_orig, x__process_container_children__mutmut_mutants, args, kwargs)
    return result 

_process_container_children.__signature__ = _mutmut_signature(x__process_container_children__mutmut_orig)
x__process_container_children__mutmut_orig.__name__ = 'x__process_container_children'


def x__get_structural_cache_key__mutmut_orig(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_1(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = None
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_2(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is not None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_3(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(None), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_4(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(None))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_5(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = None
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_6(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = None
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_7(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = None

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_8(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = None
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_9(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = None

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_10(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(None)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_11(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id not in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_12(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            break

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_13(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_14(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = None
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_15(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(None).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_16(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = None
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_17(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(None),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_18(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            break

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_19(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            None, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_20(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, None, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_21(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, None, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_22(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, None, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_23(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, None
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_24(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_25(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_26(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_27(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_28(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_29(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = None
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_30(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = None
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_31(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(None)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_32(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = None
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_33(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(None, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_34(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, None)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_35(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_36(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, )
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_37(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = None

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_38(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = None
    base_key = structural_cache.get(id(value), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_39(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = None
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_40(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(None, (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_41(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), None)
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_42(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get((type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_43(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), )
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_44(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(None), (type(value),))
    return (thread_id, base_key)


def x__get_structural_cache_key__mutmut_45(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
    import threading

    structural_cache = get_structural_key_cache()
    if structural_cache is None:
        # Fallback for when no cache is available (thread safety mode)
        return (type(value), id(value))

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    visited_ids: set[int] = set()

    # Process all items to build cache entries
    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            # For primitive values, use value-based cache keys to avoid race conditions
            # from shared object IDs (e.g., interned integers, strings)
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                structural_cache[item_id] = (type(current_item).__name__, current_item)
            else:
                structural_cache[item_id] = (type(current_item),)
            continue

        _process_container_children(
            current_item, work_stack, post_process_stack, structural_cache, visited_ids
        )

    # Build the final keys from the bottom up
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        key = _generate_container_cache_key(container, structural_cache)
        structural_cache[container_id] = key

    # Include thread identity in the final cache key for complete isolation
    thread_id = threading.get_ident()
    base_key = structural_cache.get(id(value), (type(None),))
    return (thread_id, base_key)

x__get_structural_cache_key__mutmut_mutants : ClassVar[MutantDict] = {
'x__get_structural_cache_key__mutmut_1': x__get_structural_cache_key__mutmut_1, 
    'x__get_structural_cache_key__mutmut_2': x__get_structural_cache_key__mutmut_2, 
    'x__get_structural_cache_key__mutmut_3': x__get_structural_cache_key__mutmut_3, 
    'x__get_structural_cache_key__mutmut_4': x__get_structural_cache_key__mutmut_4, 
    'x__get_structural_cache_key__mutmut_5': x__get_structural_cache_key__mutmut_5, 
    'x__get_structural_cache_key__mutmut_6': x__get_structural_cache_key__mutmut_6, 
    'x__get_structural_cache_key__mutmut_7': x__get_structural_cache_key__mutmut_7, 
    'x__get_structural_cache_key__mutmut_8': x__get_structural_cache_key__mutmut_8, 
    'x__get_structural_cache_key__mutmut_9': x__get_structural_cache_key__mutmut_9, 
    'x__get_structural_cache_key__mutmut_10': x__get_structural_cache_key__mutmut_10, 
    'x__get_structural_cache_key__mutmut_11': x__get_structural_cache_key__mutmut_11, 
    'x__get_structural_cache_key__mutmut_12': x__get_structural_cache_key__mutmut_12, 
    'x__get_structural_cache_key__mutmut_13': x__get_structural_cache_key__mutmut_13, 
    'x__get_structural_cache_key__mutmut_14': x__get_structural_cache_key__mutmut_14, 
    'x__get_structural_cache_key__mutmut_15': x__get_structural_cache_key__mutmut_15, 
    'x__get_structural_cache_key__mutmut_16': x__get_structural_cache_key__mutmut_16, 
    'x__get_structural_cache_key__mutmut_17': x__get_structural_cache_key__mutmut_17, 
    'x__get_structural_cache_key__mutmut_18': x__get_structural_cache_key__mutmut_18, 
    'x__get_structural_cache_key__mutmut_19': x__get_structural_cache_key__mutmut_19, 
    'x__get_structural_cache_key__mutmut_20': x__get_structural_cache_key__mutmut_20, 
    'x__get_structural_cache_key__mutmut_21': x__get_structural_cache_key__mutmut_21, 
    'x__get_structural_cache_key__mutmut_22': x__get_structural_cache_key__mutmut_22, 
    'x__get_structural_cache_key__mutmut_23': x__get_structural_cache_key__mutmut_23, 
    'x__get_structural_cache_key__mutmut_24': x__get_structural_cache_key__mutmut_24, 
    'x__get_structural_cache_key__mutmut_25': x__get_structural_cache_key__mutmut_25, 
    'x__get_structural_cache_key__mutmut_26': x__get_structural_cache_key__mutmut_26, 
    'x__get_structural_cache_key__mutmut_27': x__get_structural_cache_key__mutmut_27, 
    'x__get_structural_cache_key__mutmut_28': x__get_structural_cache_key__mutmut_28, 
    'x__get_structural_cache_key__mutmut_29': x__get_structural_cache_key__mutmut_29, 
    'x__get_structural_cache_key__mutmut_30': x__get_structural_cache_key__mutmut_30, 
    'x__get_structural_cache_key__mutmut_31': x__get_structural_cache_key__mutmut_31, 
    'x__get_structural_cache_key__mutmut_32': x__get_structural_cache_key__mutmut_32, 
    'x__get_structural_cache_key__mutmut_33': x__get_structural_cache_key__mutmut_33, 
    'x__get_structural_cache_key__mutmut_34': x__get_structural_cache_key__mutmut_34, 
    'x__get_structural_cache_key__mutmut_35': x__get_structural_cache_key__mutmut_35, 
    'x__get_structural_cache_key__mutmut_36': x__get_structural_cache_key__mutmut_36, 
    'x__get_structural_cache_key__mutmut_37': x__get_structural_cache_key__mutmut_37, 
    'x__get_structural_cache_key__mutmut_38': x__get_structural_cache_key__mutmut_38, 
    'x__get_structural_cache_key__mutmut_39': x__get_structural_cache_key__mutmut_39, 
    'x__get_structural_cache_key__mutmut_40': x__get_structural_cache_key__mutmut_40, 
    'x__get_structural_cache_key__mutmut_41': x__get_structural_cache_key__mutmut_41, 
    'x__get_structural_cache_key__mutmut_42': x__get_structural_cache_key__mutmut_42, 
    'x__get_structural_cache_key__mutmut_43': x__get_structural_cache_key__mutmut_43, 
    'x__get_structural_cache_key__mutmut_44': x__get_structural_cache_key__mutmut_44, 
    'x__get_structural_cache_key__mutmut_45': x__get_structural_cache_key__mutmut_45
}

def _get_structural_cache_key(*args, **kwargs):
    result = _mutmut_trampoline(x__get_structural_cache_key__mutmut_orig, x__get_structural_cache_key__mutmut_mutants, args, kwargs)
    return result 

_get_structural_cache_key.__signature__ = _mutmut_signature(x__get_structural_cache_key__mutmut_orig)
x__get_structural_cache_key__mutmut_orig.__name__ = 'x__get_structural_cache_key'


@with_inference_cache
def infer_cty_type_from_raw(value: Any) -> CtyType[Any]:  # noqa: C901
    """
    Infers the most specific CtyType from a raw Python value.
    This function uses an iterative approach with a work stack to avoid recursion limits
    and leverages a context-aware cache for performance and thread-safety.
    """
    with error_boundary(
        context={
            "operation": "cty_type_inference",
            "value_type": type(value).__name__,
            "is_attrs_class": attrs.has(type(value)) if hasattr(value, "__class__") else False,
            "value_repr": str(value)[:100] if value is not None else "None",  # Truncated for safety
        }
    ):
        from pyvider.cty.types import (
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
        )

        if isinstance(value, CtyValue) or value is None:
            return CtyDynamic()

        if isinstance(value, CtyType):
            return CtyDynamic()

        if attrs.has(type(value)):
            value = _attrs_to_dict_safe(value)

    container_cache = get_container_schema_cache()

    # If no cache is available (e.g., in worker threads for thread safety),
    # proceed without caching
    structural_key = None
    if container_cache is not None:
        structural_key = _get_structural_cache_key(value)
        if structural_key in container_cache:
            return container_cache[structural_key]

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, CtyType[Any]] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            container = work_stack.pop()
            container_id = id(container)
            processing.remove(container_id)

            if isinstance(container, dict) and all(isinstance(k, str) for k in container):
                container = {unicodedata.normalize("NFC", k): v for k, v in container.items()}

            child_values = container.values() if isinstance(container, dict) else container
            child_types = [
                (v.type if isinstance(v, CtyValue) else results.get(id(v), CtyDynamic())) for v in child_values
            ]

            inferred_schema: CtyType[Any]
            if isinstance(container, dict):
                if not container:
                    inferred_schema = CtyObject({})
                elif not all(isinstance(k, str) for k in container):
                    unified = _unify_types(set(child_types))
                    inferred_schema = CtyMap(element_type=unified)
                else:
                    attr_types = dict(zip(container.keys(), child_types, strict=True))
                    inferred_schema = CtyObject(attribute_types=attr_types)
            elif isinstance(container, tuple):
                inferred_schema = CtyTuple(element_types=tuple(child_types))
            elif isinstance(container, list | set):
                unified = _unify_types(set(child_types))
                inferred_schema = (
                    CtyList(element_type=unified)
                    if isinstance(container, list)
                    else CtySet(element_type=unified)
                )
            else:
                inferred_schema = CtyDynamic()

            results[container_id] = inferred_schema
            continue

        if attrs.has(type(current_item)) and not isinstance(current_item, CtyType):
            try:
                current_item = _attrs_to_dict_safe(current_item)
            except TypeError:
                results[id(current_item)] = CtyDynamic()
                continue

        if current_item is None:
            continue
        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue
        if isinstance(current_item, CtyValue):
            results[item_id] = current_item.type
            continue

        if not isinstance(current_item, dict | list | tuple | set):
            if isinstance(current_item, bool):
                results[item_id] = CtyBool()
            elif isinstance(current_item, int | float | Decimal):
                results[item_id] = CtyNumber()
            elif isinstance(current_item, str | bytes):
                results[item_id] = CtyString()
            else:
                results[item_id] = CtyDynamic()
            continue

        structural_key = _get_structural_cache_key(current_item)
        if container_cache is not None and structural_key in container_cache:
            results[item_id] = container_cache[structural_key]
            continue

        processing.add(item_id)
        work_stack.extend([current_item, POST_PROCESS])
        work_stack.extend(
            reversed(list(current_item.values() if isinstance(current_item, dict) else current_item))
        )

    final_type = results.get(id(value), CtyDynamic())

    # Cache the result if caching is available
    if container_cache is not None:
        final_structural_key = _get_structural_cache_key(value)
        container_cache[final_structural_key] = final_type

    return final_type


def x__unify_types__mutmut_orig(types: set[CtyType[Any]]) -> CtyType[Any]:
    """Unifies a set of CtyTypes into a single representative type."""
    from pyvider.cty.conversion.explicit import unify

    return unify(types)


def x__unify_types__mutmut_1(types: set[CtyType[Any]]) -> CtyType[Any]:
    """Unifies a set of CtyTypes into a single representative type."""
    from pyvider.cty.conversion.explicit import unify

    return unify(None)

x__unify_types__mutmut_mutants : ClassVar[MutantDict] = {
'x__unify_types__mutmut_1': x__unify_types__mutmut_1
}

def _unify_types(*args, **kwargs):
    result = _mutmut_trampoline(x__unify_types__mutmut_orig, x__unify_types__mutmut_mutants, args, kwargs)
    return result 

_unify_types.__signature__ = _mutmut_signature(x__unify_types__mutmut_orig)
x__unify_types__mutmut_orig.__name__ = 'x__unify_types'


# 🌊🪢↔️🪄
