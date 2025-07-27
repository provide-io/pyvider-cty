from __future__ import annotations

from decimal import Decimal
from typing import Any

import attrs

from pyvider.cty.types import CtyType, CtyObject
from pyvider.cty.values import CtyValue

from ._utils import _attrs_to_dict_safe

# --- OPTIMIZATION START ---
# Module-level cache for inferred container schemas.
# The key is a stable representation of the container's structure and child types.
_container_schema_cache: dict[tuple[type, frozenset[Any]], CtyType[Any]] = {}
# --- OPTIMIZATION END ---

def _unify_types(types: set[CtyType[Any]]) -> CtyType[Any]:
    """Unifies a set of CtyTypes into a single representative type."""
    from pyvider.cty.conversion.explicit import unify
    return unify(types)


def infer_cty_type_from_raw(value: Any) -> CtyType[Any]:  # noqa: C901
    """
    Infers the most specific CtyType from a raw Python value.
    This function uses an iterative approach with a work stack to avoid recursion limits.
    """
    from pyvider.cty.types import (
        CtyBool, CtyDynamic, CtyList, CtyMap, CtyNumber,
        CtyObject, CtySet, CtyString, CtyTuple, CtyType,
    )

    if isinstance(value, CtyValue | CtyType) or value is None:
        return CtyDynamic()

    if attrs.has(type(value)):
        value = _attrs_to_dict_safe(value)

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

            child_types = [
                (v.type if isinstance(v, CtyValue) else results.get(id(v), CtyDynamic()))
                for v in (container.values() if isinstance(container, dict) else container)
            ]
            
            # --- CACHING LOGIC ---
            cache_key_part = frozenset(repr(t) for t in child_types)
            if isinstance(container, dict):
                cache_key_part = frozenset(
                    (k, repr(t)) for k, t in zip(container.keys(), child_types, strict=True)
                )
            
            cache_key = (type(container), cache_key_part)
            if cache_key in _container_schema_cache:
                results[container_id] = _container_schema_cache[cache_key]
                continue
            # --- END CACHING LOGIC ---

            inferred_schema: CtyType[Any]
            if isinstance(container, dict):
                if not container:
                    inferred_schema = CtyObject({})
                elif not all(isinstance(k, str) for k in container):
                    unified = _unify_types(set(child_types))
                    inferred_schema = CtyMap(element_type=unified)
                else:
                    attr_types = dict(zip(container.keys(), child_types, strict=True))
                    unified = _unify_types(set(child_types))
                    if not isinstance(unified, CtyDynamic):
                        inferred_schema = CtyMap(element_type=unified)
                    else:
                        inferred_schema = CtyObject(attribute_types=attr_types)
            elif isinstance(container, tuple):
                inferred_schema = CtyTuple(element_types=tuple(child_types))
            elif isinstance(container, list | set):
                unified = _unify_types(set(child_types))
                inferred_schema = CtyList(element_type=unified) if isinstance(container, list) else CtySet(element_type=unified)
            
            _container_schema_cache[cache_key] = inferred_schema
            results[container_id] = inferred_schema
            continue

        if attrs.has(type(current_item)) and not isinstance(current_item, CtyType):
            try:
                current_item = _attrs_to_dict_safe(current_item)
            except TypeError:
                results[id(current_item)] = CtyDynamic()
                continue

        if current_item is None: continue
        item_id = id(current_item)
        if item_id in results or item_id in processing: continue
        if isinstance(current_item, CtyValue):
            results[item_id] = current_item.type
            continue

        if not isinstance(current_item, dict | list | tuple | set):
            if isinstance(current_item, bool): results[item_id] = CtyBool()
            elif isinstance(current_item, int | float | Decimal): results[item_id] = CtyNumber()
            elif isinstance(current_item, str | bytes): results[item_id] = CtyString()
            else: results[item_id] = CtyDynamic()
            continue

        processing.add(item_id)
        work_stack.extend([current_item, POST_PROCESS])
        work_stack.extend(reversed(list(current_item.values() if isinstance(current_item, dict) else current_item)))

    return results.get(id(value), CtyDynamic())
