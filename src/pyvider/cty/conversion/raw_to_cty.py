#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from decimal import Decimal
import threading
from typing import Any

# pyvider-cty/src/pyvider/cty/conversion/raw_to_cty.py
import unicodedata

import attrs

from pyvider.cty.conversion._utils import _attrs_to_dict_safe
from pyvider.cty.conversion.inference_cache import (
    get_container_schema_cache,
    get_structural_key_cache,
    with_inference_cache,
)
from pyvider.cty.types import CtyType
from pyvider.cty.values import CtyValue

# Module-level sentinel to avoid per-call allocation
_POST_PROCESS = object()

# Sentinel placeholder for containers during structural cache building.
# Using a single tuple avoids allocating (item_id,) per container visit.
_CONTAINER_PLACEHOLDER: tuple[Any, ...] = ("__placeholder__",)

# Cache of structural keys for primitive values, keyed by (type, value).
# Avoids allocating a new tuple per primitive when the same value recurs.
_PRIMITIVE_KEY_CACHE: dict[tuple[type, Any], tuple[Any, ...]] = {}

# Lazy-initialized singleton type instances to avoid repeated allocation.
# Cannot be created at import time due to circular import constraints.
_SINGLETONS: dict[str, CtyType[Any]] = {}


def _get_singleton(name: str) -> CtyType[Any]:
    """Get or create a singleton primitive type instance."""
    if name not in _SINGLETONS:
        from pyvider.cty.types import CtyBool, CtyDynamic, CtyNumber, CtyString

        _SINGLETONS["bool"] = CtyBool()
        _SINGLETONS["number"] = CtyNumber()
        _SINGLETONS["string"] = CtyString()
        _SINGLETONS["dynamic"] = CtyDynamic()
    return _SINGLETONS[name]


# Module-level sort key to avoid lambda allocation per call
def _repr_key_first(item: tuple[Any, Any]) -> str:
    return repr(item[0])


def _generate_container_cache_key(
    container: Any, structural_cache: dict[int, tuple[Any, ...]]
) -> tuple[Any, ...]:
    """Generate a cache key for a container based on its type and contents.

    Uses value-based keys for small containers with primitives to avoid
    race conditions from Python's object interning.
    """
    _PRIM = (bool, int, float, str, bytes, type(None))

    if isinstance(container, dict):
        items = container.items()
        # For small dicts containing only primitives, use value-based keys
        # to avoid race conditions from interned objects sharing IDs
        if len(container) <= 5 and all(isinstance(v, _PRIM) for v in container.values()):
            sorted_items = sorted(items, key=_repr_key_first)
            return (dict, frozenset(sorted_items))

        # For larger or complex dicts, use existing structural cache approach
        sorted_items = sorted(items, key=_repr_key_first)
        return (
            dict,
            frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
        )
    elif isinstance(container, list):
        # For lists containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(isinstance(v, _PRIM) for v in container):
            return (list, tuple(container))
        return (list, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, tuple):
        # For tuples containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(isinstance(v, _PRIM) for v in container):
            return (tuple, container)
        return (tuple, tuple(structural_cache[id(v)] for v in container))
    elif isinstance(container, set | frozenset):
        # For sets containing only primitives, use value-based keys to prevent race conditions
        if len(container) <= 100 and all(isinstance(v, _PRIM) for v in container):
            sorted_items = sorted(container, key=repr)
            return (frozenset, frozenset(sorted_items))

        # Sort elements by their string representation for deterministic order.
        sorted_items = sorted(container, key=repr)
        return (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
    else:
        return (type(container),)


def _process_container_children(
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
    # Use a shared sentinel tuple instead of allocating (item_id,) per call.
    structural_cache[item_id] = _CONTAINER_PLACEHOLDER
    post_process_stack.append(current_item)

    # Inline child extraction to avoid intermediate list allocation
    if isinstance(current_item, dict):
        work_stack.extend(current_item.values())
    elif isinstance(current_item, list | tuple | set | frozenset):
        work_stack.extend(current_item)


def _get_structural_cache_key(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    Includes thread identity to ensure complete isolation between concurrent operations.
    """
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
            # from shared object IDs (e.g., interned integers, strings).
            # Cache the key tuples to avoid re-allocating identical tuples for recurring values.
            if isinstance(current_item, (bool, int, float, str, bytes, type(None))):
                cache_lookup = (type(current_item), current_item)
                cached_key = _PRIMITIVE_KEY_CACHE.get(cache_lookup)
                if cached_key is None:
                    cached_key = cache_lookup
                    _PRIMITIVE_KEY_CACHE[cache_lookup] = cached_key
                structural_cache[item_id] = cached_key
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


@with_inference_cache
def infer_cty_type_from_raw(value: Any) -> CtyType[Any]:  # noqa: C901
    """
    Infers the most specific CtyType from a raw Python value.
    This function uses an iterative approach with a work stack to avoid recursion limits
    and leverages a context-aware cache for performance and thread-safety.
    """
    from pyvider.cty.types import (
        CtyList,
        CtyMap,
        CtyObject,
        CtySet,
        CtyTuple,
        CtyType,
    )

    # Fast path for primitives — avoid cache lookups and work stack allocation.
    # Uses singleton instances to avoid repeated allocation of parameterless types.
    if isinstance(value, bool):
        return _get_singleton("bool")
    if isinstance(value, int | float | Decimal):
        return _get_singleton("number")
    if isinstance(value, str | bytes):
        return _get_singleton("string")
    if isinstance(value, CtyValue) or value is None:
        return _get_singleton("dynamic")
    if isinstance(value, CtyType):
        return _get_singleton("dynamic")

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

    POST_PROCESS = _POST_PROCESS
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
            _dynamic = _get_singleton("dynamic")
            child_types = [
                (v.type if isinstance(v, CtyValue) else results.get(id(v), _dynamic)) for v in child_values
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
                inferred_schema = _get_singleton("dynamic")

            results[container_id] = inferred_schema
            continue

        if attrs.has(type(current_item)) and not isinstance(current_item, CtyType):
            try:
                current_item = _attrs_to_dict_safe(current_item)
            except TypeError:
                results[id(current_item)] = _get_singleton("dynamic")
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
                results[item_id] = _get_singleton("bool")
            elif isinstance(current_item, int | float | Decimal):
                results[item_id] = _get_singleton("number")
            elif isinstance(current_item, str | bytes):
                results[item_id] = _get_singleton("string")
            else:
                results[item_id] = _get_singleton("dynamic")
            continue

        structural_key = _get_structural_cache_key(current_item)
        if container_cache is not None and structural_key in container_cache:
            results[item_id] = container_cache[structural_key]
            continue

        processing.add(item_id)
        # Two appends avoid allocating a temporary 2-element list
        work_stack.append(current_item)
        work_stack.append(POST_PROCESS)
        # Avoid intermediate list allocation: reversed() works directly on
        # dict.values(), list, and tuple. Sets don't need ordering for inference.
        if isinstance(current_item, dict):
            work_stack.extend(reversed(current_item.values()))
        elif isinstance(current_item, list | tuple):
            work_stack.extend(reversed(current_item))
        else:
            work_stack.extend(current_item)

    final_type = results.get(id(value), _get_singleton("dynamic"))

    # Cache the result if caching is available
    if container_cache is not None:
        final_structural_key = _get_structural_cache_key(value)
        container_cache[final_structural_key] = final_type

    return final_type


def _unify_types(types: set[CtyType[Any]]) -> CtyType[Any]:
    """Unifies a set of CtyTypes into a single representative type."""
    from pyvider.cty.conversion.explicit import unify

    return unify(types)


# 🌊🪢🔚
