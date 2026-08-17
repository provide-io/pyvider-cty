#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal
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
    ERR_CHUNKLIST_TUPLE_NOT_UNIFIABLE,
    ERR_CONCAT_ARG_MUST_NOT_BE_NULL,
    ERR_CONCAT_ARGS_MUST_BE_SEQUENCES,
    ERR_CONCAT_REQUIRES_ONE,
    ERR_DISTINCT_ELEMENT_NOT_HASHABLE,
    ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE,
    ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE,
    ERR_KEYS_INPUT_MUST_BE_MAP_OBJECT,
    ERR_LENGTH_INPUT_MUST_BE_COLLECTION,
    ERR_MERGE_ALL_ARGS_MUST_BE_MAPS_OBJECTS,
    ERR_RANGE_ARG_COUNT,
    ERR_RANGE_ARGS_MUST_BE_NUMBERS,
    ERR_RANGE_END_MUST_BE_GREATER,
    ERR_RANGE_END_MUST_BE_LESS,
    ERR_RANGE_STEP_MUST_NOT_BE_ZERO,
    ERR_RANGE_TOO_MANY_VALUES,
    ERR_SETPRODUCT_ARG_MUST_BE_COLLECTION,
    ERR_SETPRODUCT_ARG_MUST_NOT_BE_NULL,
    ERR_SETPRODUCT_REQUIRES_TWO,
    ERR_SETPRODUCT_TUPLE_NOT_UNIFIABLE,
    ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT,
    MAX_RANGE_LENGTH,
)
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._args import whole_number
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.values.markers import RefinedUnknownValue


@stdlib_function("distinct")
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


@stdlib_function("flatten")
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


@stdlib_function("sort")
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


@stdlib_function("length")
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


@stdlib_function("slice")
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


@stdlib_function("concat")
def concat(*sequences: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ConcatFunc`.

    A list when every argument is a list *and* their element types unify, and a
    tuple otherwise -- because a tuple is the only type that can carry a
    different type per position, which is what concatenating a `list(number)`
    with a `list(bool)` produces.

    This used to derive the element type from the elements themselves, widening
    to dynamic at the first mismatch, so `concat(list(string), list(number))`
    came back a `list(dynamic)` holding the originals where go-cty returns a
    `list(string)` holding `["a", "1"]`. Both halves were wrong: no unification,
    and no tuple fallback.
    """
    if not sequences:
        raise CtyFunctionError(ERR_CONCAT_REQUIRES_ONE)
    for sequence in sequences:
        if not isinstance(sequence.type, CtyList | CtyTuple):
            raise CtyFunctionError(ERR_CONCAT_ARGS_MUST_BE_SEQUENCES.format(type=sequence.type.ctype))
    if any(sequence.is_null for sequence in sequences):
        raise CtyFunctionError(ERR_CONCAT_ARG_MUST_NOT_BE_NULL)

    if all(isinstance(sequence.type, CtyList) for sequence in sequences):
        unified = unify([sequence.type for sequence in sequences])
        if isinstance(unified, CtyList):
            if any(sequence.is_unknown for sequence in sequences):
                # The type is settled even though the contents are not.
                return CtyValue.unknown(unified)
            converted = [
                convert(element, unified.element_type)
                for sequence in sequences
                for element in cast(Iterable[CtyValue[Any]], sequence.value)
            ]
            return cast(CtyValue[Any], unified.validate(converted))

    elements: list[CtyValue[Any]] = []
    for sequence in sequences:
        if sequence.is_unknown:
            # A tuple type has one entry per element, so it cannot be built
            # without knowing how many elements there are.
            return CtyValue.unknown(CtyDynamic())
        elements.extend(cast(Iterable[CtyValue[Any]], sequence.value))

    result_type = CtyTuple(element_types=tuple(element.type for element in elements))
    # Built directly: the type is derived from the elements' own types, so
    # validating each against the type taken from it is a no-op by construction.
    return CtyValue(vtype=result_type, value=tuple(elements))


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


@stdlib_function("contains", allow_null=(1,))
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


@stdlib_function("keys")
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
            raise CtyFunctionError(ERR_KEYS_INPUT_MUST_BE_MAP_OBJECT.format(type=input_val.type.ctype))
        if isinstance(input_val.type, CtyObject):
            # An object's attribute names are fixed by its type, so go-cty can
            # and does give the result a tuple type with one entry per
            # attribute rather than a list.
            names = sorted(input_val.type.attribute_types)
            object_type = CtyTuple(element_types=(CtyString(),) * len(names))
            if input_val.is_null or input_val.is_unknown:
                return CtyValue.unknown(object_type)
            return cast(CtyValue[Any], object_type.validate(tuple(names)))

        result_type = CtyList(element_type=CtyString())
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(result_type)
        return cast(CtyValue[Any], result_type.validate(sorted(cast(Mapping[str, Any], input_val.value))))


@stdlib_function("values")
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
            raise CtyFunctionError(ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT.format(type=input_val.type.ctype))

        # Lexicographic by key, which is not a property of this function but of
        # the types: "cty guarantees that these types always iterate in key
        # lexicographical order". Returning them in insertion order meant `keys`
        # and `values` no longer corresponded, so `zipmap(keys(m), values(m))`
        # paired every value with the wrong key.
        if isinstance(input_val.type, CtyObject):
            attribute_types = input_val.type.attribute_types
            names = sorted(attribute_types)
            # A tuple rather than a list: an object's attributes have differing
            # types, and a list would have to widen them all to dynamic.
            object_type = CtyTuple(element_types=tuple(attribute_types[name] for name in names))
            if input_val.is_null or input_val.is_unknown:
                return CtyValue.unknown(object_type)
            payload = cast(Mapping[str, CtyValue[Any]], input_val.value)
            return cast(CtyValue[Any], object_type.validate(tuple(payload[name] for name in names)))

        result_type = CtyList(element_type=input_val.type.element_type)
        if input_val.is_null or input_val.is_unknown:
            return CtyValue.unknown(result_type)
        if not isinstance(input_val.value, dict):
            raise CtyFunctionError(ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT.format(type=input_val.type.ctype))
        mapping = cast(Mapping[str, CtyValue[Any]], input_val.value)
        return cast(CtyValue[Any], result_type.validate([mapping[name] for name in sorted(mapping)]))


@stdlib_function("reverselist")
def reverse(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyList | CtyTuple):
        raise CtyFunctionError("reverse: input must be a list or tuple")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return input_val.type.validate(list(reversed(input_val.value)))  # type: ignore[no-any-return,call-overload]


@stdlib_function("hasindex")
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


@stdlib_function("index")
def index(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    if not hasindex(collection, key).value:
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        key_val = int(key_val)  # type: ignore[call-overload]

    return collection[key_val]


@stdlib_function("element")
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


@stdlib_function("coalescelist", allow_null=True)
def coalescelist(*args: CtyValue[Any]) -> CtyValue[Any]:
    if any(v.is_unknown for v in args):
        return CtyValue.unknown(CtyDynamic())
    for arg in args:
        if (
            isinstance(arg.type, CtyList | CtyTuple) and not arg.is_null and len(arg.value) > 0  # type: ignore[arg-type]
        ):
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


@stdlib_function("compact")
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
    # A tuple whose elements have no common type has no list form, and so
    # nothing to chunk. `unify` used to answer dynamic for that, which produced
    # a `list(dynamic)` of values that had never been converted to anything.
    unified = unify(cast(CtyTuple, collection.type).element_types)
    if unified is None:
        raise CtyFunctionError(ERR_CHUNKLIST_TUPLE_NOT_UNIFIABLE)
    return unified


def _chunk_size(size: CtyValue[Any]) -> int:
    """The chunk size, or a refusal. Zero is legal and means "one chunk"."""
    count = whole_number(size, ERR_CHUNKLIST_SIZE_MUST_BE_WHOLE)
    if count < 0:
        raise CtyFunctionError(ERR_CHUNKLIST_SIZE_MUST_BE_POSITIVE)
    return count


@stdlib_function("chunklist")
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


@stdlib_function("lookup")
def lookup(collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(collection.type, CtyMap | CtyObject):
        raise CtyFunctionError("lookup: collection must be a map or object")

    element_type = collection.type.element_type if isinstance(collection.type, CtyMap) else CtyDynamic()

    if collection.is_unknown or key.is_unknown:
        # The result is either an element or the default, so its type is
        # whatever covers both; dynamic when nothing does, since an unknown of
        # dynamic is a claim about nothing rather than a wrong claim.
        return CtyValue.unknown(unify([element_type, default.type]) or CtyDynamic())

    if (
        collection.is_null
        or key.is_null
        or not isinstance(collection.value, dict)
        or key.value not in collection.value
    ):
        return default

    return collection.value[key.value]  # type: ignore[no-any-return]


def _merge_one(arg: CtyValue[Any], attribute_types: dict[str, CtyType[Any]]) -> tuple[CtyType[Any], bool]:
    """Fold one merge argument's attributes into `attribute_types`.

    Returns the type this argument contributes to the all-arguments-match test,
    and whether the attribute set is still fully known after it.
    """
    arg_type = arg.type
    if isinstance(arg_type, CtyObject):
        # A null object is treated as having no attributes at all, and it
        # compares against the other arguments as the empty object type.
        if arg.is_null:
            return CtyObject(attribute_types={}), True
        attribute_types.update(arg_type.attribute_types)
        return arg_type, True

    if not isinstance(arg_type, CtyMap):
        raise CtyFunctionError(ERR_MERGE_ALL_ARGS_MUST_BE_MAPS_OBJECTS)
    if arg.is_null:
        return arg_type, True  # Contributes nothing, but its type still counts.
    if arg.is_unknown:
        # Its keys are exactly what is unknown about it, so the attribute set
        # of the result cannot be predicted.
        return arg_type, False

    element_type = arg_type.element_type
    for key in cast(Mapping[str, Any], arg.value):
        attribute_types[key] = element_type
    return arg_type, True


def _merge_result_type(args: tuple[CtyValue[Any], ...]) -> CtyType[Any] | None:
    """The type go-cty's MergeFunc declares for these arguments.

    None stands for go-cty's DynamicPseudoType, which it uses both when an
    argument's own type is dynamic and when a mix of unknown maps leaves the
    attribute set unknowable.
    """
    attribute_types: dict[str, CtyType[Any]] = {}
    first: CtyType[Any] | None = None
    matching = True
    attributes_known = True

    for index, arg in enumerate(args):
        # Checked inside the loop rather than up front, because go-cty gives up
        # at the first dynamic argument and so never reaches a later argument
        # that would have been rejected outright.
        if isinstance(arg.type, CtyDynamic):
            return None
        arg_type, known = _merge_one(arg, attribute_types)
        attributes_known = attributes_known and known
        if index == 0:
            first = arg_type
        elif matching and arg_type != first:
            matching = False

    # Every argument had the same type, so the result keeps it -- which is how a
    # merge of maps stays a map rather than collapsing into an object.
    if matching:
        return first
    if not attributes_known:
        return None
    return CtyObject(attribute_types=attribute_types)


@stdlib_function("merge", allow_null=True)
def merge(*args: CtyValue[Any]) -> CtyValue[Any]:
    # No arguments gives an empty object: there are no key-value types to read.
    if not args:
        return cast(CtyValue[Any], CtyObject(attribute_types={}).validate({}))

    # Unwrapped first, because dynamic means two different things in the two
    # packages: in go-cty a known value never carries DynamicPseudoType, so its
    # rules for a dynamic argument are rules about a value whose type is not yet
    # settled. Here a dynamic wrapper routinely stands in front of a perfectly
    # concrete map or object, and that inner type is the one go-cty would see.
    args = tuple(_unwrap_dynamic(arg) for arg in args)

    result_type = _merge_result_type(args)
    if any(arg.is_unknown for arg in args):
        return CtyValue.unknown(result_type if result_type is not None else CtyDynamic())

    merged: dict[str, CtyValue[Any]] = {}
    for arg in args:
        if not arg.is_null:
            merged.update(cast(Mapping[str, CtyValue[Any]], arg.value))

    if result_type is None:
        # go-cty declares dynamic here but still returns a concrete ObjectVal,
        # so the value describes itself even though the signature could not.
        result_type = CtyObject(attribute_types={name: value.type for name, value in merged.items()})
    return cast(CtyValue[Any], result_type.validate(merged))


def _setproduct_element_type(arg: CtyValue[Any]) -> tuple[CtyType[Any], bool]:
    """One argument's contribution to the result element type, and whether it is ordered."""
    arg_type = arg.type
    if isinstance(arg_type, CtySet):
        return arg_type.element_type, False
    if isinstance(arg_type, CtyList):
        return arg_type.element_type, True
    if isinstance(arg_type, CtyTuple):
        # go-cty unifies a tuple's element types (`collection.go:958`), so a
        # tuple of mixed primitives reaches the `unify` gap recorded in the
        # tracker: string there, dynamic here. An empty tuple is dynamic in
        # both.
        if not arg_type.element_types:
            return CtyDynamic(), True
        unified = unify(arg_type.element_types)
        if unified is None:
            raise CtyFunctionError(ERR_SETPRODUCT_TUPLE_NOT_UNIFIABLE)
        return unified, True
    raise CtyFunctionError(ERR_SETPRODUCT_ARG_MUST_BE_COLLECTION.format(type=arg_type.ctype))


@stdlib_function("setproduct")
def setproduct(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SetProductFunc`.

    The result is a **list** when every argument is ordered, and a set only when
    one of them is a set (`collection.go:975`). This always built a set, so the
    ordering a caller asked for by passing lists was discarded -- and the
    function's own docstring in go-cty is that lists and tuples "preserve the
    input ordering".
    """
    if len(args) < 2:
        raise CtyFunctionError(ERR_SETPRODUCT_REQUIRES_TWO)

    element_types: list[CtyType[Any]] = []
    ordered = 0
    for arg in args:
        element_type, is_ordered = _setproduct_element_type(arg)
        element_types.append(element_type)
        ordered += is_ordered

    tuple_type = CtyTuple(element_types=tuple(element_types))
    result_type: CtyType[Any] = (
        CtyList(element_type=tuple_type) if ordered == len(args) else CtySet(element_type=tuple_type)
    )

    # The result type is computable from the argument types alone, so an
    # unknown argument makes the value unknown without making the type dynamic.
    if any(arg.is_unknown for arg in args):
        return CtyValue.unknown(result_type)

    # A null argument used to be dropped, which changed the arity of the result
    # tuple according to which arguments happened to be null. go-cty refuses it
    # outright, and so does this -- a type that varies with the data is a
    # different fault from the null-argument policy question.
    if any(arg.is_null for arg in args):
        raise CtyFunctionError(ERR_SETPRODUCT_ARG_MUST_NOT_BE_NULL)

    iterables = [list(cast(Iterable[Any], arg.value)) for arg in args]
    result_tuples = [tuple(item) for item in product(*iterables)]

    return result_type.validate(result_tuples)


@stdlib_function("zipmap")
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


def _range_bounds(numbers: list[Decimal]) -> tuple[Decimal, Decimal, Decimal]:
    """go-cty's start/end/step defaulting for one, two or three arguments.

    With fewer than three the step is inferred from the direction of travel, so
    `range(5, 1)` counts down rather than raising.
    """
    match numbers:
        case [end]:
            return Decimal(0), end, Decimal(-1) if end < 0 else Decimal(1)
        case [start, end]:
            return start, end, Decimal(-1) if end < start else Decimal(1)
        case [start, end, step]:
            return start, end, step
        case _:
            raise CtyFunctionError(ERR_RANGE_ARG_COUNT)


@stdlib_function("range")
def range_fn(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `RangeFunc`. Named with a suffix to leave the builtin alone."""
    for arg in args:
        if not isinstance(arg.type, CtyNumber):
            raise CtyFunctionError(ERR_RANGE_ARGS_MUST_BE_NUMBERS.format(type=arg.type.ctype))
        if arg.is_null:
            raise CtyFunctionError(ERR_RANGE_ARGS_MUST_BE_NUMBERS.format(type="null"))
    if any(arg.is_unknown for arg in args):
        return CtyValue.unknown(CtyList(element_type=CtyNumber()))

    start, end, step = _range_bounds([cast(Decimal, arg.value) for arg in args])
    if step == 0:
        # go-cty checks this with `step == cty.Zero`, which compares two structs
        # holding different big.Float pointers and so never fires: a zero step
        # loops until the 1024 cap and reports that instead. Refused cleanly
        # here, the same call this package already makes for `indent`'s negative
        # count. Both implementations refuse; only the message differs.
        raise CtyFunctionError(ERR_RANGE_STEP_MUST_NOT_BE_ZERO)

    descending = step < 0
    if descending and end > start:
        raise CtyFunctionError(ERR_RANGE_END_MUST_BE_LESS)
    if not descending and end < start:
        raise CtyFunctionError(ERR_RANGE_END_MUST_BE_GREATER)

    numbers: list[Decimal] = []
    current = start
    while current > end if descending else current < end:
        if len(numbers) >= MAX_RANGE_LENGTH:
            raise CtyFunctionError(ERR_RANGE_TOO_MANY_VALUES.format(limit=MAX_RANGE_LENGTH))
        numbers.append(current)
        current += step
    return cast(CtyValue[Any], CtyList(element_type=CtyNumber()).validate(numbers))


# 🌊🪢🔚
