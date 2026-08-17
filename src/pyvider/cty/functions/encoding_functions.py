#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections.abc import Iterator, Sequence
import csv
from decimal import Decimal
import io
import json
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
    ERR_CSVDECODE_DUPLICATE_COLUMN,
    ERR_CSVDECODE_FAILED,
    ERR_CSVDECODE_MISSING_HEADER,
    ERR_CSVDECODE_WRONG_FIELD_COUNT,
    ERR_JSONDECODE_FAILED,
    ERR_JSONDECODE_INVALID_FIRST_CHARACTER,
    ERR_JSONENCODE_FAILED,
)
from pyvider.cty.conversion import cty_to_native
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyArgumentError, CtyParameter, refine_not_null
from pyvider.cty.refinement import refine
from pyvider.cty.values.markers import RefinedUnknownValue


def _json_unknown_prefix(vtype: CtyType[Any]) -> str | None:
    """The first character of the JSON a value of `vtype` will encode to.

    go-cty refines the declined result with this so that a downstream consumer
    can still tell an object from an array without knowing the contents.
    """
    if isinstance(vtype, CtyString):
        return '"'
    if isinstance(vtype, CtyObject | CtyMap):
        return "{"
    if isinstance(vtype, CtyTuple | CtyList | CtySet):
        return "["
    return None


def _could_be_null(value: CtyValue[Any]) -> bool:
    """Whether this value may still turn out to be null. go-cty's `ValueRange.CouldBeNull`.

    A known value answers for itself. An unknown one answers from its
    refinements, and an unknown with no refinement could be anything of its
    type, null included.
    """
    if not value.is_unknown:
        return value.is_null
    refinement = value.value if isinstance(value.value, RefinedUnknownValue) else None
    return refinement is None or refinement.is_known_null is not False


@stdlib_function(
    "jsonencode",
    params=[
        CtyParameter(
            "val",
            CtyDynamic(),
            allow_null=True,
            allow_unknown=True,
            allow_dynamic_type=True,
        )
    ],
    returns=CtyString(),
    refine_result=refine_not_null,
    description="Returns a string containing a JSON representation of the given value.",
)
def jsonencode(val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `JSONEncodeFunc` (`stdlib/json.go:13`)."""
    # `is_unknown` alone is not the question. A list is known while an element
    # inside it is not, and encoding that element wrote a JSON `null` -- which
    # is not a placeholder but a different value, and a wrong one. go-cty's
    # JSONEncodeFunc tests `IsWhollyKnown` and declines, keeping whatever it can
    # still promise about the answer: its opening character. That the answer is
    # not null comes from `refine_result` and holds on every path.
    if not val.is_wholly_known():
        result = CtyValue.unknown(CtyString())
        prefix = _json_unknown_prefix(val.type)
        if prefix is None or _could_be_null(val):
            # A null encodes as the four characters `null`, so the very first
            # character of the string is what a null would change -- there is
            # nothing to promise about it until nullness is settled
            # (`json.go:34`).
            return result
        # Taken literally rather than through `safe_known_prefix`: the following
        # character is chosen by the encoder, not the caller, and none of the
        # ones it can emit combines with a brace, bracket or quote.
        return refine(result).string_prefix_full(prefix).new_value()
    try:
        native_val = cty_to_native(val)
        return CtyString().validate(json.dumps(native_val))
    except Exception as e:
        raise CtyFunctionError(ERR_JSONENCODE_FAILED.format(error=e)) from e


def _implied_leaf_type(native: Any) -> CtyType[Any]:
    # A JSON null carries no type information at all, which is what go-cty's
    # ImpliedType returns DynamicPseudoType for.
    if native is None:
        return CtyDynamic()
    if isinstance(native, bool):
        return CtyBool()
    if isinstance(native, int | float | Decimal):
        return CtyNumber()
    return CtyString()


def _implied_type(native: Any) -> CtyType[Any]:
    """The type a decoded JSON document implies, as go-cty's json.ImpliedType does.

    An object becomes an object type and an array a tuple type -- not a map and
    a list -- because JSON says nothing about its members sharing a type.

    Iterative for the same reason the rest of this package is: a document deep
    enough to be worth decoding is deep enough to exhaust the stack.
    """
    todo: list[tuple[Any, bool]] = [(native, False)]
    done: list[CtyType[Any]] = []
    while todo:
        node, expanded = todo.pop()
        if isinstance(node, dict):
            if expanded:
                names = list(node)
                element_types = [done.pop() for _ in names][::-1]
                done.append(CtyObject(attribute_types=dict(zip(names, element_types, strict=True))))
                continue
            todo.append((node, True))
            todo.extend((child, False) for child in reversed(list(node.values())))
        elif isinstance(node, list):
            if expanded:
                element_types = [done.pop() for _ in node][::-1]
                done.append(CtyTuple(element_types=tuple(element_types)))
                continue
            todo.append((node, True))
            todo.extend((child, False) for child in reversed(node))
        else:
            done.append(_implied_leaf_type(node))
    return done.pop()


def _decoded(document: str) -> Any:
    """The JSON document as native Python, with go-cty's number handling.

    `parse_float=Decimal` because go-cty decodes JSON numbers into a `big.Float`
    and this package carries numbers as `Decimal`; going through float64 first
    would round the value before it was ever a cty number.
    """
    try:
        return json.loads(document, parse_float=Decimal)
    except json.JSONDecodeError as e:
        raise CtyFunctionError(ERR_JSONDECODE_FAILED.format(error=e)) from e


def _known_string_prefix(value: CtyValue[Any]) -> str:
    """The prefix an unknown string is already known to start with, or `""`.

    go-cty's `ValueRange.StringPrefix`.
    """
    refinement = value.value if isinstance(value.value, RefinedUnknownValue) else None
    if refinement is None:
        return ""
    return refinement.string_prefix or ""


# What each character that can open a JSON value tells us about the result type.
# `{`, `[` and `n` are absent deliberately: an object or an array says nothing
# about its attributes or its length, and `n` opens `null`, which has no type of
# its own -- so all three stay dynamic (`json.go:88`).
_JSON_FIRST_CHARACTER: dict[str, CtyType[Any]] = {
    '"': CtyString(),
    "t": CtyBool(),
    "f": CtyBool(),
    **dict.fromkeys("-0123456789.", CtyNumber()),
}


def _jsondecode_type(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
    """The type the document describes: go-cty's `JSONDecodeFunc.Type` (`json.go:78`).

    The canonical value-dependent return type, and the reason go-cty's `Type`
    callback is handed values rather than types. An unknown document is not
    entirely opaque: if it has been refined with a known prefix then the first
    character either fixes the result type or is not valid JSON at all, and
    either answer is worth having before the string is known.
    """
    document = args[0]
    if document.is_unknown:
        prefix = _known_string_prefix(document).strip()
        if prefix:
            first = prefix[0]
            if first in _JSON_FIRST_CHARACTER:
                return _JSON_FIRST_CHARACTER[first]
            if first not in "{[n":
                raise CtyArgumentError(0, ERR_JSONDECODE_INVALID_FIRST_CHARACTER.format(character=first))
        return CtyDynamic()
    return _implied_type(_decoded(cast(str, document.value)))


@stdlib_function(
    "jsondecode",
    params=[CtyParameter("str", CtyString())],
    type_func=_jsondecode_type,
    wants_return_type=True,
    description=(
        "Parses the given string as JSON and returns a value corresponding to what the JSON "
        "document describes."
    ),
)
def jsondecode(val: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `JSONDecodeFunc` (`stdlib/json.go:71`).

    No `refine_result`: `jsondecode("null")` is a null, so "not null" is the one
    thing this function cannot promise -- which is why it is the only decoder in
    go-cty's stdlib without `refineNonNull`.

    The document is decoded *into* the already-decided return type, as go-cty
    passes `retType` to `json.Unmarshal`, rather than implying the type a second
    time from the same bytes.
    """
    return return_type.validate(_decoded(cast(str, val.value)))


def _csv_header(reader: Iterator[list[str]]) -> list[str]:
    """The header row, which is what decides the result type.

    Read by the `Type` callback as well as by the implementation, because in
    go-cty the column names *are* the return type and both the missing-header
    and duplicate-column refusals happen there (`csv.go:21`).
    """
    try:
        header = next(reader)
    except StopIteration:
        raise CtyFunctionError(ERR_CSVDECODE_MISSING_HEADER) from None
    except csv.Error as e:
        raise CtyFunctionError(ERR_CSVDECODE_FAILED.format(error=e)) from e

    seen: set[str] = set()
    for name in header:
        if name in seen:
            raise CtyFunctionError(ERR_CSVDECODE_DUPLICATE_COLUMN.format(name=name))
        seen.add(name)
    return header


def _csv_rows(val_str: str) -> tuple[list[str], list[list[str]]]:
    """The header and the data rows, checked as Go's encoding/csv checks them."""
    reader = csv.reader(io.StringIO(val_str))
    header = _csv_header(reader)

    rows: list[list[str]] = []
    try:
        for line, row in enumerate(reader, start=2):
            # Go's csv.Reader skips blank lines outright; Python's hands back an
            # empty record for one.
            if not row:
                continue
            if len(row) != len(header):
                # Go sets FieldsPerRecord from the header, so a ragged row is a
                # parse error rather than a row with missing or extra columns.
                raise CtyFunctionError(ERR_CSVDECODE_WRONG_FIELD_COUNT.format(line=line))
            rows.append(row)
    except csv.Error as e:
        raise CtyFunctionError(ERR_CSVDECODE_FAILED.format(error=e)) from e
    return header, rows


def _csvdecode_type(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
    """The columns of the table, as a list of objects: go-cty's `CSVDecodeFunc.Type`.

    Value-dependent, like `jsondecode`'s, and undecidable until the document is
    known -- so an unknown string answers dynamic rather than reading a `.value`
    that is not there (`csv.go:21`).
    """
    document = args[0]
    if document.is_unknown:
        return CtyDynamic()
    header = _csv_header(csv.reader(io.StringIO(cast(str, document.value))))
    # Every column is a string: CSV carries no type information, so go-cty does
    # not guess one.
    return CtyList(element_type=CtyObject(attribute_types=dict.fromkeys(header, CtyString())))


@stdlib_function(
    "csvdecode",
    params=[CtyParameter("str", CtyString())],
    type_func=_csvdecode_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Parses the given string as Comma Separated Values (as defined by RFC 4180) and returns "
        "a map of objects representing the table of data, using the first row as a header row to "
        "define the object attributes."
    ),
)
def csvdecode(val: CtyValue[Any], *, return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `CSVDecodeFunc` (`stdlib/csv.go:13`)."""
    header, rows = _csv_rows(cast(str, val.value))
    return return_type.validate([dict(zip(header, row, strict=True)) for row in rows])


# 🌊🪢🔚
