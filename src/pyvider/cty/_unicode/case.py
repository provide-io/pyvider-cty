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

Python exposes no simple mapping, so Go's is vendored whole -- see
`_case_tables.py`. Every non-ASCII character is answered from that table and
never from Python's own methods: those follow the *running* interpreter's
`unicodedata` (14.0 on Python 3.11, 16.0 on 3.14), so deferring to them for
characters the table did not list made the answer depend on the interpreter and
left every Unicode 16 and 17 case pair unmapped.
"""

from __future__ import annotations

from pyvider.cty._unicode._case_tables import SIMPLE_LOWER, SIMPLE_TITLE, SIMPLE_UPPER

__all__ = ["simple_lower", "simple_title_char", "simple_upper"]


def _mapped(text: str, table: dict[int, int]) -> str:
    """`text` with every character mapped one code point at a time.

    Per character rather than per string on purpose, twice over: it is what
    `strings.Map` does, and it leaves no room for a context-sensitive rule such
    as final sigma. A character absent from the table maps to itself.
    """
    return "".join(chr(table.get(codepoint, codepoint)) for codepoint in map(ord, text))


def simple_upper(text: str, /) -> str:
    """go-cty's `strings.ToUpper`: simple uppercase, one rune at a time."""
    if text.isascii():
        # ASCII case mapping is the same at every Unicode version and has no
        # special casing, so Python's answer is Go's -- and this is the
        # overwhelmingly common input.
        return text.upper()
    return _mapped(text, SIMPLE_UPPER)


def simple_lower(text: str, /) -> str:
    """go-cty's `strings.ToLower`: simple lowercase, one rune at a time."""
    if text.isascii():
        return text.lower()
    return _mapped(text, SIMPLE_LOWER)


def simple_title_char(character: str, /) -> str:
    """One character's simple titlecase. go-cty's `unicode.ToTitle`.

    A single character rather than a string because titlecasing a string is not
    a mapping of every character -- `strings.Title` titlecases only the first
    character of each word and leaves the rest exactly as they were, which is
    why `title("HELLO world")` is `"HELLO World"` and not `"Hello World"`.
    """
    codepoint = ord(character)
    return chr(SIMPLE_TITLE.get(codepoint, codepoint))


# 🌊🪢🔚
