from __future__ import annotations
from typing import Any
from decimal import Decimal

# Local imports to break the circular dependency cycle.
from pyvider.cty.values import CtyValue
from pyvider.cty.types import (
    CtyType, CtyList, CtySet, CtyTuple, CtyMap, CtyObject, CtyDynamic,
    CtyString, CtyNumber, CtyBool
)

def cty_to_native(value: Any) -> Any:
    """
    Converts a CtyValue to its raw Python representation using an iterative
    approach to avoid recursion limits. This is safe for deeply nested structures.
    """
    if not isinstance(value, CtyValue):
        return value

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

            if isinstance(val_to_process.type, CtyDynamic):
                # It's a wrapper. Its inner value must have been processed.
                # Link the inner value's native result to the wrapper's ID.
                inner_id = id(val_to_process.value)
                results[val_id] = results[inner_id]
            elif isinstance(val_to_process.type, (CtyObject, CtyMap)):
                results[val_id] = {k: results[id(v)] for k, v in val_to_process.value.items()}
            elif isinstance(val_to_process.type, CtyList):
                results[val_id] = [results[id(item)] for item in val_to_process.value]
            elif isinstance(val_to_process.type, CtySet):
                results[val_id] = sorted([results[id(item)] for item in val_to_process.value], key=repr)
            elif isinstance(val_to_process.type, CtyTuple):
                results[val_id] = tuple(results[id(item)] for item in val_to_process.value)
            continue

        if not isinstance(current_item, CtyValue):
            results[id(current_item)] = current_item
            continue

        if current_item.is_unknown:
            raise ValueError("Cannot convert an unknown CtyValue to a native Python type.")
        if current_item.is_null:
            results[id(current_item)] = None
            continue
        
        item_id = id(current_item)
        if item_id in results or item_id in processing:
            continue

        # For ANY non-primitive, use the sentinel pattern to process its children/inner value first.
        if isinstance(current_item.type, (CtyObject, CtyMap, CtyList, CtySet, CtyTuple, CtyDynamic)):
            processing.add(item_id)
            work_stack.extend([current_item, POST_PROCESS]) # Push self and sentinel

            if isinstance(current_item.type, CtyDynamic):
                work_stack.append(current_item.value) # Push inner value
            else: # It's a standard container
                child_values = list(current_item.value.values()) if isinstance(current_item.value, dict) else list(current_item.value)
                work_stack.extend(reversed(child_values)) # Push children in reverse
        else: # Primitive types
            inner_val = current_item.value
            if isinstance(inner_val, Decimal):
                # FIX: Use a robust method to check for whole numbers that avoids
                #      the modulo operator on potentially very large numbers.
                # `as_tuple()` is a reliable way to inspect a Decimal's components.
                # A non-negative exponent means it's an integer.
                if inner_val.as_tuple().exponent >= 0:
                    results[item_id] = int(inner_val)
                else:
                    results[item_id] = float(inner_val)
            else:
                results[item_id] = inner_val

    return results.get(id(value))
