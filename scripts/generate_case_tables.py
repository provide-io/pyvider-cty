#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Regenerate `pyvider.cty._unicode._case_tables`.

Go's `strings.ToUpper`, `ToLower` and `Title` map one rune to one rune through
the Unicode Character Database's *simple* case mapping -- fields 12, 13 and 14
of `UnicodeData.txt`. Python's `str.upper()` and friends apply the *full*
mapping from `SpecialCasing.txt` instead, which may produce more than one code
point (`ß` -> `SS`) and which has context-sensitive rules Go has none of (final
sigma). So `upper`, `lower` and `title` cannot be implemented with Python's own
case methods and match go-cty.

Python's standard library does not expose the simple mappings. Go's `unicode`
package *is* them -- it is generated from `UnicodeData.txt` and is the table
go-cty's own answers come from -- so this script reads them out of a Go
toolchain rather than re-parsing the UCD:

    go run ./scripts/_gocase   # not checked in; see _GO_PROGRAM below
    ./scripts/generate_case_tables.py

The emitted table holds only the code points where Python's per-character full
mapping *differs* from Go's simple one: 102 for uppercase, 1 for lowercase and
48 for titlecase, out of 1,114,112. Everywhere else `chr(cp).upper()` already
is the simple mapping, so storing all of it would be 7,000 redundant rows.

A **generation-time** dependency on a Go toolchain only. Nothing in `src/`
shells out to Go.
"""

from __future__ import annotations

from pathlib import Path
import subprocess  # nosec B404 - fixed argv, no shell
import sys
import tempfile

OUTPUT = Path(__file__).resolve().parent.parent / "src/pyvider/cty/_unicode/_case_tables.py"

# Every code point Go maps to something other than itself, with its simple
# upper, lower and title. Printed rather than returned because the point is to
# read Go's tables, and a Go program is the only thing that can.
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
\tfor r := rune(0); r <= 0x10FFFF; r++ {
\t\tu, l, t := unicode.ToUpper(r), unicode.ToLower(r), unicode.ToTitle(r)
\t\tif u != r || l != r || t != r {
\t\t\tfmt.Fprintf(w, "%d %d %d %d\\n", r, u, l, t)
\t\t}
\t}
}
"""

HEADER = '''#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Where Python's full case mapping differs from Unicode's simple one.

GENERATED FILE -- do not edit. Regenerate with
`scripts/generate_case_tables.py`, which needs a Go toolchain.

Go maps case one rune at a time through `UnicodeData.txt`'s simple mapping
fields, and go-cty's `upper`, `lower` and `title` are `strings.ToUpper`,
`strings.ToLower` and `strings.Title`. Python applies `SpecialCasing.txt`'s full
mapping, which can lengthen a string and which carries context-sensitive rules
Go does not implement. These three tables are exactly the disagreement: a code
point appears here only when `chr(cp).upper()` (or `.lower()`, `.title()`) is
not the single code point Go produces for it.

Everything absent from a table agrees, so `pyvider.cty._unicode.case` falls
back to Python's own method there rather than storing seven thousand rows that
say the same thing twice.
"""

from __future__ import annotations

UNICODE_VERSION = "{version}"
"""The UCD version the Go toolchain's `unicode` package carried when generated.

Python's `unicodedata` is a *different* version, and deliberately not pinned to
this one: the two agree at every one of the 1,114,112 code points on the simple
mappings, so the disagreement below is about simple-versus-full and nothing
else. That was checked at generation time rather than assumed.
"""

'''

FOOTER = "\n# 🌊🪢🔚\n"


def _go_case_data() -> tuple[str, dict[int, tuple[int, int, int]]]:
    """Go's simple case mappings, read out of a throwaway Go program."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "main.go").write_text(_GO_PROGRAM, encoding="utf-8")
        (root / "go.mod").write_text("module gocase\n\ngo 1.21\n", encoding="utf-8")
        completed = subprocess.run(  # nosec B603 B607 - fixed argv, no shell
            ["go", "run", "."], cwd=root, capture_output=True, text=True, check=True
        )
    version = ""
    mappings: dict[int, tuple[int, int, int]] = {}
    for line in completed.stdout.splitlines():
        if line.startswith("version "):
            version = line.split()[1]
            continue
        codepoint, upper, lower, title = (int(field) for field in line.split())
        mappings[codepoint] = (upper, lower, title)
    if not version:
        raise SystemExit("the Go program reported no unicode.Version")
    return version, mappings


def _exceptions(mappings: dict[int, tuple[int, int, int]]) -> tuple[dict[int, int], ...]:
    """Per method, the code points where Python and Go disagree.

    Every disagreement must be Python producing *more than one* code point,
    which is what makes it a simple-versus-full mapping difference. A
    single-code-point disagreement would instead mean the Go toolchain and
    Python carry different Unicode versions, and a table built from the newer
    one would then be wrong for callers of the older -- so that is refused here
    rather than silently vendored.
    """
    tables: tuple[dict[int, int], ...] = ({}, {}, {})
    for codepoint in range(0x110000):
        character = chr(codepoint)
        expected = mappings.get(codepoint, (codepoint, codepoint, codepoint))
        for table, method, wanted in zip(
            tables, (character.upper, character.lower, character.title), expected, strict=True
        ):
            answer = method()
            if answer == chr(wanted):
                continue
            if len(answer) == 1:
                raise SystemExit(
                    f"U+{codepoint:04X}: Python says {answer!r} and Go says {chr(wanted)!r}, both a "
                    "single code point. That is a Unicode version difference, not a "
                    "simple-versus-full mapping difference; resolve it before vendoring."
                )
            table[codepoint] = wanted
    return tables


def _render(name: str, table: dict[int, int], what: str) -> str:
    rows = "".join(f"    0x{key:04X}: 0x{value:04X},\n" for key, value in sorted(table.items()))
    return f'{name}: dict[int, int] = {{\n{rows}}}\n"""{what}"""\n\n'


def main() -> int:
    version, mappings = _go_case_data()
    upper, lower, title = _exceptions(mappings)
    body = HEADER.format(version=version)
    body += _render(
        "SIMPLE_UPPER",
        upper,
        "Code point -> its simple uppercase, where `str.upper()` disagrees.",
    )
    body += _render(
        "SIMPLE_LOWER",
        lower,
        "Code point -> its simple lowercase, where `str.lower()` disagrees.\n\n"
        "One entry: U+0130, whose full lowercase keeps a combining dot above and\n"
        "whose simple lowercase is a bare `i`.",
    )
    body += _render(
        "SIMPLE_TITLE",
        title,
        "Code point -> its simple titlecase, where `str.title()` disagrees.",
    )
    OUTPUT.write_text(body + FOOTER, encoding="utf-8")
    print(
        f"wrote {OUTPUT} from Unicode {version}: "
        f"{len(upper)} upper, {len(lower)} lower, {len(title)} title exceptions"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

# 🌊🪢🔚
