#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Case mapping answers from the vendored Go tables, whatever Python runs it.

`upper`, `lower` and `title` used to consult a table only where Python's *full*
mapping differed from Go's *simple* one, and ask `str.upper()` and friends for
everything else. That made the answer depend on the running interpreter's
`unicodedata`: 14.0 on 3.11, 15.0 on 3.12, 15.1 on 3.13, 16.0 on 3.14. None of
them is Go 1.27's 17.0.0, so a letter paired in Unicode 16 or 17 was left alone
on every supported Python.

Each case below is a mapping Unicode added after 14.0, so all of them fail on
every interpreter this package supports if Python is consulted at all.
"""

from __future__ import annotations

import unicodedata

import pytest

from pyvider.cty import CtyString
from pyvider.cty._unicode._case_tables import UNICODE_VERSION
from pyvider.cty._unicode.case import simple_lower, simple_title_char, simple_upper
from pyvider.cty.functions import title

# (added in, function, input, Go 1.27's answer)
LATE_MAPPINGS = [
    ("16.0", simple_upper, "ƛ", "Ƛ"),  # LAMBDA WITH STROKE
    ("16.0", simple_upper, "ɤ", "Ɤ"),  # RAMS HORN
    ("16.0", simple_lower, "\U00010d50", "\U00010d70"),  # GARAY CAPITAL A
    ("16.0", simple_upper, "\U00010d70", "\U00010d50"),  # GARAY SMALL A
    ("17.0", simple_lower, "꟎", "꟏"),  # LATIN CAPITAL PHARYNGEAL VOICED FRICATIVE
    ("17.0", simple_upper, "꟏", "꟎"),
    ("17.0", simple_lower, "\U00016ea0", "\U00016ebb"),  # BERIA ERFE CAPITAL
    ("17.0", simple_upper, "\U00016ebb", "\U00016ea0"),
]


def test_the_tables_are_go_1_27s() -> None:
    assert UNICODE_VERSION == "17.0.0"


@pytest.mark.parametrize(
    ("added", "function", "text", "expected"),
    LATE_MAPPINGS,
    ids=[f"{added}-{function.__name__}-U+{ord(text):04X}" for added, function, text, _ in LATE_MAPPINGS],
)
def test_a_mapping_newer_than_the_interpreter_is_still_applied(
    added: str, function: object, text: str, expected: str
) -> None:
    assert callable(function)
    # Inside a string too, where ASCII neighbours must not route it to a fast path.
    assert function(text) == expected, (
        f"Unicode {added} mapping; interpreter has {unicodedata.unidata_version}"
    )
    assert function(f"a{text}b") == f"{function('a')}{expected}{function('b')}"


def test_title_uses_the_table_for_a_late_letter() -> None:
    assert simple_title_char("ƛ") == "Ƛ"
    assert simple_title_char("꟏") == "꟎"


def test_title_starts_a_word_after_go_s_separators_only() -> None:
    """Above ASCII, `strings.Title` starts a word after `unicode.IsSpace` only."""
    assert title(CtyString().validate("\u3000a\u00a0b\u2003c")).value == "\u3000A\u00a0B\u2003C"
    # Punctuation, a symbol and a Unicode 17 letter do not start a word.
    assert title(CtyString().validate("\u00bfa\u2014b\ua7cfc")).value == "\u00bfa\u2014b\ua7cfc"


def test_an_unmapped_character_is_itself() -> None:
    for character in ("一", "\U0001f600", "1", " ", "ß"):
        assert simple_upper(character) == character
        assert simple_lower(character) == character
        assert simple_title_char(character) == character


# 🌊🪢🔚
