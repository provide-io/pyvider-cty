#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`format` and `formatlist` report their failures in go-cty's exact words.

The stdlib sweep compares *whether* a call errored, not what it said, so eight
diverging messages sat undetected behind a green differential suite. They were
found on 2026-08-21 while resolving a different `formatlist` question, and the
divergence was systemic rather than incidental: every `ERR_FORMAT_*` message
carried a `format: ` prefix go-cty does not use, `{verb!r}` spelled a verb
`'%s'` where Go's `%q` spells it `"%s"`, and `formatlist` never added go-cty's
own `error on format iteration N: ` wrapper.

These are not cosmetic. A provider surfaces a stdlib error to an operator as a
Terraform diagnostic, so a differing string is a differing diagnostic for the
same configuration -- the same argument that makes `conformance` compare its
messages rather than only its verdict.

Every expectation here was read from `soup-go cty call` against go-cty v1.19.0,
and each case is asserted against the harness at run time rather than against a
transcription, so a harness bump moves both sides together.
"""

from __future__ import annotations

import json
import subprocess  # nosec B404 - the oracle harness, path resolved by soup_go()
from typing import Any

import pytest

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import STDLIB
from tests.compatibility._oracle import soup_go

pytestmark = pytest.mark.compat

S, N, B = CtyString(), CtyNumber(), CtyBool()
LS = CtyList(element_type=S)


def _go_error(func: str, args: list[str]) -> str | None:
    """go-cty's own message for a failing call, or None if it succeeded."""
    result = subprocess.run(  # nosec B603 - fixed argv, no shell
        [soup_go(), "cty", "call", func, *args], capture_output=True, check=False
    )
    for line in result.stdout.decode().splitlines():
        if line.startswith("{"):
            reported: dict[str, Any] = json.loads(line)
            return None if reported.get("ok") else str(reported.get("error"))
    raise AssertionError(f"{func}: harness produced no result: {result.stderr.decode()[-400:]}")


def _here_error(func: str, arguments: list[Any]) -> str | None:
    try:
        STDLIB[func](*arguments)
    except CtyFunctionError as exc:
        return str(exc)
    return None


def spec(type_spec: Any, value: Any) -> str:
    return json.dumps({"type": type_spec, "value": value})


# Each case is (label, go-harness argv, this library's arguments). The two
# columns describe the same call in the two spellings the two sides accept.
CASES: list[tuple[str, str, list[str], list[Any]]] = [
    (
        "an extra argument the format string never uses",
        "format",
        [spec("string", "%s"), spec("string", "a"), spec("string", "b")],
        [S.validate("%s"), S.validate("a"), S.validate("b")],
    ),
    (
        "arguments with no verb to consume them",
        "format",
        [spec("string", "hi"), spec("string", "a")],
        [S.validate("hi"), S.validate("a")],
    ),
    (
        "a verb with no argument left for it",
        "format",
        [spec("string", "%s %s"), spec("string", "a")],
        [S.validate("%s %s"), S.validate("a")],
    ),
    (
        "a verb go-cty does not define",
        "format",
        [spec("string", "%z"), spec("string", "a")],
        [S.validate("%z"), S.validate("a")],
    ),
    (
        "a null where a value was required",
        "format",
        [spec("string", "%s"), json.dumps({"type": "string", "null": True})],
        [S.validate("%s"), S.validate(None)],
    ),
    (
        "a string that cannot be parsed as the verb's type",
        "format",
        [spec("string", "%d"), spec("string", "a")],
        [S.validate("%d"), S.validate("a")],
    ),
    (
        "a bool where a number was required",
        "format",
        [spec("string", "%d"), spec("bool", True)],
        [S.validate("%d"), B.validate(True)],
    ),
    (
        "a number where a bool was required",
        "format",
        [spec("string", "%t"), spec("number", 1)],
        [S.validate("%t"), N.validate(1)],
    ),
    (
        "a collection where a string was required",
        "format",
        [spec("string", "%s"), spec(["list", "string"], ["a"])],
        [S.validate("%s"), LS.validate(["a"])],
    ),
    (
        "formatlist naming the iteration that failed",
        "formatlist",
        [spec("string", "%s"), spec(["list", "string"], ["a"]), spec(["list", "string"], ["b"])],
        [S.validate("%s"), LS.validate(["a"]), LS.validate(["b"])],
    ),
    (
        "formatlist arguments of inconsistent length",
        "formatlist",
        [
            spec("string", "%s %s"),
            spec(["list", "string"], ["a"]),
            spec(["list", "string"], ["b", "c"]),
        ],
        [S.validate("%s %s"), LS.validate(["a"]), LS.validate(["b", "c"])],
    ),
]


@pytest.mark.parametrize(("label", "func", "go_args", "here_args"), CASES, ids=[case[0] for case in CASES])
def test_the_two_report_the_same_message(
    label: str, func: str, go_args: list[str], here_args: list[Any]
) -> None:
    theirs = _go_error(func, go_args)
    assert theirs is not None, f"{label}: go-cty accepted this call, so there is no message to match"

    ours = _here_error(func, here_args)
    assert ours is not None, f"{label}: this library accepted a call go-cty refuses"

    assert ours == theirs, label


def test_the_null_case_is_actually_a_null() -> None:
    """The harness spells a null differently from a value, and a case that
    silently sent the string "None" would compare two error paths that are not
    the same one."""
    assert S.validate(None).is_null


# 🌊🪢🔚
