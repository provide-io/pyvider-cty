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

from pyvider.cty import CtyList, CtyMap, CtyNumber, CtySet, CtyString, CtyValue
from pyvider.cty.marks import CtyMark
from pyvider.cty.refinement import CtyRefinementError, refine, safe_known_prefix

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


# 🌊🪢🔚
