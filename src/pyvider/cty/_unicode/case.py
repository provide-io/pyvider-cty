#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Unicode's *simple* case mapping, which is the one go-cty answers with.

`strings.ToUpper`, `strings.ToLower` and `strings.Title` map one rune to one
rune through `UnicodeData.txt`'s simple case mapping fields. Python's
`str.upper()`, `str.lower()` and `str.title()` apply `SpecialCasing.txt`'s
*full* mapping instead, which can make a string longer and carries
context-sensitive rules Go does not implement at all. Four consequences, every
one of them a wrong answer for `upper`, `lower` and `title` rather than a
stylistic difference:

    upper("straße")  go-cty "STRAßE"  Python "STRASSE"
    upper("ﬁ")       go-cty "ﬁ"       Python "FI"
    lower("ΣΣ")  go-cty two sigmas, Python sigma then *final* sigma
    lower("İ")       go-cty "i"       Python "i̇"    (U+0130 keeps its dot above)

The first two lengthen the string, so a `substr` or `strlen` downstream of an
`upper` disagreed about the character count as well as the characters. The third
depends on where in the string the letter sits, so the same character mapped two
ways in one call. None of it was caught because the differential sweep's only
case-mapping inputs were `héllo` and `HÉLLO`, which are NFC-composed and map
one-to-one either way.

Python exposes no simple mapping, so the disagreement is vendored as a table --
see `_case_tables.py` for where it comes from and how it was checked.
"""

from __future__ import annotations

from pyvider.cty._unicode._case_tables import SIMPLE_LOWER, SIMPLE_TITLE, SIMPLE_UPPER

__all__ = ["simple_lower", "simple_title_char", "simple_upper"]


def _mapped(text: str, exceptions: dict[int, int], method: str) -> str:
    """`text` with every character mapped one code point at a time.

    Per character rather than per string on purpose, twice over: it is what
    `strings.Map` does, and it is what takes the final-sigma rule out of play,
    since Python only applies that rule when it can see a following character.
    """
    return "".join(
        chr(mapped) if (mapped := exceptions.get(ord(character))) is not None else getattr(character, method)()
        for character in text
    )


def simple_upper(text: str, /) -> str:
    """go-cty's `strings.ToUpper`: simple uppercase, one rune at a time."""
    if text.isascii():
        # No ASCII code point has a special casing, so Python's own answer is
        # already the simple one -- and this is the overwhelmingly common input.
        return text.upper()
    return _mapped(text, SIMPLE_UPPER, "upper")


def simple_lower(text: str, /) -> str:
    """go-cty's `strings.ToLower`: simple lowercase, one rune at a time."""
    if text.isascii():
        return text.lower()
    return _mapped(text, SIMPLE_LOWER, "lower")


def simple_title_char(character: str, /) -> str:
    """One character's simple titlecase. go-cty's `unicode.ToTitle`.

    A single character rather than a string because titlecasing a string is not
    a mapping of every character -- `strings.Title` titlecases only the first
    character of each word and leaves the rest exactly as they were, which is
    why `title("HELLO world")` is `"HELLO World"` and not `"Hello World"`.
    """
    mapped = SIMPLE_TITLE.get(ord(character))
    return chr(mapped) if mapped is not None else character.title()


# 🌊🪢🔚
