#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

import csv
from decimal import Decimal
import io
import json
from typing import Any, cast

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.config.defaults import (
    ERR_CSVDECODE_ARG_MUST_BE_STRING,
    ERR_CSVDECODE_DUPLICATE_COLUMN,
    ERR_CSVDECODE_FAILED,
    ERR_CSVDECODE_MISSING_HEADER,
    ERR_CSVDECODE_WRONG_FIELD_COUNT,
    ERR_JSONDECODE_ARG_MUST_BE_STRING,
    ERR_JSONDECODE_FAILED,
    ERR_JSONENCODE_FAILED,
)
from pyvider.cty.conversion import cty_to_native
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function


@stdlib_function("jsonencode")
def jsonencode(val: CtyValue[Any]) -> CtyValue[Any]:
    if val.is_unknown:
        return CtyValue.unknown(CtyString())
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


@stdlib_function("jsondecode")
def jsondecode(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(ERR_JSONDECODE_ARG_MUST_BE_STRING.format(type=val.type.ctype))
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())
    try:
        # parse_float=Decimal because go-cty decodes JSON numbers into a
        # big.Float and this package carries numbers as Decimal; going through
        # float64 first would round the value before it was ever a cty number.
        native_val = json.loads(cast(str, val.value), parse_float=Decimal)
    except json.JSONDecodeError as e:
        raise CtyFunctionError(ERR_JSONDECODE_FAILED.format(error=e)) from e
    return _implied_type(native_val).validate(native_val)


def _csv_rows(val_str: str) -> tuple[list[str], list[list[str]]]:
    """The header and the data rows, checked as Go's encoding/csv checks them."""
    reader = csv.reader(io.StringIO(val_str))
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


@stdlib_function("csvdecode")
def csvdecode(val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(val.type, CtyString):
        raise CtyFunctionError(ERR_CSVDECODE_ARG_MUST_BE_STRING.format(type=val.type.ctype))
    if val.is_unknown or val.is_null:
        return CtyValue.unknown(CtyDynamic())

    header, rows = _csv_rows(cast(str, val.value))
    # Every column is a string: CSV carries no type information, so go-cty does
    # not guess one.
    element_type = CtyObject(attribute_types=dict.fromkeys(header, CtyString()))
    result_type = CtyList(element_type=element_type)
    return cast(
        CtyValue[Any],
        result_type.validate([dict(zip(header, row, strict=True)) for row in rows]),
    )


# 🌊🪢🔚
