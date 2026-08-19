#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from __future__ import annotations

from collections.abc import Sequence
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
from pyvider.cty._unicode import cluster_count, iter_clusters
from pyvider.cty._unicode.case import simple_lower, simple_title_char, simple_upper
from pyvider.cty.config.defaults import (
    ERR_INDENT_SPACES_MUST_BE_WHOLE,
    ERR_INDENT_SPACES_MUST_NOT_BE_NEGATIVE,
    ERR_JOIN_AT_LEAST_ONE_LIST,
    ERR_JOIN_ELEMENT_IS_NULL,
    ERR_JOIN_ELEMENT_OF_LIST_IS_NULL,
    ERR_REGEX_INVALID_PATTERN,
    ERR_REGEX_MIXED_CAPTURE_GROUPS,
    ERR_REGEX_NO_MATCH,
    ERR_SUBSTR_ARG_MUST_BE_WHOLE,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions._args import whole_number
from pyvider.cty.functions._framework import stdlib_function
from pyvider.cty.functions._function import CtyArgumentError, CtyParameter, refine_not_null
from pyvider.cty.refinement import RefinementBuilder, refine
from pyvider.cty.value_range import value_range
from pyvider.cty.values.frozen import FrozenDict

# go-cty's `unicode.IsSpace`, which is the Unicode `White_Space` property and
# what `strings.TrimSpace` trims. Python's `str.strip()` with no argument trims
# these *and* U+001C to U+001F, which Unicode does not call whitespace at all --
# so `trimspace("\x1cab")` disagreed with go-cty, which leaves it alone.
_GO_WHITESPACE = (
    "\t\n\v\f\r \u0085\u00a0\u1680"
    "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
    "\u2028\u2029\u202f\u205f\u3000"
)

# go-cty's `ChompFunc` is one `ReplaceAllString` with this pattern, so it removes
# *every* trailing line break rather than one. `\Z` is Python's spelling of Go's
# `\z`: the absolute end of the string, never before a final newline.
_TRAILING_NEWLINES = re.compile(r"(?:\r\n?|\n)*\Z")

# Go's `strings.isSeparator` treats ASCII alphanumerics and `_` as part of a
# word and everything else ASCII as a separator -- which is why `title("a-b")`
# is `"A-B"` while `title("a—b")` is `"A—b"`: an em dash is neither a
# letter, a digit, nor whitespace, so above ASCII it separates nothing.
_ASCII_WORD_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


@stdlib_function(
    "chomp",
    params=[CtyParameter("str", CtyString())],
    returns=CtyString(),
    refine_result=refine_not_null,
    description="Removes one or more newline characters from the end of the given string.",
)
def chomp(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ChompFunc` (`stdlib/string.go:365`).

    "One or more" is the whole of it: `chomp("a\\n\\n")` is `"a"`, not `"a\\n"`.
    """
    return CtyString().validate(_TRAILING_NEWLINES.sub("", cast(str, input_val.value)))


@stdlib_function(
    "strrev",
    params=[CtyParameter("str", CtyString(), allow_dynamic_type=True)],
    returns=CtyString(),
    refine_result=refine_not_null,
    description="Returns the given string with all of its Unicode characters in reverse order.",
)
def strrev(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ReverseFunc` (`stdlib/string.go:51`), by grapheme cluster.

    Reversing by code point takes a string apart below the level of a
    character: it turns `\\U0001F468\\u200D\\U0001F469` into a *different* emoji
    sequence rather than reversing anything, and moves every combining mark onto
    the wrong base.
    """
    return CtyString().validate("".join(reversed(list(iter_clusters(cast(str, input_val.value))))))


def _refine_strlen(builder: RefinementBuilder) -> RefinementBuilder:
    """go-cty's inline `RefineResult` for `StrlenFunc` (`stdlib/string.go:91`).

    Its own comment: "String length is never null and never negative. (We might
    refine the lower bound even more inside Impl.)" -- which `strlen` does, from
    the known prefix of an unknown string.
    """
    return builder.not_null().number_range_lower_bound(0, inclusive=True)


@stdlib_function(
    "strlen",
    params=[CtyParameter("str", CtyString(), allow_unknown=True, allow_dynamic_type=True)],
    returns=CtyNumber(),
    refine_result=_refine_strlen,
    description=(
        "Returns the number of Unicode characters (technically: grapheme clusters) in the given string."
    ),
)
def strlen(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `StrlenFunc` (`stdlib/string.go:80`).

    One of two stdlib functions that asks to *see* an unknown argument, because
    it can still say something about the answer: a string refined to begin with
    "abc" is at least three characters long however it turns out. Distinct from
    `length`, which go-cty refuses for a string precisely because the two
    questions have different answers -- `length` counts collection elements, and
    this counts what a reader would call characters.
    """
    if input_val.is_unknown:
        result = CtyValue.unknown(CtyNumber())
        # go-cty tests `inRng.TypeConstraint() == cty.String`: a value not yet
        # known to *be* a string has no prefix to measure, which is the case
        # `allow_dynamic_type` lets through to here.
        if isinstance(input_val.type, CtyString):
            prefix_length = cluster_count(value_range(input_val).string_prefix())
            result = refine(result).number_range_lower_bound(prefix_length, inclusive=True).new_value()
        return result
    return CtyNumber().validate(cluster_count(cast(str, input_val.value)))


@stdlib_function(
    "trimspace",
    params=[CtyParameter("str", CtyString())],
    returns=CtyString(),
    refine_result=refine_not_null,
    description=(
        "Removes any consecutive space characters (as defined by Unicode) from the start and end of "
        "the given string."
    ),
)
def trimspace(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `TrimSpaceFunc` (`stdlib/string.go:429`).

    Stripped against an explicit set rather than with a bare `strip()`, because
    "as defined by Unicode" is the point: Python also strips the four ASCII
    information separators, which Unicode's `White_Space` property excludes.
    """
    return CtyString().validate(cast(str, input_val.value).strip(_GO_WHITESPACE))


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


@stdlib_function(
    "indent",
    params=[
        CtyParameter(
            "spaces",
            CtyNumber(),
            description="Number of spaces to add after each newline character.",
        ),
        CtyParameter("str", CtyString(), description="The string to transform."),
    ],
    returns=CtyString(),
    refine_result=refine_not_null,
    description="Adds a given number of spaces after each newline character in the given string.",
)
def indent(spaces_val: CtyValue[Any], input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `IndentFunc` (`stdlib/string.go:383`): spaces after every newline.

    The first line is deliberately left alone -- the function exists to line a
    multi-line value up underneath something already written on the first line,
    so indenting that line too would push it away from what it follows.
    go-cty's whole implementation is one `strings.Replace`, which also means a
    trailing newline gets padding after it and a CR before a newline is left in
    place ahead of the padding.
    """
    pad = " " * _indent_spaces(spaces_val)
    return CtyString().validate(cast(str, input_val.value).replace("\n", f"\n{pad}"))


@stdlib_function(
    "substr",
    params=[
        CtyParameter("str", CtyString(), description="The input string.", allow_dynamic_type=True),
        CtyParameter(
            "offset",
            CtyNumber(),
            description="The starting offset in Unicode characters.",
            allow_dynamic_type=True,
        ),
        CtyParameter(
            "length",
            CtyNumber(),
            description="The maximum length of the result in Unicode characters.",
            allow_dynamic_type=True,
        ),
    ],
    returns=CtyString(),
    refine_result=refine_not_null,
    description="Extracts a substring from the given string.",
)
def substr(input_val: CtyValue[Any], offset_val: CtyValue[Any], length_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SubstrFunc` (`stdlib/string.go:126`).

    Both counts go through `gocty.FromCtyValue` into a Go `int` there, so a
    fractional offset or length is refused rather than truncated.
    """
    offset = whole_number(offset_val, ERR_SUBSTR_ARG_MUST_BE_WHOLE)
    length = whole_number(length_val, ERR_SUBSTR_ARG_MUST_BE_WHOLE)
    clusters = list(iter_clusters(cast(str, input_val.value)))

    # go-cty's algorithm, followed step for step rather than reimplemented,
    # because two of its steps are surprising and would not be arrived at
    # independently (`string.go:163-225`).
    if offset < 0:
        # A negative offset counts back from the end -- and may still be
        # negative afterwards, in which case no seeking happens at all and the
        # result starts from the beginning.
        offset += len(clusters)
    elif length == 0:
        return CtyString().validate("")

    if offset > 0:
        clusters = clusters[offset:]

    # Any negative length means "the rest". So does a zero length reached from a
    # negative offset, because the short circuit above was skipped and go-cty's
    # seek loop increments its counter before testing it, so it can never stop
    # at zero and runs to the end instead. Reproduced deliberately: it is
    # observable, and `substr(s, -3, 0)` returning the last three characters is
    # what a caller written against go-cty will be relying on.
    if length <= 0:
        return CtyString().validate("".join(clusters))
    return CtyString().validate("".join(clusters[:length]))


@stdlib_function(
    "trim",
    params=[
        CtyParameter("str", CtyString(), description="The string to trim."),
        CtyParameter(
            "cutset",
            CtyString(),
            description=(
                "A string containing all of the characters to trim. Each character is taken "
                "separately, so the order of characters is insignificant."
            ),
        ),
    ],
    returns=CtyString(),
    refine_result=refine_not_null,
    description=(
        'Removes consecutive sequences of characters in "cutset" from the start and end of the given string.'
    ),
)
def trim(input_val: CtyValue[Any], cutset_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `TrimFunc` (`stdlib/string.go:446`).

    go-cty's own note applies here too: neither implementation handles a
    character encoded as several code points, such as a letter with a combining
    diacritic or an emoji modifier sequence.
    """
    return CtyString().validate(cast(str, input_val.value).strip(cast(str, cutset_val.value)))


@stdlib_function(
    "title",
    params=[CtyParameter("str", CtyString())],
    returns=CtyString(),
    refine_result=refine_not_null,
    description=(
        "Replaces one letter after each non-letter and non-digit character with its uppercase equivalent."
    ),
)
def title(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `TitleFunc` (`stdlib/string.go:412`), which is `strings.Title`.

    Note what its description says and Python's `str.title()` does not: it
    *replaces one letter*, leaving the rest of each word exactly as it was. So
    `title("HELLO world")` is `"HELLO World"`, and `title("aBc")` is `"ABc"`.
    Python lowercases the remainder of every word, which loses characters the
    caller wrote.
    """
    text = cast(str, input_val.value)
    out: list[str] = []
    # `strings.Title` walks the string with `prev` seeded to a space, so the
    # first character is always word-initial.
    previous = " "
    for character in text:
        out.append(simple_title_char(character) if _is_separator(previous) else character)
        previous = character
    return CtyString().validate("".join(out))


def _is_separator(character: str) -> bool:
    """Go's `strings.isSeparator`, which decides where a word begins."""
    if character.isascii():
        return character not in _ASCII_WORD_CHARACTERS
    if character.isalpha() or character.isdecimal():
        # `isalpha` is Unicode category L and `isdecimal` is Nd, which are
        # exactly Go's `unicode.IsLetter` and `unicode.IsDigit`.
        return False
    # Above ASCII, Python's `isspace` and Go's `unicode.IsSpace` agree: they
    # differ only on U+001C to U+001F.
    return character.isspace()


@stdlib_function(
    "trimprefix",
    params=[
        CtyParameter("str", CtyString(), description="The string to trim."),
        CtyParameter("prefix", CtyString(), description="The prefix to remove, if present."),
    ],
    returns=CtyString(),
    refine_result=refine_not_null,
    description="Removes the given prefix from the start of the given string, if present.",
)
def trimprefix(input_val: CtyValue[Any], prefix_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `TrimPrefixFunc` (`stdlib/string.go:474`), which is `strings.TrimPrefix`."""
    return CtyString().validate(cast(str, input_val.value).removeprefix(cast(str, prefix_val.value)))


@stdlib_function(
    "trimsuffix",
    params=[
        CtyParameter("str", CtyString(), description="The string to trim."),
        CtyParameter("suffix", CtyString(), description="The suffix to remove, if present."),
    ],
    returns=CtyString(),
    refine_result=refine_not_null,
    # Verbatim from go-cty, including "start" where it means "end".
    description="Removes the given suffix from the start of the given string, if present.",
)
def trimsuffix(input_val: CtyValue[Any], suffix_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `TrimSuffixFunc` (`stdlib/string.go:499`), which is `strings.TrimSuffix`.

    `removesuffix` rather than a hand-rolled slice: `s[: -len("")]` is `s[:0]`,
    so an empty suffix used to delete the entire string.
    """
    return CtyString().validate(cast(str, input_val.value).removesuffix(cast(str, suffix_val.value)))


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


def _regex_return_type(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
    """go-cty's `RegexFunc.Type` (`stdlib/regexp.go:24`).

    The pattern's *value* decides the shape of the answer, so this is one of the
    few stdlib functions whose return type a caller cannot predict from types
    alone -- and an unknown pattern therefore makes the type unknown too.
    """
    pattern_val: CtyValue[Any] = args[0]
    if pattern_val.is_unknown:
        return CtyDynamic()
    return _capture_result_type("regex", _compile_pattern("regex", cast(str, pattern_val.value)))


def _regexall_return_type(args: Sequence[CtyValue[Any]]) -> CtyType[Any]:
    """go-cty's `RegexAllFunc.Type` (`stdlib/regexp.go:70`).

    Narrower than `regex`'s for an unknown pattern: the element type is
    undecided, but it is still definitely a list.
    """
    pattern_val: CtyValue[Any] = args[0]
    if pattern_val.is_unknown:
        return CtyList(element_type=CtyDynamic())
    element_type = _capture_result_type("regexall", _compile_pattern("regexall", cast(str, pattern_val.value)))
    return CtyList(element_type=element_type)


@stdlib_function(
    "regex",
    params=[CtyParameter("pattern", CtyString()), CtyParameter("string", CtyString())],
    type_func=_regex_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Applies the given regular expression pattern to the given string and returns information "
        "about a single match, or raises an error if there is no match."
    ),
)
def regex(
    pattern_val: CtyValue[Any], input_val: CtyValue[Any], *, return_type: CtyType[Any] = CtyDynamic()
) -> CtyValue[Any]:
    """go-cty's `RegexFunc`: `regex(pattern, string)`, pattern first.

    The result is the whole match only when the pattern has no capture groups;
    otherwise it is the groups, as a tuple or an object. A pattern that does not
    match raises, because the empty string is a legitimate match for plenty of
    patterns and a caller could not otherwise tell the two apart. Use `regexall`
    to test whether a pattern matches at all.

    `return_type` is supplied by the framework, which already decided it from
    the pattern; the default exists only so the signature can be bound by
    keyword and is never the value used.
    """
    compiled = _compile_pattern("regex", cast(str, pattern_val.value))
    match = compiled.search(cast(str, input_val.value))
    if match is None:
        raise CtyFunctionError(ERR_REGEX_NO_MATCH)
    return _capture_result(match, return_type)


@stdlib_function(
    "regexall",
    params=[CtyParameter("pattern", CtyString()), CtyParameter("string", CtyString())],
    type_func=_regexall_return_type,
    refine_result=refine_not_null,
    wants_return_type=True,
    description=(
        "Applies the given regular expression pattern to the given string and returns a list of "
        "information about all non-overlapping matches, or an empty list if there are no matches."
    ),
)
def regexall(
    pattern_val: CtyValue[Any],
    input_val: CtyValue[Any],
    *,
    return_type: CtyType[Any] = CtyList(element_type=CtyDynamic()),
) -> CtyValue[Any]:
    """go-cty's `RegexAllFunc`: every non-overlapping match, as a list.

    Each element has the shape `regex` would return for a single match, so a
    pattern with capture groups gives a list of tuples or objects rather than a
    list of strings. No matches is an empty list rather than an error.
    """
    element_type = cast(CtyList[Any], return_type).element_type
    compiled = _compile_pattern("regexall", cast(str, pattern_val.value))
    matches = [_capture_result(match, element_type) for match in compiled.finditer(cast(str, input_val.value))]
    return return_type.validate(matches)


@stdlib_function(
    "upper",
    params=[CtyParameter("str", CtyString(), allow_dynamic_type=True)],
    returns=CtyString(),
    refine_result=refine_not_null,
    description="Returns the given string with all Unicode letters translated to their uppercase equivalents.",
)
def upper(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `UpperFunc` (`stdlib/string.go:15`), which is `strings.ToUpper`.

    Simple case mapping, one code point at a time -- see
    `pyvider.cty._unicode.case` for the four inputs where Python's own
    `str.upper()` answers something else.
    """
    return CtyString().validate(simple_upper(cast(str, input_val.value)))


@stdlib_function(
    "lower",
    params=[CtyParameter("str", CtyString(), allow_dynamic_type=True)],
    returns=CtyString(),
    refine_result=refine_not_null,
    description="Returns the given string with all Unicode letters translated to their lowercase equivalents.",
)
def lower(input_val: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `LowerFunc` (`stdlib/string.go:33`), which is `strings.ToLower`."""
    return CtyString().validate(simple_lower(cast(str, input_val.value)))


@stdlib_function(
    "join",
    params=[
        CtyParameter(
            "separator",
            CtyString(),
            description="Delimiter to insert between the given strings.",
        )
    ],
    var_param=CtyParameter(
        "lists",
        CtyList(element_type=CtyString()),
        description="One or more lists of strings to join.",
    ),
    returns=CtyString(),
    refine_result=refine_not_null,
    description=(
        "Concatenates together the elements of all given lists with a delimiter, producing a single string."
    ),
)
def join(separator: CtyValue[Any], *lists: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `JoinFunc` (`stdlib/string.go:231`), which is variadic.

    Variadic over `list(string)`, and only that: go-cty's framework tests
    conformance rather than convertibility, so a *tuple* of strings is refused
    there however easily it would convert. This took one list and accepted a
    tuple, so `join(",", ["a", "b"], ["c"])` was an arity error here and an
    answer there.
    """
    if not lists:
        raise CtyFunctionError(ERR_JOIN_AT_LEAST_ONE_LIST)

    # A list is known even while one of its elements is not, so reaching the
    # body no longer means every element has a string to contribute -- and
    # `str()` of an unknown's placeholder would land in the result as if it
    # were one. Declining is still a promise that the answer is a non-null
    # string, which `refine_result` makes.
    if any(not list_val.is_wholly_known() for list_val in lists):
        return CtyValue.unknown(CtyString())

    items: list[str] = []
    for index, list_val in enumerate(lists):
        for position, element in enumerate(cast("Any", list_val.value)):
            if element.is_null:
                # go-cty numbers the list from 1 because argument 0 is the
                # separator, and words the single-list case differently.
                template = ERR_JOIN_ELEMENT_OF_LIST_IS_NULL if len(lists) > 1 else ERR_JOIN_ELEMENT_IS_NULL
                raise CtyArgumentError(index + 1, template.format(element=position, list=index + 1))
            items.append(cast(str, element.value))
    return CtyString().validate(cast(str, separator.value).join(items))


@stdlib_function(
    "split",
    params=[
        CtyParameter(
            "separator",
            CtyString(),
            description="The substring that delimits the result strings.",
        ),
        CtyParameter("str", CtyString(), description="The string to split."),
    ],
    returns=CtyList(element_type=CtyString()),
    refine_result=refine_not_null,
    description=(
        "Produces a list of one or more strings by splitting the given string at all instances of a "
        "given separator substring."
    ),
)
def split(separator: CtyValue[Any], text: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `SplitFunc` (`stdlib/string.go:332`), which is `strings.Split`.

    An empty separator is not an error there: `strings.Split` falls through to
    `explode`, which cuts between every *rune* -- so `split("", "abc")` is
    `["a", "b", "c"]`, and `split("", "")` is the empty list. Python's
    `str.split("")` raises a bare `ValueError` instead, which is not even a
    `CtyError`, so it escaped every `except CtyFunctionError` a caller wrote.

    By rune and not by grapheme cluster, deliberately: go-cty measures `substr`
    and `strlen` in clusters and splits here in runes, so `split("", family)`
    hands back the ZWJs as elements of their own.
    """
    separator_str = cast(str, separator.value)
    text_str = cast(str, text.value)
    parts = list(text_str) if not separator_str else text_str.split(separator_str)
    return cast(CtyValue[Any], CtyList(element_type=CtyString()).validate(parts))


@stdlib_function(
    "replace",
    params=[
        CtyParameter("str", CtyString(), description="The string to search within."),
        CtyParameter("substr", CtyString(), description="The substring to search for."),
        CtyParameter("replace", CtyString(), description="The new substring to replace substr with."),
    ],
    returns=CtyString(),
    refine_result=refine_not_null,
    description=(
        "Replaces all instances of the given substring in the given string with the given replacement string."
    ),
)
def replace(string: CtyValue[Any], substring: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `ReplaceFunc` (`stdlib/string_replace.go:14`)."""
    return CtyString().validate(
        cast(str, string.value).replace(cast(str, substring.value), cast(str, replacement.value))
    )


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


@stdlib_function(
    "regexreplace",
    params=[
        CtyParameter("str", CtyString()),
        CtyParameter("pattern", CtyString()),
        CtyParameter("replace", CtyString()),
    ],
    returns=CtyString(),
    refine_result=refine_not_null,
    description=(
        "Applies the given regular expression pattern to the given string and replaces all matches "
        "with the given replacement string."
    ),
)
def regexreplace(string: CtyValue[Any], pattern: CtyValue[Any], replacement: CtyValue[Any]) -> CtyValue[Any]:
    """go-cty's `RegexReplaceFunc` (`stdlib/string_replace.go:47`).

    .. warning::
       **Security Drift**: Pyvider uses Python's `re` module instead of Go's RE2
       to maintain Pyodide/WebAssembly compatibility. This means patterns are evaluated
       using a backtracking NFA, which is strictly vulnerable to Regular Expression
       Denial of Service (ReDoS). Do not evaluate untrusted patterns from remote APIs.

    Note the argument order differs from `regex`: go-cty takes `(str, pattern,
    replace)` here and `(pattern, string)` there. That asymmetry is go-cty's
    own, and this matches it rather than tidying it.
    """
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
