from itertools import product
from typing import Any

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
from pyvider.cty.exceptions import CtyFunctionError


def distinct(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"distinct: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown: return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            raise CtyFunctionError(f"distinct: element of type {cty_element.type.ctype} is not hashable. Error: {e}") from e
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList | CtySet) else CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)

def flatten(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown: return input_val
    result_elements = []
    final_element_type: CtyType[Any] | None = None
    for outer_element_val in input_val.value:
        inner_val = outer_element_val.value if isinstance(outer_element_val.type, CtyDynamic) else outer_element_val
        if inner_val.is_null: continue
        if inner_val.is_unknown: return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        if not isinstance(inner_val.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"flatten: all elements must be lists or tuples; found {inner_val.type.ctype}")
        for inner_element_val in inner_val.value:
            if final_element_type is None: final_element_type = inner_element_val.type
            elif not final_element_type.equal(inner_element_val.type): final_element_type = CtyDynamic()
            result_elements.append(inner_element_val)
    if final_element_type is None: return CtyList(element_type=CtyDynamic()).validate([])
    return CtyList(element_type=final_element_type).validate(result_elements)

def sort(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown: return input_val
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList | CtySet) else CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")
    if not hasattr(input_val.value, "__iter__"): raise CtyFunctionError("sort: input value is not iterable")
    for i, cty_element in enumerate(input_val.value):
        value_to_check = cty_element.value if isinstance(cty_element.type, CtyDynamic) else cty_element
        if value_to_check.is_null or value_to_check.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")
    return CtyList[Any](element_type=element_type).validate(sorted(input_val.value, key=lambda x: x.value))

def length(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap | CtyString):
        raise CtyFunctionError(f"length: input must be a collection or string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown: return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(input_val.value))

def slice(input_val: "CtyValue[Any]", start_val: "CtyValue[Any]", end_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if input_val.is_null or input_val.is_unknown or start_val.is_null or start_val.is_unknown or end_val.is_null or end_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)
    return CtyList(element_type=element_type).validate(input_val.value[start:end])

def concat(*lists: "CtyValue[Any]") -> "CtyValue[Any]":
    if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
        raise CtyFunctionError("concat: all arguments must be lists or tuples")
    result_elements = []
    final_element_type: CtyType[Any] | None = None
    if any(l.is_unknown for l in lists): return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    for lst in lists:
        if lst.is_null: continue
        for element in lst.value:
            if final_element_type is None: final_element_type = element.type
            elif not final_element_type.equal(element.type): final_element_type = CtyDynamic()
            result_elements.append(element)
    if final_element_type is None: return CtyList(element_type=CtyDynamic()).validate([])
    return CtyList(element_type=final_element_type).validate(result_elements)

def contains(collection: "CtyValue[Any]", value: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}")
    if collection.is_null or collection.is_unknown: return CtyValue.unknown(CtyBool())
    return CtyBool().validate(value in collection.value)

def keys(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyMap | CtyObject):
        raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown: return CtyValue.unknown(CtyList(element_type=CtyString()))
    return CtyList(element_type=CtyString()).validate(sorted(list(input_val.value.keys())))

def values(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyMap | CtyObject):
        raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
    elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
    if input_val.is_null or input_val.is_unknown: return CtyValue.unknown(CtyList(element_type=elem_type))
    if not isinstance(input_val.value, dict): raise CtyFunctionError("values: input value is not a map or object")
    return CtyList(element_type=elem_type).validate(list(input_val.value.values()))

def reverse(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null or input_val.is_unknown: return input_val
    return input_val.type.validate(list(reversed(input_val.value)))

def hasindex(collection: "CtyValue[Any]", key: "CtyValue[Any]") -> "CtyValue[Any]":
    if collection.is_unknown or key.is_unknown: return CtyValue.unknown(CtyBool())
    if collection.is_null: return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null: return CtyBool().validate(False)
        idx = int(key.value)
        return CtyBool().validate(0 <= idx < len(collection.value))
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null: return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)
    raise CtyFunctionError(f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}")

def index(collection: "CtyValue[Any]", key: "CtyValue[Any]") -> "CtyValue[Any]":
    if not hasindex(collection, key).value:
        raise CtyFunctionError("index: key does not exist in collection")
    
    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)
        
    return collection[key_val]

def element(collection: "CtyValue[Any]", idx: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(collection.type, CtyList | CtyTuple):
        raise CtyFunctionError("element: collection must be a list or tuple")
    if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
        elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
        return CtyValue.unknown(elem_type)
    length = len(collection.value)
    if length == 0: raise CtyFunctionError("element: cannot use element function with an empty list")
    return collection.value[int(idx.value) % length]

def coalescelist(*args: "CtyValue[Any]") -> "CtyValue[Any]":
    if any(v.is_unknown for v in args): return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0:
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")

def compact(collection: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple) or not isinstance(collection.type.element_type, CtyString):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if collection.is_null or collection.is_unknown: return collection
    return CtyList(element_type=CtyString()).validate([v for v in collection.value if v.value])

def chunklist(collection: "CtyValue[Any]", size: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError("chunklist: arguments must be a list/tuple and a number")
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=collection.type))
    chunk_size = int(size.value)
    if chunk_size <= 0: raise CtyFunctionError("chunklist: size must be a positive number")
    chunks = [collection.value[i:i + chunk_size] for i in range(0, len(collection.value), chunk_size)]
    return CtyList(element_type=collection.type).validate(chunks)

def lookup(collection: "CtyValue[Any]", key: "CtyValue[Any]", default: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")
    if collection.is_unknown or key.is_unknown: return CtyValue.unknown(unify([collection.type.element_type, default.type]))
    if collection.is_null or key.is_null or key.value not in collection.value:
        return default
    return collection.value[key.value]

def merge(*args: "CtyValue[Any]") -> "CtyValue[Any]":
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args): return CtyValue.unknown(CtyDynamic())
    result = {}
    for arg in args:
        if not arg.is_null: result.update(arg.value)
    return CtyDynamic().validate(result)

def setproduct(*args: "CtyValue[Any]") -> "CtyValue[Any]":
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args): return CtyValue.unknown(CtySet(element_type=CtyDynamic()))
    
    iterables = [list(arg.value) for arg in args if not arg.is_null]
    if not iterables: return CtySet(element_type=CtyDynamic()).validate([])

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]
    
    elem_types = [arg.type.element_type if isinstance(arg.type, CtyList | CtySet) else CtyDynamic() for arg in args if not arg.is_null]
    tuple_type = CtyTuple(element_types=tuple(elem_types))
    
    return CtySet(element_type=tuple_type).validate(result_tuples)

def zipmap(keys: "CtyValue[Any]", values: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown: return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null: return CtyMap(element_type=CtyDynamic()).validate({})
    
    key_list = [k.value for k in keys.value]
    val_list = list(values.value)
    
    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}
    
    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)
