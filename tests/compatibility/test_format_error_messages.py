#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`format` and `formatlist` say more than go-cty does, on purpose.

This module pins a deliberate divergence rather than a parity claim, and exists
because the stdlib sweep compares *whether* a call errored and never what it
said -- so nothing was watching these strings at all.

go-cty raises its stdlib errors bare: `must have map or object type`, with no
function name and usually no mention of what was actually passed. That is not
carelessness, it is division of labour -- HCL wraps the message with the
argument context before an operator sees it, so Terraform renders
`Invalid value for "inputMap" parameter: must have map or object type`. Nothing
wraps them here. A caller catching `CtyFunctionError` gets the string and
nothing else, so the string has to carry the context itself.

So this library names the function and says what it was given, matching the 34
other prefixed messages in `config/defaults.py`. Measured against the oracle,
the two differ on every case below, and the difference is the point:

    go-cty:  unsupported value for "%d" at 0: a number is required
    here:    format: unsupported value for '%d' at 0: number is required, got string

What is *not* deliberate, and was fixed alongside these tests, is the
interpolation of a whole `CtyConversionError` into that slot -- it nested its
cause and named Python types, so the message above used to end with "Cannot
represent str value 'a' as Decimal (source_type=CtyValue, target_type=number)".
The detail still reaches a traceback through `__cause__`; it just no longer
reaches a Terraform diagnostic.

The related behavioural question is settled and was a false alarm: go-cty does
*not* raise "too many arguments" for an iteration whose arguments are unknown,
and neither does this library. See `docs/reference/go-cty-comparison.md`.
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


# (label, function, harness argv, this library's arguments, expected message)
CASES: list[tuple[str, str, list[str], list[Any], str]] = [
    (
        "an extra argument the format string never uses",
        "format",
        [spec("string", "%s"), spec("string", "a"), spec("string", "b")],
        [S.validate("%s"), S.validate("a"), S.validate("b")],
        "format: too many arguments; only 1 used by format string",
    ),
    (
        "arguments with no verb to consume them",
        "format",
        [spec("string", "hi"), spec("string", "a")],
        [S.validate("hi"), S.validate("a")],
        "format: too many arguments; no verbs in format string",
    ),
    (
        "a verb with no argument left for it",
        "format",
        [spec("string", "%s %s"), spec("string", "a")],
        [S.validate("%s %s"), S.validate("a")],
        "format: not enough arguments for '%s' at 3: need index 2 but have 1 total",
    ),
    (
        "a verb this library does not define",
        "format",
        [spec("string", "%z"), spec("string", "a")],
        [S.validate("%z"), S.validate("a")],
        "format: unsupported verb 'z' at offset 0",
    ),
    (
        "a null where a value was required",
        "format",
        [spec("string", "%s"), json.dumps({"type": "string", "null": True})],
        [S.validate("%s"), S.validate(None)],
        "format: unsupported value for '%s' at 0: null value cannot be formatted",
    ),
    (
        "a string that cannot be parsed as the verb's type",
        "format",
        [spec("string", "%d"), spec("string", "a")],
        [S.validate("%d"), S.validate("a")],
        "format: unsupported value for '%d' at 0: number is required, got string",
    ),
    (
        "a bool where a number was required",
        "format",
        [spec("string", "%d"), spec("bool", True)],
        [S.validate("%d"), B.validate(True)],
        "format: unsupported value for '%d' at 0: number is required, got bool",
    ),
    (
        "a collection where a string was required",
        "format",
        [spec("string", "%s"), spec(["list", "string"], ["a"])],
        [S.validate("%s"), LS.validate(["a"])],
        "format: unsupported value for '%s' at 0: string is required, got list of string",
    ),
    (
        "formatlist naming the iteration that failed",
        "formatlist",
        [spec("string", "%s"), spec(["list", "string"], ["a"]), spec(["list", "string"], ["b"])],
        [S.validate("%s"), LS.validate(["a"]), LS.validate(["b"])],
        "formatlist: iteration 0: too many arguments; only 1 used by format string",
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
        "formatlist: argument 2 has length 2, which is inconsistent with argument 1 of length 1",
    ),
]

IDS = [case[0] for case in CASES]


@pytest.mark.parametrize(("label", "func", "go_args", "here_args", "expected"), CASES, ids=IDS)
def test_the_message_is_the_one_this_library_promises(
    label: str, func: str, go_args: list[str], here_args: list[Any], expected: str
) -> None:
    """The wording is pinned, so a refactor cannot quietly reword a diagnostic."""
    assert _here_error(func, here_args) == expected, label


@pytest.mark.parametrize(("label", "func", "go_args", "here_args", "expected"), CASES, ids=IDS)
def test_both_implementations_refuse_the_same_calls(
    label: str, func: str, go_args: list[str], here_args: list[Any], expected: str
) -> None:
    """The divergence is in the wording only.

    Whether a call is refused is the part that has to agree: a call go-cty
    accepts and this library rejects is a provider that cannot plan a
    configuration Terraform considers valid, which no amount of friendlier
    prose would excuse.
    """
    assert _go_error(func, go_args) is not None, f"{label}: go-cty accepted this call"
    assert _here_error(func, here_args) is not None, f"{label}: this library accepted it"


@pytest.mark.parametrize(("label", "func", "go_args", "here_args", "expected"), CASES, ids=IDS)
def test_the_extra_context_is_what_makes_them_differ(
    label: str, func: str, go_args: list[str], here_args: list[Any], expected: str
) -> None:
    """Guards the divergence itself.

    If a future change quietly adopts go-cty's bare wording, the pinned strings
    above would be updated to match and nothing would record that the library
    had changed its mind. This asserts the messages are deliberately *not*
    identical, so making them identical has to be a decision someone writes
    down here.
    """
    theirs = _go_error(func, go_args)
    assert theirs is not None, f"{label}: go-cty accepted this call"
    assert _here_error(func, here_args) != theirs, (
        f"{label}: the two now agree; if that is intended, this module is the thing to rewrite"
    )


def test_no_message_leaks_the_internal_conversion_error() -> None:
    """`format("%d", "a")` used to report the nested `CtyConversionError`.

    It named Python types at an operator who wrote HCL: "Cannot represent str
    value 'a' as Decimal (source_type=CtyValue, target_type=number)". The detail
    belongs on the traceback, not in the diagnostic.
    """
    message = _here_error("format", [S.validate("%d"), S.validate("a")])

    assert message is not None
    for leak in ("Decimal", "CtyValue", "source_type", "Traceback"):
        assert leak not in message, f"internal detail {leak!r} reached the message"


def test_the_detail_is_still_reachable_from_the_exception() -> None:
    """Dropping it from the message must not drop it from the traceback."""
    with pytest.raises(CtyFunctionError) as caught:
        STDLIB["format"](S.validate("%d"), S.validate("a"))

    assert caught.value.__cause__ is not None, "the conversion failure was not chained"
    assert "Decimal" in str(caught.value.__cause__)


# 🌊🪢🔚
