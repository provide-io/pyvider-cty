#
# SPDX-FileCopyrightText: Copyright (c) 2013-2024 Masaaki Shibata
# SPDX-License-Identifier: MIT
#

"""UAX#29 extended grapheme cluster segmentation.

A "character" as a user perceives it is a grapheme cluster, not a code point:
`\\U0001F468\\u200D\\U0001F469\\u200D\\U0001F467\\u200D\\U0001F466` is seven code
points and one character, and `\\u0067\\u0308` is two and one. go-cty measures in
grapheme clusters wherever a count or an index is user-facing -- `strlen`,
`reverse`, `substr`, and `format`'s width and precision -- via
`cty/internal/graphemes`, a one-function shim over `go-textseg`. This module is
that shim's counterpart, and exists so the four call sites here share one
implementation rather than four loops that each guess.

Ported from `uniseg`'s `graphemecluster.py` (MIT, see LICENSES/MIT.txt): the
rules and their ordering are its, restructured from its generic `Run` lookaround
framework into a single forward pass, since only the grapheme algorithm is
needed and none of the tailoring is. Verified against `uniseg` itself over an
exhaustive corpus, and against go-cty through the oracle.

Rule numbers below are UAX#29's (revision 45, Unicode 16.0.0).
"""

from __future__ import annotations

from collections.abc import Iterator

from pyvider.cty._unicode._grapheme_tables import (
    GCB_CONTROL,
    GCB_CR,
    GCB_EXTEND,
    GCB_L,
    GCB_LF,
    GCB_LV,
    GCB_LVT,
    GCB_PREPEND,
    GCB_REGIONAL_INDICATOR,
    GCB_SPACINGMARK,
    GCB_T,
    GCB_V,
    GCB_ZWJ,
    INCB_CONSONANT,
    INCB_EXTEND,
    INCB_LINKER,
    properties,
)

__all__ = ["cluster_count", "iter_clusters"]

_CONTROLS = frozenset({GCB_CONTROL, GCB_CR, GCB_LF})
_HANGUL_AFTER_L = frozenset({GCB_L, GCB_V, GCB_LV, GCB_LVT})
_HANGUL_AFTER_LV_V = frozenset({GCB_V, GCB_T})


class _Scanner:
    """The backwards context GB9c, GB11 and GB12/GB13 need.

    Each of those rules matches a run rather than a pair, but none needs more
    than two booleans and a count to recognise -- which is why a single forward
    pass suffices and `uniseg`'s general lookaround machinery does not have to
    come along.
    """

    __slots__ = ("conjunct", "consonant", "pictographic", "pictographic_zwj", "regionals")

    def __init__(self) -> None:
        # GB12/GB13: regional indicators join pairwise into flags, so the
        # decision depends on how many uninterrupted ones precede.
        self.regionals = 0
        # GB11: `pictographic` marks a trailing ExtPict Extend* run, and
        # `pictographic_zwj` that the run has since been closed by a ZWJ.
        self.pictographic = False
        self.pictographic_zwj = False
        # GB9c: `consonant` marks a trailing Consonant [Extend Linker]* run, and
        # `conjunct` that a Linker has appeared within it.
        self.consonant = False
        self.conjunct = False

    def consume(self, gcb: int, incb: int, pictographic: bool) -> None:
        self.regionals = self.regionals + 1 if gcb == GCB_REGIONAL_INDICATOR else 0

        if pictographic:
            self.pictographic, self.pictographic_zwj = True, False
        elif gcb == GCB_EXTEND and self.pictographic:
            pass  # Extend continues the run without closing it.
        elif gcb == GCB_ZWJ and self.pictographic:
            self.pictographic, self.pictographic_zwj = False, True
        else:
            self.pictographic, self.pictographic_zwj = False, False

        if incb == INCB_CONSONANT:
            self.consonant, self.conjunct = True, False
        elif incb == INCB_LINKER:
            self.conjunct = self.consonant
        elif incb != INCB_EXTEND:
            self.consonant, self.conjunct = False, False


def _breaks_before(previous_gcb: int, current: tuple[int, int, bool], state: _Scanner) -> bool:
    """Whether a cluster boundary falls immediately before `current`."""
    current_gcb, current_incb, current_pictographic = current

    # GB3: CR x LF -- a CRLF pair is one cluster.
    if previous_gcb == GCB_CR and current_gcb == GCB_LF:
        return False
    # GB4, GB5: a control stands alone on both sides.
    if previous_gcb in _CONTROLS or current_gcb in _CONTROLS:
        return True
    # GB6, GB7, GB8: Hangul jamo compose into syllables.
    if (
        (previous_gcb == GCB_L and current_gcb in _HANGUL_AFTER_L)
        or (previous_gcb in (GCB_LV, GCB_V) and current_gcb in _HANGUL_AFTER_LV_V)
        or (previous_gcb in (GCB_LVT, GCB_T) and current_gcb == GCB_T)
    ):
        return False
    # GB9: never break before a combining mark or a zero-width joiner.
    if current_gcb in (GCB_EXTEND, GCB_ZWJ):
        return False
    # GB9a, GB9b.
    if current_gcb == GCB_SPACINGMARK or previous_gcb == GCB_PREPEND:
        return False
    # GB9c: an Indic conjunct holds together across its virama.
    if state.conjunct and current_incb == INCB_CONSONANT:
        return False
    # GB11: ExtPict Extend* ZWJ x ExtPict -- what keeps an emoji ZWJ sequence,
    # a family or a profession, one character rather than the several it is
    # spelled with.
    if state.pictographic_zwj and current_pictographic:
        return False
    # GB12, GB13: flags pair up, so break only when an even number precedes.
    if current_gcb == GCB_REGIONAL_INDICATOR:
        return state.regionals % 2 == 0
    # GB999.
    return True


def iter_clusters(text: str, /) -> Iterator[str]:
    """Yield each extended grapheme cluster of `text`, in order."""
    if not text:
        return

    state = _Scanner()
    first = properties(ord(text[0]))
    state.consume(*first)
    previous_gcb = first[0]
    start = 0

    for index in range(1, len(text)):
        current = properties(ord(text[index]))
        if _breaks_before(previous_gcb, current, state):
            yield text[start:index]
            start = index
        state.consume(*current)
        previous_gcb = current[0]

    yield text[start:]


def cluster_count(text: str, /) -> int:
    """Number of extended grapheme clusters in `text`.

    This is what go-cty's `strlen` returns, and what Terraform's `length`
    reports for a string.
    """
    return sum(1 for _ in iter_clusters(text))


# 🌊🪢🔚
