from __future__ import annotations
from decimal import Decimal
from typing import Any
import attrs

# NOTE: Do NOT import from pyvider.cty.types at the top level.
# This is the root of the circular import problem.
# We will import them locally inside the functions that need them.

from pyvider.cty.values import CtyValue


def _unify_types(types: set["CtyType"]) -> "CtyType":
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

    if hasattr(inst, "vtype") or isinstance(inst, CtyType):
        raise TypeError(f"Cannot infer data type from a framework object: {type(inst).__name__}")
    res = {}
    for a in getattr(type(inst), "__attrs_attrs__", []):
        res[a.name] = getattr(inst, a.name)
    return res


def infer_cty_type_from_raw(value: Any) -> "CtyType":
    """
    Infers the most specific CtyType from a raw Python value.
    This function uses an iterative approach with a work stack to avoid recursion limits.
    """
    from pyvider.cty.types import (
        CtyType, CtyBool, CtyNumber, CtyString, CtyList, CtySet, CtyMap, CtyObject, CtyTuple, CtyDynamic
    )

    if hasattr(value, "vtype") or isinstance(value, CtyType):
        return CtyDynamic()
    if value is None:
        return CtyDynamic()

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
                if all(isinstance(k, str) and k.isidentifier() for k in container.keys()):
                    attr_types = {k: results.get(id(v), CtyDynamic()) for k, v in container.items()}
                    results[container_id] = CtyObject(attribute_types=attr_types)
                else:
                    # If any key is not a valid identifier, treat it as a map.
                    value_types = {results.get(id(v), CtyDynamic()) for v in container.values()}
                    unified_value_type = _unify_types(value_types)
                    results[container_id] = CtyMap(element_type=unified_value_type)
            elif isinstance(container, tuple):
                element_types = tuple(results.get(id(item), CtyDynamic()) for item in container)
                results[container_id] = CtyTuple(element_types=element_types)
            elif isinstance(container, list):
                element_types = {results.get(id(item), CtyDynamic()) for item in container}
                unified_element_type = _unify_types(element_types)
                results[container_id] = CtyList(element_type=unified_element_type)
            elif isinstance(container, set):
                element_types = {results.get(id(item), CtyDynamic()) for item in container}
                unified_element_type = _unify_types(element_types)
                results[container_id] = CtySet(element_type=unified_element_type)
            continue

        if attrs.has(type(current_item)):
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

        if not isinstance(current_item, (dict, list, tuple, set)):
            if isinstance(current_item, bool): results[item_id] = CtyBool()
            elif isinstance(current_item, (int, float, Decimal)): results[item_id] = CtyNumber()
            elif isinstance(current_item, (str, bytes)): results[item_id] = CtyString()
            else: results[item_id] = CtyDynamic()
            continue

        processing.add(item_id)
        work_stack.extend([current_item, POST_PROCESS])
        
        if isinstance(current_item, dict):
            work_stack.extend(reversed(list(current_item.values())))
        elif isinstance(current_item, (list, tuple, set)):
            work_stack.extend(reversed(list(current_item)))
            
    return results.get(id(value), CtyDynamic())
