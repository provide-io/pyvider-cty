#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""What the string functions answer, pinned against real go-cty.

Every expectation here was measured by running the soup-go oracle
(`soup-go cty call <func> ...`) rather than read off go-cty's source, and each
class heads a divergence the 2026-08-17 migration onto `cty/function` found. The
declarations are in `src/pyvider/cty/functions/string_functions.py`; this is the
behaviour they buy.

The through-line is that Python's string methods are not Go's, and the four
places they differ are all silent: `str.title()` lowercases the rest of each
word, `str.upper()` applies the *full* Unicode case mapping, `str.strip()` counts
four ASCII control characters as whitespace, and `str.split("")` raises where
Go splits. None of it was caught because the differential sweep's inputs were
`héllo`, `a bc` and `a\\n` -- ASCII or NFC-composed, where every one of those
methods happens to agree.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import CtyDynamic, CtyList, CtyNumber, CtyString, CtyTuple, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    chomp,
    join,
    lower,
    split,
    strlen,
    substr,
    title,
    trimprefix,
    trimspace,
    trimsuffix,
    upper,
)
from pyvider.cty.refinement import refine
from pyvider.cty.value_range import value_range

FAMILY = "\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466"

STRINGS = CtyList(element_type=CtyString())


def s(text: str) -> CtyValue[Any]:
    return CtyString().validate(text)


def n(number: Any) -> CtyValue[Any]:
    return CtyNumber().validate(number)


def strs(*items: str | CtyValue[Any]) -> CtyValue[Any]:
    return STRINGS.validate([item if isinstance(item, CtyValue) else s(item) for item in items])


class TestChompRemovesEveryTrailingNewline:
    """`ReplaceAllString` against `(?:\\r\\n?|\\n)*\\z` -- go-cty's whole body.

    This removed at most one line ending, so a value ending in two newlines kept
    one. go-cty's description says "one or more".
    """

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("a\n\n", "a"),
            ("a\r\n\r\n", "a"),
            ("a\n\r\n", "a"),
            ("a\n\r", "a"),
            ("\n\n\n", ""),
            ("a\nb\n", "a\nb"),
        ],
        ids=repr,
    )
    def test_all_of_them_go(self, text: str, expected: str) -> None:
        assert chomp(s(text)).value == expected


class TestTitleReplacesOneLetterPerWord:
    """go-cty's `TitleFunc` is `strings.Title`, which is not `str.title()`.

    Its own description is precise about it: "Replaces one letter after each
    non-letter and non-digit character with its uppercase equivalent." Python
    lowercases the *rest* of each word as well, which discards characters the
    caller wrote and cannot be recovered.
    """

    def test_the_rest_of_a_word_is_left_alone(self) -> None:
        """`str.title()` answers "Hello World" here, losing the shouting."""
        assert title(s("HELLO world")).value == "HELLO World"

    def test_interior_capitals_survive(self) -> None:
        assert title(s("aBc dEf")).value == "ABc DEf"

    def test_an_accented_word_keeps_its_case(self) -> None:
        assert title(s("étre ÉTRE")).value == "Étre ÉTRE"

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("it's", "It'S"),
            ("a1b c", "A1b C"),
            ("_ab cd", "_ab Cd"),
            ("a-b c", "A-B C"),
        ],
        ids=repr,
    )
    def test_ascii_separators_are_everything_but_alphanumerics_and_underscore(
        self, text: str, expected: str
    ) -> None:
        """Go's `isSeparator` short-circuits on ASCII, so `-` starts a word and
        `_` and a digit do not."""
        assert title(s(text)).value == expected

    def test_above_ascii_only_whitespace_separates(self) -> None:
        """An em dash is neither a letter, a digit, nor whitespace, so Go's
        `isSeparator` falls off the end and answers false -- the opposite of the
        ASCII hyphen one line up."""
        assert title(s("a—b c")).value == "A—b C"

    def test_a_titlecase_form_is_used_where_one_exists(self) -> None:
        """U+01F3 has a distinct titlecase U+01F2, which is what
        `unicode.ToTitle` gives and what a plain uppercase would not."""
        assert title(s("ǳx y")).value == "ǲx Y"

    def test_a_character_with_no_simple_titlecase_is_left_alone(self) -> None:
        """`str.title()` answers "Ss" for a leading sharp s, lengthening the
        string; Go's simple mapping has nothing to map it to."""
        assert title(s("ß x")).value == "ß X"


class TestUpperAndLowerUseSimpleCaseMapping:
    """`strings.ToUpper` and `ToLower` map one rune to one rune.

    Python applies `SpecialCasing.txt`'s full mapping instead, which can make
    the string *longer* -- so a `strlen` or `substr` downstream of an `upper`
    disagreed about the character count as well as the characters -- and carries
    a context-sensitive final-sigma rule Go does not implement at all.

    The table behind the fix is `pyvider.cty._unicode._case_tables`, generated
    from a Go toolchain's own `unicode` package and verified equal to it at every
    one of the 1,114,112 code points.
    """

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("straße", "STRAßE"),  # str.upper() -> "STRASSE"
            ("ﬁ", "ﬁ"),  # the fi ligature; str.upper() -> "FI"
            ("և", "և"),  # Armenian ech-yiwn; str.upper() -> "ԵՒ"
        ],
        ids=["sharp s", "fi ligature", "armenian ligature"],
    )
    def test_upper_never_lengthens_the_string(self, text: str, expected: str) -> None:
        assert upper(s(text)).value == expected

    def test_lower_has_no_final_sigma_rule(self) -> None:
        """Python answers sigma then *final* sigma: it lowercases the second one
        differently because of where it sits. Go maps each rune on its own."""
        assert lower(s("\u03a3\u03a3")).value == "\u03c3\u03c3"

    def test_lower_of_a_dotted_capital_i_drops_the_dot(self) -> None:
        """U+0130's *full* lowercase keeps a combining dot above; its *simple*
        lowercase is a bare `i`. This is why "one character in, one character
        out" is not enough on its own to reproduce Go."""
        assert lower(s("İ")).value == "i"

    @pytest.mark.parametrize(
        ("text", "uppered", "lowered"),
        [
            ("héllo", "HÉLLO", "héllo"),
            ("ǳ", "Ǳ", "ǳ"),
            ("ẚ", "ẚ", "ẚ"),
            ("hello", "HELLO", "hello"),
        ],
        ids=repr,
    )
    def test_the_ordinary_cases_still_agree(self, text: str, uppered: str, lowered: str) -> None:
        """Controls, measured against go-cty too. Where the simple and full
        mappings coincide -- which is all but 103 code points -- the answer is
        unchanged, so the fix narrows the behaviour rather than replacing it."""
        assert upper(s(text)).value == uppered
        assert lower(s(text)).value == lowered


class TestTrimspaceUsesUnicodeWhitespace:
    """`strings.TrimSpace` trims `unicode.IsSpace`: the `White_Space` property.

    Python's bare `strip()` also removes U+001C to U+001F, the ASCII information
    separators, which Unicode does not classify as whitespace. go-cty leaves
    them in place.
    """

    def test_the_information_separators_are_not_whitespace(self) -> None:
        assert trimspace(s("\x1cab\x1c")).value == "\x1cab\x1c"

    @pytest.mark.parametrize(
        "space",
        ["\t", "\n", "\v", "\f", "\r", " ", "\x85", "\xa0", "\u1680", "\u2028", "\u205f", "\u3000"],
    )
    def test_every_unicode_space_is_trimmed(self, space: str) -> None:
        assert trimspace(s(f"{space}ab{space}")).value == "ab"


class TestTrimprefixAndTrimsuffixWithAnEmptyAffix:
    """An empty suffix used to delete the whole string.

    `s[: -len("")]` is `s[:0]`, so `trimsuffix("abc", "")` answered `""`.
    go-cty's `strings.TrimSuffix` returns the string unchanged, which is what
    `str.removesuffix` does.
    """

    def test_an_empty_suffix_removes_nothing(self) -> None:
        assert trimsuffix(s("abc"), s("")).value == "abc"

    def test_an_empty_prefix_removes_nothing(self) -> None:
        assert trimprefix(s("abc"), s("")).value == "abc"


class TestSplitOnAnEmptySeparator:
    """`strings.Split(s, "")` cuts between every rune; Python raises.

    A bare `ValueError`, at that -- not a `CtyError` -- so it escaped every
    `except CtyFunctionError` a caller had written and surfaced as a crash.
    """

    def test_an_empty_separator_splits_into_characters(self) -> None:
        assert [element.value for element in split(s(""), s("abc")).value] == ["a", "b", "c"]

    def test_an_empty_separator_on_an_empty_string_gives_an_empty_list(self) -> None:
        """Not `[""]`: `explode` returns one element per rune, and there are
        none. The non-empty separator case *does* answer `[""]`."""
        assert list(split(s(""), s("")).value) == []
        assert [element.value for element in split(s(","), s("")).value] == [""]

    def test_an_empty_separator_splits_by_rune_and_not_by_grapheme_cluster(self) -> None:
        """go-cty measures `substr` and `strlen` in clusters and splits here in
        runes, so the zero-width joiners come back as elements of their own."""
        assert [element.value for element in split(s(""), s(FAMILY)).value] == [
            "\U0001f468",
            "‍",
            "\U0001f469",
            "‍",
            "\U0001f467",
            "‍",
            "\U0001f466",
        ]


class TestSubstrRefusesAFractionalCount:
    """Both counts go through `gocty.FromCtyValue` into a Go `int` there.

    This truncated with `int(Decimal(...))` instead, so `substr("abcdef", 1.5, 2)`
    quietly answered as though 1 had been asked for. The message is go-cty's own,
    unprefixed, so a caller comparing the two implementations sees one string.
    """

    @pytest.mark.parametrize(("offset", "length"), [("1.5", 2), (1, "1.5")], ids=["offset", "length"])
    def test_a_fraction_is_refused(self, offset: Any, length: Any) -> None:
        with pytest.raises(CtyFunctionError, match="must be a whole number"):
            substr(s("abcdef"), n(offset), n(length))


class TestJoinIsVariadic:
    """go-cty's `JoinFunc` has a `VarParam` of `list(string)`.

    This took exactly one collection and accepted a tuple for it, so
    `join(",", ["a"], ["b"])` was an arity error here and an answer there, while
    a tuple of strings was an answer here and an error there -- go-cty's
    framework tests conformance, not convertibility.
    """

    def test_several_lists_are_concatenated_in_order(self) -> None:
        assert join(s(","), strs("a", "b"), strs("c")).value == "a,b,c"

    def test_one_list_still_works(self) -> None:
        assert join(s(","), strs("a", "b")).value == "a,b"

    def test_no_lists_at_all_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError, match="at least one list is required"):
            join(s(","))

    def test_a_tuple_is_refused(self) -> None:
        """go-cty: "list of string required, but received tuple"."""
        tuple_value = CtyTuple(element_types=(CtyString(), CtyString())).validate((s("a"), s("b")))

        with pytest.raises(CtyFunctionError):
            join(s(","), tuple_value)

    def test_a_null_element_is_refused_by_position(self) -> None:
        """`str(element.value)` used to put the literal text "None" in the
        result. go-cty numbers the element from zero."""
        with pytest.raises(CtyFunctionError, match="element 1 is null; cannot concatenate null values"):
            join(s(","), strs("a", CtyValue.null(CtyString())))

    def test_a_null_element_names_its_list_when_there_are_several(self) -> None:
        """Lists are numbered from 1 because argument 0 is the separator."""
        with pytest.raises(CtyFunctionError, match="element 1 of list 1 is null"):
            join(s(","), strs("a", CtyValue.null(CtyString())), strs("b"))

    def test_an_unknown_element_defers_but_promises_a_string(self) -> None:
        result = join(s(","), strs("a", CtyValue.unknown(CtyString())))

        assert result.is_unknown
        assert result.type.equal(CtyString())
        assert value_range(result).definitely_not_null()


class TestStrlenSeesItsUnknownArgument:
    """`StrlenFunc` is one of two stdlib functions to set `AllowUnknown`.

    It can still answer something: a string refined to begin with "abc" is at
    least three characters long however it turns out. `string.go:96` reads the
    argument's refined range and derives a lower bound from the known prefix,
    which this package could not express before it had a `RefineResult` at all.
    """

    def test_a_bare_unknown_is_at_least_zero_characters(self) -> None:
        result = strlen(CtyValue.unknown(CtyString()))

        assert result.is_unknown
        assert result.type.equal(CtyNumber())
        assert value_range(result).definitely_not_null()
        assert value_range(result).number_lower_bound() == (n(0), True)

    @pytest.mark.parametrize(("prefix", "expected"), [("abc", 3), ("héllo", 5), (FAMILY, 1)], ids=repr)
    def test_a_known_prefix_raises_the_lower_bound(self, prefix: str, expected: int) -> None:
        """Counted in grapheme clusters, like `strlen` itself: a seven-code-point
        family emoji contributes one, not seven."""
        unknown = refine(CtyValue.unknown(CtyString())).string_prefix_full(prefix).new_value()

        result = strlen(unknown)

        assert value_range(result).number_lower_bound() == (n(expected), True)

    def test_a_value_not_yet_known_to_be_a_string_has_no_prefix_to_measure(self) -> None:
        """go-cty guards this with `inRng.TypeConstraint() == cty.String`. The
        answer is still a number, and still non-null and non-negative."""
        result = strlen(CtyValue.unknown(CtyDynamic()))

        assert result.type.equal(CtyNumber())
        assert value_range(result).number_lower_bound() == (n(0), True)


class TestTheUnknownsAreRefinedAndTyped:
    """Two things the framework changed for every function in the module.

    An unknown argument used to yield `unknown(dynamic)` from several of these
    bodies, and never carried a refinement -- so a caller was told "unknown"
    where go-cty says "unknown, a string, and not null", which is information
    Terraform plans on.
    """

    @pytest.mark.parametrize(
        ("function", "arguments", "expected_type"),
        [
            (chomp, (CtyValue.unknown(CtyString()),), CtyString()),
            (title, (CtyValue.unknown(CtyString()),), CtyString()),
            (trimspace, (CtyValue.unknown(CtyString()),), CtyString()),
            (upper, (CtyValue.unknown(CtyString()),), CtyString()),
            (substr, (CtyValue.unknown(CtyString()), n(0), n(1)), CtyString()),
            (split, (CtyValue.unknown(CtyString()), s("a")), CtyList(element_type=CtyString())),
        ],
        ids=["chomp", "title", "trimspace", "upper", "substr", "split"],
    )
    def test_an_unknown_answer_keeps_the_return_type_and_says_it_is_not_null(
        self, function: Any, arguments: tuple[CtyValue[Any], ...], expected_type: Any
    ) -> None:
        result = function(*arguments)

        assert result.is_unknown
        assert result.type.equal(expected_type)
        assert value_range(result).definitely_not_null()


# 🌊🪢🔚
