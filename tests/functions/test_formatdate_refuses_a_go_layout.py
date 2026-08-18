#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`formatdate` refuses a Go reference layout instead of returning it verbatim.

The only place this package declines something go-cty answers, and the reasoning
is about which failure a caller can act on rather than about parity.

go-cty defines its own format scheme -- `YYYY`, `MM`, `DD`, `hh`, `mm`, `ss`,
`EEEE`, `MMMM`, `AA`, `ZZZZZ` -- and reads digits as literal text. So

    formatdate("2006-01-02", ts)   -> "2006-01-02"

is not an error, not a date, and shaped exactly like the answer the caller
wanted. Before 0.5.0 this package translated Go's own reference layout into
`strftime`, so that call *did* return a formatted date; the change is the widest
of the forty-three breaking changes in the release and the only one whose wrong
answer looks right. A test asserting "the output looks like a date" passes, and
the wrong value reaches Terraform state.

Every expectation about go-cty here was read off v1.19.0 through the oracle,
including the escape:

    formatdate("2006-01-02", ts)    -> "2006-01-02"
    formatdate("'2006-01-02'", ts)  -> "2006-01-02"
    formatdate("Version 2006.01")   -> ERR invalid date format verb "V"
"""

from __future__ import annotations

import pytest

from pyvider.cty import CtyString
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import formatdate

TIMESTAMP = "2026-08-18T12:34:56Z"


def fmt(spec: str) -> str:
    return str(formatdate(CtyString().validate(spec), CtyString().validate(TIMESTAMP)).value)


class TestItRefusesAGoLayout:
    @pytest.mark.parametrize(
        "spec",
        [
            pytest.param("2006-01-02", id="date"),
            pytest.param("2006-01-02T15:04:05Z07:00", id="rfc3339-layout"),
            pytest.param("2006/01/02", id="slashes"),
            pytest.param("15:04:05 2006", id="time-first"),
            pytest.param("2006-01-02 15:04:05", id="date-and-time"),
        ],
    )
    def test_a_layout_carrying_two_reference_tokens_is_refused(self, spec: str) -> None:
        with pytest.raises(CtyFunctionError, match="Go's reference layout"):
            fmt(spec)

    def test_the_message_names_both_ways_out(self) -> None:
        """A caller has to be able to act on it: rewrite, or quote."""
        with pytest.raises(CtyFunctionError) as caught:
            fmt("2006-01-02")

        message = str(caught.value)
        assert "YYYY-MM-DD" in message
        assert "'2006-01-02'" in message


class TestTheTriggerIsNarrow:
    """It takes a *second* reference token to make the intent unmistakable."""

    def test_a_bare_year_is_still_a_literal(self) -> None:
        """A year on its own is a plausible thing to write, so it still works."""
        assert fmt("2006") == "2006"

    def test_a_go_cty_format_is_untouched(self) -> None:
        assert fmt("YYYY-MM-DD") == "2026-08-18"
        assert fmt("EEEE, DD MMMM YYYY") == "Tuesday, 18 August 2026"

    def test_a_format_with_no_year_token_is_untouched(self) -> None:
        """`01` and `02` alone say nothing; `2006` is the unmistakable one."""
        assert fmt("hh:mm:ss") == "12:34:56"


class TestTheEscapeWorks:
    """The refusal names quoting, so quoting has to actually work."""

    def test_a_quoted_layout_renders_as_the_literal(self) -> None:
        assert fmt("'2006-01-02'") == "2006-01-02"

    def test_only_unquoted_text_is_examined(self) -> None:
        """The first version of this guard refused its own escape."""
        assert fmt("YYYY '2006-01' MM") == "2026 2006-01 08"

    def test_a_malformed_format_still_gets_its_own_error(self) -> None:
        """The guard must not mask the error the ordinary path would give."""
        with pytest.raises(CtyFunctionError, match="unterminated literal"):
            fmt("'unterminated")


# 🐍🏗️🔚
