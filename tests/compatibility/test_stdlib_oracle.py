#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Stdlib functions compared against real go-cty, call for call.

`test_tofusoup_compat.py` checks that the two implementations agree on the
*wire*. This checks that they agree on the *answers*: same result type, same
result value, for the same call.

That distinction is not academic. Five functions here disagreed with go-cty for
as long as they had existed -- `regex` took its arguments in the opposite order
and threw away capture groups, `indent` took a prefix string instead of a
count, `flatten` returned a list instead of a tuple -- and every test in the
package passed the whole time, because every test asserted what the code did.
Nothing compared the two implementations, so nothing could notice.

Requires the `soup-go` harness. Point `SOUP_GO_BIN` at a built binary, or build
it with:

    cd /Volumes/data/pyv/tofusoup/src/tofusoup/harness/go/soup-go
    go build -o /tmp/soup-go ./...
"""

from __future__ import annotations

from collections.abc import Callable
import json
import os
from pathlib import Path
import shutil
import subprocess  # nosec
from typing import Any

import msgpack
import pytest

from pyvider.cty import CtyList, CtyNumber, CtyString, CtyTuple, CtyValue
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import chunklist, flatten, indent, regex, regexall

pytestmark = pytest.mark.compat

STRS = CtyList(element_type=CtyString())
NUMS = CtyList(element_type=CtyNumber())
LIST_OF_LISTS = ["list", ["list", "string"]]
TUPLE_STR_LIST = ["tuple", ["string", ["list", "string"]]]
TUPLE_TWO_LISTS = ["tuple", [["list", "string"], ["list", "string"]]]
TUPLE_NESTED = ["tuple", [["tuple", [["tuple", ["string"]]]]]]


def _soup_go() -> str:
    candidate = os.environ.get("SOUP_GO_BIN") or shutil.which("soup-go") or "/tmp/soup-go"  # nosec
    if not Path(candidate).exists():
        pytest.skip(
            f"soup-go harness not found at {candidate}. Build it from "
            "tofusoup/src/tofusoup/harness/go/soup-go, or set SOUP_GO_BIN."
        )
    return candidate


def _go_call(func: str, args: list[str]) -> dict[str, Any]:
    """Run go-cty's own implementation and return its reported result."""
    result = subprocess.run(  # nosec
        [_soup_go(), "cty", "call", func, *args], capture_output=True, check=False
    )
    for line in result.stdout.decode().splitlines():
        if line.startswith("{"):
            return json.loads(line)  # type: ignore[no-any-return]
    raise AssertionError(f"{func}: harness produced no result: {result.stderr.decode()[-400:]}")


def _as_wire(value: CtyValue[Any]) -> tuple[Any, Any]:
    """A pyvider result as the (type, value) pair go-cty reports.

    Routed through msgpack rather than read off the value, so what is compared
    is what would actually cross the wire.
    """
    return (
        value.type._to_wire_json(),
        msgpack.unpackb(cty_to_msgpack(value, value.type), strict_map_key=False),
    )


def s(text: str) -> str:
    return json.dumps({"type": "string", "value": text})


def num(value: int) -> str:
    return json.dumps({"type": "number", "value": value})


def seq(type_spec: Any, value: Any) -> str:
    return json.dumps({"type": type_spec, "value": value})


def _st(text: str) -> CtyValue[Any]:
    return CtyString().validate(text)


def _nm(value: int) -> CtyValue[Any]:
    return CtyNumber().validate(value)


# (label, go-cty function name, the pyvider call, the JSON arguments go-cty gets).
# The pyvider call is a thunk so that collection does not depend on it succeeding.
CASES: list[tuple[str, str, Callable[[], CtyValue[Any]], list[str]]] = [
    ("regex whole match", "regex", lambda: regex(_st("a.c"), _st("abc")), [s("a.c"), s("abc")]),
    ("regex one group", "regex", lambda: regex(_st("a(b)c"), _st("abc")), [s("a(b)c"), s("abc")]),
    ("regex two groups", "regex", lambda: regex(_st("(a)(b)"), _st("ab")), [s("(a)(b)"), s("ab")]),
    (
        "regex named groups",
        "regex",
        lambda: regex(_st("(?P<x>a)(?P<y>b)"), _st("ab")),
        [s("(?P<x>a)(?P<y>b)"), s("ab")],
    ),
    ("regex unmatched group", "regex", lambda: regex(_st("(a)|(z)"), _st("a")), [s("(a)|(z)"), s("a")]),
    (
        "regex unmatched named group",
        "regex",
        lambda: regex(_st("(?P<x>a)|(?P<y>z)"), _st("a")),
        [s("(?P<x>a)|(?P<y>z)"), s("a")],
    ),
    (
        "regexall unmatched named group",
        "regexall",
        lambda: regexall(_st("(?P<x>a)|(?P<y>z)"), _st("az")),
        [s("(?P<x>a)|(?P<y>z)"), s("az")],
    ),
    ("regexall plain", "regexall", lambda: regexall(_st("b"), _st("abcb")), [s("b"), s("abcb")]),
    ("regexall groups", "regexall", lambda: regexall(_st("a(b)"), _st("abab")), [s("a(b)"), s("abab")]),
    (
        "regexall named",
        "regexall",
        lambda: regexall(_st("(?P<x>b)"), _st("abcb")),
        [s("(?P<x>b)"), s("abcb")],
    ),
    ("regexall empty", "regexall", lambda: regexall(_st("(z)"), _st("abc")), [s("(z)"), s("abc")]),
    ("indent two", "indent", lambda: indent(_nm(2), _st("a\nb")), [num(2), s("a\nb")]),
    ("indent trailing", "indent", lambda: indent(_nm(2), _st("a\n")), [num(2), s("a\n")]),
    ("indent crlf", "indent", lambda: indent(_nm(2), _st("a\r\nb")), [num(2), s("a\r\nb")]),
    ("indent zero", "indent", lambda: indent(_nm(0), _st("a\nb")), [num(0), s("a\nb")]),
    ("indent empty", "indent", lambda: indent(_nm(2), _st("")), [num(2), s("")]),
    (
        "flatten lists",
        "flatten",
        lambda: flatten(CtyList(element_type=STRS).validate([["a"], ["b", "c"]])),
        [seq(LIST_OF_LISTS, [["a"], ["b", "c"]])],
    ),
    (
        "flatten mixed",
        "flatten",
        lambda: flatten(CtyTuple(element_types=(CtyString(), STRS)).validate(["a", ["b"]])),
        [seq(TUPLE_STR_LIST, ["a", ["b"]])],
    ),
    (
        "flatten null scalar",
        "flatten",
        lambda: flatten(CtyTuple(element_types=(CtyString(), STRS)).validate([None, ["b"]])),
        [seq(TUPLE_STR_LIST, [None, ["b"]])],
    ),
    (
        "flatten null sequence",
        "flatten",
        lambda: flatten(CtyTuple(element_types=(STRS, STRS)).validate([None, ["b"]])),
        [seq(TUPLE_TWO_LISTS, [None, ["b"]])],
    ),
    (
        "flatten deep",
        "flatten",
        lambda: flatten(
            CtyTuple(
                element_types=(CtyTuple(element_types=(CtyTuple(element_types=(CtyString(),)),)),)
            ).validate([[["a"]]])
        ),
        [seq(TUPLE_NESTED, [[["a"]]])],
    ),
    (
        "flatten empty",
        "flatten",
        lambda: flatten(CtyList(element_type=STRS).validate([])),
        [seq(LIST_OF_LISTS, [])],
    ),
    (
        "chunklist strings",
        "chunklist",
        lambda: chunklist(STRS.validate(["a", "b", "c"]), _nm(2)),
        [seq(["list", "string"], ["a", "b", "c"]), num(2)],
    ),
    (
        "chunklist size zero",
        "chunklist",
        lambda: chunklist(STRS.validate(["a", "b", "c"]), _nm(0)),
        [seq(["list", "string"], ["a", "b", "c"]), num(0)],
    ),
    (
        "chunklist numbers",
        "chunklist",
        lambda: chunklist(NUMS.validate([1, 2, 3]), _nm(2)),
        [seq(["list", "number"], [1, 2, 3]), num(2)],
    ),
    (
        "chunklist empty",
        "chunklist",
        lambda: chunklist(STRS.validate([]), _nm(2)),
        [seq(["list", "string"], []), num(2)],
    ),
    (
        "chunklist oversized",
        "chunklist",
        lambda: chunklist(STRS.validate(["a"]), _nm(5)),
        [seq(["list", "string"], ["a"]), num(5)],
    ),
]


@pytest.mark.parametrize(("label", "func", "ours", "go_args"), CASES, ids=[case[0] for case in CASES])
def test_the_two_implementations_return_the_same_thing(
    label: str, func: str, ours: Callable[[], CtyValue[Any]], go_args: list[str]
) -> None:
    theirs = _go_call(func, go_args)

    assert theirs.get("ok"), f"{label}: go-cty refused the call: {theirs.get('error')}"
    assert _as_wire(ours()) == (theirs["type"], theirs.get("value")), label


# (label, go-cty function name, the pyvider call, the JSON arguments; both must refuse)
REFUSALS: list[tuple[str, str, Callable[[], CtyValue[Any]], list[str]]] = [
    (
        "regex mixed capture groups",
        "regex",
        lambda: regex(_st("(?P<x>a)(b)"), _st("ab")),
        [s("(?P<x>a)(b)"), s("ab")],
    ),
    ("regex no match", "regex", lambda: regex(_st("z"), _st("abc")), [s("z"), s("abc")]),
    ("regex invalid pattern", "regex", lambda: regex(_st("("), _st("abc")), [s("("), s("abc")]),
    (
        "chunklist negative size",
        "chunklist",
        lambda: chunklist(STRS.validate(["a"]), _nm(-1)),
        [seq(["list", "string"], ["a"]), num(-1)],
    ),
    ("flatten a string", "flatten", lambda: flatten(_st("x")), [s("x")]),
]


@pytest.mark.parametrize(("label", "func", "ours", "go_args"), REFUSALS, ids=[case[0] for case in REFUSALS])
def test_both_implementations_refuse_the_same_calls(
    label: str, func: str, ours: Callable[[], CtyValue[Any]], go_args: list[str]
) -> None:
    """The refusals are half the parity claim, and the easier half to get wrong.

    A function that quietly returns something where go-cty errors is the
    divergence that survives longest -- `regex` returned `""` for a non-match
    for exactly that reason, and no caller could tell it from a real match.
    """
    assert not _go_call(func, go_args).get("ok"), f"{label}: go-cty accepted it after all"
    with pytest.raises(CtyFunctionError):
        ours()


# 🌊🪢🔚
