#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`regex` and `regexall` must answer what go-cty answers.

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
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import CtyNumber, CtyObject, CtyString, CtyTuple, CtyValue
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import regex, regexall


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

    def test_a_group_that_did_not_participate_is_null(self) -> None:
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
        [
            (CtyValue.null(CtyString()), s("abc")),
            (s("a"), CtyValue.null(CtyString())),
            (CtyValue.unknown(CtyString()), s("abc")),
            (s("a"), CtyValue.unknown(CtyString())),
        ],
    )
    def test_a_null_or_unknown_argument_yields_unknown(
        self, pattern: CtyValue[Any], subject: CtyValue[Any]
    ) -> None:
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
        [
            (CtyValue.null(CtyString()), s("abc")),
            (s("a"), CtyValue.null(CtyString())),
            (CtyValue.unknown(CtyString()), s("abc")),
            (s("a"), CtyValue.unknown(CtyString())),
        ],
    )
    def test_a_null_or_unknown_argument_yields_unknown(
        self, pattern: CtyValue[Any], subject: CtyValue[Any]
    ) -> None:
        assert regexall(pattern, subject).is_unknown


# 🌊🪢🔚
