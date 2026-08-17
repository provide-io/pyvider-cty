#
# SPDX-FileCopyrightText: Copyright (c) 2013-2024 Masaaki Shibata
# SPDX-License-Identifier: MIT
#

"""Unicode 16.0.0 character properties for grapheme cluster breaking.

GENERATED FILE -- do not edit. Regenerate with
`scripts/generate_grapheme_tables.py`.

Derived from `uniseg` (https://bitbucket.org/emptypage/uniseg-py), MIT licensed,
by reprojecting its thirty-column property table onto the three columns UAX#29
grapheme clustering needs. The values are the Unicode Character Database's, so
this table says what the UCD says; the copyright above covers the derivation.

Vendored rather than depended upon because `uniseg`'s wheel is 8 MB, of which
10.2 MB uncompressed is bundled Sphinx documentation and webfonts -- for 262 KB
of code, of which this package uses two modules. The reprojected table below is
4 KB and has been verified equal to `uniseg`'s at every one of the 1,114,112
code points.
"""

from __future__ import annotations

import base64
import zlib

UNICODE_VERSION = "16.0.0"
"""The UCD version these tables were generated from.

go-cty does not pin its own: `cty/internal/graphemes` selects `go-textseg` v15
or v17 by Go toolchain version, so its Unicode version follows whichever
compiler built the binary. Exact agreement is therefore not available in either
direction; what is available is knowing our version, which is what this is for.
"""

SHIFT = 7
"""Low-bit width of the two-stage lookup. Chosen to minimise total entries."""

# Grapheme_Cluster_Break property values.
GCB_OTHER = 0
GCB_CR = 1
GCB_LF = 2
GCB_CONTROL = 3
GCB_EXTEND = 4
GCB_ZWJ = 5
GCB_REGIONAL_INDICATOR = 6
GCB_PREPEND = 7
GCB_SPACINGMARK = 8
GCB_L = 9
GCB_V = 10
GCB_T = 11
GCB_LV = 12
GCB_LVT = 13

# Indic_Conjunct_Break property values, for GB9c.
INCB_NONE = 0
INCB_CONSONANT = 1
INCB_EXTEND = 2
INCB_LINKER = 3

ROWS: tuple[tuple[int, int, bool], ...] = (
    (0, 0, False),
    (0, 0, True),
    (0, 1, False),
    (1, 0, False),
    (2, 0, False),
    (3, 0, False),
    (4, 0, False),
    (4, 2, False),
    (4, 3, False),
    (5, 2, False),
    (6, 0, False),
    (7, 0, False),
    (8, 0, False),
    (9, 0, False),
    (10, 0, False),
    (11, 0, False),
    (12, 0, False),
    (13, 0, False),
)
"""(Grapheme_Cluster_Break, InCB, Extended_Pictographic) per distinct row."""

_INDEX1 = zlib.decompress(
    base64.b85decode(
        b"c-rmKRZjyj6a`>7xVyW%ySux)ySuwfaUc9yy752;3E9I)$T(lp+vc=MCDqf1WB?e#$k@cx%-q7#%G$=(&fdY%$=Su#&E3P(3-HDVA74NJ00agFhlGY9T$w~fMnwZLv4}%_LSj-fkRsDmAT2#ZIiHy&OE&(6oLnF;zo4+F7$v1;<rS4x)!OcAv~$v0RjsQ>gX|j7)T}n!(yFX&Kzm1LS9ecuU;n`1&@e_u$Hp;%$*JiXV0LbP0gFo-@3{PHufFm<T3wT6UAB$QKl@p>G+DGQ+s^LZmvsN&b9{It?|Li;Cpc9FXXk2bg}Au965?8j8*wY{?jIhXgb>PH<rzdoL_|bHL_|bHM5J?G6t8cJAMk~Uh;-9CDK?_v"
    )
)
_INDEX2 = zlib.decompress(
    base64.b85decode(
        b"c-rk;345L(42ExW>1KBQ|35qB6b#B0uwBzWy;PFCIe-wmESA15%a`Ruf|r&%a(Bx8ZYe$*!C*>@@E!pX+lT(FWw$CK*^8xv<fofPg18DRghDC9#_OGcWv<2G6deY+H-`2t?`8J4GH!MLn2@zPaMrsZ!qZT%90CM^h;EdP-Vm)A_Acdm1i9<mgIWBA`)+R7%?Fyl5c?n-|Io7f=8*sXTo8?v{<(;2{WbX3;<xb=-II&I*Wdi;_-pUPK>wH{VF2sf*uZ~dOW|+)mcn1WdS=9py%K-JL19roC<KpX=>Ix+wlIEg6NJ}ayqu%m#4v?_zW;$n0K)tZaAkiCy#p)b{{=q&4E}E`fj^)Agdb^vbYvi9TJ5S$Y>-IJFl-U!`A1gn%l~pHweG6KGMamA`Z`VXMT^-%i&rnPN`06F$xjPFE-g+5rPUaq)=y^o)ro#H5x2k8Ia$k~0HW!7j)Ztv^r<xK*Maq6xjnhe*@fmnGHHKoKvrK(W-*X6Z@9?0Gn3Fch@L1QaF?T_KuvV?+=J2^pj;V>3_%Kc%N;eJw&@+T1KH`e)SMU^?qcG5LitD#D-1IoyHM_?LC1RB^6h)N-b$5YW%8GFfpvQMu6RUQ^yeNV6`lS#*psCkq;Ajg<qfC~S=kLwIl&&X2X_U9K|~(mk;92J(@_3_{uWi~0hSk$D9vT_oE{=lsnjwl1Iszi$D4|1e5%;UX{c~k<r%9vljq~ok%mo5a}6cM$2)3v#f5z9_csE4A_`Zrpmx7p!BSHV#)z&^x{0{Ltz!<GaNmAeoHO->;?1PnlV%nPpj#p{Oo1G|RFfL9^kJ|sSQiX}?yLoe<~CiP+fQf+wtxPn>GRs>wa;t3*K+PT#%tnuWWU64_5ni{B$xeC<C=_S&@y`cHL@1?0QVBlbeMxHN5|iV8`<{}4~=fzCGOj^NB3atm(N;Hz~;FIR<_^OP74s)v3UD~e)F?;%Z4GivK6F)qbz9K#Fm{uCLyq!%|pj3^TtLqwk@C5n$OOB2e1-`t?oxt{dc<m(DYxDofrEhFF~(Gls}RN+X$%&HLwDI9WOeIhNRm8he569>+|%nXW@s2XS`+35B*T(;n-$0isP~AZ+0>X6E93lXsX#)1GD0a&&t4PBgAy)h^XN?y^tuZM6SnYfT&Yu52)Wkin~@GIiF$Jp37nT#5omuWTt}SXHwyhQda2VxT=$1)oVXmog=yA*;7bGLEG5iD$IBwjQgpeZ97sB3+z3gqbnaRh`cA2_u{Or(ejtOu#Py30Z_Xp-QU4wu2YtFYmR^SwPVm}SzYRim3nfWsJVjD#r}c4>zjQcYo;RKgJSZ3k#==a@$z$*RPjV#YsPwZ8kilcW0vPI9M@W&ax%rj+=<(Q)0v|@x6>v>YXj>?l0>=_I-!5qr~Md1mXq%1?BYGoQR+Qx2-xMV#H&S~)SCqL&yUHL4Wo;xuWWSE{_g*8asNN6Wir8kMzQ|?0L5dj!~"
    )
)


def properties(codepoint: int, /) -> tuple[int, int, bool]:
    """Return `(gcb, incb, extended_pictographic)` for a code point."""
    block = _INDEX1[codepoint >> SHIFT]
    return ROWS[_INDEX2[(block << SHIFT) + (codepoint & ((1 << SHIFT) - 1))]]


# 🌊🪢🔚
