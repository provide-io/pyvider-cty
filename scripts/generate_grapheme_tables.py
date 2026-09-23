#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Regenerate `pyvider.cty._unicode._grapheme_tables`.

The source is the Unicode Character Database itself -- `Grapheme_Cluster_Break`
from `auxiliary/GraphemeBreakProperty.txt`, `InCB` from
`DerivedCoreProperties.txt`, and `Extended_Pictographic` from
`emoji/emoji-data.txt` -- fetched from unicode.org for `UNICODE_VERSION` below.

Up to Unicode 16.0.0 this read the same three properties out of `uniseg`, which
mirrors those files. `uniseg` has no Unicode 17 release, and following OpenTofu
1.13 (Go 1.27, `go-textseg` v17) means Unicode 17, so the files are now read
directly. The direct reader was checked against the `uniseg`-derived 16.0.0
table before being pointed at 17.0.0: at `UNICODE_VERSION = "16.0.0"` it emits
a table equal to that one at every one of the 1,114,112 code points.

    ./scripts/generate_grapheme_tables.py

The emitted table is checked in. Regenerate it when adopting a new Unicode
version, and expect the drift test in `tests/unicode/` to fail until its
expected version is updated too -- that failure is the point.
"""

from __future__ import annotations

import base64
from pathlib import Path
import subprocess  # nosec B404 - fixed argv, no shell, formatting our own output
import sys
import urllib.request
import zlib

UNICODE_VERSION = "17.0.0"
"""The UCD version to generate from. Change this, rerun, and update the test."""

UCD_BASE_URL = "https://www.unicode.org/Public/{version}/ucd/"
"""Where the UCD files for a given version are published."""

UCD_FILES = {
    "Grapheme_Cluster_Break": "auxiliary/GraphemeBreakProperty.txt",
    "InCB": "DerivedCoreProperties.txt",
    "Extended_Pictographic": "emoji/emoji-data.txt",
}

# Only these three properties are needed to implement UAX#29 grapheme
# clustering. Keeping only them collapses the table to under twenty distinct
# rows, which is what makes the emitted table 4 KB.

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
# SPDX-FileCopyrightText: Copyright (c) 1991-2025 Unicode, Inc.
# SPDX-License-Identifier: Unicode-3.0
#

"""Unicode {version} character properties for grapheme cluster breaking.

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

UNICODE_VERSION = "{version}"
"""The UCD version these tables were generated from.

go-cty does not pin its own: `cty/internal/graphemes` selects `go-textseg` v15
(Unicode 15.0) below Go 1.27 and v17 (Unicode 17.0) at or above it, so its
Unicode version follows whichever compiler built the binary. OpenTofu 1.13 is
built with Go 1.27, so this follows v17; a go-cty built with an older Go still
answers from 15.0.
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


def _read_property(name: str) -> dict[int, str]:
    """Code point -> value for one UCD property, from its published file.

    Lines are `START[..END] ; VALUE # comment`, except in
    `DerivedCoreProperties.txt`, where the enumerated `InCB` property is
    `START[..END] ; InCB; VALUE # comment` among many binary properties. A binary
    property's value is its own name.
    """
    url = UCD_BASE_URL.format(version=UNICODE_VERSION) + UCD_FILES[name]
    with urllib.request.urlopen(url) as response:  # nosec B310 - fixed https URL
        text = response.read().decode("utf-8")
    # `emoji-data.txt` names only the major.minor (`# Version: 17.0`), the others
    # the full version in their file name; both contain the major.minor.
    major_minor = ".".join(UNICODE_VERSION.split(".")[:2])
    if not any(major_minor in line for line in text.splitlines()[:10]):
        raise SystemExit(f"{url} does not declare itself as Unicode {major_minor}")
    values: dict[int, str] = {}
    for line in text.splitlines():
        data = line.split("#", 1)[0].strip()
        if not data:
            continue
        fields = [field.strip() for field in data.split(";")]
        if name == "InCB":
            if fields[1] != "InCB":
                continue
            value = fields[2]
        elif fields[1] != name and name != "Grapheme_Cluster_Break":
            continue
        else:
            value = fields[1]
        first, _, last = fields[0].partition("..")
        for codepoint in range(int(first, 16), int(last or first, 16) + 1):
            values[codepoint] = value
    if not values:
        raise SystemExit(f"{url} yielded no {name} values")
    return values


def main() -> int:
    unidata_version = UNICODE_VERSION
    gcb, incb, pictographic = (_read_property(name) for name in UCD_FILES)
    span = 0x110000

    def source_row(codepoint: int) -> tuple[int, int, bool]:
        return (
            GCB_NAMES.index(gcb.get(codepoint, "Other")),
            INCB_NAMES.index(incb.get(codepoint, "None")),
            codepoint in pictographic,
        )

    flat = [source_row(codepoint) for codepoint in range(span)]
    rows = sorted(set(flat))
    row_id = {row: i for i, row in enumerate(rows)}

    # Pick the shift that minimises index1 + index2 together. Larger blocks mean
    # a shorter index1 but less deduplication in index2, and the optimum is not
    # the same for every Unicode version.
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
    OUTPUT.write_text(source, encoding="utf-8")
    subprocess.run([sys.executable, "-m", "ruff", "format", str(OUTPUT)], check=False, capture_output=True)
    print(
        f"wrote {OUTPUT.relative_to(Path.cwd())}: Unicode {unidata_version}, "
        f"{len(rows)} rows, shift={shift}, {OUTPUT.stat().st_size / 1024:.1f} KB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 🌊🪢🔚
