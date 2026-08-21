#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The collection functions that reorder or reshape a sequence.

`distinct`, `flatten`, `sort`, `slice`, `concat`, `reverse`, `coalescelist`,
`compact`, `chunklist` and `range`. go-cty's `stdlib/collection.go` and
`stdlib/sequence.go`; see the package docstring for the declared-policy model
and the two deliberate departures.
"""

from __future__ import annotations

from collections.abc import Iterable, Sized
from decimal import Decimal
from typing import Any, cast

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
    unify,
)
from pyvider.cty.config.defaults import (
    ERR_CHUNKLIST_ARGS_MUST_BE_LIST_AND_NUMBER,
    ERR_CHUNKLIST_SIZE_MUST_BE_POSITIVE,
    ERR_CHUNKLIST_SIZE_MUST_BE_WHOLE,
    ERR_CHUNKLIST_TUPLE_NOT_UNIFIABLE,
    ERR_CONCAT_ARGS_MUST_BE_SEQUENCES,
    ERR_CONCAT_REQUIRES_ONE,
    ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE,
    ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE,
    ERR_RANGE_ARG_COUNT,
    ERR_RANGE_END_MUST_BE_GREATER,
    ERR_RANGE_END_MUST_BE_LESS,
    ERR_RANGE_TOO_MANY_VALUES,
    MAX_RANGE_LENGTH,
)
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._args import whole_number
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null
from pyvider.cty.functions.collection._shared import (
    Args,
    _sequence_elements,
    _set_length_is_known,
)
from pyvider.cty.types.structural.dynamic import unwrap_dynamic

# ---------------------------------------------------------------------------
# distinct
# ---------------------------------------------------------------------------


def _distinct_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `DistinctFunc.Type`: `args[0].Type()` (`collection.go:386`).

    A set and a tuple reach here only because the parameter is widened; go-cty's
    `list(dynamic)` refuses both. Each becomes the list it would have been
    converted to.
    """
    collection_type = args[0].type
    if isinstance(collection_type, CtyList):
        return collection_type
    if isinstance(collection_type, CtySet):
        return CtyList(element_type=collection_type.element_type)
    if isinstance(collection_type, CtyTuple):
        return CtyList(element_type=CtyDynamic())
    raise CtyFunctionError(ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=collection_type.ctype))


@stdlib_function(
    "distinct",
    params=[CtyParameter("list", CtyDynamic())],
    type_func=_distinct_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Removes any duplicate values from the given list, preserving the order of remaining elements.",
)
def distinct(input_val: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `DistinctFunc` (`stdlib/collection.go:378`).

    De-duplicating asks whether two elements are equal, and two unknowns of the
    same type answer "maybe" -- but a Python `set` sees them as one and drops the
    second, asserting they will resolve alike. The result's length is undecided
    for the same reason, so go-cty declines the whole answer as soon as any
    element is not known rather than guessing either.
    """
    if not input_val.is_wholly_known():
        return CtyValue.unknown(return_type)

    # go-cty compares with the three-valued `Equal`, one element at a time
    # (`appendIfMissing`); a `set` reaches the same answer for wholly-known
    # values in one pass instead of n². It guarded against an unhashable element
    # until 2026-08-17, when `CtyValue.__hash__` started hashing containers --
    # the guard's own message said "element of type {type} is not hashable",
    # which is no longer a thing an element can be.
    seen: set[CtyValue[Any]] = set()
    result_elements: list[CtyValue[Any]] = []
    for cty_element in cast("Iterable[CtyValue[Any]]", input_val.value):
        if cty_element not in seen:
            seen.add(cty_element)
            result_elements.append(cty_element)
    return return_type.validate(result_elements)


# ---------------------------------------------------------------------------
# flatten
# ---------------------------------------------------------------------------


def _flatten_elements(seq: CtyValue[Any]) -> tuple[list[CtyValue[Any]], bool]:
    """go-cty's `flattener` (`stdlib/collection.go:542`), iteratively.

    Descends into any element that is itself a sequence, at any depth, and
    passes everything else through untouched -- including nulls, which are
    values in their own right, and a null *sequence*, which has no elements to
    descend into. An unknown sequence makes the whole result unknown, because
    its length decides the result's length and so the result's type.

    Iterative rather than recursive because the nesting it walks is the value's
    own, which can be as deep as validation allows.
    """
    if not _flattenable_length_is_known(seq):
        return [], False
    out: list[CtyValue[Any]] = []
    known = True
    stack: list[list[CtyValue[Any]]] = [_sequence_elements(seq)[::-1]]
    while stack:
        frame = stack[-1]
        if not frame:
            stack.pop()
            continue
        element = unwrap_dynamic(frame.pop())
        if element.is_unknown and isinstance(element.type, CtyDynamic | CtyList | CtySet | CtyTuple):
            known = False
        elif element.is_null or not isinstance(element.type, CtyList | CtySet | CtyTuple):
            out.append(element)
        elif not _flattenable_length_is_known(element):
            # go-cty's `flattener` opens with `if !flattenList.Length().IsKnown()`
            # and gives up on the whole result there (`collection.go:549`), so a
            # set holding an unknown makes `flatten` answer an unknown of dynamic
            # type rather than a tuple. This descended into it and produced a
            # tuple whose length go-cty does not claim to know.
            known = False
        else:
            stack.append(_sequence_elements(element)[::-1])
    return out, known


def _flattenable_length_is_known(seq: CtyValue[Any]) -> bool:
    """Whether `flatten` can predict how many elements a sequence contributes."""
    if not isinstance(seq.type, CtySet):
        return True
    return _set_length_is_known(seq, len(cast("Sized", seq.value)))


def _flatten_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `FlattenFunc.Type` (`collection.go:500`).

    The wholly-known test comes *first*, as it does there, so an unknown of any
    type answers dynamic rather than being refused for its shape -- the shape is
    not what is in doubt.
    """
    collection = args[0]
    if not collection.is_wholly_known():
        return CtyDynamic()
    collection_type = collection.type
    if not isinstance(collection_type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE.format(type=collection_type.ctype))
    elements, known = _flatten_elements(collection)
    if not known:
        return CtyDynamic()
    return CtyTuple(element_types=tuple(element.type for element in elements))


@stdlib_function(
    "flatten",
    params=[CtyParameter("list", CtyDynamic())],
    type_func=_flatten_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Transforms a list, set, or tuple value into a tuple by replacing any given elements that "
        "are themselves sequences with a flattened tuple of all of the nested elements concatenated "
        "together."
    ),
)
def flatten(input_val: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `FlattenFunc` (`stdlib/collection.go:491`).

    A tuple, not a list. Flattening a mixture of element types into a list
    would have to widen them all to dynamic to fit; a tuple carries each
    element's own type, which is why go-cty returns one.
    """
    elements, known = _flatten_elements(input_val)
    if not known:
        return CtyValue.unknown(return_type)
    result_type = CtyTuple(element_types=tuple(element.type for element in elements))
    # Built directly rather than through `validate`. The result type is derived
    # from the elements' own types, so validating each element against the type
    # taken from it is a no-op by construction -- one that cost more than the
    # flattening itself: 16 ms to 36 ms on a 10k-element input, because a tuple
    # type has one entry per element and each entry is entered separately.
    return CtyValue(vtype=result_type, value=tuple(elements))


# ---------------------------------------------------------------------------
# sort
# ---------------------------------------------------------------------------


def _sort_element_type(collection_type: CtyType[Any]) -> CtyType[Any]:
    """The element type `sort` will order, or a refusal.

    go-cty's parameter is `list(string)` and nothing else; a set, a tuple and a
    non-string element type are all this package's widening.
    """
    if not isinstance(collection_type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(f"sort: input must be a list, set, or tuple, got {collection_type.ctype}")
    if isinstance(collection_type, CtyList | CtySet):
        element_type = collection_type.element_type
    else:
        element_type = CtyDynamic()
    if not isinstance(element_type, CtyString | CtyNumber | CtyBool | CtyDynamic):
        raise CtyFunctionError(f"sort: elements must be string, number, or bool. Found: {element_type.ctype}")
    return element_type


def _sort_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `StaticReturnType(cty.List(cty.String))`, element type widened."""
    return CtyList(element_type=_sort_element_type(args[0].type))


@stdlib_function(
    "sort",
    params=[CtyParameter("list", CtyDynamic(), allow_unknown=True)],
    type_func=_sort_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Applies a lexicographic sort to the elements of the given list.",
)
def sort(input_val: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `SortFunc` (`stdlib/string.go:282`), registered here.

    An unknown element and a null element are different questions, and go-cty
    answers them differently -- this treated them alike and refused both.

    An unknown element means the *ordering* is undecided, so every position
    becomes undecided with it: go-cty refines the result to the length it already
    knows, `[n, n]`, and that refinement collapses into a list of `n` bare
    unknowns -- discarding even the elements it does know. That is lossier than
    it needs to be, but it is the answer Terraform sees, and an unknown anywhere
    wins over a null: `sort([null, unknown])` sorts rather than raising.
    """
    element_type = cast("CtyList[Any]", return_type).element_type
    if not input_val.is_wholly_known():
        if input_val.is_unknown:
            # Nothing bounds the length, so there is nothing to refine beyond
            # the non-nullness `refine_result` already promises.
            return CtyValue.unknown(return_type)
        undecided = [CtyValue.unknown(element_type)] * len(cast("Sized", input_val.value))
        return return_type.validate(undecided)

    elements = _sequence_elements(input_val)
    for position, cty_element in enumerate(elements):
        if cty_element.is_null:
            raise CtyFunctionError(
                f"sort: cannot sort list with null or unknown elements at index {position}."
            )
    return return_type.validate(sorted(elements, key=lambda element: cast("Any", element.value)))


# ---------------------------------------------------------------------------
# slice
# ---------------------------------------------------------------------------


def _slice_indexes(
    collection: CtyValue[Any], start_val: CtyValue[Any], end_val: CtyValue[Any]
) -> tuple[int, int, bool]:
    """go-cty's `sliceIndexes` (`collection.go:1206`): both ends, and whether they are known.

    Every bound is checked here rather than left to Python's forgiving slice
    syntax, which silently clamps `[0:9]` on a three-element list to the whole
    list where go-cty refuses the call.
    """
    sequence, _ = collection.unmark()
    length_known = False
    known_length = 0
    if isinstance(sequence.type, CtyTuple):
        known_length = len(sequence.type.element_types)
        length_known = True
    elif not sequence.is_unknown:
        known_length = len(cast("Sized", sequence.value))
        length_known = True

    start_index, end_index = 0, 0
    start_known, end_known = False, False
    if not start_val.is_unknown:
        start_index = whole_number(start_val, "slice: invalid start index: {value}")
        if start_index < 0:
            raise CtyFunctionError("slice: start index must not be less than zero")
        if length_known and start_index > known_length:
            raise CtyFunctionError("slice: start index must not be greater than the length of the list")
        start_known = True
    if not end_val.is_unknown:
        end_index = whole_number(end_val, "slice: invalid end index: {value}")
        if end_index < 0:
            raise CtyFunctionError("slice: end index must not be less than zero")
        if length_known and end_index > known_length:
            raise CtyFunctionError("slice: end index must not be greater than the length of the list")
        end_known = True
    if start_known and end_known and start_index > end_index:
        raise CtyFunctionError("slice: start index must not be greater than end index")
    return start_index, end_index, start_known and end_known


def _slice_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `SliceFunc.Type` (`collection.go:1147`).

    A tuple slice is a *tuple*, carrying the element types it actually kept --
    which is why the indices have to be known before the type can be.
    """
    collection = args[0]
    collection_type = collection.type
    if isinstance(collection_type, CtySet):
        raise CtyFunctionError(
            "slice: cannot slice a set, because its elements do not have indices; explicitly "
            "convert to a list if the ordering of the result is not important"
        )
    if not isinstance(collection_type, CtyList | CtyTuple):
        raise CtyFunctionError(f"slice: input must be a list or tuple, got {collection_type.ctype}")

    start_index, end_index, indexes_known = _slice_indexes(collection, args[1], args[2])
    if isinstance(collection_type, CtyList):
        return collection_type
    if not indexes_known:
        return CtyDynamic()
    return CtyTuple(element_types=collection_type.element_types[start_index:end_index])


@stdlib_function(
    "slice",
    params=[
        CtyParameter("list", CtyDynamic(), allow_marked=True),
        CtyParameter("start_index", CtyNumber()),
        CtyParameter("end_index", CtyNumber()),
    ],
    type_func=_slice_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Extracts a subslice of the given list or tuple value.",
)
def slice(
    input_val: CtyValue[Any],
    start_val: CtyValue[Any],
    end_val: CtyValue[Any],
    *,
    return_type: CtyType[Any],
) -> CtyValue[Any]:
    """go-cty's `SliceFunc` (`stdlib/collection.go:1130`).

    Only the sequence's own marks are propagated; an element's marks travel with
    the element into the result, as they do in go-cty.
    """
    sequence, marks = input_val.unmark()
    start_index, end_index, _ = _slice_indexes(sequence, start_val, end_val)
    elements = _sequence_elements(sequence)[start_index:end_index]
    return return_type.validate(elements).with_marks(marks)


# ---------------------------------------------------------------------------
# concat
# ---------------------------------------------------------------------------


def _concat_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `ConcatFunc.Type` (`sequence.go:19`).

    A list when every argument is a list *and* their element types unify, and a
    tuple otherwise -- because a tuple is the only type that can carry a
    different type per position, which is what concatenating a `list(number)`
    with a `list(bool)` produces.
    """
    if not args:
        raise CtyFunctionError(ERR_CONCAT_REQUIRES_ONE)

    if isinstance(args[0].type, CtyList) and all(isinstance(arg.type, CtyList) for arg in args):
        unified = unify([arg.type for arg in args])
        if isinstance(unified, CtyList):
            return unified

    element_types: list[CtyType[Any]] = []
    for sequence in args:
        sequence_type = sequence.type
        if isinstance(sequence_type, CtyTuple):
            element_types.extend(sequence_type.element_types)
        elif isinstance(sequence_type, CtyList):
            if sequence.is_unknown:
                # A tuple type has one entry per element, so it cannot be built
                # without knowing how many elements there are.
                return CtyDynamic()
            element_types.extend([sequence_type.element_type] * len(cast("Sized", sequence.value)))
        else:
            raise CtyFunctionError(ERR_CONCAT_ARGS_MUST_BE_SEQUENCES.format(type=sequence_type.ctype))
    return CtyTuple(element_types=tuple(element_types))


@stdlib_function(
    "concat",
    var_param=CtyParameter("seqs", CtyDynamic(), allow_marked=True),
    type_func=_concat_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Concatenates together all of the given lists or tuples into a single sequence, "
        "preserving the input order."
    ),
)
def concat(*sequences: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `ConcatFunc` (`stdlib/sequence.go:11`).

    This used to derive the element type from the elements themselves, widening
    to dynamic at the first mismatch, so `concat(list(string), list(number))`
    came back a `list(dynamic)` holding the originals where go-cty returns a
    `list(string)` holding `["a", "1"]`. Both halves were wrong: no unification,
    and no tuple fallback.
    """
    marks: frozenset[Any] = frozenset()
    unmarked: list[CtyValue[Any]] = []
    for sequence in sequences:
        stripped, sequence_marks = sequence.unmark()
        marks |= sequence_marks
        unmarked.append(stripped)

    if isinstance(return_type, CtyList):
        converted = [
            convert(element, return_type.element_type)
            for sequence in unmarked
            for element in cast("Iterable[CtyValue[Any]]", sequence.value)
        ]
        widened: CtyValue[Any] = return_type.validate(converted)
        return widened.with_marks(marks)

    elements = [
        element for sequence in unmarked for element in cast("Iterable[CtyValue[Any]]", sequence.value)
    ]
    result_type = CtyTuple(element_types=tuple(element.type for element in elements))
    # Built directly: the type is derived from the elements' own types, so
    # validating each against the type taken from it is a no-op by construction.
    return CtyValue(vtype=result_type, value=tuple(elements)).with_marks(marks)


# ---------------------------------------------------------------------------
# reverselist
# ---------------------------------------------------------------------------


def _reverse_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `ReverseListFunc.Type` (`collection.go:890`)."""
    collection_type = args[0].type
    if isinstance(collection_type, CtyTuple):
        return CtyTuple(element_types=tuple(reversed(collection_type.element_types)))
    if isinstance(collection_type, CtyList | CtySet):
        # A set is accepted "to mimic the usual behavior of auto-converting to
        # list", in go-cty's own words, and comes back a list.
        return CtyList(element_type=collection_type.element_type)
    raise CtyFunctionError(f"reverse: can only reverse list or tuple values, not {collection_type.ctype}")


@stdlib_function(
    "reverselist",
    params=[CtyParameter("list", CtyDynamic(), allow_marked=True)],
    type_func=_reverse_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Returns the given list with its elements in reverse order.",
)
def reverse(input_val: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `ReverseListFunc` (`stdlib/collection.go:881`).

    A set is reversed into a list rather than refused, which is what go-cty
    does; refusing it was stricter than the reference.
    """
    sequence, marks = input_val.unmark()
    reversed_elements = list(reversed(_sequence_elements(sequence)))
    return return_type.validate(reversed_elements).with_marks(marks)


# ---------------------------------------------------------------------------
# coalescelist
# ---------------------------------------------------------------------------


def _coalescelist_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `CoalesceListFunc.Type` (`collection.go:223`).

    Mixed argument types cannot be described by any one of them, so the answer
    is dynamic -- and so is an unknown argument, because which one wins is what
    is unknown.
    """
    if not args:
        raise CtyFunctionError("coalescelist: at least one argument is required")

    argument_types: list[CtyType[Any]] = []
    for arg in args:
        if arg.is_unknown:
            return CtyDynamic()
        arg_type = arg.type
        if not isinstance(arg_type, CtyList | CtyTuple):
            raise CtyFunctionError("coalescelist: arguments must be lists or tuples")
        argument_types.append(arg_type)

    first = argument_types[0]
    if any(not other.equal(first) for other in argument_types[1:]):
        return CtyDynamic()
    return first


@stdlib_function(
    "coalescelist",
    var_param=CtyParameter(
        "vals",
        CtyDynamic(),
        description="List or tuple values to test in the given order.",
        allow_unknown=True,
        allow_dynamic_type=True,
        allow_null=True,
    ),
    type_func=_coalescelist_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Returns the first of the given sequences that has a length greater than zero.",
)
def coalescelist(*args: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `CoalesceListFunc` (`stdlib/collection.go:212`).

    An unknown argument only stops the search when it is *reached*: a known,
    non-empty argument before it has already won.
    """
    for arg in args:
        if arg.is_unknown:
            return CtyValue.unknown(return_type)
        if arg.is_null:
            continue
        if len(cast("Sized", arg.value)) > 0:
            return arg
    raise CtyFunctionError("coalescelist: no non-empty list or tuple found in arguments")


# ---------------------------------------------------------------------------
# compact
# ---------------------------------------------------------------------------


def _compact_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `StaticReturnType(cty.List(cty.String))` (`collection.go:287`).

    The shape check that go-cty's `list(string)` parameter would have made moves
    here, because the parameter is widened to keep sets and tuples working.
    """
    collection_type = args[0].type
    refusal = "compact: argument must be a list, set, or tuple of strings"
    if isinstance(collection_type, CtyTuple):
        if not all(isinstance(t, CtyString) for t in collection_type.element_types):
            raise CtyFunctionError(refusal)
    elif isinstance(collection_type, CtyList | CtySet):
        if not isinstance(collection_type.element_type, CtyString):
            raise CtyFunctionError(refusal)
    else:
        raise CtyFunctionError(refusal)
    return CtyList(element_type=CtyString())


@stdlib_function(
    "compact",
    params=[CtyParameter("list", CtyDynamic())],
    type_func=_compact_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Removes all empty string elements from the given list of strings.",
)
def compact(collection: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `CompactFunc` (`stdlib/collection.go:279`).

    Whether an element survives depends on whether it is the empty string, and
    an unknown has not decided that yet -- its payload is a placeholder object,
    which is truthy, so it used to be kept as if it had definitely answered "not
    empty". go-cty declines instead: the result's length is not knowable, only
    that it is a list and not null. A null element is dropped alongside the
    empty strings, as go-cty drops it.
    """
    if not collection.is_wholly_known():
        return CtyValue.unknown(return_type)
    kept = [
        element
        for element in cast("Iterable[CtyValue[Any]]", collection.value)
        if not element.is_null and element.value != ""
    ]
    return return_type.validate(kept)


# ---------------------------------------------------------------------------
# chunklist
# ---------------------------------------------------------------------------


def _chunk_element_type(collection_type: CtyType[Any]) -> CtyType[Any]:
    """The type the chunks hold.

    go-cty's return type is `cty.List(args[0].Type())` -- the argument's own
    type, element type included, rather than dynamic. Its parameter is declared
    as `list(dynamic)`, which its conversion layer refuses a tuple for; this
    accepts one anyway and unifies the element types, which costs nothing and
    keeps a working call working.
    """
    if isinstance(collection_type, CtyList):
        return collection_type
    # A tuple whose elements have no common type has no list form, and so
    # nothing to chunk. `unify` used to answer dynamic for that, which produced
    # a `list(dynamic)` of values that had never been converted to anything.
    unified = unify(cast("CtyTuple", collection_type).element_types)
    if unified is None:
        raise CtyFunctionError(ERR_CHUNKLIST_TUPLE_NOT_UNIFIABLE)
    return CtyList(element_type=unified)


def _chunk_size(size: CtyValue[Any]) -> int:
    """The chunk size, or a refusal. Zero is legal and means "one chunk"."""
    count = whole_number(size, ERR_CHUNKLIST_SIZE_MUST_BE_WHOLE)
    if count < 0:
        raise CtyFunctionError(ERR_CHUNKLIST_SIZE_MUST_BE_POSITIVE)
    return count


def _chunklist_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `ChunklistFunc.Type`: `cty.List(args[0].Type())` (`collection.go:431`)."""
    collection_type = args[0].type
    if not isinstance(collection_type, CtyList | CtyTuple):
        raise CtyFunctionError(ERR_CHUNKLIST_ARGS_MUST_BE_LIST_AND_NUMBER)
    return CtyList(element_type=_chunk_element_type(collection_type))


@stdlib_function(
    "chunklist",
    params=[
        CtyParameter("list", CtyDynamic(), description="The list to split into chunks.", allow_marked=True),
        CtyParameter(
            "size",
            CtyNumber(),
            description=(
                "The maximum length of each chunk. All but the last element of the result is "
                "guaranteed to be of exactly this size."
            ),
            allow_marked=True,
        ),
    ],
    type_func=_chunklist_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Splits a single list into multiple lists where each has at most the given number of elements.",
)
def chunklist(collection: CtyValue[Any], size: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `ChunklistFunc` (`stdlib/collection.go:415`): a sequence split into fixed-size chunks.

    Both arguments' own marks reach the result; marks inside the list travel
    with the elements into their chunk, which is why go-cty calls those values
    opaque here.
    """
    sequence, marks = collection.unmark()
    size_val, size_marks = size.unmark()
    marks |= size_marks

    chunk_size = _chunk_size(size_val)
    elements = _sequence_elements(sequence)
    if not elements:
        return return_type.validate([]).with_marks(marks)
    if chunk_size == 0:
        # go-cty: "if size is 0, returns a list made of the initial list".
        return return_type.validate([elements]).with_marks(marks)
    chunks = [elements[i : i + chunk_size] for i in range(0, len(elements), chunk_size)]
    return return_type.validate(chunks).with_marks(marks)


# ---------------------------------------------------------------------------
# range
# ---------------------------------------------------------------------------


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


@stdlib_function(
    "range",
    var_param=CtyParameter("params", CtyNumber()),
    returns=CtyList(element_type=CtyNumber()),
    refine_result=refine_not_null,
    description="Returns a list of numbers spread evenly over a particular range.",
)
def range_fn(*args: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `RangeFunc` (`stdlib/sequence.go:141`). Named with a suffix to leave the builtin alone."""
    start, end, step = _range_bounds([cast("Decimal", arg.value) for arg in args])
    # No eager refusal of a zero step. go-cty has one and it never fires -- it
    # tests `step == cty.Zero`, comparing two structs that hold different
    # `*big.Float` pointers -- so a zero step there runs the loop, and the loop
    # decides: `range(0, 0, 0)` is an *empty list*, because the first iteration
    # already stops, and `range(0, 10, 0)` is the 1024-value cap error. This
    # package refused both, which was right about the second and wrong about the
    # first. Found 2026-08-19 by the stdlib fuzz; deleting the check is what
    # matches, because the loop below already answers both cases the way go-cty
    # answers them.
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
    generated: CtyValue[Any] = CtyList(element_type=CtyNumber()).validate(numbers)
    return generated


# 🌊🪢🔚
