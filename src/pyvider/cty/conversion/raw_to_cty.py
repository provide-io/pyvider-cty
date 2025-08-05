# pyvider-cty/src/pyvider/cty/conversion/raw_to_cty.py

import unicodedata
from typing import Any
from decimal import Decimal

import attrs

from pyvider.cty.types import CtyObject, CtyType
from pyvider.cty.values import CtyValue

from ._cache import (
    get_container_schema_cache,
    get_structural_key_cache,
    with_inference_cache,
)
from ._utils import _attrs_to_dict_safe


def _get_structural_cache_key(value: Any) -> tuple[Any, ...]:
    """
    Iteratively generates a stable, structural cache key from a raw Python object,
    using a context-aware cache to handle object cycles and repeated sub-objects.
    """
    structural_cache = get_structural_key_cache()
    assert structural_cache is not None

    work_stack: list[Any] = [value]
    post_process_stack: list[Any] = []
    # This set tracks everything that has been pushed to the work_stack
    # to prevent re-processing and infinite loops.
    visited_ids: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()
        item_id = id(current_item)

        if item_id in structural_cache:
            continue

        if not isinstance(current_item, dict | list | tuple | set | frozenset):
            structural_cache[item_id] = (type(current_item),)
            continue

        if item_id in visited_ids:
            continue
        
        visited_ids.add(item_id)

        # Placeholder is essential for cycle detection.
        structural_cache[item_id] = (type(current_item), item_id, "placeholder")
        post_process_stack.append(current_item)

        children = []
        if isinstance(current_item, dict):
            children.extend(current_item.values())
        elif isinstance(current_item, list | tuple | set | frozenset):
            children.extend(current_item)
        
        work_stack.extend(children)

    # Build the final keys from the bottom up.
    while post_process_stack:
        container = post_process_stack.pop()
        container_id = id(container)
        
        key: tuple[Any, ...]
        if isinstance(container, dict):
            # Sort items by key's string representation for deterministic order.
            sorted_items = sorted(container.items(), key=lambda item: repr(item[0]))
            key = (
                dict,
                frozenset((k, structural_cache[id(v)]) for k, v in sorted_items),
            )
        elif isinstance(container, list):
            key = (list, tuple(structural_cache[id(v)] for v in container))
        elif isinstance(container, tuple):
            key = (tuple, tuple(structural_cache[id(v)] for v in container))
        elif isinstance(container, set | frozenset):
            # Sort elements by their string representation for deterministic order.
            sorted_items = sorted(list(container), key=repr)
            key = (frozenset, frozenset(structural_cache[id(v)] for v in sorted_items))
        else:
            key = (type(container),)

        structural_cache[container_id] = key

    return structural_cache.get(id(value), (type(value),))


@with_inference_cache
def infer_cty_type_from_raw(value: Any) -> CtyType[Any]:  # noqa: C901
    """
    Infers the most specific CtyType from a raw Python value.
    This function uses an iterative approach with a work stack to avoid recursion limits
    and leverages a context-aware cache for performance and thread-safety.
    """
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
    assert container_cache is not None

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

            if isinstance(container, dict) and all(
                isinstance(k, str) for k in container
            ):
                container = {
                    unicodedata.normalize("NFC", k): v for k, v in container.items()
                }

            child_values = (
                container.values() if isinstance(container, dict) else container
            )
            child_types = [
                (v.type if isinstance(v, CtyValue) else results.get(id(v), CtyDynamic()))
                for v in child_values
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
        if structural_key in container_cache:
            results[item_id] = container_cache[structural_key]
            continue

        processing.add(item_id)
        work_stack.extend([current_item, POST_PROCESS])
        work_stack.extend(
            reversed(
                list(
                    current_item.values()
                    if isinstance(current_item, dict)
                    else current_item
                )
            )
        )

    final_type = results.get(id(value), CtyDynamic())

    final_structural_key = _get_structural_cache_key(value)
    container_cache[final_structural_key] = final_type

    return final_type


def _unify_types(types: set[CtyType[Any]]) -> CtyType[Any]:
    """Unifies a set of CtyTypes into a single representative type."""
    from pyvider.cty.conversion.explicit import unify

    return unify(types)
