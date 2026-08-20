#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Cross-language wire compatibility against real go-cty, via the tofusoup harness.

pyvider.cty is a Python implementation of go-cty, and the thing that has to
agree is the wire: msgpack written by one has to be readable by the other, byte
for byte, or a provider and Terraform disagree about state.

This runs the comparison rather than asserting it. Reading go-cty's source is
how two non-existent gaps came to be filed against this package -- a CHANGELOG
describes a bug *go-cty* had, which says nothing about whether an independent
implementation shares it.

What this replaces: a placeholder that read a checked-in fixture and had been
failing with `msgpack ExtraData` on `main` for some time. The fixtures are
corrupt -- 10 of the 17 were written with a trailing newline appended to the
msgpack bytes -- so the test could not have passed, and nothing noticed because
it only runs under `--run-compat`. Generating the comparison from the live
harness means there is no fixture to rot.

Requires the `soup-go` harness. `make compat` builds it from a sibling
`tofusoup` checkout into `.compat/soup-go` and runs the suite against it; set
`SOUP_GO_SRC` if the checkout is elsewhere, or point `SOUP_GO_BIN` at a binary
you built yourself.
"""

from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import subprocess  # nosec
import tempfile
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.json_codec import cty_to_json
from tests.compatibility._oracle import soup_go

pytestmark = pytest.mark.compat


def _as_json_text(native: Any) -> bytes:
    """The JSON go-cty is handed. A Decimal is written as its own digits so the
    harness parses the same number we encoded, rather than a float rounding."""
    if isinstance(native, Decimal):
        return format(native, "f").encode()
    return json.dumps(native).encode()


def _canonical(value: Any, cty_type: CtyType[Any]) -> Any:
    """Both sides in one shape, so the comparison is about content.

    Three differences here are not wire differences and must not be read as
    such. A set has no order of its own, so the order its elements come back in
    is not part of the value. A tuple decodes to a Python tuple where the JSON
    side is a list. And a number must not be compared through float.

    Byte-for-byte agreement is checked separately, by
    `test_both_implementations_emit_the_same_bytes` -- which is where set
    ordering *does* have to match, and does.
    """
    if isinstance(cty_type, CtySet):
        return sorted(
            (_canonical(element, cty_type.element_type) for element in value),
            key=lambda element: json.dumps(element, sort_keys=True, default=str),
        )
    if isinstance(cty_type, CtyList):
        return [_canonical(element, cty_type.element_type) for element in value]
    if isinstance(cty_type, CtyTuple):
        return [
            _canonical(element, element_type)
            for element, element_type in zip(value, cty_type.element_types, strict=True)
        ]
    if isinstance(cty_type, CtyMap):
        return {key: _canonical(element, cty_type.element_type) for key, element in value.items()}
    if isinstance(cty_type, CtyObject):
        return {name: _canonical(value[name], t) for name, t in cty_type.attribute_types.items()}
    if isinstance(cty_type, CtyNumber):
        return Decimal(str(value))
    return value


def _go_canonical_json(json_text: bytes, type_spec: Any) -> bytes:
    """go-cty's own JSON rendering of a value, for byte comparison.

    A JSON-to-JSON round trip through go-cty, which is not what `_go_convert`
    offers -- it crosses between the two formats. What is being compared here is
    two encoders, so both sides have to start from the same document and end in
    the same format.
    """
    binary = soup_go()
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in", Path(tmp) / "out"
        src.write_bytes(json_text)
        result = subprocess.run(  # nosec
            [
                binary,
                "cty",
                "convert",
                str(src),
                str(dst),
                "--type",
                json.dumps(type_spec),
                "--input-format",
                "json",
                "--output-format",
                "json",
            ],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(f"go-cty refused the value: {result.stderr.decode()[-400:]}")
        return dst.read_bytes().strip()


def _go_convert(payload: bytes, type_spec: Any, *, to_json: bool) -> bytes:
    """Round a value through go-cty, converting between msgpack and JSON."""
    binary = soup_go()
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in"
        dst = Path(tmp) / "out"
        src.write_bytes(payload)
        result = subprocess.run(  # nosec
            [
                binary,
                "cty",
                "convert",
                str(src),
                str(dst),
                "--type",
                json.dumps(type_spec),
                "--input-format",
                "msgpack" if to_json else "json",
                "--output-format",
                "json" if to_json else "msgpack",
            ],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(f"go-cty refused the value: {result.stderr.decode()[-400:]}")
        return dst.read_bytes()


# (label, cty type, wire type spec, native value)
CASES: list[tuple[str, CtyType[Any], Any, Any]] = [
    ("string", CtyString(), "string", "hello world"),
    ("string unicode", CtyString(), "string", "héllo wörld"),
    ("string empty", CtyString(), "string", ""),
    ("bool true", CtyBool(), "bool", True),
    ("bool false", CtyBool(), "bool", False),
    ("number int", CtyNumber(), "number", 42),
    ("number negative", CtyNumber(), "number", -17),
    ("number large", CtyNumber(), "number", 9007199254740993),
    # Fractional numbers are where the two encoders parted company. go-cty
    # emits a float64 only when the conversion is exact, and the decimal text
    # otherwise; writing the float regardless meant Terraform read back a
    # different number than was written, on every non-integer attribute.
    # Given as Decimal, not float. `0.1` the Python float is the binary
    # approximation 0.1000000000000000055511151231257827, which genuinely *is*
    # exactly float64-representable, so encoding it as a float is right. go-cty
    # is handed the decimal literal `0.1`, a different number. Comparing the two
    # only means something if both sides start from the same value.
    ("number exact half", CtyNumber(), "number", Decimal("1.5")),
    ("number exact quarter", CtyNumber(), "number", Decimal("2.25")),
    ("number inexact tenth", CtyNumber(), "number", Decimal("0.1")),
    ("number inexact third", CtyNumber(), "number", Decimal("0.3")),
    ("number inexact negative", CtyNumber(), "number", Decimal("-0.0001")),
    ("number pi-ish", CtyNumber(), "number", Decimal("3.14159")),
    ("list of strings", CtyList(element_type=CtyString()), ["list", "string"], ["a", "b", "c"]),
    ("list empty", CtyList(element_type=CtyString()), ["list", "string"], []),
    ("map of strings", CtyMap(element_type=CtyString()), ["map", "string"], {"b": "2", "a": "1"}),
    (
        "object",
        CtyObject(attribute_types={"name": CtyString(), "size": CtyNumber()}),
        ["object", {"name": "string", "size": "number"}],
        {"name": "widget", "size": 3},
    ),
    # Structural types. These were absent, and the omission mattered: the types
    # the decoders were fixed to return in August 2026 -- a tuple from
    # `jsondecode`, a `list(object(...))` from `csvdecode` -- are exactly the
    # ones this file did not check. The argument for those fixes was that the
    # type is what crosses the wire, so the wire is where they belong.
    (
        "tuple mixed",
        CtyTuple(element_types=(CtyString(), CtyNumber())),
        ["tuple", ["string", "number"]],
        ["a", 1],
    ),
    ("tuple empty", CtyTuple(element_types=()), ["tuple", []], []),
    (
        "list of objects",
        CtyList(element_type=CtyObject(attribute_types={"a": CtyString(), "b": CtyString()})),
        ["list", ["object", {"a": "string", "b": "string"}]],
        [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}],
    ),
    (
        "list of tuples",
        CtyList(element_type=CtyTuple(element_types=(CtyString(), CtyNumber()))),
        ["list", ["tuple", ["string", "number"]]],
        [["a", 1], ["b", 2]],
    ),
    # A set has no order of its own, so agreeing on bytes means agreeing on the
    # order it is written in -- checked across case, magnitude and non-ASCII,
    # since a sort that differs anywhere differs on the wire.
    ("set of strings", CtySet(element_type=CtyString()), ["set", "string"], ["b", "A", "a", "B"]),
    ("set of numbers", CtySet(element_type=CtyNumber()), ["set", "number"], [10, 2, 33, 4]),
    ("set unicode", CtySet(element_type=CtyString()), ["set", "string"], ["\u00e9", "z", "a"]),
    ("set empty", CtySet(element_type=CtyString()), ["set", "string"], []),
    (
        "object holding a list",
        CtyObject(attribute_types={"n": CtyList(element_type=CtyString())}),
        ["object", {"n": ["list", "string"]}],
        {"n": ["x", "y"]},
    ),
    (
        "map of objects",
        CtyMap(element_type=CtyObject(attribute_types={"a": CtyString()})),
        ["map", ["object", {"a": "string"}]],
        {"k": {"a": "1"}},
    ),
    (
        "object holding a list of objects holding a set",
        CtyObject(
            attribute_types={
                "l": CtyList(element_type=CtyObject(attribute_types={"s": CtySet(element_type=CtyString())}))
            }
        ),
        ["object", {"l": ["list", ["object", {"s": ["set", "string"]}]]}],
        {"l": [{"s": ["y", "x"]}]},
    ),
]


@pytest.mark.parametrize(("label", "cty_type", "type_spec", "native"), CASES, ids=[c[0] for c in CASES])
def test_go_cty_reads_what_pyvider_writes(
    label: str, cty_type: CtyType[Any], type_spec: Any, native: Any
) -> None:
    """The direction that matters most: our bytes on Terraform's side of the wire."""
    packed = cty_to_msgpack(cty_type.validate(native), cty_type)

    as_json = _go_convert(packed, type_spec, to_json=True)

    # parse_float=Decimal so a nested number is not rounded on the way in.
    theirs = json.loads(as_json, parse_float=Decimal)

    assert _canonical(theirs, cty_type) == _canonical(native, cty_type), (
        f"{label}: go-cty decoded our msgpack differently"
    )


@pytest.mark.parametrize(("label", "cty_type", "type_spec", "native"), CASES, ids=[c[0] for c in CASES])
def test_pyvider_reads_what_go_cty_writes(
    label: str, cty_type: CtyType[Any], type_spec: Any, native: Any
) -> None:
    """And the other direction: Terraform's bytes on ours."""
    packed = _go_convert(_as_json_text(native), type_spec, to_json=False)

    decoded = cty_from_msgpack(packed, cty_type)

    assert decoded.type.equal(cty_type)
    assert not decoded.is_null
    assert not decoded.is_unknown
    assert _canonical(decoded.raw_value, cty_type) == _canonical(native, cty_type), (
        f"{label}: we decoded go-cty's msgpack differently"
    )


@pytest.mark.parametrize(("label", "cty_type", "type_spec", "native"), CASES, ids=[c[0] for c in CASES])
def test_both_implementations_emit_the_same_bytes(
    label: str, cty_type: CtyType[Any], type_spec: Any, native: Any
) -> None:
    """Byte-for-byte agreement, not merely mutual intelligibility.

    Terraform compares serialized state, so two encodings that decode alike but
    differ on the wire still show up as a spurious diff.
    """
    ours = cty_to_msgpack(cty_type.validate(native), cty_type)
    theirs = _go_convert(_as_json_text(native), type_spec, to_json=False)

    assert ours == theirs, f"{label}: ours={ours!r} go-cty={theirs!r}"


@pytest.mark.parametrize(("label", "cty_type", "type_spec", "native"), CASES, ids=[c[0] for c in CASES])
def test_both_implementations_emit_the_same_json(
    label: str, cty_type: CtyType[Any], type_spec: Any, native: Any
) -> None:
    """The same standard applied to the JSON codec, for the same reason.

    Terraform state is JSON, so a value written by a provider and a value
    written by Terraform have to agree textually and not merely decode alike.
    Number formatting is where that bites: go-cty writes `big.Float.Text('f',
    -1)`, which has no exponent form and no trailing zeros.
    """
    ours = cty_to_json(cty_type.validate(native), cty_type)
    theirs = _go_canonical_json(_as_json_text(native), type_spec)

    assert ours == theirs, f"{label}: ours={ours!r} go-cty={theirs!r}"


# A null is a value of any type in cty, and go-cty encodes one inside any
# container. This package refuses two of them -- and refuses them on *read*,
# which is the direction Terraform drives. A provider handed state containing
# either raises instead of decoding it.
#
# The inconsistency is the tell, and it is the same shape as every other bug
# this parity work has turned up: a rule applied to the container types someone
# had in mind. A null decodes fine inside a map, a set and a tuple. It is
# refused inside a list, and inside an object unless the attribute was declared
# optional -- and declaring it optional is not a workaround, because optionality
# adds go-cty's third element to the wire type, so it changes the type Terraform
# is told about.
# Every container that now reads a null back. `list`, `list of object` and
# `object attribute` were xfailed here until the guards in CtyList.validate and
# CtyObject.validate were removed; they are in this list rather than deleted,
# because the next change to those code paths is exactly what they exist to
# catch.
READS_A_NULL: list[tuple[str, CtyType[Any], Any, bytes]] = [
    ("map value", CtyMap(element_type=CtyString()), ["map", "string"], b'{"k":null}'),
    ("set element", CtySet(element_type=CtyString()), ["set", "string"], b'["a",null]'),
    (
        "tuple element",
        CtyTuple(element_types=(CtyString(), CtyString())),
        ["tuple", ["string", "string"]],
        b'["a",null]',
    ),
    ("list element", CtyList(element_type=CtyString()), ["list", "string"], b'["a",null]'),
    (
        "object element of a list",
        CtyList(element_type=CtyObject(attribute_types={"a": CtyString()})),
        ["list", ["object", {"a": "string"}]],
        b'[{"a":"x"},null]',
    ),
    (
        "object attribute",
        CtyObject(attribute_types={"a": CtyString(), "b": CtyNumber()}),
        ["object", {"a": "string", "b": "number"}],
        b'{"a":null,"b":1}',
    ),
]


@pytest.mark.parametrize(
    ("label", "cty_type", "type_spec", "json_text"),
    READS_A_NULL,
    ids=[c[0] for c in READS_A_NULL],
)
def test_a_null_inside_these_containers_reads_back(
    label: str, cty_type: CtyType[Any], type_spec: Any, json_text: bytes
) -> None:
    """A null is a value of any type in cty, so every container has to hold one."""
    theirs = _go_convert(json_text, type_spec, to_json=False)

    decoded = cty_from_msgpack(theirs, cty_type)

    assert decoded.raw_value is not None, f"{label}: decoded to nothing"


def test_a_set_holding_a_null_re_encodes_to_the_same_bytes() -> None:
    """Where a null sorts among a set's elements is a wire difference.

    This was an xfail: go-cty wrote `["a", null]` and this package wrote
    `[null, "a"]` for the same set. Both decode to the same value, so nothing
    catches it except a byte comparison -- and Terraform compares serialized
    state, so it was a diff that reappeared on every plan. Set ordering agreed
    everywhere else, which is what made it look like a null-specific quirk
    rather than the inverted rank it was.
    """
    cty_type = CtySet(element_type=CtyString())
    theirs = _go_convert(b'["a",null]', ["set", "string"], to_json=False)

    decoded = cty_from_msgpack(theirs, cty_type)

    assert cty_to_msgpack(decoded, cty_type) == theirs


# 🌊🪢🔚
