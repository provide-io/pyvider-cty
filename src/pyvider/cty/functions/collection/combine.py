#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The collection functions that build one collection out of several.

`merge`, `setproduct` and `zipmap`. go-cty's `stdlib/collection.go`; see the
package docstring for the declared-policy model and the two deliberate
departures.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence, Sized
from itertools import product
from typing import Any, cast

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
    unify,
)
from pyvider.cty.config.defaults import (
    ERR_MERGE_ALL_ARGS_MUST_BE_MAPS_OBJECTS,
    ERR_SETPRODUCT_ARG_MUST_BE_COLLECTION,
    ERR_SETPRODUCT_REQUIRES_TWO,
    ERR_SETPRODUCT_TOO_LARGE,
    ERR_SETPRODUCT_TUPLE_NOT_UNIFIABLE,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null
from pyvider.cty.functions.collection._shared import (
    Args,
    _sequence_elements,
    _set_length_is_known,
)
from pyvider.cty.refinement import refine
from pyvider.cty.values.markers import RefinedUnknownValue

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


# 🌊🪢🔚
