#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from itertools import product
from typing import Any, cast

from provide.foundation.errors import error_boundary

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
from pyvider.cty.config.defaults import (
    ERR_CHUNKLIST_ARGS_MUST_BE_LIST_AND_NUMBER,
    ERR_CHUNKLIST_SIZE_MUST_BE_POSITIVE,
    ERR_CHUNKLIST_SIZE_MUST_BE_WHOLE,
    ERR_DISTINCT_ELEMENT_NOT_HASHABLE,
    ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE,
    ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE,
    ERR_LENGTH_INPUT_MUST_BE_COLLECTION,
)
from pyvider.cty.conversion import infer_cty_type_from_raw
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._args import whole_number
from pyvider.cty.functions._marks import preserve_marks
from pyvider.cty.values.markers import RefinedUnknownValue


@preserve_marks
def distinct(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val
    seen = set()
    result_elements = []
    for cty_element in input_val.value:  # type: ignore[attr-defined]
        try:
            if cty_element not in seen:
                seen.add(cty_element)
                result_elements.append(cty_element)
        except TypeError as e:
            error_message = ERR_DISTINCT_ELEMENT_NOT_HASHABLE.format(type=cty_element.type.ctype, error=e)
            raise CtyFunctionError(error_message) from e
    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    return CtyList(element_type=element_type).validate(result_elements)  # type: ignore[no-any-return]


def _unwrap_dynamic(element: CtyValue[Any]) -> CtyValue[Any]:
    """The value a CtyDynamic wrapper stands in front of."""
    while isinstance(element.type, CtyDynamic) and isinstance(element.value, CtyValue):
        element = element.value
    return element


def _sequence_elements(seq: CtyValue[Any]) -> list[CtyValue[Any]]:
    """A sequence's elements in a stable order.

    A set has no order of its own, so it is given the same one that was used to
    de-duplicate it, rather than whatever the frozenset happens to iterate in.
    """
    if isinstance(seq.value, frozenset):
        return sorted(seq.value, key=lambda element: element._canonical_sort_key())
    return list(cast(tuple[CtyValue[Any], ...], seq.value))


def _flatten_elements(seq: CtyValue[Any]) -> tuple[list[CtyValue[Any]], bool]:
    """go-cty's `flattener` (cty/function/stdlib/collection.go), iteratively.

    Descends into any element that is itself a sequence, at any depth, and
    passes everything else through untouched -- including nulls, which are
    values in their own right, and a null *sequence*, which has no elements to
    descend into. An unknown sequence makes the whole result unknown, because
    its length decides the result's length and so the result's type.

    Iterative rather than recursive because the nesting it walks is the value's
    own, which can be as deep as validation allows.
    """
    out: list[CtyValue[Any]] = []
    known = True
    stack: list[list[CtyValue[Any]]] = [_sequence_elements(seq)[::-1]]
    while stack:
        frame = stack[-1]
        if not frame:
            stack.pop()
            continue
        element = _unwrap_dynamic(frame.pop())
        if element.is_unknown and isinstance(element.type, CtyDynamic | CtyList | CtySet | CtyTuple):
            known = False
        elif element.is_null or not isinstance(element.type, CtyList | CtySet | CtyTuple):
            out.append(element)
        else:
            stack.append(_sequence_elements(element)[::-1])
    return out, known


@preserve_marks
def flatten(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `FlattenFunc`: a sequence of sequences becomes one tuple.

    A tuple, not a list. Flattening a mixture of element types into a list
    would have to widen them all to dynamic to fit; a tuple carries each
    element's own type, which is why go-cty returns one.
    """
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        error_message = ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=input_val.type.ctype)
        raise CtyFunctionError(error_message)
    if input_val.is_null or input_val.is_unknown:
        return input_val

    elements, known = _flatten_elements(input_val)
    if not known:
        return CtyValue.unknown(CtyDynamic())
    result_type = CtyTuple(element_types=tuple(element.type for element in elements))
    # Built directly rather than through `validate`. The result type is derived
    # from the elements' own types, so validating each element against the type
    # taken from it is a no-op by construction -- one that cost more than the
    # flattening itself: 16 ms to 36 ms on a 10k-element input, because a tuple
    # type has one entry per element and each entry is entered separately.
    return CtyValue(vtype=result_type, value=tuple(elements))


@preserve_marks
def sort(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {input_val.type.ctype}")

    # A null list sorts to a null list.
    if input_val.is_null:
        return input_val

    if isinstance(input_val.type, CtyList | CtySet):
        collection_type = cast(CtyList[Any] | CtySet[Any], input_val.type)  # type: ignore[redundant-cast]
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")

    # Handle a truly unknown list (where the value is not iterable).
    if not hasattr(input_val.value, "__iter__"):
        if input_val.is_unknown:
            return input_val
        raise CtyFunctionError("sort: input value is not iterable")

    # Now, iterate through the elements. A known list containing a null or
    # unknown element must raise an error.
    value_iterable = cast(list[CtyValue[Any]] | tuple[CtyValue[Any], ...], input_val.value)
    for i, cty_element in enumerate(value_iterable):
        if cty_element.is_null or cty_element.is_unknown:
            raise CtyFunctionError(f"sort: cannot sort list with null or unknown elements at index {i}.")

    result: CtyValue[Any] = CtyList[Any](element_type=element_type).validate(
        sorted(value_iterable, key=lambda x: x.value)
    )
    return result


@preserve_marks
def length(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_length",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        # go-cty declares the parameter as DynamicPseudoType and type-checks the
        # *resolved* type, so a dynamic standing in front of a list is counted
        # while one standing in front of a string is refused, exactly as a bare
        # string is. A dynamic that is unknown or null has nothing to resolve to,
        # and go-cty lets DynamicPseudoType itself through the check so that the
        # answer can stay undecided rather than becoming an error.
        collection = _unwrap_dynamic(input_val)
        undecided = isinstance(collection.type, CtyDynamic)
        if not undecided and not isinstance(collection.type, CtyList | CtySet | CtyTuple | CtyMap):
            raise CtyFunctionError(ERR_LENGTH_INPUT_MUST_BE_COLLECTION.format(type=collection.type.ctype))
        if collection.is_unknown:
            if isinstance(collection.value, RefinedUnknownValue):
                lower = collection.value.collection_length_lower_bound
                upper = collection.value.collection_length_upper_bound
                if lower is not None and lower == upper:
                    return CtyNumber().validate(lower)
            return CtyValue.unknown(CtyNumber())
        # go-cty raises "argument must not be null" here. Left as an unknown to
        # move with the same deferred strictness change as `contains`.
        if collection.is_null or undecided:
            return CtyValue.unknown(CtyNumber())
        return CtyNumber().validate(len(collection.value))  # type: ignore[arg-type]


@preserve_marks
def slice(input_val: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {input_val.type.ctype}")
    if not isinstance(start_val.type, CtyNumber) or not isinstance(end_val.type, CtyNumber):
        raise CtyFunctionError("slice: start and end must be numbers")
    element_type = input_val.type.element_type if isinstance(input_val.type, CtyList) else CtyDynamic()
    if (
        input_val.is_null
        or input_val.is_unknown
        or start_val.is_null
        or start_val.is_unknown
        or end_val.is_null
        or end_val.is_unknown
    ):
        return CtyValue.unknown(CtyList(element_type=element_type))
    start, end = int(start_val.value), int(end_val.value)  # type: ignore[call-overload]
    return CtyList(element_type=element_type).validate(input_val.value[start:end])  # type: ignore[no-any-return,index]


@preserve_marks
def concat(*lists: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_concat",
            "num_lists": len(lists),
            "list_types": [str(lst.type) for lst in lists[:3]],  # First 3 for context
        }
    ):
        if not all(isinstance(lst.type, CtyList | CtyTuple) for lst in lists):
            raise CtyFunctionError("concat: all arguments must be lists or tuples")
        result_elements = []
        final_element_type: CtyType[Any] | None = None
        if any(lst.is_unknown for lst in lists):
            return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
        for lst in lists:
            if lst.is_null:
                continue
            for element in lst.value:  # type: ignore[attr-defined]
                if final_element_type is None:
                    final_element_type = element.type
                elif not final_element_type.equal(element.type):
                    final_element_type = CtyDynamic()
                result_elements.append(element)
        if final_element_type is None:
            return CtyList(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]
        return CtyList(element_type=final_element_type).validate(result_elements)  # type: ignore[no-any-return]


# Payloads that can hide an unknown below the top level. A CtyValue holding
# anything else is a leaf, so `is_unknown` is the complete answer for it.
_NESTING_PAYLOADS = (CtyValue, dict, list, tuple, set, frozenset)


def _is_known_leaf(value: CtyValue[Any]) -> bool:
    """Wholly known and non-null, decided without a walk.

    Nulls are excluded deliberately. `CtyValue.__eq__` requires the types to
    match, but `equals` treats nulls of any type as equal, as go-cty does -- so
    the `==` shortcut disagrees with the real comparison for a null of one type
    searched for in a collection of another. False here means "ask properly".
    """
    return not value.is_unknown and not value.is_null and not isinstance(value.value, _NESTING_PAYLOADS)


@preserve_marks
def contains(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )
    if collection.is_null:
        return CtyValue.unknown(CtyBool())

    # A collection reports itself unknown as soon as any element is unknown
    # (`list.py`, `tuple.py`, `set.py`), but it keeps its elements. Returning
    # undecided on that flag alone threw away an answer that was available: a
    # list holding "a" and an unknown definitely contains "a", whatever the
    # unknown turns out to be, and go-cty's ContainsFunc says so. Only a
    # collection with nothing to scan is genuinely undecidable here.
    elements = collection.value
    if not isinstance(elements, (tuple, frozenset, list)):
        return CtyValue.unknown(CtyBool())

    # An unknown element could still turn out to be the value being searched
    # for, so a miss against a partially-unknown collection is undecided rather
    # than false. An exact match still wins outright: it cannot be un-matched by
    # whatever the unknowns resolve to.
    #
    # Comparison goes through the three-valued `equals`, as go-cty's
    # ContainsFunc does. Testing `is_unknown` on the element is not enough --
    # an object whose attribute is unknown is itself known -- and treating any
    # element containing an unknown as undecided is needlessly vague, because an
    # element can still be ruled *out* on a known attribute that differs.
    #
    # But `equals` is far heavier than `==`, and most collections hold known
    # scalars, so each element gets a cheap test first: a leaf that is not
    # unknown is wholly known, decided by two attribute reads rather than a
    # walk. Only elements that could hide an unknown reach `equals`. The cheap
    # test must stay *per element* -- an is-anything-unknown pre-pass over the
    # whole collection would defeat the early exit, which is what makes finding
    # a hit near the front cost nothing.
    hit, saw_unknown = _scan_for_value(tuple(elements), value)
    if hit:
        return CtyBool().validate(True)
    if saw_unknown:
        return CtyValue.unknown(CtyBool())
    return CtyBool().validate(False)


def _scan_for_value(elements: tuple[Any, ...], value: CtyValue[Any]) -> tuple[bool, bool]:
    """Scan for `value`, returning (found, saw_something_undecided)."""
    value_known = value.is_wholly_known() and not value.is_null
    saw_unknown = False
    for element_value in elements:
        if not isinstance(element_value, CtyValue):
            if element_value == value:
                return True, saw_unknown
            continue
        if value_known and _is_known_leaf(element_value):
            # Both sides wholly known, so `==` is the whole answer either way.
            if element_value == value:
                return True, saw_unknown
            continue
        match = element_value.equals(value)
        if match.is_unknown:
            saw_unknown = True
        elif match.value is True:
            return True, saw_unknown
    return False, saw_unknown


@preserve_marks
def keys(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_keys",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"keys: input must be a map or object, got {input_val.type.ctype}")
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=CtyString()))
        result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
            sorted(list(input_val.value.keys()))  # type: ignore[attr-defined]
        )
        return result


@preserve_marks
def values(input_val: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_values",
            "input_type": str(input_val.type),
            "input_is_null": input_val.is_null,
            "input_is_unknown": input_val.is_unknown,
        }
    ):
        if not isinstance(input_val.type, CtyMap | CtyObject):
            raise CtyFunctionError(f"values: input must be a map or object, got {input_val.type.ctype}")
        elem_type = input_val.type.element_type if isinstance(input_val.type, CtyMap) else CtyDynamic()
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(CtyList(element_type=elem_type))
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError("values: input value is not a map or object")
        return CtyList(element_type=elem_type).validate(list(input_val.value.values()))  # type: ignore[no-any-return]


@preserve_marks
def reverse(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(input_val.value)))  # type: ignore[no-any-return,call-overload]


@preserve_marks
def hasindex(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(CtyBool())
    if collection.is_null:
        return CtyBool().validate(False)
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber) or key.is_null:
            return CtyBool().validate(False)
        idx = int(key.value)  # type: ignore[call-overload]
        return CtyBool().validate(0 <= idx < len(collection.value))  # type: ignore[arg-type]
    if isinstance(collection.type, CtyMap | CtyObject):
        if not isinstance(key.type, CtyString) or key.is_null:
            return CtyBool().validate(False)
        return CtyBool().validate(key.value in collection.value)  # type: ignore[operator]
    raise CtyFunctionError(
        f"hasindex: collection must be a list, tuple, map, or object, got {collection.type.ctype}"
    )


@preserve_marks
def index(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


@preserve_marks
def element(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    with error_boundary(
        context={
            "operation": "cty_function_element",
            "collection_type": str(collection.type),
            "index_type": str(idx.type),
            "collection_is_null": collection.is_null,
            "collection_is_unknown": collection.is_unknown,
        }
    ):
        if not isinstance(collection.type, CtyList | CtyTuple):
            raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection.type}")
        if collection.is_null or collection.is_unknown or idx.is_null or idx.is_unknown:
            elem_type = collection.type.element_type if isinstance(collection.type, CtyList) else CtyDynamic()
            return CtyValue.unknown(elem_type)
        length = len(collection.value)  # type: ignore[arg-type]
        if length == 0:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        return collection.value[int(idx.value) % length]  # type: ignore[no-any-return,index,call-overload]


@preserve_marks
def coalescelist(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


@preserve_marks
def compact(collection: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    if isinstance(collection.type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection.type.element_types):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")
    else:
        collection_type = cast(CtyList[Any] | CtySet[Any], collection.type)  # type: ignore[redundant-cast]
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError("compact: argument must be a list, set, or tuple of strings")

    if collection.is_null or collection.is_unknown:
        return collection
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(
        [v for v in collection.value if v.value]  # type: ignore[attr-defined]
    )
    return result


def _chunk_element_type(collection: CtyValue[Any]) -> CtyType[Any]:
    """The type the chunks hold.

    go-cty's return type is `cty.List(args[0].Type())` -- the argument's own
    type, element type included, rather than dynamic. Its parameter is declared
    as `list(dynamic)`, which its conversion layer refuses a tuple for; this
    accepts one anyway and unifies the element types, which costs nothing and
    keeps a working call working.
    """
    if isinstance(collection.type, CtyList):
        return collection.type.element_type
    return unify(list(cast(CtyTuple, collection.type).element_types))


def _chunk_size(size: CtyValue[Any]) -> int:
    """The chunk size, or a refusal. Zero is legal and means "one chunk"."""
    count = whole_number(size, ERR_CHUNKLIST_SIZE_MUST_BE_WHOLE)
    if count < 0:
        raise CtyFunctionError(ERR_CHUNKLIST_SIZE_MUST_BE_POSITIVE)
    return count


@preserve_marks
def chunklist(collection: CtyValue[Any], size: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ChunklistFunc`: a sequence split into fixed-size chunks."""
    if not isinstance(collection.type, CtyList | CtyTuple) or not isinstance(size.type, CtyNumber):
        raise CtyFunctionError(ERR_CHUNKLIST_ARGS_MUST_BE_LIST_AND_NUMBER)
    if collection.is_null or collection.is_unknown or size.is_null or size.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyList(element_type=CtyDynamic())))

    result_type = CtyList(element_type=CtyList(element_type=_chunk_element_type(collection)))
    chunk_size = _chunk_size(size)
    elements = list(cast(tuple[CtyValue[Any], ...], collection.value))
    if not elements:
        return cast(CtyValue[Any], result_type.validate([]))
    if chunk_size == 0:
        # go-cty: "if size is 0, returns a list made of the initial list".
        return cast(CtyValue[Any], result_type.validate([elements]))
    chunks = [elements[i : i + chunk_size] for i in range(0, len(elements), chunk_size)]
    return cast(CtyValue[Any], result_type.validate(chunks))


@preserve_marks
def lookup(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        return CtyValue.unknown(unify([element_type, default.type]))

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


@preserve_marks
def merge(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyMap | CtyObject) for arg in args):
        raise CtyFunctionError("merge: all arguments must be maps or objects")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    result: dict[str, Any] = {}
    for arg in args:
        if not arg.is_null:
            result.update(arg.value)  # type: ignore[call-overload]

    inferred_type = infer_cty_type_from_raw(result)
    return inferred_type.validate(result)


@preserve_marks
def setproduct(*args: CtyValue[Any]) -> CtyValue[Any]:
    if not all(isinstance(arg.type, CtyList | CtySet | CtyTuple) for arg in args):
        raise CtyFunctionError("setproduct: all arguments must be collections")
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtySet(element_type=CtyDynamic()))

    iterables = [list(arg.value) for arg in args if not arg.is_null]  # type: ignore[call-overload]
    if not iterables:
        return CtySet(element_type=CtyDynamic()).validate([])  # type: ignore[no-any-return]

    prod = product(*iterables)
    result_tuples = [tuple(item) for item in prod]

    elem_types = []
    for arg in args:
        if not arg.is_null:
            if isinstance(arg.type, CtyList | CtySet):
                arg_type_cast = cast(CtyList[Any] | CtySet[Any], arg.type)  # type: ignore[redundant-cast]
                elem_types.append(arg_type_cast.element_type)
            else:
                elem_types.append(CtyDynamic())
    tuple_type = CtyTuple(element_types=tuple(elem_types))

    return CtySet(element_type=tuple_type).validate(result_tuples)  # type: ignore[no-any-return]


@preserve_marks
def zipmap(keys: CtyValue[Any], values: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(keys.type, CtyList | CtyTuple) or not isinstance(values.type, CtyList | CtyTuple):
        raise CtyFunctionError("zipmap: arguments must be lists or tuples")
    if keys.is_unknown or values.is_unknown:
        return CtyValue.unknown(CtyMap(element_type=CtyDynamic()))
    if keys.is_null or values.is_null:
        return CtyMap(element_type=CtyDynamic()).validate({})  # type: ignore[no-any-return]

    key_list = [k.value for k in keys.value]  # type: ignore[attr-defined]
    val_list = list(values.value)  # type: ignore[call-overload]

    result_map = {key_list[i]: val_list[i] for i in range(min(len(key_list), len(val_list)))}

    val_elem_type = values.type.element_type if isinstance(values.type, CtyList) else CtyDynamic()
    return CtyMap(element_type=val_elem_type).validate(result_map)  # type: ignore[no-any-return]


# 🌊🪢🔚
