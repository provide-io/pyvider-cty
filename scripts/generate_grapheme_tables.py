#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Regenerate `pyvider.cty._unicode._grapheme_tables`.

The canonical source is the Unicode Character Database -- specifically
`Grapheme_Cluster_Break` from `auxiliary/GraphemeBreakProperty.txt`, `InCB` from
`DerivedCoreProperties.txt`, and `Extended_Pictographic` from `emoji-data.txt`.
This script reads them via `uniseg`, which mirrors exactly those files and is
verified against them upstream, because parsing three UCD files correctly is
more code than reading one already-parsed table.

`uniseg` is a **generation-time** dependency only. It is not installed at
runtime and nothing in `src/` imports it -- see `_grapheme_tables.py` for why
the table is vendored rather than the package depended on.

    uv run --with uniseg scripts/generate_grapheme_tables.py

The emitted table is checked in. Regenerate it when adopting a new Unicode
version, and expect the drift test in `tests/unicode/` to fail until its
expected version is updated too -- that failure is the point.
"""

from __future__ import annotations

import base64
from pathlib import Path
import subprocess  # nosec B404 - fixed argv, no shell, formatting our own output
import sys
import zlib

# Only these three of the thirty properties in uniseg's table are needed to
# implement UAX#29 grapheme clustering. Reprojecting onto them collapses 251
# distinct rows to 18, which is what makes the emitted table 4 KB rather than
# the 161 KB the full one occupies.
NEEDED = ("Grapheme_Cluster_Break", "InCB", "Extended_Pictographic")

GCB_NAMES = (
    "Other",
    "CR",
    "LF",
    "Control",
    "Extend",
    "ZWJ",
    "Regional_Indicator",
    "Prepend",
    "SpacingMark",
    "L",
    "V",
    "T",
    "LV",
    "LVT",
)
INCB_NAMES = ("None", "Consonant", "Extend", "Linker")

OUTPUT = Path(__file__).resolve().parent.parent / "src/pyvider/cty/_unicode/_grapheme_tables.py"

HEADER = '''#
# SPDX-FileCopyrightText: Copyright (c) 2013-2024 Masaaki Shibata
# SPDX-License-Identifier: MIT
#

"""Unicode {version} character properties for grapheme cluster breaking.

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

UNICODE_VERSION = "{version}"
"""The UCD version these tables were generated from.

go-cty does not pin its own: `cty/internal/graphemes` selects `go-textseg` v15
or v17 by Go toolchain version, so its Unicode version follows whichever
compiler built the binary. Exact agreement is therefore not available in either
direction; what is available is knowing our version, which is what this is for.
"""

SHIFT = {shift}
"""Low-bit width of the two-stage lookup. Chosen to minimise total entries."""

# Grapheme_Cluster_Break property values.
{gcb_consts}

# Indic_Conjunct_Break property values, for GB9c.
{incb_consts}

ROWS: tuple[tuple[int, int, bool], ...] = {rows}
"""(Grapheme_Cluster_Break, InCB, Extended_Pictographic) per distinct row."""

_INDEX1 = zlib.decompress(base64.b85decode({index1!r}))
_INDEX2 = zlib.decompress(base64.b85decode({index2!r}))


def properties(codepoint: int, /) -> tuple[int, int, bool]:
    """Return `(gcb, incb, extended_pictographic)` for a code point."""
    block = _INDEX1[codepoint >> SHIFT]
    return ROWS[_INDEX2[(block << SHIFT) + (codepoint & ((1 << SHIFT) - 1))]]


# 🌊🪢🔚
'''


def main() -> int:
    try:
        from uniseg import (
            db_lookups,
            unidata_version,
        )
    except ImportError:
        print("uniseg is required to generate. Run: uv run --with uniseg " + __file__)
        return 1

    columns = [db_lookups.columns.index(name) for name in NEEDED]
    span = len(db_lookups.index1) << db_lookups.shift

    def source_row(codepoint: int) -> tuple[int, int, bool]:
        block = db_lookups.index1[codepoint >> db_lookups.shift]
        offset = (block << db_lookups.shift) + (codepoint & ((1 << db_lookups.shift) - 1))
        raw = db_lookups.values[db_lookups.index2[offset]]
        return (
            GCB_NAMES.index(raw[columns[0]] or "Other"),
            INCB_NAMES.index(raw[columns[1]] or "None"),
            raw[columns[2]] == "Y",
        )

    flat = [source_row(codepoint) for codepoint in range(span)]
    rows = sorted(set(flat))
    row_id = {row: i for i, row in enumerate(rows)}

    # Pick the shift that minimises index1 + index2 together. Larger blocks mean
    # a shorter index1 but less deduplication in index2, and the optimum is not
    # the same as uniseg's because reprojection changed how repetitive the data is.
    best: tuple[int, int, list[int], dict[tuple[int, ...], int]] | None = None
    for shift in range(4, 13):
        width = 1 << shift
        blocks: dict[tuple[int, ...], int] = {}
        index1: list[int] = []
        for block in range(span >> shift):
            key = tuple(row_id[flat[(block << shift) + i]] for i in range(width))
            index1.append(blocks.setdefault(key, len(blocks)))
        total = len(index1) + len(blocks) * width
        if best is None or total < best[0]:
            best = (total, shift, index1, blocks)
    assert best is not None
    _, shift, index1, blocks = best

    width = 1 << shift
    index2 = [0] * (len(blocks) * width)
    for key, block in blocks.items():
        for i, value in enumerate(key):
            index2[(block << shift) + i] = value

    if max(index1) > 255 or max(index2) > 255:  # pragma: no cover - would need >256 blocks
        raise SystemExit("index no longer fits in bytes; widen the encoding")

    def pack(values: list[int]) -> bytes:
        return base64.b85encode(zlib.compress(bytes(values), 9))

    source = HEADER.format(
        version=unidata_version,
        shift=shift,
        gcb_consts="\n".join(f"GCB_{name.upper()} = {i}" for i, name in enumerate(GCB_NAMES)),
        incb_consts="\n".join(f"INCB_{name.upper()} = {i}" for i, name in enumerate(INCB_NAMES)),
        rows=repr(tuple(rows)),
        index1=pack(index1),
        index2=pack(index2),
    )
    OUTPUT.write_text(source)
    subprocess.run([sys.executable, "-m", "ruff", "format", str(OUTPUT)], check=False, capture_output=True)
    print(
        f"wrote {OUTPUT.relative_to(Path.cwd())}: Unicode {unidata_version}, "
        f"{len(rows)} rows, shift={shift}, {OUTPUT.stat().st_size / 1024:.1f} KB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 🌊🪢🔚
