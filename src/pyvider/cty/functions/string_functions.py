#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from decimal import Decimal
import re
from typing import Any, cast

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtyObject,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.config.defaults import (
    ERR_INDENT_ARGS_MUST_BE_NUMBER_AND_STRING,
    ERR_INDENT_SPACES_MUST_BE_WHOLE,
    ERR_INDENT_SPACES_MUST_NOT_BE_NEGATIVE,
    ERR_REGEX_ARGS_MUST_BE_STRINGS,
    ERR_REGEX_INVALID_PATTERN,
    ERR_REGEX_MIXED_CAPTURE_GROUPS,
    ERR_REGEX_NO_MATCH,
    ERR_REGEXALL_ARGS_MUST_BE_STRINGS,
    ERR_REGEXREPLACE_ALL_ARGS_MUST_BE_STRINGS,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._args import whole_number
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.values.frozen import FrozenDict


@stdlib_function("chomp")
def chomp(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"chomp: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val

    s = input_val.value
    if s.endswith("\r\n"):  # type: ignore
        return CtyString().validate(s[:-2])  # type: ignore
    if s.endswith(("\n", "\r")):  # type: ignore
        return CtyString().validate(s[:-1])  # type: ignore
    return input_val


@stdlib_function("strrev")
def strrev(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"strrev: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value[::-1])  # type: ignore


@stdlib_function("trimspace")
def trimspace(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"trimspace: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    return CtyString().validate(input_val.value.strip())  # type: ignore


def _indent_spaces(spaces_val: CtyValue[Any]) -> int:
    """The space count, or a refusal.

    go-cty reads this through `gocty.FromCtyValue` into an `int`, which rejects
    a fractional number, and then hands it to `strings.Repeat`, which *panics*
    on a negative count -- recovered by the function framework into an opaque
    error carrying a Go stack trace. Refusing a negative count outright is the
    same outcome for a caller without reproducing the crash.
    """
    count = whole_number(spaces_val, ERR_INDENT_SPACES_MUST_BE_WHOLE)
    if count < 0:
        raise CtyFunctionError(ERR_INDENT_SPACES_MUST_NOT_BE_NEGATIVE.format(spaces=count))
    return count


@stdlib_function("indent")
def indent(spaces_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `IndentFunc`: a number of spaces after every newline.

    The first line is deliberately left alone -- the function exists to line a
    multi-line value up underneath something already written on the first line,
    so indenting that line too would push it away from what it follows.
    go-cty's whole implementation is one `strings.Replace`, which also means a
    trailing newline gets padding after it and a CR before a newline is left in
    place ahead of the padding.
    """
    if not isinstance(spaces_val.type, CtyNumber) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(ERR_INDENT_ARGS_MUST_BE_NUMBER_AND_STRING)
    if input_val.is_null or input_val.is_unknown or spaces_val.is_null or spaces_val.is_unknown:
        return CtyValue.unknown(CtyString())
    pad = " " * _indent_spaces(spaces_val)
    return CtyString().validate(str(input_val.value).replace("\n", f"\n{pad}"))


@stdlib_function("substr")
def substr(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(input_val.type, CtyString)
        or not isinstance(offset_val.type, CtyNumber)
        or not isinstance(length_val.type, CtyNumber)
    ):
        raise CtyFunctionError("substr: arguments must be string, number, number")
    if (
        input_val.is_null
        or input_val.is_unknown
        or offset_val.is_null
        or offset_val.is_unknown
        or length_val.is_null
        or length_val.is_unknown
    ):
        return CtyValue.unknown(CtyString())
    offset = int(cast(Decimal, offset_val.value))
    length = int(cast(Decimal, length_val.value))
    if offset < 0:
        raise CtyFunctionError("substr: offset must be a non-negative integer")
    if length < -1:
        raise CtyFunctionError("substr: length must be non-negative or -1")
    s = cast(str, input_val.value)
    if length == -1:
        return CtyString().validate(s[offset:])
    return CtyString().validate(s[offset : offset + length])


@stdlib_function("trim")
def trim(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(cutset_val.type, CtyString):
        raise CtyFunctionError("trim: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or cutset_val.is_null or cutset_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    cutset_str = cast(str, cutset_val.value)
    return CtyString().validate(input_str.strip(cutset_str))


@stdlib_function("title")
def title(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"title: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.title())


@stdlib_function("trimprefix")
def trimprefix(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(prefix_val.type, CtyString):
        raise CtyFunctionError("trimprefix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or prefix_val.is_null or prefix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    prefix_str = cast(str, prefix_val.value)
    if input_str.startswith(prefix_str):
        return CtyString().validate(input_str[len(prefix_str) :])
    return input_val


@stdlib_function("trimsuffix")
def trimsuffix(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString) or not isinstance(suffix_val.type, CtyString):
        raise CtyFunctionError("trimsuffix: both arguments must be strings")
    if input_val.is_null or input_val.is_unknown or suffix_val.is_null or suffix_val.is_unknown:
        return CtyValue.unknown(CtyString())
    input_str = cast(str, input_val.value)
    suffix_str = cast(str, suffix_val.value)
    if input_str.endswith(suffix_str):
        return CtyString().validate(input_str[: -len(suffix_str)])
    return input_val


def _compile_pattern(func: str, pattern: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern)
    except re.error as e:
        raise CtyFunctionError(ERR_REGEX_INVALID_PATTERN.format(func=func, error=e)) from e


def _capture_names(compiled: re.Pattern[str]) -> list[str | None]:
    """Each capture group's name by group number, or None where it has none."""
    names: list[str | None] = [None] * compiled.groups
    for name, number in compiled.groupindex.items():
        names[number - 1] = name
    return names


def _capture_result_type(func: str, compiled: re.Pattern[str]) -> CtyType[Any]:
    """The type a pattern's capture groups produce.

    go-cty decides this from the pattern alone, before matching anything, since
    a cty function has to declare its return type from its arguments
    (`regexPatternResultType`, cty/function/stdlib/regexp.go). Three shapes: no
    capture groups yields the whole match as a string; unnamed groups yield a
    tuple of the sub-matches in order; named groups yield an object keyed by
    name. A pattern mixing the two kinds is refused rather than resolved to one
    of them.
    """
    names = _capture_names(compiled)
    named = [name for name in names if name is not None]
    unnamed = len(names) - len(named)
    if unnamed and named:
        raise CtyFunctionError(ERR_REGEX_MIXED_CAPTURE_GROUPS.format(func=func))
    if not names:
        return CtyString()
    if named:
        return CtyObject(attribute_types=dict.fromkeys(named, CtyString()))
    return CtyTuple(element_types=(CtyString(),) * unnamed)


def _capture_result(match: re.Match[str], result_type: CtyType[Any]) -> CtyValue[Any]:
    """One match rendered as `result_type`.

    A group that did not participate in the match is null, not the empty
    string: `(a)|(z)` against "a" leaves the second group unmatched, which is a
    different outcome from matching an empty substring.
    """
    if isinstance(result_type, CtyString):
        return CtyString().validate(match.group(0))
    groups = [
        CtyValue.null(CtyString()) if group is None else CtyString().validate(group)
        for group in match.groups()
    ]
    if isinstance(result_type, CtyTuple):
        return cast(CtyValue[Any], result_type.validate(tuple(groups)))
    # Built directly rather than through `CtyObject.validate`, which refuses a
    # null attribute unless that attribute is declared optional. go-cty has no
    # such rule -- nullability is not part of an object type there -- and
    # declaring these optional would add go-cty's third wire element to the
    # type, so the result would no longer be the type go-cty returns. The
    # attribute values are already validated, so `validate` has nothing left to
    # do here beyond the one check that is wrong for this case.
    names = cast(list[str], _capture_names(match.re))
    return CtyValue(vtype=result_type, value=FrozenDict(dict(zip(names, groups, strict=True))))


@stdlib_function("regex")
def regex(pattern_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `RegexFunc`: `regex(pattern, string)`, pattern first.

    The result is the whole match only when the pattern has no capture groups;
    otherwise it is the groups, as a tuple or an object. A pattern that does not
    match raises, because the empty string is a legitimate match for plenty of
    patterns and a caller could not otherwise tell the two apart. Use `regexall`
    to test whether a pattern matches at all.
    """
    if not isinstance(pattern_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(ERR_REGEX_ARGS_MUST_BE_STRINGS)
    if pattern_val.is_null or pattern_val.is_unknown:
        # The result type is read off the pattern, so without one the type is
        # unpredictable as well as the value: go-cty returns DynamicPseudoType.
        return CtyValue.unknown(CtyDynamic())
    compiled = _compile_pattern("regex", cast(str, pattern_val.value))
    result_type = _capture_result_type("regex", compiled)
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(result_type)
    match = compiled.search(cast(str, input_val.value))
    if match is None:
        raise CtyFunctionError(ERR_REGEX_NO_MATCH)
    return _capture_result(match, result_type)


@stdlib_function("regexall")
def regexall(pattern_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `RegexAllFunc`: every non-overlapping match, as a list.

    Each element has the shape `regex` would return for a single match, so a
    pattern with capture groups gives a list of tuples or objects rather than a
    list of strings. No matches is an empty list rather than an error.
    """
    if not isinstance(pattern_val.type, CtyString) or not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(ERR_REGEXALL_ARGS_MUST_BE_STRINGS)
    if pattern_val.is_null or pattern_val.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyDynamic()))
    compiled = _compile_pattern("regexall", cast(str, pattern_val.value))
    element_type = _capture_result_type("regexall", compiled)
    result_type = CtyList(element_type=element_type)
    if input_val.is_null or input_val.is_unknown:
        return CtyValue.unknown(result_type)
    matches = [_capture_result(match, element_type) for match in compiled.finditer(cast(str, input_val.value))]
    return cast(CtyValue[Any], result_type.validate(matches))


@stdlib_function("upper")
def upper(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"upper: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.upper())


@stdlib_function("lower")
def lower(input_val: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(input_val.type, CtyString):
        raise CtyFunctionError(f"lower: input must be a string, got {input_val.type.ctype}")
    if input_val.is_null or input_val.is_unknown:
        return input_val
    input_str = cast(str, input_val.value)
    return CtyString().validate(input_str.lower())


@stdlib_function("join")
def join(separator: CtyValue[Any], elements: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(elements.type, CtyList | CtyTuple):
        raise CtyFunctionError("join: arguments must be string and list/tuple")
    if separator.is_null or separator.is_unknown or elements.is_null or elements.is_unknown:
        return CtyValue.unknown(CtyString())

    sep_str = cast(str, separator.value)
    elements_list = cast(list[Any] | tuple[Any, ...], elements.value)
    str_elements = [str(el.value) for el in elements_list]
    return CtyString().validate(sep_str.join(str_elements))


@stdlib_function("split")
def split(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    if not isinstance(separator.type, CtyString) or not isinstance(text.type, CtyString):
        raise CtyFunctionError("split: arguments must be strings")
    if separator.is_null or separator.is_unknown or text.is_null or text.is_unknown:
        return CtyValue.unknown(CtyList(element_type=CtyString()))

    sep_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = text_str.split(sep_str)
    result: CtyValue[Any] = CtyList(element_type=CtyString()).validate(parts)
    return result


@stdlib_function("replace")
def replace(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(substring.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError("replace: all arguments must be strings")
    if (
        string.is_null
        or string.is_unknown
        or substring.is_null
        or substring.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    string_str = cast(str, string.value)
    substring_str = cast(str, substring.value)
    replacement_str = cast(str, replacement.value)
    result = string_str.replace(substring_str, replacement_str)
    return CtyString().validate(result)


def _group_number(name: str) -> int | None:
    """The capture-group number `name` denotes, or None if it names one instead.

    Go reads the run as a number only when every byte is an ASCII digit, and
    rejects a leading zero and anything from 10^8 up -- in which case the run
    falls back to being a *name*, which is why `${01}` looks up a group called
    "01" and finds nothing rather than meaning group 1.
    """
    if not (name.isascii() and name.isdigit()):
        return None
    if name[0] == "0" and len(name) > 1:
        return None
    number = int(name)
    return number if number < 100_000_000 else None


def _extract_reference(template: str, start: int) -> tuple[str | None, int]:
    """Read the group reference beginning just after a `$`.

    Returns the name and the index to resume at, or `(None, start)` when the
    reference is malformed -- an empty name, or `${` with no closing brace.
    Go's `extract` treats both as "not a reference at all".
    """
    index = start
    braced = index < len(template) and template[index] == "{"
    if braced:
        index += 1

    name_start = index
    while index < len(template) and (template[index].isalnum() or template[index] == "_"):
        index += 1
    name = template[name_start:index]
    if not name:
        return None, start

    if braced:
        if index >= len(template) or template[index] != "}":
            return None, start
        index += 1
    return name, index


# A parsed replacement template: literal text, a numbered group, or a named one.
# Parsed once per call rather than once per match -- re-parsing per match made a
# 40k-match replacement 6.6x slower than `re.sub`, and the template does not
# change between matches.
_LITERAL, _NUMBERED, _NAMED = 0, 1, 2
GoTemplate = list[tuple[int, Any]]


def _parse_go_template(template: str) -> GoTemplate:
    """`template` split into literal text and the group references between it.

    Go's rules, three of which a shorter version gets wrong and each of which
    is pinned by a test: a name is the longest run of letters, digits and
    underscores, so `$1W` is the group named "1W" rather than group 1 followed
    by a "W" -- which is why go-cty's own test writes `${1}W`; `$$` is one
    literal `$`; and a malformed reference emits a bare `$` and carries on from
    the next character.
    """
    segments: GoTemplate = []
    index = 0
    while index < len(template):
        dollar = template.find("$", index)
        if dollar < 0:
            segments.append((_LITERAL, template[index:]))
            break
        if dollar > index:
            segments.append((_LITERAL, template[index:dollar]))
        index = dollar + 1

        if index < len(template) and template[index] == "$":
            segments.append((_LITERAL, "$"))
            index += 1
            continue

        name, resumed = _extract_reference(template, index)
        if name is None:
            segments.append((_LITERAL, "$"))
            index = resumed
            continue
        index = resumed

        number = _group_number(name)
        segments.append((_NUMBERED, number) if number is not None else (_NAMED, name))
    return segments


def _expand_go_template(match: re.Match[str], segments: GoTemplate) -> str:
    """A match rendered through an already-parsed template.

    A reference to a group that does not exist, or that did not participate in
    this match, contributes nothing -- Go neither errors nor leaves it literal.
    """
    out: list[str] = []
    for kind, value in segments:
        if kind is _LITERAL:
            out.append(value)
            continue
        if kind is _NUMBERED:
            captured = match.group(value) if value <= match.re.groups else None
        else:
            captured = match.groupdict().get(value)
        if captured is not None:
            out.append(captured)
    return "".join(out)


@stdlib_function("regexreplace")
def regexreplace(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `RegexReplaceFunc`.

    Note the argument order differs from `regex`: go-cty takes `(str, pattern,
    replace)` here and `(pattern, string)` there. That asymmetry is go-cty's
    own, and this matches it rather than tidying it.
    """
    if (
        not isinstance(string.type, CtyString)
        or not isinstance(pattern.type, CtyString)
        or not isinstance(replacement.type, CtyString)
    ):
        raise CtyFunctionError(ERR_REGEXREPLACE_ALL_ARGS_MUST_BE_STRINGS)
    if (
        string.is_null
        or string.is_unknown
        or pattern.is_null
        or pattern.is_unknown
        or replacement.is_null
        or replacement.is_unknown
    ):
        return CtyValue.unknown(CtyString())

    compiled = _compile_pattern("regexreplace", cast(str, pattern.value))
    template = cast(str, replacement.value)
    subject = cast(str, string.value)

    if "$" not in template and "\\" not in template:
        # Inert in both dialects -- Go expands only `$`, Python only `\`. Handing
        # it straight to `sub` keeps the whole replacement at C speed, which is
        # the common "replace with a fixed string" case.
        return CtyString().validate(compiled.sub(template, subject))

    # A per-match Python callback, which costs about 2.7x `re.sub` on a
    # 40k-match subject. The faster shape is to rewrite the Go template into
    # Python's own `\g<1>` dialect and let the C expander run it -- deliberately
    # not done. It needs a second escaping layer to keep literal text literal in
    # a dialect where backslash is significant, plus resolving away references
    # to groups that do not exist, since Python raises where Go expands nothing.
    # That is a lot of new surface on the function that just shipped a silent
    # wrong answer, to save 8 ms on an input size no provider produces.
    segments = _parse_go_template(template)
    return CtyString().validate(compiled.sub(lambda match: _expand_go_template(match, segments), subject))


# 🌊🪢🔚
