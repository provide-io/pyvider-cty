# pyvider-cty/src/pyvider/cty/functions/collection_functions.py
from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.exceptions import (
    CtyFunctionError,
)


def distinct(input_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"distinct: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            raise CtyFunctionError(f"distinct: element of type {cty_element.type.ctype} is not hashable. Error: {e}")
    # Infer the element type of the resulting list
    element_types = {el.type for el in result_elements}
    final_element_type = CtyDynamic() if len(element_types) > 1 else (element_types.pop() if element_types else CtyDynamic())
    return CtyList(element_type=final_element_type).validate(result_elements)

def flatten(input_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"flatten: input must be a list or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    result_elements = []
    final_element_type: CtyType | None = None
    for outer_element_val in input_val.value:
        if outer_element_val.is_null: continue
        if outer_element_val.is_unknown: return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        if not isinstance(outer_element_val.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"flatten: all elements must be lists or tuples; found {outer_element_val.type.ctype}")
        for inner_element_val in outer_element_val.value:
            result_elements.append(inner_element_val)
            current_inner_type = inner_element_val.type
            if final_element_type is None:
                final_element_type = current_inner_type
            elif not final_element_type.equal(current_inner_type):
                final_element_type = CtyDynamic()
    return CtyList(element_type=(final_element_type or CtyDynamic())).validate(result_elements)

def sort(input_val: CtyValue) -> CtyValue:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    elements_to_sort = list(input_val.value)
    if not elements_to_sort:
        el_type = input_val.type.element_type if hasattr(input_val.type, "element_type") else CtyDynamic()
        return CtyList(element_type=el_type).validate([])
    first_element_type = elements_to_sort[0].type
    if not isinstance(first_element_type, CtyString | CtyNumber | CtyBool):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {first_element_type.ctype}")
    py_values_to_sort = []
    for i, cty_element in enumerate(elements_to_sort):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")
        validated_to_first_type = first_element_type.validate(cty_element)
        py_values_to_sort.append(validated_to_first_type.value)
    sorted_py_values = sorted(py_values_to_sort)
    sorted_cty_elements = [first_element_type.validate(pv) for pv in sorted_py_values]
    return CtyList(element_type=first_element_type).validate(sorted_cty_elements)
