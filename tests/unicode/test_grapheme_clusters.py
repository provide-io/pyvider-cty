#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The vendored UAX#29 segmentation, tested where it is decided rather than used.

The stdlib sweep already compares `strlen`, `strrev`, `substr` and `format`
against go-cty. This covers the layer underneath: the individual break rules,
each with a string chosen because it exercises that rule and nothing else, so a
regression names the rule it broke instead of naming four functions.

The rule numbers are UAX#29's.
"""

from __future__ import annotations

import pytest

from pyvider.cty._unicode import cluster_count, iter_clusters
from pyvider.cty._unicode._grapheme_tables import UNICODE_VERSION

# The version the checked-in tables were generated from. This is asserted rather
# than read, so regenerating against a newer UCD fails here and forces a
# deliberate decision -- the drift is otherwise invisible, and it changes
# answers: GB9c arrived in 15.1 and made `क्ष` one character instead of two.
EXPECTED_UNICODE_VERSION = "16.0.0"


def test_the_table_version_is_the_one_we_think_it_is() -> None:
    assert UNICODE_VERSION == EXPECTED_UNICODE_VERSION


@pytest.mark.parametrize(
    ("rule", "text", "expected"),
    [
        ("GB1/GB2 empty", "", []),
        ("GB3 CRLF is one cluster", "\r\n", ["\r\n"]),
        ("GB4 control stands alone", "a\rb", ["a", "\r", "b"]),
        ("GB5 LF stands alone", "\n\n", ["\n", "\n"]),
        ("GB6/GB7/GB8 hangul jamo compose", "각", ["각"]),
        ("GB9 combining mark attaches", "g̈", ["g̈"]),
        ("GB9 skin tone attaches", "\U0001f44d\U0001f3fd", ["\U0001f44d\U0001f3fd"]),
        ("GB9a spacing mark attaches", "நி", ["நி"]),
        (
            "GB11 ZWJ emoji sequence is one cluster",
            "\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466",
            ["\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466"],
        ),
        (
            "GB12/GB13 regional indicators pair into flags",
            "\U0001f1fa\U0001f1f8\U0001f1ef\U0001f1f5",
            ["\U0001f1fa\U0001f1f8", "\U0001f1ef\U0001f1f5"],
        ),
        (
            "GB12/GB13 an odd indicator stands alone",
            "\U0001f1fa\U0001f1f8\U0001f1ef",
            ["\U0001f1fa\U0001f1f8", "\U0001f1ef"],
        ),
        ("GB9c indic conjunct holds together", "क्ष", ["क्ष"]),
        ("GB999 otherwise break", "abc", ["a", "b", "c"]),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_each_break_rule(rule: str, text: str, expected: list[str]) -> None:
    assert list(iter_clusters(text)) == expected, rule


def test_a_zwj_that_does_not_follow_an_emoji_does_not_join() -> None:
    """GB11 requires ExtPict before the ZWJ, so a bare joiner is not a licence.

    A flag implemented as "no break after any ZWJ" passes every emoji test and
    is still wrong here, which is why this case exists separately.
    """
    assert list(iter_clusters("a‍b")) == ["a‍", "b"]


def test_an_emoji_sequence_broken_by_a_letter_does_not_rejoin() -> None:
    """The ExtPict Extend* ZWJ run has to be contiguous."""
    assert list(iter_clusters("\U0001f468x‍\U0001f469")) == [
        "\U0001f468",
        "x‍",
        "\U0001f469",
    ]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", 0),
        ("abc", 3),
        ("\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466", 1),
        ("ab\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466cd", 5),
        ("\U0001f1fa\U0001f1f8\U0001f1ef\U0001f1f5", 2),
    ],
    ids=str,
)
def test_cluster_count(text: str, expected: int) -> None:
    assert cluster_count(text) == expected


def test_clusters_reassemble_into_the_original() -> None:
    """Segmentation must partition, not merely split.

    Cheap to state and the strongest single invariant available: any rule that
    drops or duplicates a code point fails here regardless of where it broke.
    """
    for text in (
        "",
        "abc",
        "\r\n\r\n",
        "\U0001f468‍\U0001f469ẍ\U0001f1fa\U0001f1f8क्ष가",
    ):
        assert "".join(iter_clusters(text)) == text


# 🌊🪢🔚
