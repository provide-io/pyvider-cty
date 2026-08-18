#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""formatdate and timeadd against go-cty's `cty/function/stdlib/datetime.go`.

Every expectation here was taken from the go-cty oracle rather than from
reading the Go source, since the two disagreed in several places when this was
written -- notably that `formatdate` uses go-cty's own YYYY-MM-DD dialect and
not Go's 2006-01-02 layout, which is what this package used to implement.
"""

from collections.abc import Callable
from typing import Any

import pytest

from pyvider.cty import CtyString, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import SIGNATURES, formatdate, timeadd
from pyvider.cty.values.markers import RefinedUnknownValue


def S(v: str) -> object:
    return CtyString().validate(v)


UTC_NOON = "2020-01-02T13:04:05Z"


class TestFormatDateVerbs:
    """Each verb, at each length go-cty accepts."""

    @pytest.mark.parametrize(
        ("spec", "expected"),
        [
            ("YY", "20"),
            ("YYYY", "2020"),
            ("M", "1"),
            ("MM", "01"),
            ("MMM", "Jan"),
            ("MMMM", "January"),
            ("D", "2"),
            ("DD", "02"),
            ("EEE", "Thu"),
            ("EEEE", "Thursday"),
            ("h", "13"),
            ("hh", "13"),
            ("H", "1"),
            ("HH", "01"),
            ("AA", "PM"),
            ("aa", "pm"),
            ("m", "4"),
            ("mm", "04"),
            ("s", "5"),
            ("ss", "05"),
            ("Z", "Z"),
            ("ZZZ", "UTC"),
            ("ZZZZ", "+0000"),
            ("ZZZZZ", "+00:00"),
        ],
    )
    def test_verb(self, spec: str, expected: str) -> None:
        assert formatdate(S(spec), S(UTC_NOON)).value == expected

    def test_midnight_is_twelve_am(self) -> None:
        """The 12-hour verbs read 0 as 12, and the meridiem marker follows."""
        midnight = "2020-01-02T00:30:00Z"

        assert formatdate(S("H"), S(midnight)).value == "12"
        assert formatdate(S("HH"), S(midnight)).value == "12"
        assert formatdate(S("AA"), S(midnight)).value == "AM"
        assert formatdate(S("aa"), S(midnight)).value == "am"

    def test_noon_is_twelve_pm(self) -> None:
        noon = "2020-01-02T12:30:00Z"

        assert formatdate(S("HH"), S(noon)).value == "12"
        assert formatdate(S("AA"), S(noon)).value == "PM"

    @pytest.mark.parametrize(
        ("spec", "expected"),
        [
            ("Z", "-08:00"),
            ("ZZZ", "-0800"),
            ("ZZZZ", "-0800"),
            ("ZZZZZ", "-08:00"),
        ],
    )
    def test_timezone_verbs_off_utc(self, spec: str, expected: str) -> None:
        """Only the one-letter and three-letter forms special-case UTC."""
        assert formatdate(S(spec), S("2020-11-22T13:04:05-08:00")).value == expected


class TestFormatDateLiterals:
    def test_a_whole_format(self) -> None:
        assert (
            formatdate(S("EEEE, DD MMMM YYYY hh:mm:ss ZZZZ"), S("2020-01-02T03:04:05Z")).value
            == "Thursday, 02 January 2020 03:04:05 +0000"
        )

    def test_non_letters_are_literal(self) -> None:
        assert formatdate(S("YYYY-MM-DD"), S("2020-01-02T03:04:05Z")).value == "2020-01-02"

    def test_digits_are_literal(self) -> None:
        """The dialect is go-cty's, not Go's: every digit is literal text.

        Shown through the quoted form, because the *unquoted* Go reference
        layout is now refused rather than returned -- the one place this package
        declines something go-cty answers, on the grounds that a wrong answer
        shaped like a right one is worse than a refusal. The reasoning and the
        full matrix are in `test_formatdate_refuses_a_go_layout.py`; this file
        keeps the parity claim the refusal is built on, which is that go-cty
        would hand the digits straight back.
        """
        assert formatdate(S("'2006-01-02'"), S("2020-02-03T04:05:06Z")).value == "2006-01-02"
        assert formatdate(S("2006"), S("2020-02-03T04:05:06Z")).value == "2006"

    def test_quoted_text_is_not_interpreted(self) -> None:
        assert formatdate(S("'today is' YYYY"), S("2020-01-02T03:04:05Z")).value == "today is 2020"

    def test_a_doubled_quote_is_one_quote(self) -> None:
        assert formatdate(S("''"), S("2020-01-02T03:04:05Z")).value == "'"

    def test_a_doubled_quote_inside_a_sequence(self) -> None:
        assert formatdate(S("'it''s' YYYY"), S("2020-01-02T03:04:05Z")).value == "it's 2020"

    def test_an_empty_format_is_an_empty_string(self) -> None:
        assert formatdate(S(""), S("2020-01-02T03:04:05Z")).value == ""

    @pytest.mark.parametrize("spec", ["'", "'unterminated"])
    def test_an_unterminated_literal_is_an_error(self, spec: str) -> None:
        with pytest.raises(CtyFunctionError, match="unterminated literal"):
            formatdate(S(spec), S("2020-01-02T03:04:05Z"))


class TestFormatDateRejects:
    @pytest.mark.parametrize("spec", ["YYY", "YYYYY", "MMMMM", "DDD", "EE", "hhh", "A", "aaa", "ZZ", "ZZZZZZ"])
    def test_a_verb_of_the_wrong_length(self, spec: str) -> None:
        with pytest.raises(CtyFunctionError, match="invalid date format verb"):
            formatdate(S(spec), S("2020-01-02T03:04:05Z"))

    @pytest.mark.parametrize("spec", ["Q", "b", "xx"])
    def test_a_letter_that_is_not_a_verb(self, spec: str) -> None:
        with pytest.raises(CtyFunctionError, match="invalid date format verb"):
            formatdate(S(spec), S("2020-01-02T03:04:05Z"))


class TestRFC3339Parsing:
    """go-cty keeps its own RFC3339 definition, deliberately stricter than the host language's."""

    @pytest.mark.parametrize(
        "timestamp",
        [
            "2020-01-02T03:04:05Z",
            "2020-01-02T03:04:05.123Z",
            "2020-01-02T03:04:05.123456789Z",
            "2020-01-02T03:04:05+02:00",
            "2020-01-02T03:04:05-08:30",
        ],
    )
    def test_accepted(self, timestamp: str) -> None:
        assert formatdate(S("YYYY"), S(timestamp)).value == "2020"

    @pytest.mark.parametrize(
        "timestamp",
        [
            "2020-01-02",  # date alone
            "2020-01-02 03:04:05Z",  # space for the T
            "2020-01-02t03:04:05Z",  # lowercase introducer
            "2020-01-02T03:04:05z",  # lowercase zone
            "2020-1-02T03:04:05Z",  # month not zero-padded
            "2020-01-02T3:04:05Z",  # hour not zero-padded
            "2020-01-02T03:04:05",  # no zone at all
            "2020-01-02T03:04:05+0000",  # offset without its colon
            "2020-01-02T03:04:05.Z",  # empty fractional part
            "2020-13-02T03:04:05Z",  # month out of range
            "2020-02-30T03:04:05Z",  # day out of range for the month
            "2020-01-02T24:04:05Z",  # hour out of range
            "not a timestamp",
            "",
        ],
    )
    def test_rejected(self, timestamp: str) -> None:
        with pytest.raises(CtyFunctionError):
            formatdate(S("YYYY"), S(timestamp))

    def test_sub_microsecond_precision_is_truncated_not_rounded(self) -> None:
        """datetime resolves to microseconds; the extra digits are dropped.

        Invisible in RFC3339 output, which carries no fractional part at all,
        but it is the one place this implementation cannot follow Go exactly.
        """
        assert timeadd(S("2020-01-02T03:04:05.999999999Z"), S("0")).value == "2020-01-02T03:04:05Z"


class TestTimeAdd:
    @pytest.mark.parametrize(
        ("timestamp", "duration", "expected"),
        [
            ("2020-01-01T00:00:00Z", "1h", "2020-01-01T01:00:00Z"),
            ("2020-01-01T00:00:00Z", "1h30m", "2020-01-01T01:30:00Z"),
            ("2020-01-01T00:00:00Z", "1.5h", "2020-01-01T01:30:00Z"),
            ("2020-01-01T00:00:00Z", "-2h5m", "2019-12-31T21:55:00Z"),
            ("2020-01-01T00:00:00Z", "+1h", "2020-01-01T01:00:00Z"),
            ("2020-01-01T00:00:00Z", "0", "2020-01-01T00:00:00Z"),
            ("2020-01-01T00:00:00Z", "1500ms", "2020-01-01T00:00:01Z"),
            ("2020-01-01T00:00:00Z", "1000000us", "2020-01-01T00:00:01Z"),
            ("2020-01-01T00:00:00Z", "1000000µs", "2020-01-01T00:00:01Z"),
            ("2020-01-01T00:00:00Z", "1000000000ns", "2020-01-01T00:00:01Z"),
            ("2020-12-31T23:00:00Z", "2h", "2021-01-01T01:00:00Z"),
        ],
    )
    def test_go_duration_units(self, timestamp: str, duration: str, expected: str) -> None:
        assert timeadd(S(timestamp), S(duration)).value == expected

    def test_utc_is_rendered_as_z(self) -> None:
        """Go's RFC3339 layout writes Z for a zero offset; isoformat writes +00:00.

        Terraform compares these strings, so the two spellings are a perpetual
        diff rather than a cosmetic difference.
        """
        assert timeadd(S("2020-01-01T00:00:00Z"), S("1h")).value.endswith("Z")

    def test_an_offset_survives_the_addition(self) -> None:
        assert timeadd(S("2020-01-01T00:00:00+02:00"), S("1h")).value == "2020-01-01T01:00:00+02:00"

    def test_the_fractional_part_is_dropped_from_the_result(self) -> None:
        assert timeadd(S("2020-01-01T00:00:00.500Z"), S("1s")).value == "2020-01-01T00:00:01Z"

    @pytest.mark.parametrize("duration", ["not a duration", "h", "", "1d", "1h-30m", "1", "-", "1.h5"])
    def test_a_duration_go_rejects(self, duration: str) -> None:
        with pytest.raises(CtyFunctionError):
            timeadd(S("2020-01-01T00:00:00Z"), S(duration))

    def test_the_int64_ceiling_is_inclusive(self) -> None:
        """Exactly maxint64 nanoseconds is accepted; one more is not.

        Both sides agree on the boundary itself, which is the only place a `>`
        and a `>=` differ -- and a mutation run showed nothing here noticed the
        difference.
        """
        assert timeadd(S("2020-01-01T00:00:00Z"), S("9223372036854775807ns")).value == "2312-04-11T23:47:16Z"

        with pytest.raises(CtyFunctionError):
            timeadd(S("2020-01-01T00:00:00Z"), S("9223372036854775808ns"))

    @pytest.mark.parametrize("duration", ["3000000h", "1000000000000000000000ns"])
    def test_a_duration_too_large_for_an_int64(self, duration: str) -> None:
        """time.Duration counts nanoseconds in an int64, so ~292 years is the ceiling.

        Nothing in Python's arithmetic objects to these, so the limit has to be
        checked rather than inherited. go-cty refuses both.
        """
        with pytest.raises(CtyFunctionError):
            timeadd(S("2020-01-01T00:00:00Z"), S(duration))


class TestTheDeclaredSignatures:
    """What each function accepts and promises, taken from its `function.Spec`."""

    def test_both_return_a_string_before_any_value_is_known(self) -> None:
        assert SIGNATURES["formatdate"].return_type([CtyString(), CtyString()]) == CtyString()
        assert SIGNATURES["timeadd"].return_type([CtyString(), CtyString()]) == CtyString()

    @pytest.mark.parametrize("position", [0, 1])
    @pytest.mark.parametrize("function", [formatdate, timeadd])
    def test_neither_parameter_accepts_a_null(
        self, function: Callable[..., CtyValue[Any]], position: int
    ) -> None:
        """Changed on 2026-08-17: both used to answer *unknown* for a null.

        Neither declaration sets `AllowNull` (`datetime.go:16`,
        `datetime.go:211`), so go-cty refuses the call outright -- and it must,
        because a null is a value that is definitely absent rather than one
        nobody knows yet, and answering unknown for it invites a plan that can
        never apply. The message is now the framework's, matching go-cty's own
        `argument must not be null`.
        """
        arguments = [S("YYYY") if function is formatdate else S(UTC_NOON), S("1h")]
        arguments[position] = CtyValue.null(CtyString())

        with pytest.raises(CtyFunctionError, match="must not be null"):
            function(*arguments)

    def test_formatdate_promises_a_non_null_answer_and_timeadd_does_not(self) -> None:
        """The asymmetry is go-cty's, and it is transcribed rather than tidied.

        `FormatDateFunc` carries `RefineResult: refineNonNull`
        (`datetime.go:27`) and `TimeAddFunc` carries no `RefineResult` at all
        (`datetime.go:209`). Nothing in go-cty explains why -- `timeadd` always
        produces a timestamp -- but the oracle answers exactly this: an
        unknown-and-not-null string from `formatdate`, a bare unknown from
        `timeadd`. A refinement invented here would be a promise Terraform acts
        on with nothing behind it.

        New on 2026-08-17; before it, neither function refined anything.
        """
        deferred_format = formatdate(CtyValue.unknown(CtyString()), S(UTC_NOON))
        deferred_add = timeadd(CtyValue.unknown(CtyString()), S("1h"))

        assert isinstance(deferred_format.value, RefinedUnknownValue)
        assert deferred_format.value.is_known_null is False
        assert not isinstance(deferred_add.value, RefinedUnknownValue)


# 🌊🪢🔚
