#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `stdlib/collection.go` and `stdlib/sequence.go`, declared rather than re-derived.

Every function here carries the `Spec` go-cty gives it: the per-parameter null,
unknown, dynamic and mark policy, the `Type` callback that decides the return
type before the values are known, and the `RefineResult` that says what stays
true of the answer even when the answer is unknown. `collection.go` is the
densest file in go-cty's stdlib for that declared policy -- fifteen
`RefineResult`, sixteen `AllowMarked`, six `AllowDynamicType`, four
`AllowUnknown` and three `AllowNull` -- and none of it was expressible before
`_function.py` existed.

Two deliberate departures, both recorded rather than accidental:

**Parameter types are widened where this package already accepted more than
go-cty does.** go-cty declares four of these parameters concretely -- `distinct`
and `chunklist` take `list(dynamic)`, `compact` and `sort` take `list(string)` --
and relies on its caller (HCL) to convert an argument to the parameter type
before the call. Nothing converts here, so declaring those types verbatim would
turn `sort` of a `list(number)`, `compact` of a set and `chunklist` of a tuple
from working calls into type errors. The precedent is `chunklist`'s tuple
support, which `tests/functions/test_gocty_stdlib_parity.py` documents as "a
deliberate superset". So the parameter is declared `dynamic` and go-cty's shape
check moves into the `Type` callback, which is where it can still refuse an
*unknown* of the wrong type. Every such widening is named at the function.

`zipmap`'s keys are the one concrete parameter kept verbatim, because there the
element type is load-bearing rather than incidental: the keys become map keys or
object attribute names, and a widened parameter admitted a `list(dynamic)` of
containers that `str()` then turned into a map keyed by a Python repr.

**`flatten` and `length` do not take `AllowMarked`, though go-cty gives it to
them.** go-cty's `flattener` propagates only the marks of the *sequences* it
unwraps, and `Value.Length()` only the collection's own top-level marks, so in
go-cty a mark on an inner element stays on that element (`flatten`) or is
dropped entirely (`length`). This package's rule is the framework default --
collect marks from anywhere inside the argument and re-apply their union to the
result -- and `tests/functions/test_mark_propagation.py` pins it for exactly
these two functions. Matching go-cty there would move a sensitivity flag off the
top level of a result, which is a declassification and not a decision to take
while migrating. The other fourteen `AllowMarked` parameters are declared and
handled as go-cty handles them.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence, Sized
from decimal import Decimal
from itertools import product
from typing import Any, cast

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
    ERR_CONCAT_ARGS_MUST_BE_SEQUENCES,
    ERR_CONCAT_REQUIRES_ONE,
    ERR_DISTINCT_INPUT_MUST_BE_LIST_SET_TUPLE,
    ERR_FLATTEN_INPUT_MUST_BE_LIST_SET_TUPLE,
    ERR_KEYS_INPUT_MUST_BE_MAP_OBJECT,
    ERR_LENGTH_INPUT_MUST_BE_COLLECTION,
    ERR_MERGE_ALL_ARGS_MUST_BE_MAPS_OBJECTS,
    ERR_RANGE_ARG_COUNT,
    ERR_RANGE_END_MUST_BE_GREATER,
    ERR_RANGE_END_MUST_BE_LESS,
    ERR_RANGE_TOO_MANY_VALUES,
    ERR_SETPRODUCT_ARG_MUST_BE_COLLECTION,
    ERR_SETPRODUCT_REQUIRES_TWO,
    ERR_SETPRODUCT_TOO_LARGE,
    ERR_SETPRODUCT_TUPLE_NOT_UNIFIABLE,
    ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT,
    MAX_RANGE_LENGTH,
)
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import CtyError, CtyFunctionError
from pyvider.cty.functions._args import INT64_MAX, exact_int64, whole_number
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null
from pyvider.cty.refinement import refine
from pyvider.cty.values.markers import RefinedUnknownValue
from pyvider.cty.values.set_order import order_key as set_order_key

# go-cty's thresholds for how far it is worth bounding a set product's length
# (`collection.go:1036`). Named because both numbers are arbitrary in go-cty too
# and it says so: past them it gives up and returns an unrefined unknown.
_SETPRODUCT_MAX_ARG_LENGTH = 1024
_SETPRODUCT_MAX_RESULT_LENGTH = 2048

# A cartesian product needs at least two factors (`collection.go:942`).
_SETPRODUCT_MIN_ARGS = 2

# The largest product this package will materialize. go-cty has no such cap and
# will happily allocate whatever the arguments multiply out to, so this is a
# deliberate divergence: six 10-element arguments are 1,000,000 tuples from a
# payload small enough to fit in a plan request. Applied only once the length is
# *known*, because an unknown-length product allocates nothing.
_SETPRODUCT_MAX_TOTAL_ELEMENTS = 1_000_000

# The lowest number of stored elements at which a set's count can be in doubt.
_AMBIGUOUS_SET_SIZE = 2

Args = Sequence[CtyValue[Any]]


def _unwrap_dynamic(element: CtyValue[Any]) -> CtyValue[Any]:
    """The value a CtyDynamic wrapper stands in front of.

    The framework does this to the *arguments*; this is for values found inside
    one, which it never touches.
    """
    while isinstance(element.type, CtyDynamic) and isinstance(element.value, CtyValue):
        element = element.value
    return element


def _sequence_elements(seq: CtyValue[Any]) -> list[CtyValue[Any]]:
    """A sequence's elements in a stable order.

    A set has no order of its own, so it is given the same one that was used to
    de-duplicate it, rather than whatever the frozenset happens to iterate in.
    """
    if isinstance(seq.value, frozenset):
        return sorted(seq.value, key=set_order_key)
    return list(cast("tuple[CtyValue[Any], ...]", seq.value))


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
        element = _unwrap_dynamic(frame.pop())
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
# length
# ---------------------------------------------------------------------------


def _length_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `LengthFunc.Type` (`collection.go:123`).

    `DynamicPseudoType` passes the check deliberately, so an argument of no
    decided type leaves the answer undecided rather than refused.
    """
    collection_type = args[0].type
    if not isinstance(collection_type, CtyList | CtySet | CtyTuple | CtyMap | CtyDynamic):
        raise CtyFunctionError(ERR_LENGTH_INPUT_MUST_BE_COLLECTION.format(type=collection_type.ctype))
    return CtyNumber()


def _unknown_length(collection: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `valueRefineLengthResult`: the count inherits the collection's bounds.

    An unknown collection has a length range even when it has no length, so the
    count is an unknown number bounded by it -- `[0, maxint]` for a collection
    nothing is known about, which is what go-cty answers and what this returned
    as a bare unknown.
    """
    refinement = collection.value if isinstance(collection.value, RefinedUnknownValue) else None
    lower = (refinement.collection_length_lower_bound if refinement else None) or 0
    upper = refinement.collection_length_upper_bound if refinement else None
    return (
        refine(CtyValue.unknown(CtyNumber()))
        .not_null()
        .number_range_inclusive(lower, INT64_MAX if upper is None else upper)
        .new_value()
    )


def _set_length_is_known(collection: CtyValue[Any], stored: int) -> bool:
    """When a set knows how many elements it has. go-cty's `Value.Length()`.

    Two conditions, and go-cty checks them in this order (`value_ops.go:1126`):
    a store of one element knows its length whatever that element is, because
    there is nothing for it to coalesce with; otherwise the set has to be
    **wholly** known.

    Wholly, which is the half that was wrong here until 2026-08-19: this asked
    whether any element `is_unknown`, which is one level deep, so a set of lists
    holding an unknown *inside* a list counted itself as known and answered a
    length go-cty leaves undecided. Found by the stdlib fuzz.
    """
    return stored < _AMBIGUOUS_SET_SIZE or collection.is_wholly_known()


def _set_length(collection: CtyValue[Any], stored: int) -> CtyValue[Any]:
    """A set's length is undecided while it holds an unknown element.

    Counting the stored elements would over-claim. An unknown element may still
    resolve to a value equal to another member, and the set would then hold
    fewer distinct values than it currently stores -- so the count is a *bound*,
    not an answer. go-cty returns an unknown number refined to `[1, stored]`,
    and its lower bound is 1 no matter how many definitely-distinct known
    elements are present; it does not credit them.

    The one exception is a set storing a single element: whatever that element
    turns out to be, there is exactly one of it.

    Only reachable since sets stopped flagging themselves unknown on behalf of
    their elements -- before that this returned unknown for the whole set, which
    was vaguer but never wrong.
    """
    if _set_length_is_known(collection, stored):
        return CtyNumber().validate(stored)
    return refine(CtyValue.unknown(CtyNumber())).not_null().number_range_inclusive(1, stored).new_value()


@stdlib_function(
    "length",
    params=[CtyParameter("collection", CtyDynamic(), allow_dynamic_type=True, allow_unknown=True)],
    type_func=_length_return_type,
    refine_result=refine_not_null,
    description="Returns the number of elements in the given collection.",
)
def length(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `LengthFunc` (`stdlib/collection.go:112`), which is `Value.Length()`.

    A tuple is counted from its *type*, so its length is known even when its
    value is not. `AllowMarked` is deliberately not declared; see the module
    docstring.
    """
    if isinstance(input_val.type, CtyTuple):
        return CtyNumber().validate(len(input_val.type.element_types))
    if input_val.is_unknown:
        return _unknown_length(input_val)
    if isinstance(input_val.type, CtySet):
        return _set_length(input_val, len(cast("Sized", input_val.value)))
    return CtyNumber().validate(len(cast("Sized", input_val.value)))


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
# contains
# ---------------------------------------------------------------------------

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


@stdlib_function(
    "contains",
    params=[
        CtyParameter("list", CtyDynamic()),
        CtyParameter("value", CtyDynamic(), allow_null=True),
    ],
    returns=CtyBool(),
    refine_result=refine_not_null,
    description="Returns true if the given value is a value in the given list, tuple, or set, or false otherwise.",
)
def contains(collection: CtyValue[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ContainsFunc` (`stdlib/collection.go:317`).

    The shape check lives here rather than in a `Type` callback because go-cty's
    does: its `Type` is `StaticReturnType(cty.Bool)`, so an unknown of the wrong
    type short-circuits to an unknown bool instead of being refused.

    A collection reports itself unknown as soon as any element is unknown, but
    it keeps its elements. An unknown element could still turn out to be the
    value being searched for, so a miss against a partially-unknown collection
    is undecided rather than false. An exact match still wins outright: it
    cannot be un-matched by whatever the unknowns resolve to.
    """
    if not isinstance(collection.type, CtyList | CtySet | CtyTuple):
        raise CtyFunctionError(
            f"contains: collection must be a list, set, or tuple, got {collection.type.ctype}"
        )

    elements = tuple(cast("Iterable[Any]", collection.value))
    if not elements:
        return CtyBool().validate(False)

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
    hit, saw_unknown = _scan_for_value(elements, value)
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


# ---------------------------------------------------------------------------
# keys and values
# ---------------------------------------------------------------------------


def _keys_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `KeysFunc.Type` (`collection.go:600`).

    An object's attribute names are fixed by its type, so the result is a tuple
    with one entry per attribute rather than a list.
    """
    mapping_type = args[0].type
    if isinstance(mapping_type, CtyMap):
        return CtyList(element_type=CtyString())
    if isinstance(mapping_type, CtyObject):
        return CtyTuple(element_types=(CtyString(),) * len(mapping_type.attribute_types))
    raise CtyFunctionError(ERR_KEYS_INPUT_MUST_BE_MAP_OBJECT.format(type=mapping_type.ctype))


@stdlib_function(
    "keys",
    params=[CtyParameter("inputMap", CtyDynamic(), allow_unknown=True, allow_marked=True)],
    type_func=_keys_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Returns a list of the keys of the given map in lexicographical order.",
)
def keys(input_val: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `KeysFunc` (`stdlib/collection.go:589`).

    An unknown *object* still answers: its attribute names come from its type,
    so there is nothing undecided about them. This returned an unknown tuple.

    Only the mapping's own marks reach the result. go-cty says why in as many
    words: "since we don't mark map keys, we can throw away any nested marks,
    which would only apply to values" -- so a sensitive value does not make its
    key sensitive.
    """
    mapping, marks = input_val.unmark()
    if isinstance(mapping.type, CtyObject):
        names = sorted(mapping.type.attribute_types)
        return return_type.validate(tuple(names)).with_marks(marks)
    if mapping.is_unknown:
        return CtyValue.unknown(return_type).with_marks(marks)
    ordered = sorted(cast("Mapping[str, Any]", mapping.value))
    return return_type.validate(ordered).with_marks(marks)


def _values_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `ValuesFunc.Type` (`collection.go:1262`).

    A tuple for an object rather than a list: an object's attributes have
    differing types, and a list would have to widen them all to dynamic.
    """
    mapping_type = args[0].type
    if isinstance(mapping_type, CtyMap):
        return CtyList(element_type=mapping_type.element_type)
    if isinstance(mapping_type, CtyObject):
        attribute_types = mapping_type.attribute_types
        return CtyTuple(element_types=tuple(attribute_types[name] for name in sorted(attribute_types)))
    raise CtyFunctionError(ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT.format(type=mapping_type.ctype))


@stdlib_function(
    "values",
    params=[CtyParameter("mapping", CtyDynamic(), allow_marked=True)],
    type_func=_values_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Returns the values of elements of a given map, or the values of attributes of a given "
        "object, in lexicographic order by key or attribute name."
    ),
)
def values(input_val: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `ValuesFunc` (`stdlib/collection.go:1253`).

    Lexicographic by key, which is not a property of this function but of the
    types: "cty guarantees that these types always iterate in key
    lexicographical order". Returning them in insertion order meant `keys` and
    `values` no longer corresponded, so `zipmap(keys(m), values(m))` paired
    every value with the wrong key.
    """
    mapping, marks = input_val.unmark()
    payload = cast("Mapping[str, CtyValue[Any]]", mapping.value)
    ordered = [payload[name] for name in sorted(payload)]
    return return_type.validate(ordered).with_marks(marks)


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
# hasindex and index
# ---------------------------------------------------------------------------


def _hasindex_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `HasIndexFunc.Type` (`collection.go:29`).

    A set and an object are refused: neither is indexable by go-cty's rules,
    which name list, map and tuple only.
    """
    collection_type = args[0].type
    if not isinstance(collection_type, CtyList | CtyTuple | CtyMap | CtyDynamic):
        raise CtyFunctionError(
            f"hasindex: collection must be a list, a map or a tuple, got {collection_type.ctype}"
        )
    return CtyBool()


@stdlib_function(
    "hasindex",
    params=[
        CtyParameter("collection", CtyDynamic(), allow_dynamic_type=True),
        CtyParameter("key", CtyDynamic(), allow_dynamic_type=True),
    ],
    type_func=_hasindex_return_type,
    refine_result=refine_not_null,
    description=(
        "Returns true if if the given collection can be indexed with the given key without "
        "producing an error, or false otherwise."
    ),
)
def hasindex(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `HasIndexFunc` (`stdlib/collection.go:15`), which is `Value.HasIndex`.

    A null collection used to answer False, which claims it was looked in. The
    framework refuses it now, as go-cty's parameter spec does.

    A key that names no position is a False rather than an error, and go-cty
    decides which those are by whether `big.Float.Int64()` converted exactly.
    Truncating instead -- `int(Decimal("1.5"))` -- made `index(list, 1.5)`
    return the element at 1, and a non-finite key escaped as an unhandled
    `OverflowError` from the same call.
    """
    if isinstance(collection.type, CtyList | CtyTuple):
        if not isinstance(key.type, CtyNumber):
            return CtyBool().validate(False)
        idx = exact_int64(key)
        if idx is None or idx < 0:
            return CtyBool().validate(False)
        return CtyBool().validate(idx < len(cast("Sized", collection.value)))
    if not isinstance(key.type, CtyString):
        return CtyBool().validate(False)
    return CtyBool().validate(key.value in cast("Mapping[str, Any]", collection.value))


def _index_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `IndexFunc.Type` (`collection.go:55`).

    The element's own type, which for a tuple means the index has to be known
    and in range before the type can be decided at all.
    """
    collection, key = args[0], args[1]
    collection_type, key_type = collection.type, key.type
    if isinstance(collection_type, CtyTuple):
        if not isinstance(key_type, CtyNumber | CtyDynamic):
            raise CtyFunctionError("index: key for tuple must be number")
        if key.is_unknown:
            # Each tuple element can have its own type, so nothing is decided.
            return CtyDynamic()
        position = whole_number(key, "index: invalid key for tuple: {value}")
        element_types = collection_type.element_types
        if not 0 <= position < len(element_types):
            raise CtyFunctionError(f"index: key must be between 0 and {len(element_types)} inclusive")
        return element_types[position]
    if isinstance(collection_type, CtyList):
        if not isinstance(key_type, CtyNumber | CtyDynamic):
            raise CtyFunctionError("index: key for list must be number")
        return collection_type.element_type
    if isinstance(collection_type, CtyMap):
        if not isinstance(key_type, CtyString | CtyDynamic):
            raise CtyFunctionError("index: key for map must be string")
        return collection_type.element_type
    raise CtyFunctionError(f"index: collection must be a list, a map or a tuple, got {collection_type.ctype}")


@stdlib_function(
    "index",
    params=[
        CtyParameter("collection", CtyDynamic()),
        CtyParameter("key", CtyDynamic(), allow_dynamic_type=True),
    ],
    type_func=_index_return_type,
    description=(
        "Returns the element with the given key from the given collection, or raises an error if "
        "there is no such element."
    ),
)
def index(collection: CtyValue[Any], key: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `IndexFunc` (`stdlib/collection.go:42`).

    No `RefineResult`: the element may legitimately be null, so this is one of
    the two functions in the file that promises nothing about its answer.
    """
    if hasindex(collection, key).is_false():
        raise CtyFunctionError("index: key does not exist in collection")

    key_val = key.value
    if isinstance(key.type, CtyNumber):
        # Safe: hasindex has already refused every key Int64 could not read
        # exactly, so what is left is a whole number inside the int64 range.
        key_val = int(cast("Decimal", key_val))

    return collection[key_val]


# ---------------------------------------------------------------------------
# element
# ---------------------------------------------------------------------------


def _element_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `ElementFunc.Type` (`collection.go:149`)."""
    collection, idx = args[0], args[1]
    collection_type = collection.type
    if isinstance(collection_type, CtyList):
        return collection_type.element_type
    if isinstance(collection_type, CtyTuple):
        if idx.is_unknown:
            # Each tuple element can have its own type, so the result type
            # cannot be predicted before the index is.
            return CtyDynamic()
        element_types = collection_type.element_types
        if not element_types:
            raise CtyFunctionError("element: cannot use element function with an empty list")
        position = whole_number(idx, "element: invalid index: {value}")
        return element_types[position % len(element_types)]
    raise CtyFunctionError(f"element: collection must be a list or tuple, got {collection_type.ctype}")


@stdlib_function(
    "element",
    params=[
        CtyParameter("list", CtyDynamic(), allow_marked=True),
        CtyParameter("index", CtyNumber()),
    ],
    type_func=_element_return_type,
    description=(
        "Returns the element with the given index from the given list or tuple, applying the modulo "
        "operation to the given index if it's greater than the number of elements."
    ),
)
def element(collection: CtyValue[Any], idx: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ElementFunc` (`stdlib/collection.go:136`).

    The sequence's own marks are re-applied to whichever element comes back; the
    element keeps its own. go-cty does exactly this, and it is the reason the
    parameter takes `AllowMarked` -- the alternative would put every *other*
    element's marks on a result they say nothing about.

    No `RefineResult`: an element may be null.
    """
    sequence, marks = collection.unmark()
    position = whole_number(idx, "element: invalid index: {value}")
    count = len(cast("Sized", sequence.value))
    if count == 0:
        raise CtyFunctionError("element: cannot use element function with an empty list")
    chosen = _sequence_elements(sequence)[position % count]
    return chosen.with_marks(marks)


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
# lookup
# ---------------------------------------------------------------------------


def _lookup_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `LookupFunc.Type` (`collection.go:686`).

    For a map the default has to be *convertible* to the element type, and the
    result is that element type -- so `lookup(map(string), k, 5)` answers with
    the string `"5"` rather than the number it was given.
    """
    collection, key, default = args[0], args[1], args[2]
    collection_type = collection.type
    if isinstance(collection_type, CtyObject):
        if key.is_unknown:
            return CtyDynamic()
        name = str(key.unmark()[0].value)
        if name in collection_type.attribute_types:
            return collection_type.attribute_types[name]
        return default.type
    if isinstance(collection_type, CtyMap):
        try:
            convert(default.unmark()[0], collection_type.element_type)
        except CtyError as exc:
            raise CtyFunctionError(
                "lookup: the default value must have the same type as the map elements"
            ) from exc
        return collection_type.element_type
    raise CtyFunctionError("lookup: collection must be a map or object")


@stdlib_function(
    "lookup",
    params=[
        CtyParameter("inputMap", CtyDynamic(), allow_marked=True),
        CtyParameter("key", CtyString(), allow_marked=True),
        CtyParameter("default", CtyDynamic(), allow_marked=True),
    ],
    type_func=_lookup_return_type,
    wants_return_type=True,
    description=(
        "Returns the value of the element with the given key from the given map, or returns the "
        "default value if there is no such element."
    ),
)
def lookup(
    collection: CtyValue[Any], key: CtyValue[Any], default: CtyValue[Any], *, return_type: CtyType[Any]
) -> CtyValue[Any]:
    """go-cty's `LookupFunc` (`stdlib/collection.go:667`).

    The map's and the key's marks reach the result -- a key that is sensitive
    discloses which entry was read, so it has to. The default is left marked and
    carries its own.

    No `RefineResult`: the element or the default may be null.
    """
    mapping, marks = collection.unmark()
    key_value, key_marks = key.unmark()
    marks |= key_marks
    name = str(key_value.value)

    if not mapping.is_wholly_known():
        return CtyValue.unknown(return_type).with_marks(marks)

    payload = cast("Mapping[str, CtyValue[Any]]", mapping.value)
    if isinstance(mapping.type, CtyObject):
        if name in mapping.type.attribute_types:
            return payload[name].with_marks(marks)
    elif name in payload:
        return payload[name].with_marks(marks)

    return convert(default, return_type).with_marks(marks)


# ---------------------------------------------------------------------------
# merge
# ---------------------------------------------------------------------------


def _merge_one(arg: CtyValue[Any], attribute_types: dict[str, CtyType[Any]]) -> tuple[CtyType[Any], bool]:
    """Fold one merge argument's attributes into `attribute_types`.

    Returns the type this argument contributes to the all-arguments-match test,
    and whether the attribute set is still fully known after it.
    """
    arg, _ = arg.unmark()  # Marks are attached to values; a type check ignores them.
    arg_type = arg.type
    if isinstance(arg_type, CtyObject):
        # A null object is treated by go-cty as having no attributes at all, and
        # it compares against the other arguments as the empty object type.
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
    for key in cast("Mapping[str, Any]", arg.value):
        attribute_types[key] = element_type
    return arg_type, True


def _merge_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `MergeFunc.Type` (`collection.go:770`).

    Dynamic stands for go-cty's `DynamicPseudoType`, which it uses both when an
    argument's own type is dynamic and when a mix of unknown maps leaves the
    attribute set unknowable.
    """
    # No arguments gives an empty object: there are no key-value types to read.
    if not args:
        return CtyObject(attribute_types={})

    attribute_types: dict[str, CtyType[Any]] = {}
    first: CtyType[Any] = CtyDynamic()
    matching = True
    attributes_known = True

    for index, arg in enumerate(args):
        # Checked inside the loop rather than up front, because go-cty gives up
        # at the first dynamic argument and so never reaches a later argument
        # that would have been rejected outright.
        if isinstance(arg.type, CtyDynamic):
            return CtyDynamic()
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
        return CtyDynamic()
    return CtyObject(attribute_types=attribute_types)


@stdlib_function(
    "merge",
    var_param=CtyParameter("maps", CtyDynamic(), allow_null=True, allow_dynamic_type=True, allow_marked=True),
    type_func=_merge_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Merges all of the elements from the given maps into a single map, or the attributes from "
        "given objects into a single object."
    ),
)
def merge(*args: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `MergeFunc` (`stdlib/collection.go:760`).

    A later argument's key wins over an earlier one's. Each argument's own marks
    reach the result; the values keep theirs, being copied across verbatim.
    """
    merged: dict[str, CtyValue[Any]] = {}
    marks: frozenset[Any] = frozenset()
    for arg in args:
        if arg.is_null:
            continue
        unmarked, arg_marks = arg.unmark()
        marks |= arg_marks
        merged.update(cast("Mapping[str, CtyValue[Any]]", unmarked.value))

    result_type = return_type
    if isinstance(result_type, CtyDynamic):
        # go-cty declares dynamic here but still returns a concrete ObjectVal,
        # so the value describes itself even though the signature could not.
        result_type = CtyObject(attribute_types={name: value.type for name, value in merged.items()})
    return result_type.validate(merged).with_marks(marks)


# ---------------------------------------------------------------------------
# setproduct
# ---------------------------------------------------------------------------


def _setproduct_element_type(arg: CtyValue[Any], position: int) -> tuple[CtyType[Any], bool]:
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
    del position  # go-cty reports the argument index; the message here does not.
    raise CtyFunctionError(ERR_SETPRODUCT_ARG_MUST_BE_COLLECTION.format(type=arg_type.ctype))


def _setproduct_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `SetProductFunc.Type` (`collection.go:941`).

    A **list** when every argument is ordered, and a set only when one of them
    is a set. This always built a set, so the ordering a caller asked for by
    passing lists was discarded -- and go-cty's own parameter documentation is
    that lists and tuples "preserve the input ordering".
    """
    if len(args) < _SETPRODUCT_MIN_ARGS:
        raise CtyFunctionError(ERR_SETPRODUCT_REQUIRES_TWO)

    element_types: list[CtyType[Any]] = []
    ordered = 0
    for position, arg in enumerate(args):
        element_type, is_ordered = _setproduct_element_type(arg, position)
        element_types.append(element_type)
        ordered += is_ordered

    tuple_type = CtyTuple(element_types=tuple(element_types))
    if ordered == len(args):
        return CtyList(element_type=tuple_type)
    return CtySet(element_type=tuple_type)


def _setproduct_length_known(arg: CtyValue[Any]) -> bool:
    """go-cty's `arg.IsKnown() && arg.Length().IsKnown()` (`collection.go:994`).

    A set holding an unknown element has an unknown length: the unknown may
    still turn out to equal another member and coalesce with it.
    """
    if arg.is_unknown:
        return False
    if isinstance(arg.type, CtySet):
        return _set_length_is_known(arg, len(cast("Sized", arg.value)))
    return True


def _length_upper_bound(arg: CtyValue[Any]) -> int | None:
    """go-cty's `ValueRange.LengthUpperBound` (`value_range.go:233`).

    None stands for its `math.MaxInt`, which is what an unknown collection with
    no length refinement reports -- and it is also what a *known* collection
    whose length is unknown reports, because `Range` synthesises `[0, maxint]`
    for one (`value_range.go:66`). A known collection whose length is known
    synthesises `[len, len]`, so it bounds the product exactly.
    """
    if isinstance(arg.type, CtyTuple):
        return len(arg.type.element_types)
    if arg.is_unknown:
        refinement = arg.value if isinstance(arg.value, RefinedUnknownValue) else None
        return refinement.collection_length_upper_bound if refinement else None
    if not _setproduct_length_known(arg):
        return None
    return len(cast("Sized", arg.value))


def _setproduct_unknown(args: Sequence[CtyValue[Any]], return_type: CtyType[Any]) -> CtyValue[Any]:
    """An unknown product, bounded where the arguments' lengths allow (`collection.go:1005`)."""
    unknown = CtyValue.unknown(return_type)
    max_length = 1
    for arg in args:
        bound = _length_upper_bound(arg)
        # go-cty imposes both thresholds out of pragmatism: an unrefined
        # collection's upper bound is maxint, and multiplying those overflows.
        if bound is None or bound > _SETPRODUCT_MAX_ARG_LENGTH:
            return unknown
        max_length *= bound
        if max_length > _SETPRODUCT_MAX_RESULT_LENGTH:
            return unknown

    if max_length == 0:
        # Typically collapses the unknown into a known empty collection.
        return refine(unknown).not_null().collection_length(0).new_value()
    # A nonzero maximum means set element coalescing cannot reduce the result
    # below one element.
    return (
        refine(unknown)
        .not_null()
        .collection_length_lower_bound(1)
        .collection_length_upper_bound(max_length)
        .new_value()
    )


@stdlib_function(
    "setproduct",
    var_param=CtyParameter(
        "sets",
        CtyDynamic(),
        description=(
            "The sets to consider. Also accepts lists and tuples, and if all arguments are of list "
            "or tuple type then the result will preserve the input ordering"
        ),
        allow_unknown=True,
        allow_marked=True,
    ),
    type_func=_setproduct_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description="Calculates the cartesian product of two or more sets.",
)
def setproduct(*args: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `SetProductFunc` (`stdlib/collection.go:931`).

    Every argument is walked even after one turns out to have an unknown length,
    so that no argument's marks are missed on the way out.
    """
    marks: frozenset[Any] = frozenset()
    unmarked: list[CtyValue[Any]] = []
    unknown_length = False
    total = 1
    for arg in args:
        stripped, arg_marks = arg.unmark()
        marks |= arg_marks
        unmarked.append(stripped)
        if not _setproduct_length_known(stripped):
            unknown_length = True
            continue
        total *= len(cast("Sized", stripped.value))

    if unknown_length:
        # Before the cap, deliberately. The unknown path builds a refinement
        # rather than a product, so there is nothing to exhaust -- and this is
        # the shape Terraform sends at plan time, where refusing it would break
        # the one case that cannot be a DoS.
        return _setproduct_unknown(unmarked, return_type).with_marks(marks)

    if total > _SETPRODUCT_MAX_TOTAL_ELEMENTS:
        raise CtyFunctionError(
            ERR_SETPRODUCT_TOO_LARGE.format(total=total, limit=_SETPRODUCT_MAX_TOTAL_ELEMENTS)
        )

    if total == 0:
        # Any empty argument makes the whole product empty.
        return return_type.validate([]).with_marks(marks)

    iterables = [_sequence_elements(arg) for arg in unmarked]
    result_tuples = [tuple(item) for item in product(*iterables)]
    return return_type.validate(result_tuples).with_marks(marks)


# ---------------------------------------------------------------------------
# zipmap
# ---------------------------------------------------------------------------


def _zipmap_key_names(keys_val: CtyValue[Any]) -> list[CtyValue[Any]]:
    """The key elements, unmarked individually.

    A map key cannot carry a mark, so go-cty takes each key's marks off and
    accumulates them onto the result instead.
    """
    unmarked, _ = keys_val.unmark()
    return [element.unmark()[0] for element in _sequence_elements(unmarked)]


def _zipmap_return_type(args: Args) -> CtyType[Any]:
    """go-cty's `ZipmapFunc.Type` (`collection.go:1336`).

    A tuple of values produces an **object**, one attribute per key, because
    only an object can give each entry its own type. This returned
    `map(dynamic)` for that case, discarding every value's type.

    Nothing here checks the *keys*: their parameter is declared `list(string)`,
    so the framework's conformance check has already refused anything else.
    """
    keys_val, values_val = args[0], args[1]
    values_type = values_val.type

    if isinstance(values_type, CtyList):
        return CtyMap(element_type=values_type.element_type)
    if isinstance(values_type, CtyTuple):
        if not keys_val.is_wholly_known():
            # An object needs all of its attribute names before it has a type.
            return CtyDynamic()
        names = _zipmap_key_names(keys_val)
        value_types = values_type.element_types
        if len(names) != len(value_types):
            raise CtyFunctionError(
                f"zipmap: number of keys ({len(names)}) does not match number of values ({len(value_types)})"
            )
        attribute_types: dict[str, CtyType[Any]] = {}
        for position, name in enumerate(names):
            if name.is_null:
                raise CtyFunctionError(f"zipmap: keys list has null value at index {position}")
            attribute_types[str(name.value)] = value_types[position]
        return CtyObject(attribute_types=attribute_types)
    raise CtyFunctionError("zipmap: values argument must be a list or tuple value")


@stdlib_function(
    "zipmap",
    params=[
        # go-cty's own `cty.List(cty.String)`, kept verbatim rather than widened
        # like the rest of this module: the keys become map keys or object
        # attribute names, and a key that is not a string has no name to become.
        # Widening it let a `list(dynamic)` of containers through to `str()`,
        # which produced a map keyed by a Python repr.
        CtyParameter("keys", CtyList(element_type=CtyString()), allow_marked=True),
        CtyParameter("values", CtyDynamic(), allow_marked=True),
    ],
    type_func=_zipmap_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Constructs a map from a list of keys and a corresponding list of values, which must both "
        "be of the same length."
    ),
)
def zipmap(keys: CtyValue[Any], values: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `ZipmapFunc` (`stdlib/collection.go:1322`).

    An unknown *value* is no obstacle -- it goes into the map as an unknown
    entry, and go-cty builds exactly that map. An unknown *key* is: there is no
    name to file its entry under, so the whole map is undecided. This used to
    hand the placeholder to `CtyMap.validate`, which refused it as a non-string
    key and raised out of the function.

    Mismatched lengths are an error rather than a truncation: zipping two lists
    of different lengths silently dropped entries.
    """
    key_list, marks = keys.unmark()
    value_list, value_marks = values.unmark()
    marks |= value_marks

    if not key_list.is_wholly_known():
        return CtyValue.unknown(return_type).with_marks(marks)

    names = _sequence_elements(key_list)
    entries = _sequence_elements(value_list)
    if len(names) != len(entries):
        raise CtyFunctionError(
            f"zipmap: number of keys ({len(names)}) does not match number of values ({len(entries)})"
        )

    output: dict[str, CtyValue[Any]] = {}
    for name, entry in zip(names, entries, strict=True):
        unmarked_name, name_marks = name.unmark()
        marks |= name_marks
        output[str(unmarked_name.value)] = entry
    return return_type.validate(output).with_marks(marks)


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
