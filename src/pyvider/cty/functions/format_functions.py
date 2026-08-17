#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""go-cty's `cty/function/stdlib/format.go`.

A printf dialect, not Python's and not quite Go's. It is close enough to Go's
that go-cty leans on `fmt.Sprintf` for the numeric verbs, and far enough from
Python's that leaning on `%` or `str.format` here would be wrong in several
places at once -- `%v` has no Python equivalent, `%q` produces JSON rather than
a Python repr, the argument index is `%[1]s` rather than `%(1)s`, and width and
precision are counted in characters rather than bytes.
"""

from __future__ import annotations

from collections.abc import Iterable, Sized
from decimal import Decimal
import json
import re
from typing import Any, cast

from pyvider.cty.config.defaults import (
    ERR_FORMAT_INCONSISTENT_LENGTH,
    ERR_FORMAT_INVALID,
    ERR_FORMAT_NO_VERBS,
    ERR_FORMAT_NOT_ENOUGH_ARGUMENTS,
    ERR_FORMAT_NULL_VALUE,
    ERR_FORMAT_REQUIRES_INTEGER,
    ERR_FORMAT_TOO_MANY_ARGUMENTS,
    ERR_FORMAT_UNSUPPORTED_VALUE,
    ERR_FORMAT_UNSUPPORTED_VERB,
)
from pyvider.cty.conversion import convert
from pyvider.cty.exceptions import CtyConversionError, CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.cty.values import CtyValue

# `%` flags width .precision [argument-index] verb.
#
# The argument index sits immediately before the verb, which is go-cty's own
# placement and not Go's -- Go has no such syntax, so go-cty strips the segment
# back out before handing the rest to `fmt.Sprintf`.
_VERB = re.compile(
    r"%"
    r"(?P<flags>[-+ 0#]*)"
    r"(?P<width>\d+)?"
    r"(?:\.(?P<precision>\d+))?"
    r"(?:\[(?P<argnum>\d+)\])?"
    r"(?P<verb>[a-zA-Z%])"
)

_INTEGER_VERBS = frozenset("bdoxX")
_FLOAT_VERBS = frozenset("eEfgG")


class _Verb:
    """One `%` sequence, parsed."""

    __slots__ = ("argnum", "flags", "offset", "precision", "raw", "verb", "width")

    def __init__(self, match: re.Match[str], argnum: int) -> None:
        self.raw = match.group(0)
        self.offset = match.start()
        self.flags = match.group("flags") or ""
        self.width = int(match.group("width")) if match.group("width") else None
        self.precision = int(match.group("precision")) if match.group("precision") else None
        self.argnum = argnum
        self.verb = match.group("verb")

    @property
    def zero(self) -> bool:
        return "0" in self.flags

    @property
    def minus(self) -> bool:
        return "-" in self.flags

    @property
    def sharp(self) -> bool:
        return "#" in self.flags


def _pad(verb: _Verb, text: str) -> str:
    """Pad to the requested width.

    go-cty measures width in *grapheme clusters*; this measures code points,
    which is the same answer for everything outside combining marks and emoji
    sequences. Widening that is the same UAX#29 decision `strlen` waits on, and
    is pinned as a known divergence rather than silently approximated.
    """
    if verb.width is None or len(text) >= verb.width:
        return text
    padding = ("0" if verb.zero else " ") * (verb.width - len(text))
    return text + padding if verb.minus else padding + text


def _json_number(number: Decimal) -> str:
    """A number as go-cty's JSON encoder writes it: plain decimal, no exponent."""
    return format(number.normalize(), "f") if number.is_finite() else str(number)


def _json_of(value: CtyValue[Any]) -> str:
    """The value as go-cty's JSON encoding of it, which is what `%v` falls back to."""
    from pyvider.cty.conversion import cty_to_native

    def encode(item: Any) -> Any:
        return _json_number(item) if isinstance(item, Decimal) else str(item)

    if isinstance(value.type, CtyNumber) and not value.is_null:
        return _json_number(cast(Decimal, value.value))
    return json.dumps(cty_to_native(value), separators=(",", ":"), default=encode)


def _exponent_form(number: Decimal, precision: int, *, upper: bool) -> str:
    """`d.dddde±dd`, with the two-digit exponent Go always writes.

    Python writes `e+1` where Go writes `e+01`, and `Decimal.__format__` reports
    a zero's exponent as whatever scale it happens to carry -- `%e` of zero came
    out `0.000000e+6`.
    """
    sign = "-" if number < 0 else ""
    magnitude = abs(number)
    exponent = magnitude.adjusted() if magnitude else 0
    mantissa = magnitude.scaleb(-exponent) if magnitude else Decimal(0)
    rendered = format(mantissa, f".{precision}f")
    if Decimal(rendered) >= 10:  # rounding carried, as in 9.99 -> 10.0
        exponent += 1
        rendered = format(magnitude.scaleb(-exponent), f".{precision}f")
    marker = "E" if upper else "e"
    return f"{sign}{rendered}{marker}{'+' if exponent >= 0 else '-'}{abs(exponent):02d}"


def _general_form(number: Decimal, precision: int | None, *, upper: bool) -> str:
    """Go's `%g`: exponent form for large and small exponents, plain otherwise.

    Trailing zeros are dropped either way, which is what makes `%g` the shortest
    faithful rendering and so also what `%v` uses for a number.
    """
    if not number.is_finite():
        return str(number)
    magnitude = abs(number)
    exponent = magnitude.adjusted() if magnitude else 0
    significant = precision if precision is not None else max(len(number.normalize().as_tuple()[1]), 1)
    if precision == 0:
        significant = 1

    if exponent < -4 or exponent >= significant:
        rendered = _exponent_form(number, max(significant - 1, 0), upper=upper)
        mantissa, marker, tail = rendered.partition("E" if upper else "e")
        if "." in mantissa:
            mantissa = mantissa.rstrip("0").rstrip(".")
        return mantissa + marker + tail
    rendered = format(number, f".{max(significant - 1 - exponent, 0)}f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def _number_text(number: Decimal) -> str:
    """A number the way Go renders `%v` for one: the shortest `%g` that round-trips."""
    if not number.is_finite():
        return str(number)
    return _general_form(number, None, upper=False)


def _as(value: CtyValue[Any], target: CtyType[Any], verb: _Verb) -> CtyValue[Any]:
    try:
        return convert(value, target)
    except CtyConversionError as exc:
        raise CtyFunctionError(
            ERR_FORMAT_UNSUPPORTED_VALUE.format(verb=verb.raw, offset=verb.offset, error=exc)
        ) from exc


def _format_integer(verb: _Verb, number: Decimal) -> str:
    if number != number.to_integral_value():
        raise CtyFunctionError(ERR_FORMAT_REQUIRES_INTEGER.format(verb=verb.raw, offset=verb.offset))
    whole = int(number)
    rendered = format(abs(whole), {"b": "b", "d": "d", "o": "o", "x": "x", "X": "X"}[verb.verb])
    sign = "-" if whole < 0 else ("+" if "+" in verb.flags else (" " if " " in verb.flags else ""))
    if verb.zero and verb.width is not None and not verb.minus:
        rendered = rendered.rjust(max(0, verb.width - len(sign)), "0")
    return _pad(verb, sign + rendered)


def _format_float(verb: _Verb, number: Decimal) -> str:
    upper = verb.verb in "EG"
    if verb.verb in "gG":
        rendered = _general_form(number, verb.precision, upper=upper)
    elif verb.verb in "eE":
        rendered = _exponent_form(number, 6 if verb.precision is None else verb.precision, upper=upper)
    else:
        rendered = format(number, f".{6 if verb.precision is None else verb.precision}f")

    sign = ""
    if rendered.startswith("-"):
        sign, rendered = "-", rendered[1:]
    elif "+" in verb.flags:
        sign = "+"
    elif " " in verb.flags:
        sign = " "
    # The sign goes outside the zero padding, not inside it: `%08.2f` of -42 is
    # `-0042.00`, and padding the signed text gave `00-42.00`.
    if verb.zero and verb.width is not None and not verb.minus:
        rendered = rendered.rjust(max(0, verb.width - len(sign)), "0")
    return _pad(verb, sign + rendered)


def _format_one(verb: _Verb, value: CtyValue[Any]) -> str:  # noqa: C901
    if verb.verb != "v" and value.is_null:
        raise CtyFunctionError(ERR_FORMAT_NULL_VALUE.format(verb=verb.raw, offset=verb.offset))

    if verb.verb == "v":
        if not verb.sharp and not value.is_null:
            if isinstance(value.type, CtyString):
                return _pad(verb, str(value.value))
            if isinstance(value.type, CtyNumber):
                return _pad(verb, _number_text(cast(Decimal, value.value)))
        return _pad(verb, _json_of(value))

    if verb.verb == "t":
        return _pad(verb, "true" if _as(value, CtyBool(), verb).value else "false")

    if verb.verb in _INTEGER_VERBS:
        return _format_integer(verb, cast(Decimal, _as(value, CtyNumber(), verb).value))

    if verb.verb in _FLOAT_VERBS:
        return _format_float(verb, cast(Decimal, _as(value, CtyNumber(), verb).value))

    if verb.verb in ("s", "q"):
        text = str(_as(value, CtyString(), verb).value)
        if verb.precision is not None and verb.precision > 0:
            text = text[: verb.precision]
        if verb.verb == "q":
            text = json.dumps(text)
        return _pad(verb, text)

    raise CtyFunctionError(ERR_FORMAT_UNSUPPORTED_VERB.format(verb=verb.verb, offset=verb.offset))


def _render(template: str, arguments: list[CtyValue[Any]]) -> str:
    """go-cty's `formatFSM`, as a scan rather than a state machine."""
    out: list[str] = []
    position = 0
    next_argument = 1
    highest_used = 0
    while position < len(template):
        percent = template.find("%", position)
        if percent == -1:
            out.append(template[position:])
            break
        out.append(template[position:percent])

        match = _VERB.match(template, percent)
        if match is None:
            raise CtyFunctionError(ERR_FORMAT_INVALID.format(offset=percent))
        if match.group("verb") == "%":
            out.append("%")
            position = match.end()
            continue

        explicit = match.group("argnum")
        argnum = int(explicit) if explicit else next_argument
        next_argument = argnum + 1
        verb = _Verb(match, argnum)

        if argnum > len(arguments):
            raise CtyFunctionError(
                ERR_FORMAT_NOT_ENOUGH_ARGUMENTS.format(
                    verb=verb.raw, offset=verb.offset, want=argnum, have=len(arguments)
                )
            )
        highest_used = max(highest_used, argnum)
        out.append(_format_one(verb, arguments[argnum - 1]))
        position = match.end()

    # An argument the format string never reaches is a mistake worth reporting:
    # the caller believes it is being printed. go-cty says so in two different
    # ways depending on whether there were any verbs at all.
    if highest_used < len(arguments):
        raise CtyFunctionError(
            ERR_FORMAT_NO_VERBS
            if highest_used == 0
            else ERR_FORMAT_TOO_MANY_ARGUMENTS.format(used=highest_used)
        )
    return "".join(out)


@stdlib_function("format", allow_null=True)
def format_fn(template: CtyValue[Any], *arguments: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `FormatFunc`.

    `allow_null` because `%v` renders a null as the literal `null`; every other
    verb refuses one, which `_format_one` enforces per verb rather than the
    framework enforcing it per argument. The format string itself must not be
    null, which is checked here for the same reason.
    """
    if template.is_null:
        raise CtyFunctionError(ERR_FORMAT_NULL_VALUE.format(verb="the format string", offset=0))
    if template.is_unknown or not all(argument.is_wholly_known() for argument in arguments):
        return CtyValue.unknown(CtyString())
    return CtyString().validate(_render(str(template.value), list(arguments)))


_UNKNOWN_LENGTH = object()


def _iteration_count(arguments: tuple[CtyValue[Any], ...]) -> Any:
    """How many rows the sequence arguments dictate, and whether they agree.

    `None` means every argument was scalar, so there is exactly one row.
    """
    iterations: int | None = None
    chooser = 0
    for position, argument in enumerate(arguments):
        if argument.is_unknown or isinstance(argument.type, CtyDynamic):
            return _UNKNOWN_LENGTH
        length = _sequence_length(argument)
        if length is None:
            continue
        if iterations is None:
            iterations, chooser = length, position
        elif length != iterations:
            raise CtyFunctionError(
                ERR_FORMAT_INCONSISTENT_LENGTH.format(
                    position=position + 1, length=length, other=chooser + 1, other_length=iterations
                )
            )
    return iterations


def _sequence_length(argument: CtyValue[Any]) -> int | None:
    """The number of iterations this argument dictates, or None if it is scalar."""
    if argument.is_null or not isinstance(argument.type, CtyList | CtySet | CtyTuple):
        return None
    return len(cast(Sized, argument.value))


def _elements_of(argument: CtyValue[Any]) -> list[CtyValue[Any]]:
    """A sequence argument's elements, in the order go-cty iterates them.

    A set has no order of its own, so `list(frozenset)` gives whatever the hash
    table yields -- `formatlist("%s", toset(["a", "b"]))` came back `["b", "a"]`.
    Sets are given the same canonical order used to de-duplicate them, which is
    the one go-cty's own set iteration follows.
    """
    if isinstance(argument.value, frozenset):
        return sorted(argument.value, key=lambda element: element._canonical_sort_key())
    return list(cast(Iterable[CtyValue[Any]], argument.value))


@stdlib_function("formatlist", allow_null=True)
def formatlist(template: CtyValue[Any], *arguments: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `FormatListFunc`: `format` once per element, in lockstep.

    Sequence arguments are iterated together and must agree on length; anything
    else is reused unchanged on every iteration.
    """
    result_type = CtyList(element_type=CtyString())
    if template.is_null:
        raise CtyFunctionError(ERR_FORMAT_NULL_VALUE.format(verb="the format string", offset=0))
    if template.is_unknown:
        return CtyValue.unknown(result_type)

    iterations = _iteration_count(arguments)
    if iterations is _UNKNOWN_LENGTH:
        return CtyValue.unknown(result_type)

    if iterations == 0:
        return cast(CtyValue[Any], result_type.validate([]))

    rows: list[CtyValue[Any]] = []
    for index in range(1 if iterations is None else iterations):
        row: list[CtyValue[Any]] = []
        for argument in arguments:
            if _sequence_length(argument) is None:
                row.append(argument)
            else:
                row.append(_elements_of(argument)[index])
        if not all(element.is_wholly_known() for element in row):
            # One unresolved row does not make the others unresolvable.
            rows.append(CtyValue.unknown(CtyString()))
            continue
        rows.append(CtyString().validate(_render(str(template.value), row)))
    return cast(CtyValue[Any], result_type.validate(rows))


# 🌊🪢🔚
