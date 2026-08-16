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

Requires the `soup-go` harness. Point `SOUP_GO_BIN` at a built binary, or build
it with:

    cd /Volumes/data/pyv/tofusoup/src/tofusoup/harness/go/soup-go
    go build -o /tmp/soup-go ./...
"""

from __future__ import annotations

from decimal import Decimal
import json
import os
from pathlib import Path
import shutil
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
    CtyString,
    CtyType,
)
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack

pytestmark = pytest.mark.compat


def _soup_go() -> str:
    """The harness binary, or skip. Never silently passes without it."""
    candidate = os.environ.get("SOUP_GO_BIN") or shutil.which("soup-go") or "/tmp/soup-go"  # nosec
    if not Path(candidate).exists():
        pytest.skip(
            f"soup-go harness not found at {candidate}. Build it from "
            "tofusoup/src/tofusoup/harness/go/soup-go, or set SOUP_GO_BIN."
        )
    return candidate


def _as_json_text(native: Any) -> bytes:
    """The JSON go-cty is handed. A Decimal is written as its own digits so the
    harness parses the same number we encoded, rather than a float rounding."""
    if isinstance(native, Decimal):
        return format(native, "f").encode()
    return json.dumps(native).encode()


def _same_number(left: Any, right: Any) -> bool:
    """Numeric comparison that does not route through float."""
    return Decimal(str(left)) == Decimal(str(right))


def _go_convert(payload: bytes, type_spec: Any, *, to_json: bool) -> bytes:
    """Round a value through go-cty, converting between msgpack and JSON."""
    binary = _soup_go()
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
]


@pytest.mark.parametrize(("label", "cty_type", "type_spec", "native"), CASES, ids=[c[0] for c in CASES])
def test_go_cty_reads_what_pyvider_writes(
    label: str, cty_type: CtyType[Any], type_spec: Any, native: Any
) -> None:
    """The direction that matters most: our bytes on Terraform's side of the wire."""
    packed = cty_to_msgpack(cty_type.validate(native), cty_type)

    as_json = _go_convert(packed, type_spec, to_json=True)

    if isinstance(native, Decimal):
        assert _same_number(as_json.decode().strip(), native), (
            f"{label}: go-cty decoded our msgpack differently"
        )
    else:
        assert json.loads(as_json) == native, f"{label}: go-cty decoded our msgpack differently"


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
    if isinstance(native, Decimal):
        assert _same_number(decoded.raw_value, native), f"{label}: we decoded go-cty's msgpack differently"
    else:
        assert decoded.raw_value == native, f"{label}: we decoded go-cty's msgpack differently"


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
