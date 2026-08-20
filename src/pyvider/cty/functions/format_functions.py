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
from decimal import Decimal, localcontext
from itertools import islice
import json
import re
from typing import Any, cast

from pyvider.cty._unicode import cluster_count, iter_clusters
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
from pyvider.cty.conversion._utils import exact_normalize, non_finite_text
from pyvider.cty.exceptions import CtyConversionError, CtyFunctionError
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyParameter, refine_not_null
from pyvider.cty.functions._unknowns import unknown_not_null
from pyvider.cty.json_codec import _marshal_string
from pyvider.cty.refinement import refine
from pyvider.cty.types import (
    CtyBool,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.cty.values import CtyValue
from pyvider.cty.values.set_order import order_key as set_order_key

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


# Integer verbs, where a precision means "at least this many digits" and so
# supersedes zero-padding entirely.
_PRECISION_CANCELS_ZERO = frozenset("bdoxX")


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
        # Go ignores the zero flag outright when a precision is given: the
        # precision has already fixed the digit count, so the remaining width is
        # filled with spaces. `%05.2d` of 42 is "   42", not "00042".
        if self.precision is not None and self.verb in _PRECISION_CANCELS_ZERO:
            return False
        return "0" in self.flags

    @property
    def minus(self) -> bool:
        return "-" in self.flags

    @property
    def sharp(self) -> bool:
        return "#" in self.flags


# The base prefix each verb gets under the alternate (`#`) form.
_ALTERNATE_PREFIX = {"x": "0x", "X": "0X", "o": "0", "b": "0b"}


def _pad(verb: _Verb, text: str, *, allow_zero: bool = True) -> str:
    """Pad to the requested width, measured in grapheme clusters.

    Width is a display concern, so go-cty counts what a reader sees rather than
    how it is encoded (`format.go:500`). Padding a four-code-point emoji to
    width 5 adds one space there and four here if width is measured in code
    points -- the column that padding exists to line up would not line up.

    `allow_zero=False` is for text that is not a number and so cannot be
    zero-padded, which in practice means an infinity or a NaN under a float
    verb. That is Go's rule and not go-cty's own, which is why it is a caller's
    decision here: `%08.2f` of an infinity is "    +Inf" because the float verbs
    delegate to Go's `fmt`, while `%08v` of the same value is "0000+Inf" because
    `%v` pads through go-cty's `formatPadWidth`, which honours the flag.
    """
    if verb.width is None:
        return text
    measured = cluster_count(text)
    if measured >= verb.width:
        return text
    # Go drops the zero flag when minus is present ("if both are set, 0 is
    # ignored"), and it matters far more than a spacing nit: padding 42 on the
    # right with zeros produced "42000", which does not read as a padded 42 at
    # all but as a different number.
    zero = allow_zero and verb.zero and not verb.minus
    padding = ("0" if zero else " ") * (verb.width - measured)
    return text + padding if verb.minus else padding + text


def _json_number(number: Decimal, verb: _Verb) -> str:
    """A number as go-cty's JSON encoder writes it: plain decimal, no exponent.

    An infinity has no JSON form and go-cty says so rather than inventing one
    (`cty/json/marshal.go:45`). This wrote the bare token `Infinity`, which is a
    Python spelling that no JSON parser accepts -- so `%#v` of an infinity
    produced a document that could not be read back.
    """
    if not number.is_finite():
        raise CtyFunctionError(
            ERR_FORMAT_UNSUPPORTED_VALUE.format(
                verb=verb.raw, offset=verb.offset, error="cannot serialize infinity as JSON"
            )
        )
    return format(exact_normalize(number), "f")


def _json_of(value: CtyValue[Any], verb: _Verb) -> str:
    """The value as go-cty's JSON encoding of it, which is what `%v` falls back to.

    Assembled here rather than handed to `json.dumps`, because numbers have to
    be written as go-cty writes them -- plain decimal, never exponent notation.
    Routing through native Python turned a number into a float and `json.dumps`
    then wrote Python's repr of it, so `%v` of a `list(number)` holding 0.00001
    came out `[1e-05]` against go-cty's `[0.00001]`. Only visible one level
    down: a bare number was already special-cased. Subclassing `float` to
    override its repr does not work either -- `json.dumps` calls the C
    `float.__repr__` regardless.

    Keys are sorted, which is what go-cty's encoder does for both objects and
    maps, and set elements take the canonical order used to de-duplicate them.
    """
    if value.is_null:
        return "null"
    if isinstance(value.type, CtyNumber):
        return _json_number(cast(Decimal, value.value), verb)
    if isinstance(value.type, CtyString):
        # The codec's encoder, not `json.dumps`: Go's `encoding/json` escapes
        # `<`, `>` and `&` by default and Python's does not, so `%#v` of
        # `a<b>&c` differed from go-cty in three characters -- the same gap
        # `%q` had.
        return _marshal_string(str(value.value))
    if isinstance(value.type, CtyBool):
        return "true" if value.value else "false"
    if isinstance(value.type, CtyMap | CtyObject):
        items = cast(dict[str, CtyValue[Any]], value.value)
        rendered = ",".join(
            f"{json.dumps(name)}:{_json_of(item, verb)}" for name, item in sorted(items.items())
        )
        return "{" + rendered + "}"
    if isinstance(value.type, CtyList | CtySet | CtyTuple):
        return "[" + ",".join(_json_of(element, verb) for element in _elements_of(value)) + "]"
    if isinstance(value.type, CtyDynamic) and isinstance(value.value, CtyValue):
        return _json_of(value.value, verb)
    return json.dumps(str(value.value))


def _exponent_form(number: Decimal, precision: int, *, upper: bool) -> str:
    """`d.dddde±dd`, with the two-digit exponent Go always writes.

    Python writes `e+1` where Go writes `e+01`, and `Decimal.__format__` reports
    a zero's exponent as whatever scale it happens to carry -- `%e` of zero came
    out `0.000000e+6`.
    """
    sign = "-" if number < 0 else ""
    # `copy_abs`, not `abs`: taking a magnitude is a context operation too, so
    # `abs` rounded the value to 28 significant digits before anything below
    # could widen the context, and the widening then had nothing left to keep.
    magnitude = number.copy_abs()
    exponent = magnitude.adjusted() if magnitude else 0
    # `scaleb` is a context operation, so it rounded the mantissa to the default
    # 28 significant digits: `%v` of 10**28 + 1 came out `1e+28` where go-cty
    # writes `1.0000000000000000000000000001e+28`. Widened to whatever the value
    # and the requested precision need. Found 2026-08-19 by the stdlib fuzz.
    with localcontext() as ctx:
        ctx.prec = max(len(magnitude.as_tuple().digits), precision + 1, 1)
        mantissa = magnitude.scaleb(-exponent) if magnitude else Decimal(0)
        rendered = format(mantissa, f".{precision}f")
        if Decimal(rendered) >= 10:  # rounding carried, as in 9.99 -> 10.0
            exponent += 1
            rendered = format(magnitude.scaleb(-exponent), f".{precision}f")
    marker = "E" if upper else "e"
    return f"{sign}{rendered}{marker}{'+' if exponent >= 0 else '-'}{abs(exponent):02d}"


# Go's strconv uses eprec = 6 for the shortest-form %e/%f decision.
_SHORTEST_EXPONENT_THRESHOLD = 6


def _general_form(number: Decimal, precision: int | None, *, upper: bool) -> str:
    """Go's `%g`: exponent form for large and small exponents, plain otherwise.

    Trailing zeros are dropped either way, which is what makes `%g` the shortest
    faithful rendering and so also what `%v` uses for a number.
    """
    if not number.is_finite():
        return str(number)
    magnitude = number.copy_abs()
    exponent = magnitude.adjusted() if magnitude else 0
    shortest = precision is None
    significant = precision if precision is not None else max(len(exact_normalize(number).as_tuple()[1]), 1)
    if precision == 0:
        significant = 1

    # Go decides between %e and %f on the exponent alone, and in shortest mode it
    # compares against a FIXED 6 rather than against the digit count it is about
    # to print (`strconv/ftoa.go`: "if precision was the shortest possible, use
    # precision 6 for this decision"). Comparing against the value's own
    # significant digits instead made every round number exponential -- 10 came
    # out as "1e+01" and 250000 as "2.5e+05" -- and 1234567 came out fixed where
    # Go gives "1.234567e+06". %v is the default verb, so this reached every
    # format() of a number and every collection containing one.
    threshold = _SHORTEST_EXPONENT_THRESHOLD if shortest else significant

    if exponent < -4 or exponent >= threshold:
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
    """A number the way Go renders `%v` for one: the shortest `%g` that round-trips.

    go-cty spells this with `bf.Text('g', -1)` (`format.go:377`), and `Text` has
    its own answer for a non-finite value -- `+Inf`, not `str(Decimal)`'s
    `Infinity`.
    """
    return non_finite_text(number) or _general_form(number, None, upper=False)


def _as(value: CtyValue[Any], target: CtyType[Any], verb: _Verb) -> CtyValue[Any]:
    try:
        return convert(value, target)
    except CtyConversionError as exc:
        raise CtyFunctionError(
            ERR_FORMAT_UNSUPPORTED_VALUE.format(verb=verb.raw, offset=verb.offset, error=exc)
        ) from exc


def _format_integer(verb: _Verb, number: Decimal) -> str:
    # `bf.Int(nil)` reports an inexact conversion for an infinity as well as for
    # a fraction, so go-cty answers "an integer is required" for both
    # (`format.go:434`). Checked before the equality test, which an infinity
    # passes -- `Decimal("Infinity").to_integral_value()` is itself -- leaving
    # `int()` to raise `OverflowError` out of the function's own body.
    if not number.is_finite() or number != number.to_integral_value():
        raise CtyFunctionError(ERR_FORMAT_REQUIRES_INTEGER.format(verb=verb.raw, offset=verb.offset))
    whole = int(number)
    rendered = format(abs(whole), {"b": "b", "d": "d", "o": "o", "x": "x", "X": "X"}[verb.verb])
    sign = "-" if whole < 0 else ("+" if "+" in verb.flags else (" " if " " in verb.flags else ""))

    # Precision on an integer verb is a MINIMUM DIGIT COUNT, zero-filled
    # (`%.5d` of 42 is "00042"). It was parsed and then never read, so every
    # precision on an integer was silently discarded.
    if verb.precision is not None:
        rendered = rendered.rjust(verb.precision, "0")

    # The alternate form's base prefix, likewise parsed and never read.
    if verb.sharp:
        rendered = _ALTERNATE_PREFIX.get(verb.verb, "") + rendered

    # Go ignores the zero flag when a precision is given -- the precision has
    # already said how many digits there are, so width is padded with spaces.
    if verb.zero and verb.width is not None and not verb.minus and verb.precision is None:
        rendered = rendered.rjust(max(0, verb.width - len(sign)), "0")
    return _pad(verb, sign + rendered)


def _format_non_finite(verb: _Verb, number: Decimal) -> str:
    """Go's `fmt` on an infinity or a NaN (`fmt/format.go`, `fmtFloat`).

    Three departures from the finite path, all because the text is not a number:
    the precision is ignored, there being no digits to round; the zero flag is
    dropped ("Special handling for infinities and NaN, which don't look like a
    number so shouldn't be padded with '0'"); and the sign is decided by what
    the value is rather than by the digits, so an unsigned infinity shows a `+`
    and an unsigned NaN shows nothing.
    """
    text = cast(str, non_finite_text(number))
    sign, bare = (text[0], text[1:]) if text[0] in "+-" else ("+", text)
    if sign == "+" and " " in verb.flags and "+" not in verb.flags:
        sign = " "
    if bare == "NaN" and " " not in verb.flags and "+" not in verb.flags:
        sign = ""
    return _pad(verb, sign + bare, allow_zero=False)


def _format_float(verb: _Verb, number: Decimal) -> str:
    if not number.is_finite():
        return _format_non_finite(verb, number)
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
        return _pad(verb, _json_of(value, verb))

    if verb.verb == "t":
        # go-cty returns before padding for %t, so a width is accepted and then
        # ignored: `%10t` is "true", not "      true". This differs from Go's own
        # fmt, and the oracle is what this package tracks.
        return "true" if _as(value, CtyBool(), verb).value else "false"

    if verb.verb in _INTEGER_VERBS:
        return _format_integer(verb, cast(Decimal, _as(value, CtyNumber(), verb).value))

    if verb.verb in _FLOAT_VERBS:
        return _format_float(verb, cast(Decimal, _as(value, CtyNumber(), verb).value))

    if verb.verb in ("s", "q"):
        text = str(_as(value, CtyString(), verb).value)
        if verb.precision is not None and verb.precision > 0:
            # Truncation counts grapheme clusters too (`format.go:469`), so a
            # precision never cuts a character in half -- slicing code points
            # would emit a lone joiner or a stranded combining mark.
            text = "".join(islice(iter_clusters(text), verb.precision))
        if verb.verb == "q":
            # go-cty's `%q` is not Go's. It is `ctyjson.Marshal(cty.StringVal(s))`
            # (`stdlib/format.go:480`), so the string comes back JSON-encoded --
            # non-ASCII kept as itself, and `<`, `>` and `&` escaped, because
            # Go's `encoding/json` escapes those by default. `json.dumps` does
            # not, so `format("%q", "a<b>&c")` differed from go-cty in three
            # characters. The codec's own encoder is used rather than a second
            # copy of the escape table. Found 2026-08-19 by the stdlib fuzz.
            text = _marshal_string(text)
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


_VARIADIC_FORMAT_ARGS = CtyParameter(
    "args",
    CtyDynamic(),
    allow_null=True,
    allow_unknown=True,
    allow_dynamic_type=True,
)


@stdlib_function(
    "format",
    params=[CtyParameter("format", CtyString())],
    var_param=_VARIADIC_FORMAT_ARGS,
    returns=CtyString(),
    refine_result=refine_not_null,
    description=(
        r"Constructs a string by applying formatting verbs to a series of arguments, "
        r"using a similar syntax to the C function \"printf\"."
    ),
)
def format_fn(template: CtyValue[Any], *arguments: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `FormatFunc` (`stdlib/format.go:20`).

    `allow_null` on the variadic parameter because `%v` renders a null as the
    literal `null`; every other verb refuses one, which `_format_one` enforces
    per verb rather than the framework enforcing it per argument. The format
    string is declared without it, so a null there is the framework's refusal.
    """
    if not all(argument.is_wholly_known() for argument in arguments):
        # A collection can only be rendered as JSON, and JSON needs it wholly
        # known. The literal text before the first verb is decided either way,
        # though, so go-cty promises that much of the answer (`format.go:44`).
        text = str(template.value)
        percent = text.find("%")
        if percent > 0:
            return refine(CtyValue.unknown(CtyString())).string_prefix(text[:percent]).new_value()
        return CtyValue.unknown(CtyString())
    return CtyString().validate(_render(str(template.value), list(arguments)))


def _is_sequence(argument: CtyValue[Any]) -> bool:
    """Whether `formatlist` iterates this argument rather than repeating it.

    A null sequence is not iterated: go-cty's `!arg.IsNull()` guard sends it to
    the single-value branch, where `%v` renders it as `null` (`format.go:99`).
    """
    return not argument.is_null and isinstance(argument.type, CtyList | CtySet | CtyTuple)


def _has_known_length(argument: CtyValue[Any]) -> bool:
    """Whether this sequence's element count is decided. go-cty's `Value.Length`.

    A tuple's length is in its type, so it is known even when the value is not.
    A list's is its own structure. A set's is neither: an unknown element may
    turn out to equal another member and coalesce with it, so a set holding one
    is only as long as it looks if there is nothing else in it to coalesce with
    (`value_ops.go:1126`).
    """
    if isinstance(argument.type, CtyTuple):
        return True
    if argument.is_unknown:
        return False
    if isinstance(argument.type, CtySet):
        return len(cast(Sized, argument.value)) == 1 or argument.is_wholly_known()
    return True


def _sequence_length(argument: CtyValue[Any]) -> int:
    """How many rows this sequence dictates. go-cty's `Value.LengthInt`.

    A tuple's length comes from its type rather than from its elements, so an
    unknown tuple has one anyway (`value_ops.go:1174`).
    """
    if isinstance(argument.type, CtyTuple):
        return len(argument.type.element_types)
    return len(cast(Sized, argument.value))


def _iteration_plan(arguments: tuple[CtyValue[Any], ...]) -> tuple[int, bool]:
    """The number of rows, and whether any argument leaves them all undecided.

    go-cty's first pass over `FormatListFunc`'s arguments (`format.go:96`). `-1`
    rows means every argument was scalar, so there is exactly one row.

    An argument whose length is undecided does not end the pass: go-cty
    deliberately falls through so that the *later* arguments still have their
    lengths checked against each other, and an inconsistent length is reported
    even when an earlier argument is unknown.
    """
    iterations = -1
    chooser = 0
    undecided = False
    for position, argument in enumerate(arguments):
        if not _is_sequence(argument):
            # go-cty's `arg == cty.DynamicVal`: a value of no decided type
            # cannot even be classified as a sequence yet.
            undecided = undecided or (argument.is_unknown and isinstance(argument.type, CtyDynamic))
            continue
        if not _has_known_length(argument):
            undecided = True
            continue
        length = _sequence_length(argument)
        if iterations == -1:
            iterations, chooser = length, position
        elif length != iterations:
            raise CtyFunctionError(
                ERR_FORMAT_INCONSISTENT_LENGTH.format(
                    position=position + 1, length=length, other=chooser + 1, other_length=iterations
                )
            )
        if argument.is_unknown:
            # An unknown tuple got this far for the length check above, which is
            # all it can contribute -- its elements are not there to iterate.
            undecided = True
    return iterations, undecided


def _elements_of(argument: CtyValue[Any]) -> list[CtyValue[Any]]:
    """A sequence argument's elements, in the order go-cty iterates them.

    A set has no order of its own, so `list(frozenset)` gives whatever the hash
    table yields -- `formatlist("%s", toset(["a", "b"]))` came back `["b", "a"]`.
    Sets are given the same canonical order used to de-duplicate them, which is
    the one go-cty's own set iteration follows.
    """
    if isinstance(argument.value, frozenset):
        return sorted(argument.value, key=set_order_key)
    return list(cast(Iterable[CtyValue[Any]], argument.value))


@stdlib_function(
    "formatlist",
    params=[CtyParameter("format", CtyString())],
    var_param=_VARIADIC_FORMAT_ARGS,
    returns=CtyList(element_type=CtyString()),
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        r"Constructs a list of strings by applying formatting verbs to a series of arguments, "
        r"using a similar syntax to the C function \"printf\"."
    ),
)
def formatlist(template: CtyValue[Any], *arguments: CtyValue[Any], return_type: CtyType[Any]) -> CtyValue[Any]:
    """go-cty's `FormatListFunc` (`stdlib/format.go:58`): `format` per element, in lockstep.

    Sequence arguments are iterated together and must agree on length; anything
    else is reused unchanged on every iteration.
    """
    iterations, undecided = _iteration_plan(arguments)
    if undecided:
        return CtyValue.unknown(return_type)

    if iterations == 0:
        return return_type.validate([])

    rows: list[CtyValue[Any]] = []
    for index in range(1 if iterations == -1 else iterations):
        row: list[CtyValue[Any]] = []
        for argument in arguments:
            if _is_sequence(argument):
                row.append(_elements_of(argument)[index])
            else:
                row.append(argument)
        if not all(element.is_wholly_known() for element in row):
            # One unresolved row does not make the others unresolvable. The row
            # is refined not-null because formatting always produces a string:
            # whatever the argument turns out to be, this element will not be
            # null, and go-cty says so on the wire (ext 12 rather than a bare
            # `d4 00 00`). Terraform can act on that during a plan.
            #
            # `refine_result` does not cover this: it refines the *list*, which
            # here is known, and says nothing about an element inside it.
            # go-cty spells this one out per row too (`format.go:174`).
            rows.append(unknown_not_null(CtyString()))
            continue
        rows.append(CtyString().validate(_render(str(template.value), row)))
    return return_type.validate(rows)


# 🌊🪢🔚
