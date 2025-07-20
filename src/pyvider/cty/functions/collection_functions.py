from typing import Any

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError


def distinct(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"distinct: input must be a list, set, or tuple, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            raise CtyFunctionError(
                f"distinct: element of type {cty_element.type.ctype} is not hashable. Error: {e}"
            ) from e
    return CtyList(element_type=input_val.type.element_type).validate(result_elements)  # type: ignore


def _get_element_type(t: "CtyType[Any]") -> "CtyType[Any]":
    if isinstance(t, CtyList):
        return t.element_type
    if isinstance(t, CtyTuple):
        # This is a simplification. A more robust implementation would find a
        # common type.
        return t.element_types[0].element_type if t.element_types and isinstance(t.element_types[0], CtyList) else CtyDynamic()
    return CtyDynamic()


def flatten(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(
            f"flatten: input must be a list or tuple, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val
    result_elements = []
    final_element_type: CtyType[Any] | None = None
    for outer_element_val in input_val.value:  # type: ignore
        if outer_element_val.is_null:
            continue
        if outer_element_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        if not isinstance(outer_element_val.type, CtyList | CtyTuple):
            raise CtyFunctionError(
                f"flatten: all elements must be lists or tuples; found {outer_element_val.type.ctype}"
            )
        for inner_element_val in outer_element_val.value:
            if final_element_type is None:
                final_element_type = inner_element_val.type
            elif not final_element_type.equal(inner_element_val.type):
                final_element_type = CtyDynamic()
            result_elements.append(inner_element_val)
    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])
    return CtyList(element_type=final_element_type).validate(result_elements)


def sort(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return input_val

    element_type = input_val.type.element_type  # type: ignore
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(
            f"sort: elements must be string, number, or bool. Found: {element_type.ctype}"
        )

    for i, cty_element in enumerate(input_val.value):  # type: ignore
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(
                f"sort: cannot sort list with null or unknown elements at index {i}."
            )

    return CtyList(element_type=element_type).validate(
        sorted(input_val.value, key=lambda x: x.value)  # type: ignore
    )


def length(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple | CtyMap):
        raise CtyFunctionError(
            f"length: input must be a list, set, tuple, or map, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyNumber())
    return CtyNumber().validate(len(input_val.value))  # type: ignore


def slice(
    input_val: "CtyValue[Any]", start_val: "CtyValue[Any]", end_val: "CtyValue[Any]"
) -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(
            f"slice: input must be a list or tuple, got {input_val.type.ctype}"
        )
    if not isinstance(start_val.type, CtyNumber) or not isinstance(
        end_val.type, CtyNumber
    ):
        raise CtyFunctionError("slice: start and end must be numbers")
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(input_val.type)

    start = int(start_val.value)  # type: ignore
    end = int(end_val.value)  # type: ignore
    return CtyList(
        element_type=input_val.type.element_type
    ).validate(  # type: ignore
        input_val.value[start:end]  # type: ignore
    )


def concat(*lists: "CtyValue[Any]") -> "CtyValue[Any]":
    if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
        raise CtyFunctionError("concat: all arguments must be lists or tuples")

    result_elements = []
    final_element_type: CtyType[Any] | None = None
    for lst in lists:
        if lst.is_null or lst.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for element in lst.value:  # type: ignore
            if final_element_type is None:
                final_element_type = element.type
            elif not final_element_type.equal(element.type):
                final_element_type = CtyDynamic()
            result_elements.append(element)

    if final_element_type is None:
        return CtyList(element_type=CtyDynamic()).validate([])
    return CtyList(element_type=final_element_type).validate(result_elements)


def contains(collection: "CtyValue[Any]", value: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )
    if collection.is_null or collection.is_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(value in collection.value)  # type: ignore


def keys(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyMap):
        raise CtyFunctionError(f"keys: input must be a map, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))
    return CtyList(element_type=CtyString()).validate(list(input_val.value.keys()))  # type: ignore


def values(input_val: "CtyValue[Any]") -> "CtyValue[Any]":
    if not isinstance(input_val.type, CtyMap):
        raise CtyFunctionError(
            f"values: input must be a map, got {input_val.type.ctype}"
        )
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=input_val.type.element_type))  # type: ignore
    return CtyList(element_type=input_val.type.element_type).validate(  # type: ignore
        list(input_val.value.values())  # type: ignore
    )
