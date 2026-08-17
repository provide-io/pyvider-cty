#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`regex`, `regexall` and `regexreplace` must answer what go-cty answers.

Every expectation here was taken from running real go-cty through the soup-go
oracle (`soup-go cty call regex ...`), not from reading its source. The
divergences these pin were all present before this file existed:

  - The arguments were in the opposite order. go-cty is `(pattern, string)`;
    this package took `(string, pattern)`. Both are strings, so a call written
    against one order type-checks against the other and silently returns a
    wrong answer.
  - Capture groups were ignored. `regex("a(b)c", "abc")` returned the whole
    match `"abc"` where go-cty returns the tuple `["b"]`. Terraform's `regex()`
    exists *for* capture groups, so this was a wrong answer rather than a
    stylistic difference.
  - A non-match returned `""`, where go-cty raises. `""` is a legitimate match
    for plenty of patterns, so the caller could not tell the two apart.
  - `regexreplace` expanded the replacement with Python's `re.sub` rules, which
    are the *inverse* of Go's: Go expands `$1` and treats `\\1` as literal text,
    Python expands `\\1` and treats `$1` as literal text. Every replacement
    referring to a capture group was silently wrong, in both directions.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import CtyNumber, CtyObject, CtyString, CtyTuple, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import regex, regexall, regexreplace


def s(text: str) -> CtyValue[Any]:
    return CtyString().validate(text)


class TestRegexReturnType:
    """The result type is decided by the pattern's capture groups.

    go-cty computes it in `regexPatternResultType` (cty/function/stdlib/regexp.go)
    before running the match at all, because a cty function has to declare its
    return type from its arguments' types and, here, the pattern's value.
    """

    def test_a_pattern_without_capture_groups_returns_the_whole_match(self) -> None:
        result = regex(s("a.c"), s("abc"))

        assert result.type.equal(CtyString())
        assert result.value == "abc"

    def test_unnamed_capture_groups_return_a_tuple_of_submatches(self) -> None:
        result = regex(s("a(b)c"), s("abc"))

        assert result.type.equal(CtyTuple(element_types=(CtyString(),)))
        assert [v.value for v in result.value] == ["b"]

    def test_several_unnamed_groups_keep_their_order(self) -> None:
        result = regex(s("(a)(b)"), s("ab"))

        assert result.type.equal(CtyTuple(element_types=(CtyString(), CtyString())))
        assert [v.value for v in result.value] == ["a", "b"]

    def test_named_capture_groups_return_an_object(self) -> None:
        result = regex(s("(?P<x>a)(?P<y>b)"), s("ab"))

        assert result.type.equal(CtyObject(attribute_types={"x": CtyString(), "y": CtyString()}))
        assert {k: v.value for k, v in result.value.items()} == {"x": "a", "y": "b"}

    def test_mixing_named_and_unnamed_groups_is_rejected(self) -> None:
        """go-cty refuses the pattern rather than pick one of the two shapes."""
        with pytest.raises(CtyFunctionError, match="cannot mix both named and unnamed"):
            regex(s("(?P<x>a)(b)"), s("ab"))

    def test_a_group_that_did_not_participate_is_refuses_a_null(self) -> None:
        """`(a)|(z)` against "a" leaves the second group unmatched.

        Not the empty string: a group that matched nothing and a group that
        matched an empty substring are different outcomes.
        """
        result = regex(s("(a)|(z)"), s("a"))

        assert result.value[0].value == "a"
        assert result.value[1].is_null

    def test_a_named_group_that_did_not_participate_is_null_too(self) -> None:
        """The object case, which `CtyObject.validate` refuses outright.

        A non-optional attribute may not be null here, a rule go-cty does not
        have -- nullability is not part of an object type there. Declaring the
        attribute optional instead would add go-cty's third wire element to the
        type, so the result would no longer be the type go-cty returns.
        """
        result = regex(s("(?P<x>a)|(?P<y>z)"), s("a"))

        assert result.type.equal(CtyObject(attribute_types={"x": CtyString(), "y": CtyString()}))
        assert result.value["x"].value == "a"
        assert result.value["y"].is_null


class TestRegexArgumentOrder:
    """Pattern first, string second, as in go-cty and Terraform."""

    def test_the_first_argument_is_the_pattern(self) -> None:
        assert regex(s("l+"), s("hello")).value == "ll"

    def test_the_second_argument_is_the_string(self) -> None:
        """Reversed, this pattern does not compile, which makes the order visible."""
        with pytest.raises(CtyFunctionError):
            regex(s("hello"), s("l+("))


class TestRegexFailureModes:
    def test_a_pattern_that_does_not_match_raises(self) -> None:
        with pytest.raises(CtyFunctionError, match="did not match"):
            regex(s("z"), s("abc"))

    def test_an_invalid_pattern_raises(self) -> None:
        with pytest.raises(CtyFunctionError, match="invalid regexp pattern"):
            regex(s("("), s("abc"))

    def test_a_non_string_argument_raises(self) -> None:
        with pytest.raises(CtyFunctionError):
            regex(CtyNumber().validate(123), s("."))
        with pytest.raises(CtyFunctionError):
            regex(s("."), CtyNumber().validate(123))


class TestRegexUnknowns:
    """An unknown pattern makes the *type* unpredictable, not just the value."""

    def test_an_unknown_pattern_gives_an_unknown_of_unpredictable_type(self) -> None:
        from pyvider.cty import CtyDynamic

        result = regex(CtyValue.unknown(CtyString()), s("abc"))

        assert result.is_unknown
        assert result.type.equal(CtyDynamic())

    def test_an_unknown_subject_keeps_the_type_the_pattern_implies(self) -> None:
        result = regex(s("a(b)c"), CtyValue.unknown(CtyString()))

        assert result.is_unknown
        assert result.type.equal(CtyTuple(element_types=(CtyString(),)))

    @pytest.mark.parametrize(
        ("pattern", "subject"),
        [(CtyValue.null(CtyString()), s("abc")), (s("a"), CtyValue.null(CtyString()))],
    )
    def test_a_null_argument_is_refused(self, pattern: CtyValue[Any], subject: CtyValue[Any]) -> None:
        with pytest.raises(CtyFunctionError):
            regex(pattern, subject)

    @pytest.mark.parametrize(
        ("pattern", "subject"),
        [(CtyValue.unknown(CtyString()), s("abc")), (s("a"), CtyValue.unknown(CtyString()))],
    )
    def test_an_unknown_argument_yields_unknown(self, pattern: CtyValue[Any], subject: CtyValue[Any]) -> None:
        assert regex(pattern, subject).is_unknown


class TestRegexAll:
    """Same result shape as `regex`, once per match, in a list."""

    def test_no_capture_groups_gives_a_list_of_whole_matches(self) -> None:
        result = regexall(s("b"), s("abcb"))

        assert result.type.element_type.equal(CtyString())
        assert [v.value for v in result.value] == ["b", "b"]

    def test_capture_groups_give_a_list_of_tuples(self) -> None:
        result = regexall(s("a(b)"), s("abab"))

        assert result.type.element_type.equal(CtyTuple(element_types=(CtyString(),)))
        assert [[g.value for g in v.value] for v in result.value] == [["b"], ["b"]]

    def test_named_groups_give_a_list_of_objects(self) -> None:
        result = regexall(s("(?P<x>b)"), s("abcb"))

        assert result.type.element_type.equal(CtyObject(attribute_types={"x": CtyString()}))
        assert [v.value["x"].value for v in result.value] == ["b", "b"]

    def test_a_named_group_may_be_null_in_some_matches_and_not_others(self) -> None:
        result = regexall(s("(?P<x>a)|(?P<y>z)"), s("az"))

        assert [(m.value["x"].value, m.value["y"].value) for m in result.value] == [
            ("a", None),
            (None, "z"),
        ]

    def test_no_matches_gives_an_empty_list_of_the_right_element_type(self) -> None:
        """Empty, not an error -- `regexall` is the way to test for a match."""
        result = regexall(s("(z)"), s("abc"))

        assert list(result.value) == []
        assert result.type.element_type.equal(CtyTuple(element_types=(CtyString(),)))

    def test_the_first_argument_is_the_pattern(self) -> None:
        assert [v.value for v in regexall(s(r"\w+"), s("hello world")).value] == ["hello", "world"]

    def test_an_invalid_pattern_raises(self) -> None:
        with pytest.raises(CtyFunctionError, match="invalid regexp pattern"):
            regexall(s("["), s("abc"))

    def test_a_non_string_argument_raises(self) -> None:
        with pytest.raises(CtyFunctionError):
            regexall(CtyNumber().validate(123), s("."))
        with pytest.raises(CtyFunctionError):
            regexall(s("."), CtyNumber().validate(123))

    @pytest.mark.parametrize(
        ("pattern", "subject"),
        [(CtyValue.null(CtyString()), s("abc")), (s("a"), CtyValue.null(CtyString()))],
    )
    def test_a_null_argument_is_refused(self, pattern: CtyValue[Any], subject: CtyValue[Any]) -> None:
        with pytest.raises(CtyFunctionError):
            regexall(pattern, subject)

    @pytest.mark.parametrize(
        ("pattern", "subject"),
        [(CtyValue.unknown(CtyString()), s("abc")), (s("a"), CtyValue.unknown(CtyString()))],
    )
    def test_an_unknown_argument_yields_unknown(self, pattern: CtyValue[Any], subject: CtyValue[Any]) -> None:
        assert regexall(pattern, subject).is_unknown


class TestRegexReplace:
    """`re.ReplaceAllString(str, replace)` -- Go's replacement template.

    Go and Python expand opposite syntaxes, so this was not "slightly
    different formatting": each engine emitted the other's placeholder as
    literal text. A replacement referring to a capture group came out wrong
    whichever dialect the caller wrote it in.

    Note the argument order differs from `regex`: go-cty's `RegexReplaceFunc`
    takes `(str, pattern, replace)`, string first, while `RegexFunc` takes
    `(pattern, string)`. That asymmetry is go-cty's own, and this package
    matches it rather than tidying it.
    """

    def test_a_replacement_without_placeholders_is_literal(self) -> None:
        assert regexreplace(s("-ab-axxb-"), s("a(x*)b"), s("T")).value == "-T-T-"

    def test_a_braced_group_reference_expands(self) -> None:
        """go-cty's own test case for this function."""
        assert regexreplace(s("-ab-axxb-"), s("a(x*)b"), s("${1}W")).value == "-W-xxW-"

    def test_a_bare_dollar_reference_expands(self) -> None:
        assert regexreplace(s("-ab-axxb-"), s("a(x*)b"), s("$1")).value == "--xx-"

    def test_a_name_run_swallows_following_letters(self) -> None:
        """`$1W` is the group named "1W", not group 1 followed by "W" -- Go
        takes the longest run of letters, digits and underscores. No such group
        exists, so it expands to nothing. This is why go-cty's own test writes
        `${1}W`, and it is the case a naive translation gets wrong."""
        assert regexreplace(s("-ab-axxb-"), s("a(x*)b"), s("$1W")).value == "---"

    def test_a_backslash_reference_is_literal_text(self) -> None:
        """Python's `re.sub` would expand this. Go emits it verbatim."""
        assert regexreplace(s("-ab-axxb-"), s("a(x*)b"), s(r"\1W")).value == r"-\1W-\1W-"

    def test_a_doubled_dollar_is_one_literal_dollar(self) -> None:
        assert regexreplace(s("ab"), s("b"), s("$$")).value == "a$"

    def test_a_named_group_expands_by_name(self) -> None:
        assert regexreplace(s("abc"), s("(?P<mid>b)"), s("[${mid}]")).value == "a[b]c"

    def test_an_unknown_group_name_expands_to_nothing(self) -> None:
        """Not an error, and not left as literal text."""
        assert regexreplace(s("abc"), s("(b)"), s("${nope}")).value == "ac"

    def test_an_out_of_range_group_number_expands_to_nothing(self) -> None:
        assert regexreplace(s("abc"), s("(b)"), s("${9}")).value == "ac"

    def test_a_group_that_did_not_participate_expands_to_nothing(self) -> None:
        assert regexreplace(s("a"), s("(a)|(z)"), s("[$2]")).value == "[]"

    @pytest.mark.parametrize(
        ("replacement", "expected"),
        [
            ("$", "a$"),
            ("$}", "a$}"),
            ("${", "a${"),
            ("${1", "a${1"),
            ("${}", "a${}"),
        ],
        ids=["bare", "stray brace", "unclosed", "unclosed named", "empty name"],
    )
    def test_a_malformed_reference_is_emitted_as_a_literal_dollar(
        self, replacement: str, expected: str
    ) -> None:
        """Go's `extract` returns not-ok and `expand` writes a raw `$`, then
        carries on parsing from the next character."""
        assert regexreplace(s("ab"), s("b"), s(replacement)).value == expected

    def test_a_leading_zero_is_a_name_rather_than_a_number(self) -> None:
        """Go disallows leading zeros when reading a group number, and falls
        back to treating the run as a group *name*."""
        assert regexreplace(s("abc"), s("(b)"), s("${01}")).value == "ac"

    def test_an_invalid_pattern_is_refused(self) -> None:
        with pytest.raises(CtyFunctionError, match="regexreplace"):
            regexreplace(s("x"), s("("), s("y"))

    @pytest.mark.parametrize("index", [0, 1, 2])
    def test_an_unknown_argument_yields_unknown(self, index: int) -> None:
        args = [s("ab"), s("b"), s("c")]
        args[index] = CtyValue.unknown(CtyString())

        assert regexreplace(*args).is_unknown

    @pytest.mark.parametrize("index", [0, 1, 2])
    def test_a_null_argument_is_refused(self, index: int) -> None:
        """Was folded in with the unknown case above until 2026-08-17.

        The old docstring said go-cty raises "argument must not be null" here
        and that this was "left as unknown to move with the same deferred
        strictness change as `contains` and `length`". That change has now
        arrived for the whole module: `RegexReplaceFunc` declares three
        parameters with `AllowNull` unset (`stdlib/string_replace.go:47`), so
        the framework refuses a null before the body runs. An unknown is a value
        nobody knows yet; a null is one that is definitely absent, and treating
        them alike is what let a null reach a computation at all.
        """
        args = [s("ab"), s("b"), s("c")]
        args[index] = CtyValue.null(CtyString())

        with pytest.raises(CtyFunctionError):
            regexreplace(*args)


# 🌊🪢🔚
