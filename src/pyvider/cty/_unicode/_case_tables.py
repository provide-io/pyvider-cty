#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Go's simple case mappings, all of them, at Unicode 17.0.0.

GENERATED FILE -- do not edit. Regenerate with
`scripts/generate_case_tables.py`, which needs a Go toolchain.

go-cty's `upper`, `lower` and `title` are `strings.ToUpper`, `strings.ToLower`
and `strings.Title`, which map one rune at a time through the Go `unicode`
package's simple case mapping. These tables are that mapping, read out of Go
itself: every code point `unicode.ToUpper`, `ToLower` or `ToTitle` changes, and
nothing else. `pyvider.cty._unicode.case` answers from them alone, so the result
does not depend on which Unicode version the running Python carries.

Packed as signed 32-bit little-endian integers, four per mapped code point --
the gap from the previous code point, then upper, lower and title as offsets
from the code point itself -- compressed and base85-encoded, because
2,989 code points written as dict literals would be thousands of lines.
"""

from __future__ import annotations

import base64
import struct
import zlib

UNICODE_VERSION = "17.0.0"
"""Go's `unicode.Version` when these tables were generated.

Go 1.27, which OpenTofu 1.13 builds with, carries 17.0.0.
"""

_PACKED = b"c-rlqTWAzl7{~XPiw(UgQjMwFf+kIfmxy91B?(#z_Q671p#h62Li;GCKBNyJqz}^KL#Yp?5N%4Vg*=&u7OE{KQBf?mN!txc7PLt<J`{?9LM*81ewqK^*)KcJtb3cy{1?Kvzxkj0`OcY{b7nTJA?vdqHca*vS0w-boS&Z$!G_7c;+K;4R>bNnu~qcnf^wt?`O*Ii$Hi#x4)k@0(f_8MNBDV!r%rvT>o4M%@G5*?Re<~>0dM~Z{f~M8^drXnlJETfxNoso;qwT4-iY^Gnsl-$&o3FKcU6VE>M_1OU+h)kt|<OF%kunca67)Y8~X1m{AdRG^+D@{-g?Snu}<m74erMGZbKi-aeun$lNsh`hmYnd{RtIrBFF8K@R(lIga7V?CbrDD?+P2?&G`4zlqcWegFIgkfCtzfp0D3>?O$K1^X26No<FHmchfs@jQ1}O*DG+mp+2+o@qRVl>x}r#_%1dbdrALgmHsO#-m3+^p2|jFhx)HW{cFHA;I-hj;7y3X3Gti2O_<NOfww_7S@a#?9pLTY?Fhg38(gC&Z7fZCuR#|p@wY<X3jICkVukC#b>Q9L-H5*#@i!xWBe)T4h8LcD!D6us*Wb{^Mpb-C{~p5ML-+>h4Y=N`2aBzgeG-HhEBZ$08<E~F<hKjuF?DILdg%3Obm6n$v*22Atpoo67F(XQ8^B^^KW8QKTZ#OZgT;QEv~R-q#5QE<uWr}Ju{8HL4`X}&{m|G?Txct`f3iX4>%?~W7RAjfd~=cZXSiRLIZwjBCgGn6aKZy~KWs5ifv0?0zCrLHcnCb?!1Ady{AC#WF!W2{OPHTV!K2WxfUkh>fba17&lh?>xF38Pd>UL~oI8Y%LO*Jxf5Et3?8W!q4E8Vn^LYOnQTG>NkNmnyH)zcBZ*ZCC=U}s*&x6K1|5JC;m$7}QQ_s8pWC^VoXRFVGXW9SMsZ*yO_~$>isBmO*E?D*_N8oQG@JBK^S6q!38V}T@`X8B`3yvr*S1iv%4B9W%B0ibySI*R5zs3L<`66|EkjZ3nP`EObAC~!8KW~&v{y3S@=eH~tEBZ0;F>nvK2Ydp2!hw&2kAqKwPl6NR1bFxptFB_*)+6letCoLLpN}Dv{m9V_!=Fk1#Xhx;iIwLOXP&TF?9)lR6S~+BxPD2UI(6#QsZ*z(Q(f*iE`l!_@3*y1^Zj7z)TvVsx?X9l*%gCB#+qI+IG^>4=DGY)_8;qC!u}gm`9&Uq&Ga&5`cEjd2gmj}@ILUqN92RxgAUvU?sDKm;6o1F3GPh8oF7?#*5A2&G9TLS;E65snEv-JJZH?eiNCO4nzUsO`Sq*#nev>&`9#;Z!ejk<9JtIS{a7gV_ZqyOKR<I}`}Y|t9NMo-h1cBe!gl-B<3Qi^gZ5llFS?!@{>=3U<&jT~VQ(NUvCDD%DRmzbB)*OIxQ+X*AaTs){<8@Kq*{d|`-f-HUo+@mvVZs)Ou&2}ha6Pq`$FU(vzPV%Wn-z=@71%ZyxP#?aqGKS;c@VIym0#!H{z+~i>mTZDSbNbZ9m&hx9{bKRQj5^pG2KHb?VeJ(JQlz@3x-uc+&P_y;W?OOwJ)k6qhSr(ZTUged+2e*ghq#A6eq{i?aWzQ(v<BV>wFy?%~o{&x(1BKi-!5zH&C@*<$Q5@co$F=s&il`rClw?-ZX?Y{$3z;~%AuDgIk=Z**}vgWMk@>iM6aRC`^{@%->*8`sZG{oLEuvDGf&_b2`Kz+H>QJ}dLm`xc80lgVUqK=|D^ta)<1nm5V*V0j#k|NqIqd<r*Ib*lf!<U;W{{Ba!qNhTMH+d2NoS#TN06FCb$3_q$>{^eJWlvsI7t-cWt`UL!E0{-M@F17NOT7BK}yMP~<Zc+Y3CX*Ml{516-#?K(e6PZj-&+l-(JFi^D_3FIxnkxER(3#^QxZM60{h#BX;~}X09Q<I7@(*%xSRTv0iT=5X{vsET8$Yu8<$2X#WU|fI;4jzUKV-7a{{!LrPf7"


def _unpack() -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    raw = zlib.decompress(base64.b85decode(_PACKED))
    values = struct.unpack(f"<{len(raw) // 4}i", raw)
    upper: dict[int, int] = {}
    lower: dict[int, int] = {}
    title: dict[int, int] = {}
    codepoint = 0
    for i in range(0, len(values), 4):
        codepoint += values[i]
        for table, offset in zip((upper, lower, title), values[i + 1 : i + 4], strict=True):
            if offset:
                table[codepoint] = codepoint + offset
    return upper, lower, title


SIMPLE_UPPER, SIMPLE_LOWER, SIMPLE_TITLE = _unpack()
"""Code point -> Go's `unicode.ToUpper`, `ToLower` and `ToTitle`, where not itself."""

TITLE_SEPARATORS: frozenset[int] = frozenset(
    {
        0x0085,
        0x00A0,
        0x1680,
        0x2000,
        0x2001,
        0x2002,
        0x2003,
        0x2004,
        0x2005,
        0x2006,
        0x2007,
        0x2008,
        0x2009,
        0x200A,
        0x2028,
        0x2029,
        0x202F,
        0x205F,
        0x3000,
    }
)
"""Non-ASCII runes after which `strings.Title` titlecases the next one.

Go's `isSeparator` above ASCII: not a letter, not a digit, and `unicode.IsSpace`.
"""

# 🌊🪢🔚
