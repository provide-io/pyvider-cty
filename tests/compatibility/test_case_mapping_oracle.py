#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`upper`, `lower` and `title` against go-cty, at every code point.

The case tables are Go's, read out of a Go toolchain, so this is the check that
they are the *oracle's* Go: every scalar value goes through both
implementations, in strings short enough to pass as one argument each.

Each code point is preceded by a space. For `upper` and `lower` that keeps a
combining mark from composing with its neighbour under the NFC normalisation
both sides apply to a string; for `title` it makes every code point
word-initial, so each one is titlecased. The last pass puts an `a` after each
code point instead, which exercises `strings.Title`'s word-separator test: the
`a` is capitalised exactly when the code point before it separates words.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
import json
import subprocess  # nosec
from typing import Any

import pytest

from pyvider.cty import CtyString, CtyValue
from pyvider.cty.functions import lower, title, upper
from tests.compatibility._oracle import soup_go

pytestmark = pytest.mark.compat

# Code points per harness call. Linux caps one argv string at 128 KiB, and a
# supplementary code point is four bytes of UTF-8 plus the space.
CHUNK = 8192

SCALARS = [codepoint for codepoint in range(0x110000) if not 0xD800 <= codepoint <= 0xDFFF]


def _chunks() -> Iterator[list[int]]:
    for start in range(0, len(SCALARS), CHUNK):
        yield SCALARS[start : start + CHUNK]


def _go(func: str, text: str) -> str:
    completed = subprocess.run(  # nosec
        [soup_go(), "cty", "call", func, json.dumps({"type": "string", "value": text}, ensure_ascii=False)],
        capture_output=True,
        check=False,
    )
    for line in completed.stdout.decode().split("\n"):
        if line.startswith("{"):
            answer = json.loads(line)
            assert answer["ok"], answer
            return str(answer["value"])
    raise AssertionError(f"{func}: harness produced no result: {completed.stderr.decode()[-400:]}")


def _first_difference(ours: str, theirs: str) -> str:
    for index, (a, b) in enumerate(zip(ours, theirs, strict=False)):
        if a != b:
            return f"at {index}: ours U+{ord(a):04X}, go-cty U+{ord(b):04X}"
    return f"lengths {len(ours)} and {len(theirs)}"


SHAPES: list[tuple[str, Callable[[CtyValue[Any]], CtyValue[Any]], Callable[[int], str]]] = [
    ("upper", upper, lambda cp: f" {chr(cp)}"),
    ("lower", lower, lambda cp: f" {chr(cp)}"),
    ("title", title, lambda cp: f" {chr(cp)}"),
    ("title", title, lambda cp: f"{chr(cp)}a "),
]


@pytest.mark.parametrize(
    ("name", "function", "shape"),
    SHAPES,
    ids=["upper", "lower", "title-word-initial", "title-separators"],
)
def test_every_code_point_maps_as_go_cty_maps_it(
    name: str, function: Callable[[CtyValue[Any]], CtyValue[Any]], shape: Callable[[int], str]
) -> None:
    for chunk in _chunks():
        text = "".join(shape(codepoint) for codepoint in chunk)
        ours = str(function(CtyString().validate(text)).value)
        theirs = _go(name, text)
        assert ours == theirs, (
            f"{name} over U+{chunk[0]:04X}..U+{chunk[-1]:04X} {_first_difference(ours, theirs)}"
        )


# 🌊🪢🔚
