from __future__ import annotations

from decimal import Decimal
from typing import Any

import attrs

# NOTE: Do NOT import from pyvider.cty.types at the top level.
# This is the root of the circular import problem.
# We will import them locally inside the functions that need them.
from pyvider.cty.types import CtyType


def _unify_types(types: set[CtyType[Any]]) -> CtyType[Any]:
    """Unifies a set of CtyTypes into a single representative type."""
    from pyvider.cty.types import CtyDynamic

    if not types:
        return CtyDynamic()

    first_type = next(iter(types))

    if all(t.equal(first_type) for t in types):
        return first_type

    return CtyDynamic()


def _attrs_to_dict_safe(inst: Any) -> dict[str, Any]:
    """Safely converts an attrs instance to a dict, avoiding Cty framework types."""
    from pyvider.cty.types import CtyType

    if isinstance(inst, CtyType):
        raise TypeError(
            f"Cannot infer data type from a CtyType instance: {type(inst).__name__}"
        )
    if hasattr(inst, "vtype"):
        raise TypeError(
            f"Cannot infer data type from a CtyValue instance: {type(inst).__name__}"
        )

    res = {}
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def infer_cty_type_from_raw(value: Any) -> CtyType[Any]:
    """
    Infers the most specific CtyType from a raw Python value.
    This function uses an iterative approach with a work stack to avoid recursion limits.
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

    if hasattr(value, "vtype") or isinstance(value, CtyType):
        return CtyDynamic()
    if value is None:
        return CtyDynamic()

    if attrs.has(type(value)):
        value = _attrs_to_dict_safe(value)

    POST_PROCESS = object()
    work_stack: list[Any] = [value]
    results: dict[int, CtyType] = {}
    processing: set[int] = set()

    while work_stack:
        current_item = work_stack.pop()

        if current_item is POST_PROCESS:
            container = work_stack.pop()
            container_id = id(container)
            processing.remove(container_id)

            if isinstance(container, dict):
                # FIX: Check if all keys are valid identifiers. If not, infer CtyMap.
                if all(isinstance(k, str) and k.isidentifier() for k in container):
                    attr_types = {
                        k: results.get(id(v), CtyDynamic())
                        for k, v in container.items()
                    }
                    results[container_id] = CtyObject(attribute_types=attr_types)
                else:
                    # If any key is not a valid identifier, treat it as a map.
                    value_types = {
                        results.get(id(v), CtyDynamic()) for v in container.values()
                    }
                    unified_value_type = _unify_types(value_types)
                    results[container_id] = CtyMap(element_type=unified_value_type)
            elif isinstance(container, tuple):
                element_types_tuple = tuple(
                    results.get(id(item), CtyDynamic()) for item in container
                )
                results[container_id] = CtyTuple(element_types=element_types_tuple)
            elif isinstance(container, list):
                element_types_set = {
                    results.get(id(item), CtyDynamic()) for item in container
                }
                unified_element_type = _unify_types(element_types_set)
                results[container_id] = CtyList(element_type=unified_element_type)
            elif isinstance(container, set):
                element_types_set = {
                    results.get(id(item), CtyDynamic()) for item in container
                }
                unified_element_type = _unify_types(element_types_set)
                results[container_id] = CtySet(element_type=unified_element_type)
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

        if attrs.has(type(current_item)):
            current_item = _attrs_to_dict_safe(current_item)

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

        processing.add(item_id)
        work_stack.extend([current_item, POST_PROCESS])

        if isinstance(current_item, dict):
            work_stack.extend(reversed(list(current_item.values())))
        elif isinstance(current_item, list | tuple | set):
            work_stack.extend(reversed(list(current_item)))

    return results.get(id(value), CtyDynamic())
