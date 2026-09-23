#
# SPDX-FileCopyrightText: Copyright (c) 1991-2025 Unicode, Inc.
# SPDX-License-Identifier: Unicode-3.0
#

"""Unicode 17.0.0 character properties for grapheme cluster breaking.

GENERATED FILE -- do not edit. Regenerate with
`scripts/generate_grapheme_tables.py`.

Derived from the Unicode Character Database (see LICENSES/Unicode-3.0.txt):
`Grapheme_Cluster_Break`, `InCB` and `Extended_Pictographic`, the three
properties UAX#29 grapheme clustering needs, packed into a two-stage lookup.
The values are the UCD's, so this table says what the UCD says.

Vendored rather than read at runtime so that nothing here needs the UCD files
or a network. Python's `unicodedata` exposes none of these three properties.
"""

from __future__ import annotations

import base64
import zlib

UNICODE_VERSION = "17.0.0"
"""The UCD version these tables were generated from.

go-cty does not pin its own: `cty/internal/graphemes` selects `go-textseg` v15
(Unicode 15.0) below Go 1.27 and v17 (Unicode 17.0) at or above it, so its
Unicode version follows whichever compiler built the binary. OpenTofu 1.13 is
built with Go 1.27, so this follows v17; a go-cty built with an older Go still
answers from 15.0.
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
        b"c-rmKRZE3I5C&j<?e6aG?(XjH?(XjH`s}Vh>K?ri6~v1p$nkw(XO`K44OU4Rf(oDtHFXV5Eo~iLJ$(a1BV!X&Gjj_|D{C8DJHQ@q92}jTUEu2G?&0YLZ&}61*Uuja2t*KqLqfyCfe2BJ1frs2Wb3hUBE;igNJs>dl2cOC(vgvwm7SBDmoM*BAfJ;KzQ&?rl!#P{vhokB6_v7B1ytA6*3~yOHZ`}jwzZ?9v#T3D=<Vwt7{t)<$SB6ff4t+wuf6)@*V5Fq2s2{L&i&cXGXImN1u+(vmOoWjR^R7q>*B5(VzP-XY>T|J`=NJl|KRXQIzEw3&(1F{admxjE8R(e^yVH!L_|bHL_|bHL`0-;9v+{bAHTsDA|g^uFYceEH2"
    )
)
_INDEX2 = zlib.decompress(
    base64.b85decode(
        b"c-rk8i*}th%x0rvLu<SL|Ji}%H#RnYa<iy8O>zP2ElaY<x+?f{UH@1w!1}_P0(~bx@8;~Q0StyX37;qscKoBSQgpk3AbPeop!{;vNFnY_5h0|Mq2oP8;4{<eU=$4&Nh^bF%UGHE?HRT*dyLRp>^OVMiSV-2k^_Li5K*skz=o*EP<IK_3xK|UJeY-_>F@G}Q++`A89Ns_@VlC&n_c|pbB;HL_|KI%@lV268c+I<cTcYT4gc~-ji0O&9sYfc0R<@A#tQrg+K~LE-G=1PmX;CmKrhHY<RE16d{J;7%iw>pESpKYR{_HC&lYWH2_Fv0Ki~d<Bmi!F2e{Key4Hb({=b0nKPmrh56HhC{{cH9g2*#4q*^l7Dl`}f%`hy9GWb0$x5a<El*qdZW$EobDtukG`A5lYIp0e@5PeemY!jxogx3?7gp0spZ#wi5xNgKyapEsGz?}Z+3_lyeuTIcA4KGVmYZe7~;@L|9XeR(vVb<h<u$8*y@$5RM3e8c|r21G2S^Q5CR|>s%!6o<368l(C8wlGd$F|MIj^9wXeWW*tRDo(0Kq^XS*uTxtVew{%cvgRspi{CGc!XntgCdF0$&*E*i$zI-_HxbjYq~|j=orW_WR<2}xfury`*G`!zvBJYP&<}Ke~C9(r?>AOugD*L+yc0O%ZGz4ne##HHYGYCR4rNFOrCs#K6nf4LKLp4ar)wNUGZK0#vK~eQ(RKOJ^5NhizRqaa3LkgH3%`&XqeL5RV12TW}b_QPp!^fCJk1>5jVo+7dc;DQ?H~=i&uHBr;;0Mo8p$uLs8fni_q|Q2P=44<^ls4ZnPcK{lhk;xr*ZK>m4=g=0d*q+bbb_A_{lDAgbS9&Qj71Mi1_!l<+us=EXT^+@AMsb58abtZFjv;7`}2ks~L+zXWW#mdF_u^OZwF>Xp!@%1!roP1U?GU{46pt#5grF0C1|`^%`$T9Q(0(!aL+M|`o+X~^$?<M4g$``Y)lzSnZ@vHdl2JaS&@aP|R15|Z0_sc}O_GhiK^e~s(~zQDZLI}OH|^5PwT>l`J06n#FjeT0=)nsF1qua6#$ov~#+s|k>Eqbe4T-<56);OY^cj{l)4e$HuGH^S^ieB>Ruo1?7F=XODSQpfn`j|JtgU2IwttHBDRWv!0tEYzIjy*ncSOIQ*87tf=K`8%3Fl=GLt$&2%np}?oau8hx`IC~UI@kKfS8bCdabBF$YJnt+TqGks@6sjzr&eO-9g<Av9m_*)R^h22kd(3DQMtkUQb}(@RZyR#7Loe1${!RKxGdwD&Y&-7wt_Y0EL*#T0^9G)M{!I>%KmJBTL$*n5-g<(F+y&_!ByVcvGcx-e7ZS0uS-R+q2lueO$T=Ar$D2C-WOj09j&gQr;yB_>0?{x2YJHYy%5}&N@89zXjO6L<Kx8~aI}iRm7u1zQ4}78f%<16HOO-@EiRH67ta`-#+ih3|J)03wniHSz0C(<_*32`1Ok3P3K0${rpQ$(Zscz{SrhiA@<-^91wNnM(!|G)JEN<$o;N|Nkq2i6URxRt<VPLke&QY58VlMQR@n|vE;>;bj<9y5zeq@%KF5T0fNnmvS0leLj%M+yWLijrh{*no+unBbSA%eM%?l-`A>S>O@6J|M|e*n!B&y{U8GoJmi#GSTK19q+E=lR8FdBA1$8x@|5IzMt}B;S6cqLb~E$J$D)Hx9$-EttU7F}p~fylUtP#Lq|k<;f#NZ-gIS#($afvSIdGC(rloEvdi1*Zc3$t&;)%XW;YyALInK2>"
    )
)


def properties(codepoint: int, /) -> tuple[int, int, bool]:
    """Return `(gcb, incb, extended_pictographic)` for a code point."""
    block = _INDEX1[codepoint >> SHIFT]
    return ROWS[_INDEX2[(block << SHIFT) + (codepoint & ((1 << SHIFT) - 1))]]


# 🌊🪢🔚
