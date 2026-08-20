#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
import re
from typing import Any, cast

from pyvider.cty import CtyString, CtyValue
from pyvider.cty.config.defaults import (
    ERR_FORMATDATE_GO_LAYOUT,
    ERR_FORMATDATE_INVALID_TIMESTAMP,
    ERR_FORMATDATE_INVALID_VERB,
    ERR_FORMATDATE_INVALID_VERB_LENGTH,
    ERR_FORMATDATE_UNTERMINATED_LITERAL,
    ERR_INVALID_DURATION_FORMAT,
    ERR_INVALID_RFC3339_TIMESTAMP,
    ERR_TIMEADD_INVALID_FORMAT,
    ERR_TIMEADD_OUT_OF_RANGE,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null

# go-cty deliberately keeps its own definition of RFC3339 rather than deferring
# to whatever the host language accepts, so that these functions do not shift
# behaviour underneath callers (cty/function/stdlib/datetime_rfc3339.go says so
# in as many words). Python's own datetime.fromisoformat is far more permissive
# -- it takes a bare date, a space in place of the T, an offset without its
# colon -- so matching go-cty means parsing the grammar here rather than
# delegating.
_RFC3339 = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"(?:\.(?P<fraction>\d+))?"
    r"(?:Z|(?P<sign>[+-])(?P<offhour>\d{2}):(?P<offminute>\d{2}))\Z"
)

_NANOSECONDS_PER_MICROSECOND = 1000
_NANOSECONDS_PER_SECOND = 10**9
_INT64_MAX = 2**63 - 1

# The units time.ParseDuration accepts, in nanoseconds. Both spellings of "micro"
# are here because Go accepts the micro sign and the Greek mu alike.
_DURATION_UNITS: dict[str, int] = {
    "ns": 1,
    "us": 1000,
    "µs": 1000,
    "μs": 1000,
    "ms": 10**6,
    "s": _NANOSECONDS_PER_SECOND,
    "m": 60 * _NANOSECONDS_PER_SECOND,
    "h": 3600 * _NANOSECONDS_PER_SECOND,
}

# [-+]?([0-9]*(\.[0-9]*)?[a-z]+)+ , tightened so that a magnitude must carry at
# least one digit on one side of the point, which is what Go's "pre or post"
# check amounts to.
_DURATION_MAGNITUDE = r"(?:\d+(?:\.\d*)?|\.\d+)"
_DURATION_UNIT = r"[^0-9.]+"
_DURATION = re.compile(rf"(?P<sign>[-+])?(?:{_DURATION_MAGNITUDE}{_DURATION_UNIT})+\Z")
_DURATION_PART = re.compile(rf"({_DURATION_MAGNITUDE})({_DURATION_UNIT})")

_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

# Indexed by datetime.weekday(), which counts from Monday.
_WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def _parse_rfc3339_parts(timestamp: str) -> tuple[datetime, int]:
    """An RFC3339 timestamp as a whole-second instant and its nanoseconds.

    Split rather than folded into one `datetime` because a `datetime` resolves
    to microseconds and Go's `time.Time` to nanoseconds, so the last three
    digits of a nine-digit fraction have nowhere to go. Keeping them separate
    lets `timeadd` do its arithmetic at Go's resolution and only then come back
    to the calendar, which is the whole of what the sub-microsecond divergence
    was.

    Go truncates anything finer than a nanosecond, so the fraction is read to
    nine digits and no further.
    """
    matched = _RFC3339.fullmatch(timestamp)
    if matched is None:
        raise ValueError(ERR_INVALID_RFC3339_TIMESTAMP.format(timestamp=timestamp))

    parts = matched.groupdict()
    if parts["sign"] is None:
        tzinfo = UTC
    else:
        offset = timedelta(hours=int(parts["offhour"]), minutes=int(parts["offminute"]))
        tzinfo = timezone(-offset if parts["sign"] == "-" else offset)

    fraction = parts["fraction"] or ""
    nanoseconds = int(fraction[:9].ljust(9, "0")) if fraction else 0

    # datetime does the remaining range checking -- month 13, day 32, hour 24 and
    # the like all raise ValueError from here, which is where they should raise.
    moment = datetime(
        year=int(parts["year"]),
        month=int(parts["month"]),
        day=int(parts["day"]),
        hour=int(parts["hour"]),
        minute=int(parts["minute"]),
        second=int(parts["second"]),
        tzinfo=tzinfo,
    )
    return moment, nanoseconds


def _parse_rfc3339(timestamp: str) -> datetime:
    """The same instant as a plain `datetime`, for the callers that render it.

    `formatdate` has no verb finer than a second, so the microsecond truncation
    here reaches nothing it can print.
    """
    moment, nanoseconds = _parse_rfc3339_parts(timestamp)
    return moment.replace(microsecond=nanoseconds // _NANOSECONDS_PER_MICROSECOND)


def _utc_offset_parts(moment: datetime) -> tuple[str, int, int]:
    """The sign, hours and minutes of a moment's UTC offset."""
    offset = moment.utcoffset() or timedelta(0)
    total_seconds = int(offset.total_seconds())
    sign = "-" if total_seconds < 0 else "+"
    total_seconds = abs(total_seconds)
    return sign, total_seconds // 3600, (total_seconds % 3600) // 60


def _format_rfc3339(moment: datetime) -> str:
    """Render as Go's time.RFC3339 layout does: no fractional part, Z for UTC."""
    sign, hours, minutes = _utc_offset_parts(moment)
    zone = "Z" if hours == 0 and minutes == 0 else f"{sign}{hours:02d}:{minutes:02d}"
    return (
        f"{moment.year:04d}-{moment.month:02d}-{moment.day:02d}"
        f"T{moment.hour:02d}:{moment.minute:02d}:{moment.second:02d}{zone}"
    )


def _parse_duration_nanoseconds(duration_str: str) -> int:
    """A duration by the rules of Go's `time.ParseDuration`, in nanoseconds.

    A `time.Duration` *is* an int64 count of nanoseconds, so this is the shape
    Go holds it in, and returning it unrounded is what lets `timeadd` be exact.
    An earlier version came back as a `timedelta`, which resolves to
    microseconds, and the rounding it had to do was the whole of a divergence:
    truncating the magnitude rather than flooring the signed count put every
    negative sub-microsecond shift on the far side of the second boundary --
    `timeadd("0002-01-01T00:00:00Z", "-1ns")` came back unchanged where go-cty
    answers `0001-12-31T23:59:59Z`, a different second, day and year.
    """
    # ParseDuration's one special case: a bare zero needs no unit.
    if duration_str in {"0", "+0", "-0"}:
        return 0

    matched = _DURATION.fullmatch(duration_str)
    if matched is None:
        raise ValueError(ERR_INVALID_DURATION_FORMAT.format(duration_str=duration_str))

    total_nanoseconds = 0
    for magnitude, unit in _DURATION_PART.findall(duration_str):
        scale = _DURATION_UNITS.get(unit)
        if scale is None:
            raise ValueError(ERR_INVALID_DURATION_FORMAT.format(duration_str=duration_str))
        # Exact rather than float: Go computes the fractional part in float64,
        # so this is the more accurate of the two, and the difference is far
        # below the resolution either of them can carry.
        total_nanoseconds += int(Decimal(magnitude) * scale)

    if abs(total_nanoseconds) > _INT64_MAX:
        # time.Duration is an int64 count of nanoseconds, and ParseDuration
        # refuses anything that will not fit in one.
        raise ValueError(ERR_INVALID_DURATION_FORMAT.format(duration_str=duration_str))

    if matched.group("sign") == "-":
        total_nanoseconds = -total_nanoseconds

    return total_nanoseconds


def _split_date_format(spec: str) -> list[str]:
    """Tokenize a format string into literals, quoted literals and verb runs.

    A port of go-cty's splitDateFormat. A run of one repeated letter is a verb
    whose length selects the variant; everything else is literal text, except
    that a single quote opens a literal sequence in which '' means a quote.
    """
    tokens: list[str] = []
    index = 0
    length = len(spec)
    while index < length:
        char = spec[index]
        if char == "'":
            tokens.append(_scan_quoted(spec, index))
        elif _starts_verb(char):
            run = index
            while run < length and spec[run] == char:
                run += 1
            tokens.append(spec[index:run])
        else:
            run = index + 1
            while run < length and spec[run] != "'" and not _starts_verb(spec[run]):
                run += 1
            tokens.append(spec[index:run])
        index += len(tokens[-1])
    return tokens


def _scan_quoted(spec: str, start: int) -> str:
    """The quoted token beginning at `start`, closing quote included."""
    if spec[start + 1 : start + 2] == "'":
        return "''"
    index = start + 1
    while index < len(spec):
        if spec[index] == "'":
            if spec[index + 1 : index + 2] == "'":
                index += 2
                continue
            return spec[start : index + 1]
        index += 1
    # Unterminated. Returned as it stands so the renderer can report it; the
    # tokenizer's job is only to say where the token ends.
    return spec[start:]


def _starts_verb(char: str) -> bool:
    return char.isascii() and char.isalpha()


def _render_quoted(token: str) -> str:
    if token[-1] != "'" or len(token) == 1:
        raise CtyFunctionError(ERR_FORMATDATE_UNTERMINATED_LITERAL)
    if len(token) == 2:
        return "'"
    raw = token[1:-1]
    rendered: list[str] = []
    index = 0
    while index < len(raw):
        rendered.append(raw[index])
        # A doubled quote inside the sequence stands for one quote.
        index += 2 if raw[index] == "'" else 1
    return "".join(rendered)


def _render_timezone(moment: datetime, length: int) -> str | None:
    sign, hours, minutes = _utc_offset_parts(moment)
    is_utc = hours == 0 and minutes == 0
    match length:
        case 1:
            return "Z" if is_utc else f"{sign}{hours:02d}:{minutes:02d}"
        case 3:
            return "UTC" if is_utc else f"{sign}{hours:02d}{minutes:02d}"
        case 4:
            return f"{sign}{hours:02d}{minutes:02d}"
        case 5:
            return f"{sign}{hours:02d}:{minutes:02d}"
        case _:
            return None


# Each verb maps its run length to a renderer, alongside the message go-cty
# gives when the run is some other length.
_Renderers = dict[int, Callable[[datetime], str]]
_DATE_VERBS: dict[str, tuple[_Renderers, str]] = {
    "Y": (
        {2: lambda t: f"{t.year % 100:02d}", 4: lambda t: f"{t.year:04d}"},
        'year must either be "YY" or "YYYY"',
    ),
    "M": (
        {
            1: lambda t: f"{t.month:d}",
            2: lambda t: f"{t.month:02d}",
            3: lambda t: _MONTH_NAMES[t.month - 1][:3],
            4: lambda t: _MONTH_NAMES[t.month - 1],
        },
        'month must be "M", "MM", "MMM", or "MMMM"',
    ),
    "D": (
        {1: lambda t: f"{t.day:d}", 2: lambda t: f"{t.day:02d}"},
        'day of month must either be "D" or "DD"',
    ),
    "E": (
        {
            3: lambda t: _WEEKDAY_NAMES[t.weekday()][:3],
            4: lambda t: _WEEKDAY_NAMES[t.weekday()],
        },
        'day of week must either be "EEE" or "EEEE"',
    ),
    "h": (
        {1: lambda t: f"{t.hour:d}", 2: lambda t: f"{t.hour:02d}"},
        '24-hour must either be "h" or "hh"',
    ),
    "H": (
        {1: lambda t: f"{t.hour % 12 or 12:d}", 2: lambda t: f"{t.hour % 12 or 12:02d}"},
        '12-hour must either be "H" or "HH"',
    ),
    "A": ({2: lambda t: "AM" if t.hour < 12 else "PM"}, 'must be "AA"'),
    "a": ({2: lambda t: "am" if t.hour < 12 else "pm"}, 'must be "aa"'),
    "m": (
        {1: lambda t: f"{t.minute:d}", 2: lambda t: f"{t.minute:02d}"},
        'minute must either be "m" or "mm"',
    ),
    "s": (
        {1: lambda t: f"{t.second:d}", 2: lambda t: f"{t.second:02d}"},
        'second must either be "s" or "ss"',
    ),
}


def _render_verb(token: str, moment: datetime) -> str:
    verb = token[0]
    if verb == "Z":
        rendered = _render_timezone(moment, len(token))
        if rendered is None:
            raise CtyFunctionError(
                ERR_FORMATDATE_INVALID_VERB_LENGTH.format(
                    verb=token, expected="timezone must be Z, ZZZZ, or ZZZZZ"
                )
            )
        return rendered

    entry = _DATE_VERBS.get(verb)
    if entry is None:
        raise CtyFunctionError(ERR_FORMATDATE_INVALID_VERB.format(verb=token))

    renderers, expected = entry
    renderer = renderers.get(len(token))
    if renderer is None:
        raise CtyFunctionError(ERR_FORMATDATE_INVALID_VERB_LENGTH.format(verb=token, expected=expected))
    return renderer(moment)


# Go's reference layout, which go-cty's dialect deliberately does not use: it
# defines YYYY/MM/DD/hh/mm/ss and reads digits as literal text. `2006` is the
# unmistakable token -- a format carrying it *alongside* another of these is a
# call written against the pre-0.5.0 implementation, which translated Go layouts
# into strftime.
_GO_LAYOUT_YEAR = "2006"
# Split by how they have to be matched. A numeric token is only a Go token when
# it is a *whole* run of digits, or part of one long enough to be the packed
# `20060102150405` layout: `"2006-2015"` is a year range, and reading the `15`
# out of `2015` refused a format go-cty returns as the literal text it is. The
# textual ones carry their own punctuation and cannot collide that way.
_GO_LAYOUT_NUMERIC_TOKENS = ("01", "02", "03", "04", "05", "15")
_GO_LAYOUT_TEXT_TOKENS = ("Jan", "Mon", "MST", "PM", "-0700", "Z07:00")
# Above this length a digit run is not a number anyone writes literally; it is
# Go reference fields concatenated. `2006` plus `01` is the shortest of those.
_GO_LAYOUT_PACKED_RUN = 4
_DIGIT_RUN = re.compile(r"\d+")


def _go_layout_numeric_token(runs: list[str], token: str) -> bool:
    """Whether `token` appears in `runs` as a Go layout field rather than a digit."""
    return any(run == token or (len(run) > _GO_LAYOUT_PACKED_RUN and token in run) for run in runs)


def _is_go_reference_layout(spec: str) -> bool:
    """Whether `spec` is a Go layout rather than a go-cty format.

    This package refuses those, where go-cty returns them as literal text. The
    only place it declines something go-cty answers, and the reasoning is about
    which failure a caller can act on.

    `formatdate("2006-01-02", ts)` returns the string `"2006-01-02"` in go-cty:
    not an error, not a date, and shaped exactly like the answer the caller
    wanted. It is the worst of the forty-three breaking changes in 0.5.0 -- a
    test asserting "the output looks like a date" passes, and the wrong value
    reaches Terraform state. Every other silent break in that list either raises
    or produces visibly wrong output.

    The trigger is narrow on purpose. `2006` alone still formats as the literal
    it is, since a year is a plausible thing to write; it takes a *second*
    reference token to make the intent unmistakable. go-cty already refuses any
    letter it does not know as a verb -- `"Version 2006.01"` is
    `invalid date format verb "V"` there -- so the false-positive surface is a
    format of digits and punctuation only, carrying both tokens, meant
    literally. The one such format a human plausibly writes is a *year range*,
    and `"2006-2015"` used to be refused because `2015` contains `15`; a numeric
    token now has to be a whole digit run, or sit inside one long enough to be
    the packed layout. Those keep working through the quoting the message names:
    `'2006-01-02'` renders as `2006-01-02` on both sides, checked against
    v1.19.0 -- which is why only the unquoted text is examined.
    """
    if _GO_LAYOUT_YEAR not in spec:
        return False

    # Only the *unquoted* text counts. Quoting is what the refusal tells the
    # caller to reach for, so a check that fires on `'2006-01-02'` makes the
    # message a lie -- which is what the first version of this did.
    try:
        unquoted = "".join(token for token in _split_date_format(spec) if token[0] != "'")
    except CtyFunctionError:
        # A malformed format is not this function's problem; the ordinary path
        # is about to report it properly.
        return False

    runs = _DIGIT_RUN.findall(unquoted)
    if not _go_layout_numeric_token(runs, _GO_LAYOUT_YEAR):
        return False
    if any(token in unquoted for token in _GO_LAYOUT_TEXT_TOKENS):
        return True
    return any(_go_layout_numeric_token(runs, token) for token in _GO_LAYOUT_NUMERIC_TOKENS)


@stdlib_function(
    "formatdate",
    params=[CtyParameter("format", CtyString()), CtyParameter("time", CtyString())],
    returns=CtyString(),
    refine_result=refine_not_null,
    description=(
        "Formats a timestamp given in RFC 3339 syntax into another timestamp in some other "
        "machine-oriented time syntax, as described in the format string."
    ),
)
def formatdate(spec: CtyValue[Any], timestamp: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `FormatDateFunc` (`stdlib/datetime.go:14`).

    **A deliberate divergence, and the only one in this package that refuses
    something go-cty answers.** See `_is_go_reference_layout` for why.
    """
    spec_text = cast(str, spec.value)
    if _is_go_reference_layout(spec_text):
        raise CtyFunctionError(ERR_FORMATDATE_GO_LAYOUT.format(spec=spec_text))

    try:
        moment = _parse_rfc3339(cast(str, timestamp.value))
    except ValueError as e:
        raise CtyFunctionError(ERR_FORMATDATE_INVALID_TIMESTAMP.format(error=e)) from e

    rendered: list[str] = []
    for token in _split_date_format(spec_text):
        if token[0] == "'":
            rendered.append(_render_quoted(token))
        elif _starts_verb(token[0]):
            rendered.append(_render_verb(token, moment))
        else:
            rendered.append(token)
    return CtyString().validate("".join(rendered))


@stdlib_function(
    "timeadd",
    params=[CtyParameter("timestamp", CtyString()), CtyParameter("duration", CtyString())],
    returns=CtyString(),
    description=(
        "Adds the duration represented by the given duration string to the given RFC 3339 "
        "timestamp string, returning another RFC 3339 timestamp."
    ),
)
def timeadd(timestamp: CtyValue[Any], duration: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `TimeAddFunc` (`stdlib/datetime.go:209`).

    No `refine_result`, and the asymmetry with `formatdate` is deliberate:
    `FormatDateFunc` carries `refineNonNull` and this does not. Nothing in go-cty
    explains the asymmetry and it looks like an oversight -- `timeadd` always
    produces a timestamp string -- but a refinement this package makes and
    go-cty does not is a promise Terraform would act on with no authority
    behind it, so the declaration follows the source rather than the reasoning.

    **A recorded divergence at the ends of the range.** Go's `time.Time` spans
    to year 292277026596; Python's `datetime` stops at 9999, so
    `timeadd("9999-12-31T23:59:59Z", "1h")` is `10000-01-01T00:59:59Z` in go-cty
    and a refusal here. Matching it means not using `datetime` -- an integer
    nanosecond count plus civil-calendar conversion, which is what Go holds --
    and the case is unreachable from Terraform, whose `timestamp()` cannot
    produce a year near the boundary. Held as strict xfails in the sweep so it
    stays visible rather than becoming folklore.

    What is *not* acceptable is the shape of the refusal. `datetime` signals the
    boundary with `OverflowError`, which is not a `CtyError`, so it escaped the
    taxonomy as a `CtyFunctionPanicError` -- an unhandled Python exception
    reaching a provider from a function whose contract is to answer or refuse.
    """
    try:
        moment, nanoseconds = _parse_rfc3339_parts(cast(str, timestamp.value))
        shift = _parse_duration_nanoseconds(cast(str, duration.value))
    except ValueError as e:
        raise CtyFunctionError(ERR_TIMEADD_INVALID_FORMAT.format(error=e)) from e
    # Nanoseconds first, then the calendar. `divmod` floors, so a shift that
    # crosses a second boundary downwards borrows from the second rather than
    # rounding towards zero -- the remainder is always in [0, 1e9), whichever
    # sign the shift had.
    seconds, _remaining_nanoseconds = divmod(nanoseconds + shift, _NANOSECONDS_PER_SECOND)
    try:
        shifted = moment + timedelta(seconds=seconds)
    except OverflowError as e:
        raise CtyFunctionError(ERR_TIMEADD_OUT_OF_RANGE) from e
    return CtyString().validate(_format_rfc3339(shifted))


# 🌊🪢🔚
