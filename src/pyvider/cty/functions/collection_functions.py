# pyvider-cty/src/pyvider/cty/functions/collection_functions.py

from pyvider.cty import (
    CtyList, CtySet, CtyTuple, CtyDynamic, CtyString, CtyNumber, CtyBool,
    CtyValue, CtyType
)
from pyvider.cty.exceptions import CtyFunctionError, CtyCollectionValidationError, CtyTypeValidationError
from pyvider.cty.types.collections.list import CtyList # For isinstance checks
from pyvider.cty.types.collections.set import CtySet # For isinstance checks
from pyvider.cty.types.collections.map import CtyMap # For isinstance checks, if needed later
from pyvider.cty.types.structural.tuple import CtyTuple # For isinstance checks


def distinct(input_val: CtyValue) -> CtyValue:
    """
    Removes duplicate values from a list.
    Order of first appearance is preserved.
    Elements must be hashable and comparable for equality.
    """
    if not isinstance(input_val.type, (CtyList, CtySet, CtyTuple)): # Accept list, set, or tuple for distinct
        raise CtyFunctionError(f"distinct: input must be a list, set, or tuple, got {input_val.type.ctype}")

    if input_val.is_null or input_val.is_unknown:
        return input_val

    element_type: CtyType
    if isinstance(input_val.type, CtyList):
        element_type = input_val.type.element_type
    elif isinstance(input_val.type, CtySet):
        element_type = input_val.type.element_type
    elif isinstance(input_val.type, CtyTuple):
        # For a tuple, if all elements are the same type, use that.
        # Otherwise, the distinct list will have dynamic elements.
        # This simplification: assume tuple elements become dynamic for the output list.
        # A more advanced version could unify tuple element types.
        if len(input_val.type.element_types) > 0:
            is_homogeneous = all(et.equal(input_val.type.element_types[0]) for et in input_val.type.element_types) # Changed .equals to .equal
            element_type = input_val.type.element_types[0] if is_homogeneous else CtyDynamic()
        else: # Empty tuple
            element_type = CtyDynamic() # Or perhaps the type of the input tuple itself if it was typed?

    else: # Should not be reached due to initial type check
        raise CtyFunctionError("distinct: Unexpected input type after initial check.")


    seen = set()
    result_elements = []

    # input_val.value here is the Python list/set/tuple of CtyValues
    for cty_element in input_val.value:
        if not isinstance(cty_element, CtyValue):
             # This should not happen if the input_val was correctly validated
            raise CtyFunctionError("distinct: internal error - element is not a CtyValue.")

        # For hashability in 'seen' set, we need a stable hash.
        # CtyValue's hash should be suitable.
        # If CtyValue itself is not hashable (e.g. wrapping an unhashable list), this will fail.
        try:
            # Using the CtyValue directly for seen set.
            # If value is complex (like list), CtyValue needs a good hash.
            # CtyValue.__hash__ needs to be robust.
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e: # Typically "unhashable type"
            raise CtyFunctionError(f"distinct: element of type {cty_element.type.ctype} is not hashable. Error: {e}")

    # The result is always a list, with the determined element type.
    # Assuming CtyList.validate can handle a list of already validated CtyValues.
    return CtyList(element_type=element_type).validate(result_elements)


def flatten(input_val: CtyValue) -> CtyValue:
    """
    Takes a list of lists/tuples and concatenates them into a single list.
    If inner collections have mixed types, the resulting list's elements become dynamic.
    """
    if not isinstance(input_val.type, (CtyList, CtyTuple)):
        raise CtyFunctionError(f"flatten: input must be a list or tuple, got {input_val.type.ctype}")

    if input_val.is_null or input_val.is_unknown:
        return input_val

    result_elements = []
    final_element_type: CtyType | None = None

    for outer_element_val in input_val.value: # outer_element_val is a CtyValue
        if not isinstance(outer_element_val, CtyValue):
            raise CtyFunctionError("flatten: internal error - outer element is not a CtyValue.")

        if outer_element_val.is_null: # Skip null inner lists/tuples
            continue
        if outer_element_val.is_unknown: # If any inner list is unknown, result is unknown list of dynamic
            return CtyValue.unknown(CtyList(element_type=CtyDynamic())) # Corrected constructor

        # Inner element must be a list or tuple
        if not isinstance(outer_element_val.type, (CtyList, CtyTuple)):
            # If an element is not a list/tuple, it's an error according to go-cty flatten.
            # However, some implementations wrap it in a list. Here, we'll error.
            raise CtyFunctionError(
                f"flatten: all elements of the input list/tuple must themselves be lists or tuples; "
                f"found element of type {outer_element_val.type.ctype}"
            )

        inner_collection_elements = outer_element_val.value # This is a list/tuple of CtyValues

        for inner_element_val in inner_collection_elements:
            if not isinstance(inner_element_val, CtyValue):
                 raise CtyFunctionError("flatten: internal error - inner element is not a CtyValue.")

            result_elements.append(inner_element_val)

            current_inner_type = inner_element_val.type
            if final_element_type is None:
                final_element_type = current_inner_type
            elif not final_element_type.equals(current_inner_type):
                # If types diverge, the final list must be list(dynamic)
                # A more sophisticated version might try to find a common supertype.
                final_element_type = CtyDynamic()

    if not result_elements: # Flattening an empty list or list of empty lists
        # Determine element type from input if possible, else dynamic
        if isinstance(input_val.type, CtyList) and isinstance(input_val.type.element_type, (CtyList, CtyTuple)):
             # e.g. list(list(string)) -> list(string)
            inner_coll_type = input_val.type.element_type
            if isinstance(inner_coll_type, CtyList):
                final_element_type = inner_coll_type.element_type
            elif isinstance(inner_coll_type, CtyTuple) and inner_coll_type.element_types:
                # If tuple elements are uniform, use that, else dynamic for empty result
                if all(et.equals(inner_coll_type.element_types[0]) for et in inner_coll_type.element_types):
                    final_element_type = inner_coll_type.element_types[0]
                else:
                    final_element_type = CtyDynamic()
            else: # e.g. list(tuple()) or list(list(dynamic))
                final_element_type = CtyDynamic()

        elif isinstance(input_val.type, CtyTuple): # Input is tuple
            # If input tuple had elements, and they were all list/tuple types...
            # This gets complex to infer perfectly. Default to dynamic for empty result from tuple.
            final_element_type = CtyDynamic()
        else: # Fallback for empty results
            final_element_type = CtyDynamic()

    return CtyList(element_type=(final_element_type or CtyDynamic())).validate(result_elements)


def sort(input_val: CtyValue) -> CtyValue:
    """
    Sorts a list of primitive types (strings, numbers, bools).
    Elements must all be of the same primitive type or convertible to it.
    The primary type for comparison is determined by the first element if types are mixed but convertible.
    """
    if not isinstance(input_val.type, (CtyList, CtySet, CtyTuple)):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    if input_val.is_null or input_val.is_unknown:
        return input_val # Passthrough null/unknown

    elements_to_sort = list(input_val.value) # Convert set/tuple to list of CtyValues

    if not elements_to_sort:
        # Sorting an empty collection results in an empty list of the original element type (if list/set)
        # or list(dynamic) if input was empty tuple or set of mixed types.
        el_type: CtyType
        if isinstance(input_val.type, (CtyList, CtySet)):
            el_type = input_val.type.element_type
        else: # CtyTuple, even if empty, implies dynamic for list output
            el_type = CtyDynamic()
            return CtyList(element_type=el_type).validate([]) # Corrected constructor

    # Determine the sort type from the first element. All others must be compatible.
    first_element_type = elements_to_sort[0].type
    if not isinstance(first_element_type, (CtyString, CtyNumber, CtyBool)):
        raise CtyFunctionError(
            f"sort: elements must be string, number, or bool for sorting. Found type: {first_element_type.ctype}"
        )

    # Validate all elements are compatible with the first element's type and extract Python values for sorting
    py_values_to_sort = []
    for i, cty_element in enumerate(elements_to_sort):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

        try:
            # Attempt to validate/convert current element to the type of the first element
            # This ensures consistent comparison. e.g. if first is num, all become num.
            validated_to_first_type = first_element_type.validate(cty_element)
            py_values_to_sort.append(validated_to_first_type.value)
        except CtyValidationError:
            raise CtyFunctionError(
                f"sort: all elements must be compatible for sorting. Element at index {i} "
                f"of type {cty_element.type.ctype} is not compatible with first element type {first_element_type.ctype}."
            )

    try:
        # Python's list.sort() or sorted() can handle Decimal, str, bool directly.
        # For bools, False < True.
        sorted_py_values = sorted(py_values_to_sort)
    except TypeError as e: # Should not happen if all converted to same primitive type
        raise CtyFunctionError(f"sort: failed to sort elements. This may indicate an internal type issue. Error: {e}")

    # Convert sorted Python values back to CtyValues of the determined sort type
    sorted_cty_elements = [first_element_type.validate(pv) for pv in sorted_py_values]

    return CtyList(element_type=first_element_type).validate(sorted_cty_elements) # Corrected
