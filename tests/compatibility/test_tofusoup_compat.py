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

    assert json.loads(as_json) == native, f"{label}: go-cty decoded our msgpack differently"


@pytest.mark.parametrize(("label", "cty_type", "type_spec", "native"), CASES, ids=[c[0] for c in CASES])
def test_pyvider_reads_what_go_cty_writes(
    label: str, cty_type: CtyType[Any], type_spec: Any, native: Any
) -> None:
    """And the other direction: Terraform's bytes on ours."""
    packed = _go_convert(json.dumps(native).encode(), type_spec, to_json=False)

    decoded = cty_from_msgpack(packed, cty_type)

    assert decoded.type.equal(cty_type)
    assert not decoded.is_null
    assert not decoded.is_unknown
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
    theirs = _go_convert(json.dumps(native).encode(), type_spec, to_json=False)

    assert ours == theirs, f"{label}: ours={ours!r} go-cty={theirs!r}"
