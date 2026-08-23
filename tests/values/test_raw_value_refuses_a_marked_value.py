#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`raw_value` is the way out of cty, and a mark does not fit through it.

What comes back is a `str` or a `dict`, with nowhere left to record that it was
sensitive. Every other route out of a marked container carries the marks along
-- a subscript, iteration, a path step -- and both codecs refuse a marked value
outright. This was the one door left open, and what it handed back was the
secret itself.

go-cty draws the line in the same place and for the same reason: its
value-to-Go-native escapes (`AsString`, `AsBigFloat`, `AsValueSlice`,
`EncapsulatedValue`, `cty/value_ops.go:1456` onward) all call `assertUnmarked`
and panic, while everything that answers with another `Value` unmarks, acts and
remarks.

Deliberately narrower than go-cty's rule. `len()`, `bool()` and `in` are also
value-to-native escapes and are **not** changed: go-cty's panic sites are all
explicit method calls, while those three are invoked by Python *syntax*, so
refusing there would raise on lines no reader would recognise as a
declassification. Tests below hold that line so it is a decision rather than an
oversight.
"""

from __future__ import annotations

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtyObject, CtyString, CtyValue
from pyvider.cty.exceptions import CtyMarksSerializationError
from pyvider.cty.marks import CtyMark

S, N = CtyString(), CtyNumber()
SENSITIVE = CtyMark("sensitive")

LIST = CtyList(element_type=S)
MAP = CtyMap(element_type=S)
OBJECT = CtyObject({"a": S})


def marked_values() -> list[tuple[str, CtyValue[object]]]:
    return [
        ("string", S.validate("secret").mark(SENSITIVE)),
        ("number", N.validate(1).mark(SENSITIVE)),
        ("list", LIST.validate(["secret"]).mark(SENSITIVE)),
        ("map", MAP.validate({"k": "secret"}).mark(SENSITIVE)),
        ("object", OBJECT.validate({"a": "secret"}).mark(SENSITIVE)),
        ("null", CtyValue.null(S).mark(SENSITIVE)),
    ]


@pytest.mark.parametrize(("kind", "value"), marked_values(), ids=[case[0] for case in marked_values()])
class TestAMarkedValueRefuses:
    def test_it_raises(self, kind: str, value: CtyValue[object]) -> None:
        with pytest.raises(CtyMarksSerializationError):
            _ = value.raw_value

    def test_the_message_names_the_mark(self, kind: str, value: CtyValue[object]) -> None:
        with pytest.raises(CtyMarksSerializationError, match="sensitive"):
            _ = value.raw_value

    def test_it_says_what_to_do_instead(self, kind: str, value: CtyValue[object]) -> None:
        with pytest.raises(CtyMarksSerializationError, match="unmark"):
            _ = value.raw_value


class TestUnmarkingFirstIsTheWayThrough:
    def test_an_unmarked_copy_answers(self) -> None:
        marked = S.validate("secret").mark(SENSITIVE)

        assert marked.unmark()[0].raw_value == "secret"

    def test_the_marks_come_back_so_the_caller_decides(self) -> None:
        marked = S.validate("secret").mark(SENSITIVE)

        assert marked.unmark()[1] == frozenset({SENSITIVE})

    def test_a_container_unmarks_at_the_top_level(self) -> None:
        marked = LIST.validate(["secret"]).mark(SENSITIVE)

        assert marked.unmark()[0].raw_value == ["secret"]


class TestAnUnmarkedValueIsUntouched:
    def test_a_string(self) -> None:
        assert S.validate("x").raw_value == "x"

    def test_a_list(self) -> None:
        assert LIST.validate(["x"]).raw_value == ["x"]

    def test_a_null_is_still_none(self) -> None:
        assert CtyValue.null(S).raw_value is None

    def test_an_unknown_still_raises_valueerror(self) -> None:
        """Unchanged, and a different complaint from the marked one."""
        with pytest.raises(ValueError):
            _ = CtyValue.unknown(S).raw_value


class TestTheOtherEscapesAreDeliberatelyLeftOpen:
    """Not an oversight. See this module's docstring.

    `len(v)`, `if v:` and `x in v` are invoked by syntax rather than by an
    explicit call, so refusing there raises on lines that do not read as a
    declassification. They are a 0.6.0 decision, not this one.
    """

    def test_len_still_answers(self) -> None:
        assert len(LIST.validate(["a", "b"]).mark(SENSITIVE)) == 2

    def test_bool_still_answers(self) -> None:
        assert bool(S.validate("x").mark(SENSITIVE)) is True

    def test_contains_still_answers(self) -> None:
        assert S.validate("a") in LIST.validate(["a"]).mark(SENSITIVE)

    def test_the_payload_is_still_reachable(self) -> None:
        assert S.validate("x").mark(SENSITIVE).value == "x"


# 🌊🪢🔚
