#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Regenerate `pyvider.cty._unicode._case_tables`.

Go's `strings.ToUpper`, `ToLower` and `Title` map one rune to one rune through
the Unicode Character Database's *simple* case mapping -- fields 12, 13 and 14
of `UnicodeData.txt` -- as carried by the Go toolchain's `unicode` package.
go-cty's `upper`, `lower` and `title` are exactly those functions, so the
answer is whatever that package says, at whatever Unicode version it carries.

This script reads the package directly, through a throwaway Go program, and
vendors *all* of it: every code point `unicode.ToUpper`, `ToLower` or `ToTitle`
maps to something other than itself, plus the non-ASCII runes
`strings.Title` treats as word separators. Nothing is compared against Python.

An earlier version stored only where Python's full mapping disagreed with Go's
simple one and asked `str.upper()` for the rest. That made the answer follow
the *running* interpreter's `unicodedata` -- 14.0 on Python 3.11, 16.0 on 3.14
-- and so could never reach the Unicode version Go carries.

    ./scripts/generate_case_tables.py

A **generation-time** dependency on a Go toolchain only. Nothing in `src/`
shells out to Go. Use the Go that OpenTofu builds with: its `unicode.Version`
becomes `UNICODE_VERSION` in the emitted table.
"""

from __future__ import annotations

import base64
import importlib.util
from pathlib import Path
import struct
import subprocess  # nosec B404 - fixed argv, no shell
import sys
import tempfile
import zlib

OUTPUT = Path(__file__).resolve().parent.parent / "src/pyvider/cty/_unicode/_case_tables.py"

# Every code point Go maps to something other than itself, with its simple
# upper, lower and title, then every non-ASCII rune `strings.Title` starts a
# word after. Printed rather than returned because the point is to read Go's
# tables, and a Go program is the only thing that can. `isSeparator` is
# transcribed from `strings/strings.go`, which does not export it.
_GO_PROGRAM = """package main

import (
\t"bufio"
\t"fmt"
\t"os"
\t"unicode"
)

func main() {
\tw := bufio.NewWriter(os.Stdout)
\tdefer w.Flush()
\tfmt.Fprintf(w, "version %s\\n", unicode.Version)
\tfor r := rune(0); r <= unicode.MaxRune; r++ {
\t\tu, l, t := unicode.ToUpper(r), unicode.ToLower(r), unicode.ToTitle(r)
\t\tif u != r || l != r || t != r {
\t\t\tfmt.Fprintf(w, "map %d %d %d %d\\n", r, u, l, t)
\t\t}
\t\tif r > 0x7F && !unicode.IsLetter(r) && !unicode.IsDigit(r) && unicode.IsSpace(r) {
\t\t\tfmt.Fprintf(w, "sep %d\\n", r)
\t\t}
\t}
}
"""

HEADER = '''#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Go's simple case mappings, all of them, at Unicode {version}.

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
{count:,} code points written as dict literals would be thousands of lines.
"""

from __future__ import annotations

import base64
import struct
import zlib

UNICODE_VERSION = "{version}"
"""Go's `unicode.Version` when these tables were generated.

Go 1.27, which OpenTofu 1.13 builds with, carries 17.0.0.
"""

_PACKED = {packed!r}


def _unpack() -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    raw = zlib.decompress(base64.b85decode(_PACKED))
    values = struct.unpack(f"<{{len(raw) // 4}}i", raw)
    upper: dict[int, int] = {{}}
    lower: dict[int, int] = {{}}
    title: dict[int, int] = {{}}
    codepoint = 0
    for i in range(0, len(values), 4):
        codepoint += values[i]
        for table, offset in zip((upper, lower, title), values[i + 1 : i + 4], strict=True):
            if offset:
                table[codepoint] = codepoint + offset
    return upper, lower, title


SIMPLE_UPPER, SIMPLE_LOWER, SIMPLE_TITLE = _unpack()
"""Code point -> Go's `unicode.ToUpper`, `ToLower` and `ToTitle`, where not itself."""

TITLE_SEPARATORS: frozenset[int] = frozenset({{{separators}}})
"""Non-ASCII runes after which `strings.Title` titlecases the next one.

Go's `isSeparator` above ASCII: not a letter, not a digit, and `unicode.IsSpace`.
"""
'''

FOOTER = "\n# 🌊🪢🔚\n"


def _go_case_data() -> tuple[str, dict[int, tuple[int, int, int]], list[int]]:
    """Go's simple case mappings and title separators, from a throwaway Go program."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "main.go").write_text(_GO_PROGRAM, encoding="utf-8")
        (root / "go.mod").write_text("module gocase\n\ngo 1.21\n", encoding="utf-8")
        completed = subprocess.run(  # nosec B603 B607 - fixed argv, no shell
            ["go", "run", "."], cwd=root, capture_output=True, text=True, check=True
        )
    version = ""
    mappings: dict[int, tuple[int, int, int]] = {}
    separators: list[int] = []
    for line in completed.stdout.splitlines():
        kind, *fields = line.split()
        if kind == "version":
            version = fields[0]
        elif kind == "map":
            codepoint, upper, lower, title = (int(field) for field in fields)
            mappings[codepoint] = (upper, lower, title)
        elif kind == "sep":
            separators.append(int(fields[0]))
    if not version or not mappings:
        raise SystemExit("the Go program reported no unicode.Version or no mappings")
    return version, mappings, separators


def _pack(mappings: dict[int, tuple[int, int, int]]) -> bytes:
    values: list[int] = []
    previous = 0
    for codepoint in sorted(mappings):
        upper, lower, title = mappings[codepoint]
        values += [codepoint - previous, upper - codepoint, lower - codepoint, title - codepoint]
        previous = codepoint
    return base64.b85encode(zlib.compress(struct.pack(f"<{len(values)}i", *values), 9))


def main() -> int:
    version, mappings, separators = _go_case_data()
    body = HEADER.format(
        version=version,
        count=len(mappings),
        packed=_pack(mappings),
        separators=", ".join(f"0x{codepoint:04X}" for codepoint in separators),
    )
    OUTPUT.write_text(body + FOOTER, encoding="utf-8")
    subprocess.run([sys.executable, "-m", "ruff", "format", str(OUTPUT)], check=False, capture_output=True)

    # Read the emitted module back and check it against Go at every code point,
    # so a packing bug cannot ship as a table that merely looks plausible.
    spec = importlib.util.spec_from_file_location("_emitted_case_tables", OUTPUT)
    assert spec is not None and spec.loader is not None
    emitted = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(emitted)
    tables = (emitted.SIMPLE_UPPER, emitted.SIMPLE_LOWER, emitted.SIMPLE_TITLE)
    for codepoint in range(0x110000):
        expected = mappings.get(codepoint, (codepoint, codepoint, codepoint))
        got = tuple(table.get(codepoint, codepoint) for table in tables)
        if got != expected:
            raise SystemExit(f"U+{codepoint:04X}: emitted {got}, Go says {expected}")
    if frozenset(separators) != emitted.TITLE_SEPARATORS:
        raise SystemExit("emitted title separators differ from Go's")

    print(
        f"wrote {OUTPUT} from Unicode {version}: {len(mappings)} mapped code points, "
        f"{len(separators)} title separators, {OUTPUT.stat().st_size / 1024:.1f} KB; "
        "verified at all 1,114,112 code points"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 🌊🪢🔚
