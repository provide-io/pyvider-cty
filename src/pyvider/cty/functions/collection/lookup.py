#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The collection functions that read from a collection without reshaping it.

`length`, `contains`, `keys`, `values`, `hasindex`, `index`, `element` and
`lookup`. go-cty's `stdlib/collection.go`; see the package docstring for the
declared-policy model and the two deliberate departures.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sized
from decimal import Decimal
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
)
from pyvider.cty.config.defaults import (
    ERR_KEYS_INPUT_MUST_BE_MAP_OBJECT,
    ERR_LENGTH_INPUT_MUST_BE_COLLECTION,
    ERR_VALUES_INPUT_MUST_BE_MAP_OBJECT,
)
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import CtyError, CtyFunctionError
from pyvider.cty.functions._args import INT64_MAX, exact_int64, whole_number
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null
from pyvider.cty.functions.collection._shared import (
    Args,
    _sequence_elements,
    _set_length_is_known,
)
from pyvider.cty.refinement import refine
from pyvider.cty.values.markers import RefinedUnknownValue

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


# 🌊🪢🔚
