#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`formatlist` pairs row N of every argument, which go-cty does not.

go-cty walks its arguments with element iterators and advances them inside the
same loop that formats a row::

    for i := range fmtArgs {
        iterator := iterators[i]
        iterator.Next()
        _, val := iterator.Element()
        fmtArgs[i] = val

        if !fmtArgs[i].IsWhollyKnown() {
            ret = append(ret, cty.UnknownVal(cty.String).RefineNotNull())
            continue Results        // <- leaves later iterators un-advanced
        }
    }

`continue Results` jumps to the next *row*, so any argument after the unknown
one never had `Next()` called for that row. From then on the iterators are out
of step by the number of rows skipped, and go-cty pairs row N of one argument
with row N-k of another.

The result is not an unknown, which would be defensible -- it is a confidently
wrong known string:

    formatlist("%s-%s", [unknown, "a"], ["x", "y"])
    go-cty  ["<unknown>", "a-x"]     <- "a" paired with "x"
    here    ["<unknown>", "a-y"]     <- "a" paired with "y"

This package indexes each argument by the row number, so it cannot drift. That
makes this one of the few places where matching go-cty would mean adopting a
defect, alongside the set-to-list conversion recorded in
`docs/reference/go-cty-comparison.md`.

Found on 2026-08-21 by `test_stdlib_fuzz.py`, from
``formatlist("%d-%s", [null, unknown, null], [unknown, unknown, null])`` -- a
shape no hand-written table held, and which only misbehaves because the unknown
sits *before* a row that would otherwise have been formatted.

These run without a Go toolchain; the go-cty answers above were read from
`soup-go cty call formatlist` against v1.19.0 and are quoted, not computed.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import CtyList, CtyString
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import STDLIB
from pyvider.cty.values import CtyValue

S = CtyString()
LS = CtyList(element_type=S)


def rows(result: CtyValue[Any]) -> list[str | None]:
    """Each row as its text, or None where the row is unknown."""
    return [None if element.is_unknown else element.value for element in result.value]


def listed(*members: str | None) -> CtyValue[Any]:
    """A list value; None marks an unknown element."""
    return CtyValue(
        vtype=LS,
        value=tuple(CtyValue.unknown(S) if member is None else S.validate(member) for member in members),
    )


class TestAnUnknownRowDoesNotShiftTheRowsAfterIt:
    def test_the_case_that_proves_go_cty_wrong(self) -> None:
        """go-cty answers `a-x` here. The second row's arguments are `a` and `y`."""
        result = STDLIB["formatlist"](S.validate("%s-%s"), listed(None, "a"), listed("x", "y"))

        assert rows(result) == [None, "a-y"]

    def test_the_shift_grows_with_the_number_of_skipped_rows(self) -> None:
        """Two unknown rows would put go-cty two behind, not one."""
        result = STDLIB["formatlist"](S.validate("%s-%s"), listed(None, None, "c"), listed("x", "y", "z"))

        assert rows(result) == [None, None, "c-z"]

    def test_an_unknown_in_the_later_argument_shifts_nothing(self) -> None:
        """The asymmetry is the tell: go-cty only drifts when the unknown comes
        before an argument it has not read yet, so this case agrees on both
        sides and is worth keeping to show the boundary."""
        result = STDLIB["formatlist"](S.validate("%s-%s"), listed("a", "b"), listed(None, "y"))

        assert rows(result) == [None, "b-y"]

    def test_every_row_unknown_is_still_every_row_unknown(self) -> None:
        result = STDLIB["formatlist"](S.validate("%s-%s"), listed(None, None), listed("x", "y"))

        assert rows(result) == [None, None]


class TestTheRowsThatCanBeFormattedStillAre:
    """The correction must not turn a formattable row into an unknown."""

    def test_no_unknowns_at_all(self) -> None:
        result = STDLIB["formatlist"](S.validate("%s-%s"), listed("a", "b"), listed("x", "y"))

        assert rows(result) == ["a-x", "b-y"]

    def test_a_scalar_argument_is_reused_on_every_row(self) -> None:
        result = STDLIB["formatlist"](S.validate("%s-%s"), listed("a", "b"), S.validate("z"))

        assert rows(result) == ["a-z", "b-z"]


def test_a_null_row_still_fails_when_no_unknown_precedes_it() -> None:
    """Nulls are known, so a row holding one is formatted and refused.

    Worth stating next to the above: the fuzz case that found the drift held
    nulls *and* unknowns, and it would be easy to conclude the nulls were the
    subject. They are not -- go-cty refuses this identically.
    """
    with pytest.raises(CtyFunctionError, match="null value cannot be formatted"):
        STDLIB["formatlist"](S.validate("%d"), LS.validate([None]))


# 🌊🪢🔚
