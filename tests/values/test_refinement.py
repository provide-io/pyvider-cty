#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`refine()` — go-cty's `Value.Refine()` builder, and `safe_known_prefix`.

The data model was already here. What these cover is the part that makes it
trustworthy: a refinement is a *promise* about a value nobody knows yet, and
Terraform plans on it. A promise that contradicts the value produces a plan that
cannot apply, discovered at apply time by a practitioner rather than at refine
time by the provider — so the refusals below are the feature, not its edges.
"""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

import pytest

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtySet, CtyString, CtyValue, value_range
from pyvider.cty.marks import CtyMark
from pyvider.cty.refinement import CtyRefinementError, refine, safe_known_prefix
from pyvider.cty.values.equality import equals

S, N = CtyString(), CtyNumber()
LIST = CtyList(element_type=S)


class TestSafeKnownPrefix:
    def test_the_last_grapheme_is_dropped(self) -> None:
        """`"hello"` is not safe: the string could still turn out to be `"hellö"`.

        go-cty's own documentation uses that example. The `o` was never final,
        because a combining diacritic appended later changes it.
        """
        assert safe_known_prefix("hello") == "hell"

    def test_a_combining_sequence_is_dropped_whole(self) -> None:
        assert safe_known_prefix("hé") == "h"

    def test_an_emoji_cluster_is_dropped_whole(self) -> None:
        """Not by code point -- half a ZWJ sequence is not a prefix of anything."""
        assert safe_known_prefix("a\U0001f468‍\U0001f469") == "a"

    @pytest.mark.parametrize("text", ["", "a"], ids=["empty", "single"])
    def test_a_prefix_with_nothing_to_keep_is_empty(self, text: str) -> None:
        assert safe_known_prefix(text) == ""

    def test_a_trailing_delimiter_is_kept(self) -> None:
        """`"hi "` is safe whole: a space never combines with what follows.

        go-cty keeps a final grapheme cluster when it is a single code point
        from an allowlist of delimiters (`ctystrings/prefix.go:140`) -- built
        for exactly the `format("hi %s", unknown)` shape, where dropping the
        space weakens the promise for no safety gained. Until 2026-08-17 this
        package dropped the final cluster unconditionally: sound, but a
        strictly weaker refinement than go-cty's for the same value.
        """
        assert safe_known_prefix("hi ") == "hi "
        assert safe_known_prefix("a.") == "a."
        assert safe_known_prefix("x-") == "x-"
        assert safe_known_prefix('{"key": "') == '{"key": "'

    def test_a_lone_delimiter_is_kept(self) -> None:
        assert safe_known_prefix(" ") == " "

    def test_a_delimiter_with_a_combining_mark_is_dropped_whole(self) -> None:
        """The allowlist admits a *single-code-point* cluster only.

        A combining mark can attach to a space, and the result is one
        two-code-point cluster; go-cty's heuristic tests `RuneCountInString(s)
        != 1` before consulting the allowlist, so such a cluster stays unsafe.
        """
        assert safe_known_prefix("hi ́") == "hi"

    def test_a_non_delimiter_final_character_is_still_dropped(self) -> None:
        """A newline cannot be extended either, but it is not in go-cty's
        allowlist, and the allowlist is the contract: growing it here would
        promise more than go-cty promises for the same value."""
        assert safe_known_prefix("hi\n") == "hi"


class TestRecording:
    def test_bounds_are_recorded_on_an_unknown(self) -> None:
        refined = refine(CtyValue.unknown(N)).not_null().number_range_inclusive(1, 10).new_value()

        assert refined.is_unknown
        assert refined.value.number_lower_bound == (Decimal(1), True)
        assert refined.value.number_upper_bound == (Decimal(10), True)
        assert refined.value.is_known_null is False

    def test_refining_only_ever_narrows(self) -> None:
        """A widening bound is discarded rather than recorded.

        Refinement is monotonic in go-cty: later information may add certainty
        and may never remove it. Accepting a wider bound would let a caller
        un-learn something Terraform has already planned against.
        """
        refined = (
            refine(CtyValue.unknown(N)).number_range_lower_bound(5).number_range_lower_bound(1).new_value()
        )

        assert refined.value.number_lower_bound == (Decimal(5), True)

    def test_an_existing_refinement_is_carried_forward(self) -> None:
        once = refine(CtyValue.unknown(N)).number_range_lower_bound(1).new_value()

        twice = refine(once).number_range_upper_bound(10).new_value()

        assert twice.value.number_lower_bound == (Decimal(1), True)
        assert twice.value.number_upper_bound == (Decimal(10), True)

    def test_marks_survive_refinement(self) -> None:
        sensitive = CtyMark("sensitive")

        refined = refine(CtyValue.unknown(N).mark(sensitive)).not_null().new_value()

        assert sensitive in refined.marks


class TestCollapsingToKnown:
    """Refining hard enough produces a value that is no longer unknown."""

    def test_equal_inclusive_bounds_pin_the_number(self) -> None:
        refined = refine(CtyValue.unknown(N)).not_null().number_range_inclusive(5, 5).new_value()

        assert not refined.is_unknown
        assert refined.value == Decimal(5)

    def test_a_known_null_refinement_produces_the_null(self) -> None:
        """There is only one null of each type, so this is now fully known."""
        refined = refine(CtyValue.unknown(N)).null().new_value()

        assert refined.is_null
        assert not refined.is_unknown

    def test_a_zero_length_collection_is_the_empty_collection(self) -> None:
        refined = refine(CtyValue.unknown(LIST)).not_null().collection_length(0).new_value()

        assert not refined.is_unknown
        assert refined.value == ()

    def test_a_known_value_is_returned_untouched(self) -> None:
        """A refinement of a known value is a claim to check, not data to store."""
        known = N.validate(5)

        assert refine(known).not_null().number_range_inclusive(1, 10).new_value() is known


class TestRefusals:
    @pytest.mark.parametrize(
        ("label", "build"),
        [
            ("null then not-null", lambda: refine(CtyValue.unknown(N)).null().not_null()),
            ("not-null then null", lambda: refine(CtyValue.unknown(N)).not_null().null()),
            ("a null value is not non-null", lambda: refine(CtyValue.null(N)).not_null()),
            ("a known value is not null", lambda: refine(N.validate(1)).null()),
            (
                "lower above upper",
                lambda: refine(CtyValue.unknown(N)).number_range_lower_bound(10).number_range_upper_bound(1),
            ),
            (
                "length upper below lower",
                lambda: (
                    refine(CtyValue.unknown(LIST))
                    .collection_length_lower_bound(5)
                    .collection_length_upper_bound(2)
                ),
            ),
            ("bounds on a string", lambda: refine(CtyValue.unknown(S)).number_range_lower_bound(1)),
            ("prefix on a number", lambda: refine(CtyValue.unknown(N)).string_prefix("x")),
            ("length on a number", lambda: refine(CtyValue.unknown(N)).collection_length(1)),
            (
                "bound contradicting a known value",
                lambda: refine(N.validate(3)).number_range_lower_bound(10),
            ),
            (
                "length contradicting a known collection",
                lambda: refine(LIST.validate(["a"])).collection_length_lower_bound(5),
            ),
            (
                "prefix contradicting a known value",
                lambda: refine(S.validate("abc")).string_prefix_full("xyz"),
            ),
            (
                "prefix contradicting an earlier prefix",
                lambda: refine(CtyValue.unknown(S)).string_prefix_full("abc").string_prefix_full("xyz"),
            ),
        ],
        ids=lambda v: v if isinstance(v, str) else "",
    )
    def test_an_inconsistent_refinement_is_refused(self, label: str, build: Callable[[], object]) -> None:
        with pytest.raises(CtyRefinementError):
            build()

    def test_a_longer_consistent_prefix_wins(self) -> None:
        """Extending a prefix is narrowing, and narrowing is always allowed."""
        refined = refine(CtyValue.unknown(S)).string_prefix_full("ab").string_prefix_full("abc").new_value()

        assert refined.value.string_prefix == "abc"


@pytest.mark.parametrize("collection", [LIST, CtySet(element_type=S), CtyMap(element_type=S)], ids=str)
def test_every_collection_kind_accepts_length_bounds(collection: object) -> None:
    refined = refine(CtyValue.unknown(collection)).collection_length_lower_bound(2).new_value()

    assert refined.value.collection_length_lower_bound == 2


class TestValueRange:
    """`value_range()` — the read side, and where `equals` gets its sharpness."""

    def test_a_known_value_ranges_over_itself(self) -> None:
        """So a caller can ask the same questions of known and unknown alike."""
        known = value_range(N.validate(5))

        assert known.number_lower_bound() == (N.validate(5), True)
        assert known.number_upper_bound() == (N.validate(5), True)
        assert known.includes(N.validate(6)).value is False
        assert known.definitely_not_null()

    def test_even_a_known_value_does_not_confirm_membership(self) -> None:
        """It looks like it should answer `True`, and go-cty answers "cannot say".

        This asserted `True` until a harness could ask real go-cty, which is the
        whole reason the assertion survived: it described what this library did.
        go-cty builds a *synthetic* range for a known value -- for a number,
        bounds of exactly 5 to 5 -- and `Includes` never concludes from bounds
        that a candidate is the value, only that it is not. Its own docstring
        says the rules "focus mainly on answering false".

        Answering `True` here is more useful and still a divergence: a caller
        porting a comparison between the two implementations would get a
        different answer for the same values.
        """
        assert value_range(N.validate(5)).includes(N.validate(5)).is_unknown

    def test_bounds_exclude_definitely(self) -> None:
        refined = value_range(refine(CtyValue.unknown(N)).not_null().number_range_inclusive(1, 10).new_value())

        assert refined.includes(N.validate(50)).value is False
        assert refined.includes(CtyValue.null(N)).value is False

    def test_being_within_the_bounds_is_not_equality(self) -> None:
        """The distinction the whole three-valued answer exists for.

        A candidate that passes every bound has only failed to be ruled out.
        Answering `True` would claim the unknown *is* that value.
        """
        refined = value_range(refine(CtyValue.unknown(N)).not_null().number_range_inclusive(1, 10).new_value())

        assert refined.includes(N.validate(5)).is_unknown

    def test_an_unrefined_unknown_decides_nothing(self) -> None:
        assert value_range(CtyValue.unknown(N)).includes(N.validate(5)).is_unknown
        assert value_range(CtyValue.unknown(N)).could_be_null()

    def test_a_prefix_excludes_a_non_matching_string(self) -> None:
        ranged = value_range(refine(CtyValue.unknown(S)).string_prefix_full("abc").new_value())

        assert ranged.includes(S.validate("xyz")).value is False
        assert ranged.includes(S.validate("abcd")).is_unknown

    def test_a_length_bound_excludes_a_wrong_length(self) -> None:
        ranged = value_range(refine(CtyValue.unknown(LIST)).collection_length_lower_bound(3).new_value())

        assert ranged.includes(LIST.validate(["a"])).value is False
        assert ranged.includes(LIST.validate(["a", "b", "c"])).is_unknown

    def test_asking_a_type_inappropriate_question_raises(self) -> None:
        with pytest.raises(TypeError):
            value_range(CtyValue.unknown(N)).string_prefix()
        with pytest.raises(TypeError):
            value_range(CtyValue.unknown(S)).number_lower_bound()


class TestEqualsConsultsTheRange:
    """The concrete payoff, and the reason `Value.Range` was worth porting.

    `equality.py` recorded this as deliberately unimplemented: go-cty rules some
    comparisons out from an unknown's bounds and pyvider could not, so everything
    fell through to unknown.
    """

    def test_a_refined_unknown_is_definitely_not_an_excluded_value(self) -> None:
        refined = refine(CtyValue.unknown(N)).not_null().number_range_inclusive(1, 10).new_value()

        assert equals(refined, N.validate(50)).value is False

    def test_a_candidate_within_the_bounds_stays_undecided(self) -> None:
        refined = refine(CtyValue.unknown(N)).not_null().number_range_inclusive(1, 10).new_value()

        assert equals(refined, N.validate(5)).is_unknown

    def test_an_unrefined_unknown_is_still_undecided(self) -> None:
        """The previous behaviour, preserved wherever the range cannot decide."""
        assert equals(CtyValue.unknown(N), N.validate(5)).is_unknown

    def test_a_prefix_rules_out_a_non_matching_string(self) -> None:
        refined = refine(CtyValue.unknown(S)).string_prefix_full("abc").new_value()

        assert equals(refined, S.validate("xyz")).value is False


# 🌊🪢🔚
